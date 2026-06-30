#!/usr/bin/env python3
"""
Phase 004B Division 3: Multi-Stage Collapse Trajectories

Track ED, synchronization, and function through sequential degradation stages.

Key questions:
1. Is collapse gradual or sudden (phase transition)?
2. Does function degrade before or after representation?
3. Are there critical thresholds where behavior changes qualitatively?
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
N_STAGES = 20


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
        record['mean_state'] = float(np.mean(self.consensus_state))
        self.history.append(record)
        return record

    def compute_function(self):
        if not self.history:
            return 0.0
        return self.history[-1]['consensus_accuracy']

    def get_synchronization(self):
        return 1.0 - np.std(self.consensus_state)


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
        record['pathogen_variance'] = float(np.var(self.pathogen))
        self.history.append(record)
        return record

    def compute_function(self):
        if not self.history:
            return 0.0
        return self.history[-1]['suppression']

    def get_synchronization(self):
        return 1.0 - np.std(self.pathogen) / (np.mean(self.pathogen) + 1e-8)


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
        record['mean_decision'] = float(np.mean(self.decisions))
        self.history.append(record)
        return record

    def compute_function(self):
        return float(self.stability)

    def get_synchronization(self):
        return 1.0 - np.std(self.decisions)


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
        record['grid_variance'] = float(np.var(self.grid))
        record['mean_grid'] = float(np.mean(self.grid))
        self.history.append(record)
        return record

    def compute_function(self):
        if not self.history:
            return 0.0
        return self.history[-1]['efficiency']

    def get_synchronization(self):
        return 1.0 - np.std(self.grid)


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
# MULTI-STAGE COLLAPSE
# ============================================================

def run_multi_stage_collapse(system_class, system_kwargs, n_stages=N_STAGES):
    """Track system through progressive collapse stages."""
    results_per_seed = []

    for seed in range(NUM_SEEDS):
        stage_results = []

        for stage in range(n_stages + 1):
            collapse_severity = stage / n_stages  # 0 to 1

            # Create and run system
            system = system_class(seed=seed, **system_kwargs)
            for _ in range(NUM_TIMESTEPS // 2):
                system.step()

            # Apply collapse (synchronization)
            if hasattr(system, 'consensus_state'):
                mean_val = np.mean(system.consensus_state)
                system.consensus_state = (
                    system.consensus_state * (1 - collapse_severity) +
                    mean_val * collapse_severity
                )
            elif hasattr(system, 'decisions'):
                mean_val = np.mean(system.decisions)
                system.decisions = (
                    system.decisions * (1 - collapse_severity) +
                    mean_val * collapse_severity
                )
            elif hasattr(system, 'pathogen'):
                mean_val = np.mean(system.pathogen)
                system.pathogen = (
                    system.pathogen * (1 - collapse_severity) +
                    mean_val * collapse_severity
                )
            elif hasattr(system, 'grid'):
                mean_val = np.mean(system.grid)
                system.grid = (
                    system.grid * (1 - collapse_severity) +
                    mean_val * collapse_severity
                )

            # Run more steps after collapse
            for _ in range(NUM_TIMESTEPS // 2):
                system.step()

            # Measure
            matrix, _ = trajectory_to_matrix(system.history)
            ed = compute_effective_dimensionality(matrix)
            function = system.compute_function()
            synchronization = system.get_synchronization()

            stage_results.append({
                'stage': stage,
                'collapse_severity': float(collapse_severity),
                'ED': float(ed),
                'function': float(function),
                'synchronization': float(synchronization),
            })

        results_per_seed.append(stage_results)

    # Average across seeds
    averaged = []
    for i in range(n_stages + 1):
        entry = {
            'stage': results_per_seed[0][i]['stage'],
            'collapse_severity': results_per_seed[0][i]['collapse_severity'],
            'ED_mean': float(np.mean([r[i]['ED'] for r in results_per_seed])),
            'ED_std': float(np.std([r[i]['ED'] for r in results_per_seed])),
            'function_mean': float(np.mean([r[i]['function'] for r in results_per_seed])),
            'function_std': float(np.std([r[i]['function'] for r in results_per_seed])),
            'synchronization_mean': float(np.mean([r[i]['synchronization'] for r in results_per_seed])),
            'synchronization_std': float(np.std([r[i]['synchronization'] for r in results_per_seed])),
        }
        averaged.append(entry)

    return averaged


def detect_phase_transitions(stage_results):
    """Detect sudden changes (phase transitions) in metrics."""
    eds = [r['ED_mean'] for r in stage_results]
    funcs = [r['function_mean'] for r in stage_results]
    syncs = [r['synchronization_mean'] for r in stage_results]
    severities = [r['collapse_severity'] for r in stage_results]

    transitions = []

    # Detect ED transitions (largest drop)
    ed_diffs = np.diff(eds)
    if len(ed_diffs) > 0:
        max_drop_idx = np.argmin(ed_diffs)
        if ed_diffs[max_drop_idx] < -0.1 * eds[0]:
            transitions.append({
                'metric': 'ED',
                'severity': severities[max_drop_idx + 1],
                'magnitude': float(ed_diffs[max_drop_idx]),
                'type': 'collapse',
            })

    # Detect function transitions
    func_diffs = np.diff(funcs)
    if len(func_diffs) > 0:
        max_drop_idx = np.argmin(func_diffs)
        if func_diffs[max_drop_idx] < -0.1 * max(funcs[0], 0.01):
            transitions.append({
                'metric': 'function',
                'severity': severities[max_drop_idx + 1],
                'magnitude': float(func_diffs[max_drop_idx]),
                'type': 'collapse',
            })

    # Detect synchronization transitions
    sync_diffs = np.diff(syncs)
    if len(sync_diffs) > 0:
        max_drop_idx = np.argmin(sync_diffs)
        if sync_diffs[max_drop_idx] < -0.1:
            transitions.append({
                'metric': 'synchronization',
                'severity': severities[max_drop_idx + 1],
                'magnitude': float(sync_diffs[max_drop_idx]),
                'type': 'collapse',
            })

    return transitions


# ============================================================
# MAIN
# ============================================================

def run_phase_004b_division_3():
    print("=" * 70)
    print("PHASE 004B DIVISION 3: MULTI-STAGE COLLAPSE TRAJECTORIES")
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
        results = run_multi_stage_collapse(cls, kwargs, n_stages=N_STAGES)
        transitions = detect_phase_transitions(results)
        all_results[name] = {
            'stage_results': results,
            'transitions': transitions,
        }

    print()
    print("=" * 70)
    print("MULTI-STAGE COLLAPSE RESULTS")
    print("=" * 70)
    print()

    for name, data in all_results.items():
        print(f"{name}:")
        if data['transitions']:
            print(f"  Phase transitions detected:")
            for t in data['transitions']:
                print(f"    {t['metric']}: severity={t['severity']:.2f}, magnitude={t['magnitude']:.3f} ({t['type']})")
        else:
            print(f"  No phase transitions detected (gradual collapse)")
        print()

        print(f"  {'Severity':<10} {'ED':<15} {'Function':<15} {'Sync':<15}")
        print(f"  {'-'*10} {'-'*15} {'-'*15} {'-'*15}")
        for r in data['stage_results']:
            ed_str = f"{r['ED_mean']:.3f} ± {r['ED_std']:.3f}"
            func_str = f"{r['function_mean']:.3f} ± {r['function_std']:.3f}"
            sync_str = f"{r['synchronization_mean']:.3f} ± {r['synchronization_std']:.3f}"
            print(f"  {r['collapse_severity']:<10.2f} {ed_str:<15} {func_str:<15} {sync_str:<15}")
        print()

    output_path = Path(OUTPUT_DIR) / 'multi_stage_collapse_results.json'
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"Results saved to: {output_path}")
    return all_results


if __name__ == '__main__':
    run_phase_004b_division_3()
