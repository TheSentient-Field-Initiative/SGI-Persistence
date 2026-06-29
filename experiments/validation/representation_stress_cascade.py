#!/usr/bin/env python3
"""
Phase 003J Division 4: Representation Stress Cascade
Applies sequential degradation:
1. corruption
2. projection
3. quantization
4. shuffling
5. truncation

Tracks:
- Survivor decay trajectories
- Collapse ordering
- Irreversibility

Usage:
    python experiments/validation/representation_stress_cascade.py
"""

import numpy as np
import json
import os
import sys
import time

# Add source paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'distributed'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'immune'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'ant_colony'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'institution'))

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_SEEDS = 5
NUM_TIMESTEPS = 200
NUM_DEGRADATION_LEVELS = 10  # 0%, 10%, 20%, ..., 90%, 100%


# ============================================================
# SYNTHETIC SYSTEMS
# ============================================================

class EpidemicSystem:
    def __init__(self, n_nodes=100, seed=42):
        self.n_nodes = n_nodes
        self.rng = np.random.RandomState(seed)
        self.state = self.rng.choice(['S', 'I', 'R'], size=n_nodes, p=[0.7, 0.2, 0.1])
        self.adjacency = self._create_random_graph()
        self.history = []

    def _create_random_graph(self):
        adj = np.zeros((self.n_nodes, self.n_nodes))
        for i in range(self.n_nodes):
            n_neighbors = self.rng.randint(2, 6)
            neighbors = self.rng.choice(self.n_nodes, n_neighbors, replace=False)
            adj[i, neighbors] = 1
            adj[neighbors, i] = 1
        return adj

    def step(self):
        new_state = self.state.copy()
        for i in range(self.n_nodes):
            if self.state[i] == 'S':
                infected_neighbors = np.sum(self.adjacency[i, self.state == 'I'])
                if infected_neighbors > 0 and self.rng.random() < 0.3 * infected_neighbors / 5:
                    new_state[i] = 'I'
            elif self.state[i] == 'I':
                if self.rng.random() < 0.1:
                    new_state[i] = 'R'
        self.state = new_state
        state_map = {'S': 0, 'I': 1, 'R': 2}
        numerical = np.array([state_map[s] for s in self.state], dtype=float)
        record = {'timestep': len(self.history)}
        for i, val in enumerate(numerical):
            record[f'node_{i}'] = float(val)
        self.history.append(record)
        return record


class NeuralSystem:
    def __init__(self, n_neurons=100, seed=42):
        self.n_neurons = n_neurons
        self.rng = np.random.RandomState(seed)
        self.weights = self.rng.randn(n_neurons, n_neurons) * 0.1
        self.activity = self.rng.randn(n_neurons) * 0.5
        self.history = []

    def step(self):
        noise = self.rng.randn(self.n_neurons) * 0.01
        self.activity = np.tanh(self.weights @ self.activity + noise)
        outer = np.outer(self.activity, self.activity)
        self.weights = self.weights * 0.9 + 0.01 * outer
        self.weights = np.clip(self.weights, -2, 2)
        record = {'timestep': len(self.history)}
        for i, val in enumerate(self.activity):
            record[f'neuron_{i}'] = float(val)
        self.history.append(record)
        return record


class MarketSystem:
    def __init__(self, n_agents=100, seed=42):
        self.n_agents = n_agents
        self.rng = np.random.RandomState(seed)
        self.wealth = self.rng.uniform(10, 100, n_agents)
        self.strategy = self.rng.choice(['bull', 'bear', 'neutral'], n_agents)
        self.price = 50.0
        self.history = []

    def step(self):
        demand = sum(1 if s == 'bull' else -1 if s == 'bear' else 0 for s in self.strategy)
        self.price += 0.1 * demand / self.n_agents + self.rng.randn() * 0.5
        self.price = max(1, self.price)
        for i in range(self.n_agents):
            if self.rng.random() < 0.1:
                if self.price > 60:
                    self.strategy[i] = 'bear'
                elif self.price < 40:
                    self.strategy[i] = 'bull'
                else:
                    self.strategy[i] = self.rng.choice(['bull', 'bear', 'neutral'])
            if self.strategy[i] == 'bull':
                self.wealth[i] *= (1 + 0.1 * self.rng.randn())
            elif self.strategy[i] == 'bear':
                self.wealth[i] *= (1 - 0.1 * self.rng.randn())
            self.wealth[i] = max(0, self.wealth[i])
        record = {'timestep': len(self.history)}
        for i, val in enumerate(self.wealth):
            record[f'agent_{i}'] = float(val)
        self.history.append(record)
        return record


