#!/usr/bin/env python3
"""
Phase 003J Division 3: Survivor Universality Tests
Tests whether Tier-1 survivors remain stable across:
- All low-rank systems
- All non-low-rank systems
- Mixed populations

Usage:
    python experiments/validation/survivor_universality.py
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

NUM_SEEDS = 10
NUM_TIMESTEPS = 200
ED_THRESHOLD = 2.0  # Systems with ED < 2.0 are classified as LOW-RANK


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
# TIER-1 SURVIVOR OBSERVABLES
# ============================================================

def compute_tier1_survivors(matrix):
    """Compute Tier-1 survivor observables."""
    results = {}

    # 1. Lagged stability (temporal autocorrelation)
    if len(matrix) > 10:
        autocorr = []
        for lag in range(1, min(11, len(matrix) // 2)):
            c = np.corrcoef(matrix[:-lag].flatten(), matrix[lag:].flatten())[0, 1]
            if not np.isnan(c):
                autocorr.append(c)
        results['lagged_stability'] = float(np.mean(autocorr)) if autocorr else 0.0
    else:
        results['lagged_stability'] = 0.0

    # 2. Transition density (fraction of dimensions that change)
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


def run_survivor_universality():
    """Test Tier-1 survivor universality across systems."""
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

    all_results = {}
    low_rank_systems = []
    non_low_rank_systems = []

    for sys_name, sys_info in systems.items():
        print(f"\nTesting {sys_name}...")
        seed_results = []

        for seed in range(NUM_SEEDS):
            try:
                system = sys_info["class"](seed=seed, **sys_info["kwargs"])
                trajectory = []
                for _ in range(NUM_TIMESTEPS):
                    trajectory.append(system.step())

                matrix, keys = trajectory_to_matrix(trajectory)
                ed = compute_effective_dimensionality(matrix)
                survivors = compute_tier1_survivors(matrix)
                survivors['seed'] = seed
                survivors['effective_dimensionality'] = ed
                survivors['is_low_rank'] = ed < ED_THRESHOLD
                seed_results.append(survivors)
            except Exception as e:
                print(f"  Seed {seed}: ERROR - {e}")

        if seed_results:
            # Aggregate across seeds
            agg = {}
            for key in seed_results[0]:
                if key in ('seed', 'effective_dimensionality', 'is_low_rank'):
                    continue
                values = [r[key] for r in seed_results]
                cv = np.std(values) / np.mean(values) if np.mean(values) != 0 else float("inf")
                agg[key] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'cv': float(cv),
                    'is_stable': cv < 0.2
                }

            is_low_rank = seed_results[0]['is_low_rank']
            all_results[sys_name] = {
                'seeds': seed_results,
                'aggregate': agg,
                'is_low_rank': is_low_rank,
                'n_seeds': len(seed_results)
            }

            if is_low_rank:
                low_rank_systems.append(sys_name)
            else:
                non_low_rank_systems.append(sys_name)

            print(f"  ED: {seed_results[0]['effective_dimensionality']:.4f}")
            print(f"  Low-rank: {is_low_rank}")
            for obs_name, stats in agg.items():
                status = "STABLE" if stats['is_stable'] else "UNSTABLE"
                print(f"  {obs_name}: CV={stats['cv']:.4f} [{status}]")

    return all_results, low_rank_systems, non_low_rank_systems


def compute_universality_stats(all_results, low_rank_systems, non_low_rank_systems):
    """Compute universality statistics across system groups."""
    universality = {}

    # Test each Tier-1 survivor
    for obs_name in ['lagged_stability', 'transition_density', 'approx_entropy']:
        # Low-rank systems
        lr_cvs = []
        for sys_name in low_rank_systems:
            if sys_name in all_results and obs_name in all_results[sys_name]['aggregate']:
                lr_cvs.append(all_results[sys_name]['aggregate'][obs_name]['cv'])

        # Non-low-rank systems
        nlr_cvs = []
        for sys_name in non_low_rank_systems:
            if sys_name in all_results and obs_name in all_results[sys_name]['aggregate']:
                nlr_cvs.append(all_results[sys_name]['aggregate'][obs_name]['cv'])

        # All systems
        all_cvs = lr_cvs + nlr_cvs

        universality[obs_name] = {
            'low_rank': {
                'mean_cv': float(np.mean(lr_cvs)) if lr_cvs else float('inf'),
                'is_universal': all(cv < 0.2 for cv in lr_cvs) if lr_cvs else False,
                'n_stable': sum(1 for cv in lr_cvs if cv < 0.2),
                'n_total': len(lr_cvs)
            },
            'non_low_rank': {
                'mean_cv': float(np.mean(nlr_cvs)) if nlr_cvs else float('inf'),
                'is_universal': all(cv < 0.2 for cv in nlr_cvs) if nlr_cvs else False,
                'n_stable': sum(1 for cv in nlr_cvs if cv < 0.2),
                'n_total': len(nlr_cvs)
            },
            'all': {
                'mean_cv': float(np.mean(all_cvs)) if all_cvs else float('inf'),
                'is_universal': all(cv < 0.2 for cv in all_cvs) if all_cvs else False,
                'n_stable': sum(1 for cv in all_cvs if cv < 0.2),
                'n_total': len(all_cvs)
            }
        }

    return universality


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 003J DIVISION 3: SURVIVOR UNIVERSALITY TESTS")
    print("=" * 70)
    print(f"Seeds: {NUM_SEEDS}")
    print(f"Timesteps: {NUM_TIMESTEPS}")
    print(f"ED threshold: {ED_THRESHOLD}")
    print(f"Tier-1 survivors: lagged_stability, transition_density, approx_entropy")

    start_time = time.time()

    # Run universality tests
    all_results, low_rank_systems, non_low_rank_systems = run_survivor_universality()

    # Compute universality statistics
    universality = compute_universality_stats(all_results, low_rank_systems, non_low_rank_systems)

    # Print summary
    print(f"\n{'=' * 70}")
    print(f"UNIVERSALITY SUMMARY")
    print(f"{'=' * 70}")
    print(f"Low-rank systems: {low_rank_systems}")
    print(f"Non-low-rank systems: {non_low_rank_systems}")

    for obs_name, stats in universality.items():
        print(f"\n{obs_name}:")
        print(f"  Low-rank: {stats['low_rank']['n_stable']}/{stats['low_rank']['n_total']} stable, "
              f"mean CV={stats['low_rank']['mean_cv']:.4f} "
              f"[{'UNIVERSAL' if stats['low_rank']['is_universal'] else 'NOT UNIVERSAL'}]")
        print(f"  Non-low-rank: {stats['non_low_rank']['n_stable']}/{stats['non_low_rank']['n_total']} stable, "
              f"mean CV={stats['non_low_rank']['mean_cv']:.4f} "
              f"[{'UNIVERSAL' if stats['non_low_rank']['is_universal'] else 'NOT UNIVERSAL'}]")
        print(f"  All: {stats['all']['n_stable']}/{stats['all']['n_total']} stable, "
              f"mean CV={stats['all']['mean_cv']:.4f} "
              f"[{'UNIVERSAL' if stats['all']['is_universal'] else 'NOT UNIVERSAL'}]")

    # Save results
    output = {
        "metadata": {
            "num_seeds": NUM_SEEDS,
            "num_timesteps": NUM_TIMESTEPS,
            "ed_threshold": ED_THRESHOLD,
            "total_time": time.time() - start_time,
            "low_rank_systems": low_rank_systems,
            "non_low_rank_systems": non_low_rank_systems
        },
        "system_results": {k: {kk: vv for kk, vv in v.items() if kk != 'seeds'}
                          for k, v in all_results.items()},
        "universality": universality
    }

    output_file = os.path.join(OUTPUT_DIR, "survivor_universality_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print(f"UNIVERSALITY TESTS COMPLETE")
    print(f"{'=' * 70}")
    print(f"Total runtime: {output['metadata']['total_time']:.1f}s")
    print(f"Results saved to: {output_file}")

    # Determine if any observable is truly universal
    universal_count = sum(1 for stats in universality.values() if stats['all']['is_universal'])
    print(f"\nUniversal observables: {universal_count}/3")
    if universal_count == 3:
        print("CONCLUSION: All Tier-1 survivors are universal")
    elif universal_count > 0:
        print("CONCLUSION: Some Tier-1 survivors are universal")
    else:
        print("CONCLUSION: No Tier-1 survivors are universal across all systems")
