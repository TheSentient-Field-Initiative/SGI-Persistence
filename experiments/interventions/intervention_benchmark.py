#!/usr/bin/env python3
"""
Phase 004B Division 4: Intervention Benchmark

Compare all interventions under identical conditions.

Interventions from Phase 004A:
1. Coupling reduction
2. Synchronization suppression
3. Noise injection
4. Combined approach

Measures both ED recovery and functional recovery.
"""

import numpy as np
import json
import os
import sys
import time
from pathlib import Path

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_SEEDS = 10
NUM_TIMESTEPS = 200
COLLAPSE_STEPS = 100
RECOVERY_STEPS = 100


# ============================================================
# SYSTEM DEFINITIONS
# ============================================================

class DistributedSystem:
    def __init__(self, n_nodes=100, seed=42):
        self.n_nodes = n_nodes
        self.rng = np.random.RandomState(seed)
        self.adjacency = self._create_random_graph()
        self.history = []
        self.consensus_state = self.rng.uniform(0, 1, size=n_nodes)
        self.target_state = self.rng.choice([0, 1], size=n_nodes)

    def _create_random_graph(self):
        adj = np.zeros((self.n_nodes, self.n_nodes))
        for i in range(self.n_nodes):
            n_neighbors = self.rng.randint(2, 6)
            neighbors = self.rng.choice(self.n_nodes, n_neighbors, replace=False)
            adj[i, neighbors] = 1
            adj[neighbors, i] = 1
        return adj

    def step(self):
        new_state = self.consensus_state.copy()
        for i in range(self.n_nodes):
            neighbors = np.where(self.adjacency[i] > 0)[0]
            if len(neighbors) > 0:
                new_state[i] = np.mean(self.consensus_state[neighbors])
        self.consensus_state = new_state
        record = {'timestep': len(self.history)}
        record['state_variance'] = float(np.var(self.consensus_state))
        record['consensus_accuracy'] = float(np.mean(np.abs(self.consensus_state - self.target_state) < 0.5))
        self.history.append(record)
        return record

    def compute_function(self):
        if not self.history:
            return 0.0
        return self.history[-1]['consensus_accuracy']


class ImmuneSignalingNetwork:
    def __init__(self, n_cells=100, seed=42):
        self.n_cells = n_cells
        self.rng = np.random.RandomState(seed)
        self.n_pathogen = n_cells // 2
        self.n_immune = n_cells - self.n_pathogen
        self.pathogen = self.rng.exponential(1.0, self.n_pathogen)
        self.immune = self.rng.exponential(0.5, self.n_immune)
        self.history = []

    def step(self):
        kill_rate = 0.1
        growth_rate = 0.05
        new_pathogen = self.pathogen * (1 + growth_rate) - self.immune.mean() * kill_rate * self.pathogen
        new_pathogen = np.maximum(new_pathogen, 0)
        self.pathogen = new_pathogen
        record = {'timestep': len(self.history)}
        record['mean_pathogen'] = float(np.mean(self.pathogen))
        record['suppression'] = float(1.0 / (1.0 + np.mean(self.pathogen)))
        self.history.append(record)
        return record

    def compute_function(self):
        if not self.history:
            return 0.0
        return self.history[-1]['suppression']


class InstitutionNetwork:
    def __init__(self, n_agents=100, seed=42):
        self.n_agents = n_agents
        self.rng = np.random.RandomState(seed)
        self.history = []
        self.decisions = self.rng.uniform(0, 1, size=n_agents)
        self.stability = 1.0

    def step(self):
        new_decisions = self.decisions.copy()
        for i in range(self.n_agents):
            neighbors = np.where(self.rng.random(self.n_agents) < 0.1)[0]
            if len(neighbors) > 0:
                new_decisions[i] = np.mean(self.decisions[neighbors])
        self.stability = 0.95 * self.stability + 0.05 * (1.0 - np.std(new_decisions))
        self.decisions = new_decisions
        record = {'timestep': len(self.history)}
        record['decision_variance'] = float(np.std(self.decisions))
        record['stability'] = float(self.stability)
        self.history.append(record)
        return record

    def compute_function(self):
        return float(self.stability)