class EcologicalSystem:
    def __init__(self, n_patches=100, seed=42):
        self.n_patches = n_patches
        self.rng = np.random.RandomState(seed)
        self.prey = self.rng.uniform(20, 80, n_patches)
        self.predators = self.rng.uniform(10, 30, n_patches)
        self.history = []

    def step(self):
        noise_prey = self.rng.randn(self.n_patches) * 0.5
        noise_pred = self.rng.randn(self.n_patches) * 0.2
        d_prey = 0.5 * self.prey - 0.02 * self.prey * self.predators + noise_prey
        d_pred = 0.5 * self.prey * self.predators - 0.3 * self.predators + noise_pred
        self.prey = np.clip(self.prey + d_prey, 0, 200)
        self.predators = np.clip(self.predators + d_pred, 0, 100)
        record = {'timestep': len(self.history)}
        for i in range(self.n_patches):
            record[f'prey_{i}'] = float(self.prey[i])
            record[f'predator_{i}'] = float(self.predators[i])
        self.history.append(record)
        return record


def trajectory_to_matrix(trajectory, max_dim=64):
    all_keys = set()
    for state in trajectory[:5]:
        all_keys.update(state.keys())
    all_keys.discard('timestep')
    all_keys.discard('cov_eigenvalues')
    keys = sorted(all_keys)[:max_dim]
    vectors = []
    for state in trajectory:
        v = []
        for k in keys:
            val = state.get(k, 0)
            if isinstance(val, (list, tuple, np.ndarray)):
                v.append(0.0)
            elif isinstance(val, str):
                v.append(0.0)
            else:
                v.append(float(val))
        vectors.append(v)
    return np.array(vectors), keys


def compute_effective_dimensionality(matrix):
    if len(matrix) > matrix.shape[1]:
        try:
            cov = np.cov(matrix.T)
            eigenvalues = np.linalg.eigvalsh(cov)
            eigenvalues = eigenvalues[eigenvalues > 1e-10]
            if len(eigenvalues) > 0:
                participation_ratio = (np.sum(eigenvalues) ** 2) / np.sum(eigenvalues ** 2)
                return float(participation_ratio)
        except:
            pass
    return 1.0


# ============================================================
# DEGRADATION OPERATORS
# ============================================================

def apply_corruption(matrix, level, rng):
    """Apply additive Gaussian corruption."""
    noise = rng.randn(*matrix.shape) * level * np.std(matrix)
    return matrix + noise


