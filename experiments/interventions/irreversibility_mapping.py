#!/usr/bin/env python3
"""
Phase 004B Division 2: Irreversibility Mapping (v3)

Central question: At what collapse severity does recovery become impossible?

Uses absolute metrics instead of ratios to avoid division-by-zero instability.
"""

import numpy as np
import json
import os
import sys
import time
from scipy import stats
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
        record['grid_variance'] = float(np.var(self.grid))
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
# COLLAPSE AND RECOVERY
# ============================================================

class SynchronizationCollapse:
    """Collapse by pushing states toward the mean (synchronization)."""

    def __init__(self, system, severity=0.0):
        self.system = system
        self.severity = severity

    def apply(self):
        if hasattr(self.system, 'consensus_state'):
            mean_val = np.mean(self.system.consensus_state)
            self.system.consensus_state = (
                self.system.consensus_state * (1 - self.severity / 100) +
                mean_val * (self.severity / 100)
            )
        elif hasattr(self.system, 'decisions'):
            mean_val = np.mean(self.system.decisions)
            self.system.decisions = (
                self.system.decisions * (1 - self.severity / 100) +
                mean_val * (self.severity / 100)
            )
        elif hasattr(self.system, 'pathogen'):
            mean_val = np.mean(self.system.pathogen)
            self.system.pathogen = (
                self.system.pathogen * (1 - self.severity / 100) +
                mean_val * (self.severity / 100)
            )
        elif hasattr(self.system, 'grid'):
            mean_val = np.mean(self.system.grid)
            self.system.grid = (
                self.system.grid * (1 - self.severity / 100) +
                mean_val * (self.severity / 100)
            )


class NoiseRecovery:
    """Recover by injecting noise to restore diversity."""

    def __init__(self, system, noise_level=0.0):
        self.system = system
        self.noise_level = noise_level

    def apply(self):
        if hasattr(self.system, 'consensus_state'):
            noise = self.system.rng.normal(0, self.noise_level, len(self.system.consensus_state))
            self.system.consensus_state = np.clip(self.system.consensus_state + noise, 0, 1)
        elif hasattr(self.system, 'decisions'):
            noise = self.system.rng.normal(0, self.noise_level, len(self.system.decisions))
            self.system.decisions = np.clip(self.system.decisions + noise, 0, 1)
        elif hasattr(self.system, 'pathogen'):
            noise = self.system.rng.normal(0, self.noise_level, len(self.system.pathogen))
            self.system.pathogen = np.maximum(self.system.pathogen + noise, 0)
        elif hasattr(self.system, 'grid'):
            noise = self.system.rng.normal(0, self.noise_level, self.system.grid.shape)
            self.system.grid = np.clip(self.system.grid + noise, 0, 1)


# ============================================================
# IRREVERSIBILITY SWEEP
# ============================================================

def run_irreversibility_sweep(system_class, system_kwargs, n_severity_levels=11):
    results_per_seed = []

    for seed in range(NUM_SEEDS):
        seed_results = []

        for severity in np.linspace(0, 100, n_severity_levels):
            severity = round(float(severity), 1)

            # Phase 0: Baseline
            system = system_class(seed=seed, **system_kwargs)
            for _ in range(NUM_TIMESTEPS):
                system.step()
            baseline_matrix, _ = trajectory_to_matrix(system.history)
            baseline_ed = compute_effective_dimensionality(baseline_matrix)
            baseline_function = system.compute_function()

            # Phase 1: Collapse via synchronization
            system = system_class(seed=seed, **system_kwargs)
            collapse = SynchronizationCollapse(system, severity=severity)
            for step in range(COLLAPSE_STEPS):
                current_severity = severity * (step + 1) / COLLAPSE_STEPS
                collapse.severity = current_severity
                system.step()
                collapse.apply()
            collapsed_matrix, _ = trajectory_to_matrix(system.history)
            collapsed_ed = compute_effective_dimensionality(collapsed_matrix)
            collapsed_function = system.compute_function()

            # Phase 2: Recovery via noise injection
            system = system_class(seed=seed, **system_kwargs)
            collapse = SynchronizationCollapse(system, severity=severity)
            for step in range(COLLAPSE_STEPS):
                current_severity = severity * (step + 1) / COLLAPSE_STEPS
                collapse.severity = current_severity
                system.step()
                collapse.apply()

            recovery = NoiseRecovery(system, noise_level=severity / 100 * 0.5)
            for step in range(RECOVERY_STEPS):
                recovery.apply()
                system.step()
            recovered_matrix, _ = trajectory_to_matrix(system.history)
            recovered_ed = compute_effective_dimensionality(recovered_matrix)
            recovered_function = system.compute_function()

            seed_results.append({
                'severity': severity,
                'baseline_ED': float(baseline_ed),
                'collapsed_ED': float(collapsed_ed),
                'recovered_ED': float(recovered_ed),
                'baseline_function': float(baseline_function),
                'collapsed_function': float(collapsed_function),
                'recovered_function': float(recovered_function),
                # Absolute recovery (not ratio)
                'ed_recovery_absolute': float(recovered_ed - collapsed_ed),
                'function_recovery_absolute': float(recovered_function - collapsed_function),
                # Percentage of baseline lost
                'ed_loss_pct': float((baseline_ed - collapsed_ed) / (baseline_ed + 1e-8) * 100),
                'function_loss_pct': float((baseline_function - collapsed_function) / (baseline_function + 1e-8) * 100),
            })

        results_per_seed.append(seed_results)

    averaged = []
    for i in range(n_severity_levels):
        entry = {
            'severity': results_per_seed[0][i]['severity'],
            'baseline_ED_mean': float(np.mean([r[i]['baseline_ED'] for r in results_per_seed])),
            'collapsed_ED_mean': float(np.mean([r[i]['collapsed_ED'] for r in results_per_seed])),
            'recovered_ED_mean': float(np.mean([r[i]['recovered_ED'] for r in results_per_seed])),
            'baseline_function_mean': float(np.mean([r[i]['baseline_function'] for r in results_per_seed])),
            'collapsed_function_mean': float(np.mean([r[i]['collapsed_function'] for r in results_per_seed])),
            'recovered_function_mean': float(np.mean([r[i]['recovered_function'] for r in results_per_seed])),
            'ed_recovery_absolute_mean': float(np.mean([r[i]['ed_recovery_absolute'] for r in results_per_seed])),
            'ed_recovery_absolute_std': float(np.std([r[i]['ed_recovery_absolute'] for r in results_per_seed])),
            'function_recovery_absolute_mean': float(np.mean([r[i]['function_recovery_absolute'] for r in results_per_seed])),
            'function_recovery_absolute_std': float(np.std([r[i]['function_recovery_absolute'] for r in results_per_seed])),
            'ed_loss_pct_mean': float(np.mean([r[i]['ed_loss_pct'] for r in results_per_seed])),
            'ed_loss_pct_std': float(np.std([r[i]['ed_loss_pct'] for r in results_per_seed])),
            'function_loss_pct_mean': float(np.mean([r[i]['function_loss_pct'] for r in results_per_seed])),
            'function_loss_pct_std': float(np.std([r[i]['function_loss_pct'] for r in results_per_seed])),
        }
        averaged.append(entry)

    return averaged