class AntColony:
    def __init__(self, n_agents=50, grid_size=20, seed=42):
        self.n_agents = n_agents
        self.grid_size = grid_size
        self.rng = np.random.RandomState(seed)
        self.grid = self.rng.random((grid_size, grid_size))
        self.food = self.rng.random((grid_size, grid_size)) > 0.7
        self.history = []

    def step(self):
        for _ in range(self.n_agents):
            x, y = self.rng.randint(0, self.grid_size, 2)
            if self.food[x, y]:
                self.grid[x, y] = min(self.grid[x, y] + 0.1, 1.0)
        record = {'timestep': len(self.history)}
        record['efficiency'] = float(np.mean(self.grid[self.food]) if np.any(self.food) else 0.0)
        self.history.append(record)
        return record

    def compute_function(self):
        if not self.history:
            return 0.0
        return self.history[-1]['efficiency']


# ============================================================
# ANALYSIS UTILITIES
# ============================================================

def trajectory_to_matrix(trajectory, max_dim=64):
    all_keys = set()
    for state in trajectory[:5]:
        all_keys.update(state.keys())
    all_keys.discard('timestep')
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
# INTERVENTIONS
# ============================================================

def apply_collapse(system, severity=0.5):
    """Apply synchronization-based collapse."""
    if hasattr(system, 'consensus_state'):
        mean_val = np.mean(system.consensus_state)
        system.consensus_state = system.consensus_state * (1 - severity) + mean_val * severity
    elif hasattr(system, 'decisions'):
        mean_val = np.mean(system.decisions)
        system.decisions = system.decisions * (1 - severity) + mean_val * severity
    elif hasattr(system, 'pathogen'):
        mean_val = np.mean(system.pathogen)
        system.pathogen = system.pathogen * (1 - severity) + mean_val * severity
    elif hasattr(system, 'grid'):
        mean_val = np.mean(system.grid)
        system.grid = system.grid * (1 - severity) + mean_val * severity


def intervention_coupling_reduction(system, level=0.5):
    """Reduce coupling strength."""
    if hasattr(system, 'adjacency'):
        system.adjacency = system.adjacency * (1 - level)


def intervention_synchronization_suppression(system, level=0.5):
    """Suppress synchronization by adding noise."""
    if hasattr(system, 'consensus_state'):
        noise = system.rng.normal(0, level * 0.1, len(system.consensus_state))
        system.consensus_state = np.clip(system.consensus_state + noise, 0, 1)
    elif hasattr(system, 'decisions'):
        noise = system.rng.normal(0, level * 0.1, len(system.decisions))
        system.decisions = np.clip(system.decisions + noise, 0, 1)


def intervention_noise_injection(system, level=0.5):
    """Inject noise to restore diversity."""
    if hasattr(system, 'consensus_state'):
        noise = system.rng.normal(0, level * 0.2, len(system.consensus_state))
        system.consensus_state = np.clip(system.consensus_state + noise, 0, 1)
    elif hasattr(system, 'decisions'):
        noise = system.rng.normal(0, level * 0.2, len(system.decisions))
        system.decisions = np.clip(system.decisions + noise, 0, 1)
    elif hasattr(system, 'pathogen'):
        noise = system.rng.normal(0, level * 0.2, len(system.pathogen))
        system.pathogen = np.maximum(system.pathogen + noise, 0)
    elif hasattr(system, 'grid'):
        noise = system.rng.normal(0, level * 0.2, system.grid.shape)
        system.grid = np.clip(system.grid + noise, 0, 1)


def intervention_combined(system, level=0.5):
    """Combine coupling reduction + noise injection."""
    intervention_coupling_reduction(system, level)
    intervention_noise_injection(system, level)


# ============================================================
# BENCHMARK
# ============================================================