def apply_projection(matrix, level, rng):
    """Project onto top-k dimensions (retain 1-level fraction)."""
    n_dims = matrix.shape[1]
    keep_dims = max(1, int(n_dims * (1 - level)))
    if keep_dims >= n_dims:
        return matrix
    # PCA projection
    cov = np.cov(matrix.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    # Sort by eigenvalue (descending)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, idx[:keep_dims]]
    return matrix @ eigenvectors


def apply_quantization(matrix, level, rng):
    """Quantize to fewer levels."""
    if level == 0:
        return matrix
    n_levels = max(2, int(256 * (1 - level)))
    # Quantize each dimension
    quantized = np.zeros_like(matrix)
    for d in range(matrix.shape[1]):
        col = matrix[:, d]
        min_val, max_val = col.min(), col.max()
        if max_val > min_val:
            # Map to [0, n_levels-1] and back
            normalized = (col - min_val) / (max_val - min_val)
            quantized_levels = np.round(normalized * (n_levels - 1))
            quantized[:, d] = quantized_levels / (n_levels - 1) * (max_val - min_val) + min_val
        else:
            quantized[:, d] = col
    return quantized


def apply_shuffling(matrix, level, rng):
    """Shuffle temporal order."""
    if level == 0:
        return matrix
    n_shuffle = int(len(matrix) * level)
    shuffled = matrix.copy()
    indices = rng.permutation(len(matrix))[:n_shuffle]
    shuffled[indices] = rng.permutation(shuffled[indices])
    return shuffled


def apply_truncation(matrix, level, rng):
    """Truncate to fewer timesteps."""
    if level == 0:
        return matrix
    keep_timesteps = max(2, int(len(matrix) * (1 - level)))
    return matrix[:keep_timesteps]


# ============================================================
# SURVIVOR OBSERVABLES
# ============================================================

def compute_tier1_survivors(matrix):
    """Compute Tier-1 survivor observables."""
    results = {}

    # 1. Lagged stability
    if len(matrix) > 10:
        autocorr = []
        for lag in range(1, min(11, len(matrix) // 2)):
            c = np.corrcoef(matrix[:-lag].flatten(), matrix[lag:].flatten())[0, 1]
            if not np.isnan(c):
                autocorr.append(c)
        results['lagged_stability'] = float(np.mean(autocorr)) if autocorr else 0.0
    else:
        results['lagged_stability'] = 0.0

    # 2. Transition density
    if len(matrix) > 1:
        changes = np.abs(np.diff(matrix, axis=0))
        std_per_dim = np.std(matrix, axis=0)
        std_per_dim[std_per_dim == 0] = 1
        transition_mask = changes > 0.1 * std_per_dim
        results['transition_density'] = float(np.mean(transition_mask))
    else:
        results['transition_density'] = 0.0

    # 3. Approximate entropy
    flat = matrix.flatten()
    hist, _ = np.histogram(flat, bins=50, density=True)
    hist = hist[hist > 0]
    results['approx_entropy'] = float(-np.sum(hist * np.log(hist + 1e-10)))

    return results


# ============================================================
# CASCADE EXPERIMENT
# ============================================================

def run_representation_stress_cascade():
    """Run the full representation stress cascade."""
    from study_001 import DistributedSystem
    from study_001c_immune import ImmuneSignalingNetwork
    from study_001b_colony import AntColony
    from study_001d_institution import InstitutionNetwork

    systems = {
        "distributed": {"class": DistributedSystem, "kwargs": {"n_nodes": 100}},
        "immune": {"class": ImmuneSignalingNetwork, "kwargs": {"n_cells": 100}},
        "ant_colony": {"class": AntColony, "kwargs": {"n_ants": 50, "n_food": 100}},
        "institution": {"class": InstitutionNetwork, "kwargs": {"n_agents": 100}},
        "epidemic": {"class": EpidemicSystem, "kwargs": {"n_nodes": 100}},
        "neural": {"class": NeuralSystem, "kwargs": {"n_neurons": 100}},
        "market": {"class": MarketSystem, "kwargs": {"n_agents": 100}},
        "ecological": {"class": EcologicalSystem, "kwargs": {"n_patches": 100}},
    }

    degradation_operators = {
        'corruption': apply_corruption,
        'projection': apply_projection,
        'quantization': apply_quantization,
        'shuffling': apply_shuffling,
        'truncation': apply_truncation
    }

    all_results = {}

    for sys_name, sys_info in systems.items():
        print(f"\nRunning cascade for {sys_name}...")
        sys_results = {}

        for seed in range(NUM_SEEDS):
            try:
                system = sys_info["class"](seed=seed, **sys_info["kwargs"])
                trajectory = []
                for _ in range(NUM_TIMESTEPS):
                    trajectory.append(system.step())

                matrix, keys = trajectory_to_matrix(trajectory)
                baseline_survivors = compute_tier1_survivors(matrix)
                baseline_ed = compute_effective_dimensionality(matrix)

                seed_results = {
                    'baseline': {
                        'survivors': baseline_survivors,
                        'effective_dimensionality': baseline_ed
                    },
                    'cascade': {}
                }

                for op_name, op_func in degradation_operators.items():
                    op_results = []
                    rng = np.random.RandomState(seed)

                    for level in np.linspace(0, 1, NUM_DEGRADATION_LEVELS):
                        degraded = op_func(matrix, level, rng)
                        survivors = compute_tier1_survivors(degraded)
                        ed = compute_effective_dimensionality(degraded)
                        op_results.append({
                            'level': float(level),
                            'survivors': survivors,
                            'effective_dimensionality': ed
                        })

                    seed_results['cascade'][op_name] = op_results

                sys_results[seed] = seed_results
                print(f"  Seed {seed}: baseline ED={baseline_ed:.4f}")

            except Exception as e:
                print(f"  Seed {seed}: ERROR - {e}")

        # Aggregate across seeds
        if sys_results:
            agg = aggregate_cascade_results(sys_results, degradation_operators.keys())
            all_results[sys_name] = {
                'seeds': sys_results,
                'aggregate': agg,
                'n_seeds': len(sys_results)
            }

    return all_results


def aggregate_cascade_results(sys_results, operator_names):
    """Aggregate cascade results across seeds."""
    agg = {}

    for op_name in operator_names:
        op_agg = []
        for level_idx, level in enumerate(np.linspace(0, 1, NUM_DEGRADATION_LEVELS)):
            level_data = {
                'level': float(level),
                'survivors': {},
                'effective_dimensionality': []
            }

            for seed, seed_data in sys_results.items():
                if op_name in seed_data['cascade']:
                    op_result = seed_data['cascade'][op_name][level_idx]
                    level_data['effective_dimensionality'].append(op_result['effective_dimensionality'])
                    for obs_name, val in op_result['survivors'].items():
                        if obs_name not in level_data['survivors']:
                            level_data['survivors'][obs_name] = []
                        level_data['survivors'][obs_name].append(val)

            # Compute statistics
            level_data['ed_mean'] = float(np.mean(level_data['effective_dimensionality']))
            level_data['ed_std'] = float(np.std(level_data['effective_dimensionality']))
            for obs_name in level_data['survivors']:
                values = level_data['survivors'][obs_name]
                level_data['survivors'][obs_name] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values))
                }

            op_agg.append(level_data)

        agg[op_name] = op_agg

    return agg


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 003J DIVISION 4: REPRESENTATION STRESS CASCADE")
    print("=" * 70)
    print(f"Seeds: {NUM_SEEDS}")
    print(f"Timesteps: {NUM_TIMESTEPS}")
    print(f"Degradation levels: {NUM_DEGRADATION_LEVELS}")
    print(f"Operators: corruption, projection, quantization, shuffling, truncation")

    start_time = time.time()

    # Run cascade
    results = run_representation_stress_cascade()

    # Analyze collapse ordering
    print(f"\n{'=' * 70}")
    print(f"COLLAPSE ORDERING ANALYSIS")
    print(f"{'=' * 70}")

    collapse_ordering = {}
    for sys_name, sys_data in results.items():
        print(f"\n{sys_name}:")
        ordering = []
        for op_name, op_data in sys_data['aggregate'].items():
            # Find level where ED drops below 50% of baseline
            baseline_ed = sys_data['seeds'][0]['baseline']['effective_dimensionality']
            collapse_level = None
            for level_data in op_data:
                if level_data['ed_mean'] < 0.5 * baseline_ed:
                    collapse_level = level_data['level']
                    break
            if collapse_level is None:
                collapse_level = 1.0
            ordering.append((op_name, collapse_level))
            print(f"  {op_name}: collapse at {collapse_level:.2f}")

        # Sort by collapse level (earliest collapse first)
        ordering.sort(key=lambda x: x[1])
        collapse_ordering[sys_name] = [op[0] for op in ordering]
        print(f"  Order: {[op[0] for op in ordering]}")

    # Save results
    output = {
        "metadata": {
            "num_seeds": NUM_SEEDS,
            "num_timesteps": NUM_TIMESTEPS,
            "num_degradation_levels": NUM_DEGRADATION_LEVELS,
            "total_time": time.time() - start_time
        },
        "results": {k: {kk: vv for kk, vv in v.items() if kk != 'seeds'}
                   for k, v in results.items()},
        "collapse_ordering": collapse_ordering
    }

    output_file = os.path.join(OUTPUT_DIR, "representation_stress_cascade_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print(f"REPRESENTATION STRESS CASCADE COMPLETE")
    print(f"{'=' * 70}")
    print(f"Total runtime: {output['metadata']['total_time']:.1f}s")
    print(f"Results saved to: {output_file}")