def find_irreversible_threshold(severity_results):
    """Find severity where recovery consistently fails (absolute recovery < 10% of baseline)."""
    severities = [r['severity'] for r in severity_results]
    ed_losses = [r['ed_loss_pct_mean'] for r in severity_results]
    func_losses = [r['function_loss_pct_mean'] for r in severity_results]
    ed_recoveries = [r['ed_recovery_absolute_mean'] for r in severity_results]
    func_recoveries = [r['function_recovery_absolute_mean'] for r in severity_results]

    # ED threshold: where loss exceeds 50% and recovery is negative
    ed_threshold = 100.0
    for i, (loss, rec) in enumerate(zip(ed_losses, ed_recoveries)):
        if loss > 50 and rec < 0:
            ed_threshold = severities[i]
            break

    # Function threshold: where loss exceeds 50% and recovery is negative
    func_threshold = 100.0
    for i, (loss, rec) in enumerate(zip(func_losses, func_recoveries)):
        if loss > 50 and rec < 0:
            func_threshold = severities[i]
            break

    # Dissociation: ED recovers but function doesn't
    dissociation_threshold = None
    for i, (ed_rec, func_rec, ed_loss, func_loss) in enumerate(zip(
        ed_recoveries, func_recoveries, ed_losses, func_losses
    )):
        if ed_rec > 0 and func_rec < 0 and ed_loss < 30 and func_loss > 30:
            dissociation_threshold = severities[i]
            break

    return {
        'ed_irreversible_threshold': ed_threshold,
        'function_irreversible_threshold': func_threshold,
        'dissociation_threshold': dissociation_threshold,
        'has_dissociation': dissociation_threshold is not None,
    }


# ============================================================
# MAIN
# ============================================================

def run_phase_004b_division_2():
    print("=" * 70)
    print("PHASE 004B DIVISION 2: IRREVERSIBILITY MAPPING (v3)")
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
        results = run_irreversibility_sweep(cls, kwargs, n_severity_levels=11)
        thresholds = find_irreversible_threshold(results)
        all_results[name] = {
            'severity_results': results,
            'thresholds': thresholds,
        }

    print()
    print("=" * 70)
    print("IRREVERSIBILITY MAPPING RESULTS")
    print("=" * 70)
    print()

    for name, data in all_results.items():
        th = data['thresholds']
        print(f"{name}:")
        print(f"  ED irreversible threshold: {th['ed_irreversible_threshold']}%")
        print(f"  Function irreversible threshold: {th['function_irreversible_threshold']}%")
        if th['has_dissociation']:
            print(f"  *** DISSOCIATION threshold: {th['dissociation_threshold']}% ***")
        else:
            print(f"  No dissociation detected")
        print()

        print(f"  {'Severity':<10} {'ED Loss%':<15} {'ED Recovery':<15} {'Func Loss%':<15} {'Func Recovery':<15}")
        print(f"  {'-'*10} {'-'*15} {'-'*15} {'-'*15} {'-'*15}")
        for r in data['severity_results']:
            ed_loss = f"{r['ed_loss_pct_mean']:.1f}% ± {r['ed_loss_pct_std']:.1f}%"
            ed_rec = f"{r['ed_recovery_absolute_mean']:.3f} ± {r['ed_recovery_absolute_std']:.3f}"
            func_loss = f"{r['function_loss_pct_mean']:.1f}% ± {r['function_loss_pct_std']:.1f}%"
            func_rec = f"{r['function_recovery_absolute_mean']:.3f} ± {r['function_recovery_absolute_std']:.3f}"
            print(f"  {r['severity']:<10.1f} {ed_loss:<15} {ed_rec:<15} {func_loss:<15} {func_rec:<15}")
        print()

    output_path = Path(OUTPUT_DIR) / 'irreversibility_mapping_v3_results.json'
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"Results saved to: {output_path}")
    return all_results


if __name__ == '__main__':
    run_phase_004b_division_2()