def run_intervention_benchmark(system_class, system_kwargs, collapse_severity=0.5):
    """Benchmark all interventions on one system."""
    interventions = {
        'none': lambda s, l: None,
        'coupling_reduction': intervention_coupling_reduction,
        'synchronization_suppression': intervention_synchronization_suppression,
        'noise_injection': intervention_noise_injection,
        'combined': intervention_combined,
    }

    results_per_seed = {name: [] for name in interventions}

    for seed in range(NUM_SEEDS):
        for int_name, int_func in interventions.items():
            # Phase 0: Baseline
            system = system_class(seed=seed, **system_kwargs)
            for _ in range(NUM_TIMESTEPS):
                system.step()
            baseline_matrix, _ = trajectory_to_matrix(system.history)
            baseline_ed = compute_effective_dimensionality(baseline_matrix)
            baseline_function = system.compute_function()

            # Phase 1: Collapse
            system = system_class(seed=seed, **system_kwargs)
            for _ in range(COLLAPSE_STEPS):
                system.step()
                apply_collapse(system, collapse_severity)
            collapsed_matrix, _ = trajectory_to_matrix(system.history)
            collapsed_ed = compute_effective_dimensionality(collapsed_matrix)
            collapsed_function = system.compute_function()

            # Phase 2: Recovery
            system = system_class(seed=seed, **system_kwargs)
            for _ in range(COLLAPSE_STEPS):
                system.step()
                apply_collapse(system, collapse_severity)
            for step in range(RECOVERY_STEPS):
                int_func(system, collapse_severity)
                system.step()
            recovered_matrix, _ = trajectory_to_matrix(system.history)
            recovered_ed = compute_effective_dimensionality(recovered_matrix)
            recovered_function = system.compute_function()

            ed_recovery = (recovered_ed - collapsed_ed) / (baseline_ed - collapsed_ed + 1e-8)
            func_recovery = (recovered_function - collapsed_function) / (baseline_function - collapsed_function + 1e-8)

            results_per_seed[int_name].append({
                'baseline_ED': float(baseline_ed),
                'collapsed_ED': float(collapsed_ed),
                'recovered_ED': float(recovered_ed),
                'baseline_function': float(baseline_function),
                'collapsed_function': float(collapsed_function),
                'recovered_function': float(recovered_function),
                'ed_recovery': float(ed_recovery),
                'function_recovery': float(func_recovery),
            })

    # Average across seeds
    averaged = {}
    for int_name, seed_results in results_per_seed.items():
        averaged[int_name] = {
            'ed_recovery_mean': float(np.mean([r['ed_recovery'] for r in seed_results])),
            'ed_recovery_std': float(np.std([r['ed_recovery'] for r in seed_results])),
            'function_recovery_mean': float(np.mean([r['function_recovery'] for r in seed_results])),
            'function_recovery_std': float(np.std([r['function_recovery'] for r in seed_results])),
            'baseline_ED_mean': float(np.mean([r['baseline_ED'] for r in seed_results])),
            'collapsed_ED_mean': float(np.mean([r['collapsed_ED'] for r in seed_results])),
            'recovered_ED_mean': float(np.mean([r['recovered_ED'] for r in seed_results])),
            'baseline_function_mean': float(np.mean([r['baseline_function'] for r in seed_results])),
            'collapsed_function_mean': float(np.mean([r['collapsed_function'] for r in seed_results])),
            'recovered_function_mean': float(np.mean([r['recovered_function'] for r in seed_results])),
        }

    return averaged


# ============================================================
# MAIN
# ============================================================

def run_phase_004b_division_4():
    print("=" * 70)
    print("PHASE 004B DIVISION 4: INTERVENTION BENCHMARK")
    print("=" * 70)
    print()

    systems = [
        ('distributed', DistributedSystem, {'n_nodes': 100}),
        ('immune', ImmuneSignalingNetwork, {'n_cells': 100}),
        ('institution', InstitutionNetwork, {'n_agents': 100}),
        ('ant_colony', AntColony, {'n_agents': 50, 'grid_size': 20}),
    ]

    all_results = {}

    for name, cls, kwargs in systems:
        print(f"Processing {name}...")
        results = run_intervention_benchmark(cls, kwargs, collapse_severity=0.5)
        all_results[name] = results

    print()
    print("=" * 70)
    print("INTERVENTION BENCHMARK RESULTS")
    print("=" * 70)
    print()

    for name, data in all_results.items():
        print(f"{name}:")
        print(f"  {'Intervention':<30} {'ED Recovery':<20} {'Func Recovery':<20}")
        print(f"  {'-'*30} {'-'*20} {'-'*20}")
        for int_name, metrics in data.items():
            ed_str = f"{metrics['ed_recovery_mean']:.1%} ± {metrics['ed_recovery_std']:.1%}"
            func_str = f"{metrics['function_recovery_mean']:.1%} ± {metrics['function_recovery_std']:.1%}"
            print(f"  {int_name:<30} {ed_str:<20} {func_str:<20}")
        print()

    output_path = Path(OUTPUT_DIR) / 'intervention_benchmark_results.json'
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"Results saved to: {output_path}")
    return all_results


if __name__ == '__main__':
    run_phase_004b_division_4()
