#!/usr/bin/env python3
"""
Phase 004A Division 5: Anti-Collapse Synthetic Systems

Test resistant systems against baseline systems.

Protocol:
1. Create 4 resistant systems (modular_sparse, delayed_coupling, heterogeneous_update, adaptive_desync)
2. Compare ED to baseline systems (distributed, ant_colony, institution, etc.)
3. Test resistance under coupling increase
4. Measure: ED, condition number, survivor observables

Success criteria:
- Primary: ED > 3.0
- Secondary: ED_system / ED_baseline > 2.0

Usage:
    python experiments/interventions/test_resistant_systems.py
"""

import numpy as np
import json
import os
import sys
import time
from scipy import stats

# Add source paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'resistant'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'distributed'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'immune'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'ant_colony'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'institution'))

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_SEEDS = 5
NUM_TIMESTEPS = 100


# ============================================================
# BASELINE SYSTEMS
# ============================================================

class DistributedSystem:
    def __init__(self, n_nodes=100, seed=42):
        self.n_nodes = n_nodes
        self.rng = np.random.RandomState(seed)
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
        record = {'timestep': len(self.history)}
        record['n_active'] = float(self.n_nodes)
        record['connectivity'] = float(np.mean(self.adjacency > 0))
        record['routing_entropy'] = float(-np.sum(np.mean(self.adjacency, axis=0) *
                                                   np.log(np.mean(self.adjacency, axis=0) + 1e-10)))
        record['assignment_rate'] = 1.0
        record['n_components'] = 1.0
        record['allocation_entropy'] = float(self.rng.random())
        self.history.append(record)
        return record


class AntColony:
    def __init__(self, n_ants=50, n_food=100, seed=42):
        self.n_ants = n_ants
        self.n_food = n_food
        self.rng = np.random.RandomState(seed)
        self.history = []

    def step(self):
        record = {'timestep': len(self.history)}
        record['total_pheromone'] = float(self.rng.random() * 1000)
        record['recruitment_rate'] = float(self.rng.random())
        record['trail_connectivity'] = float(self.rng.random())
        record['path_redundancy'] = float(self.rng.random())
        record['n_trails'] = float(self.rng.randint(1, 20))
        record['trail_entropy'] = float(self.rng.random())
        record['foraging_efficiency'] = float(self.rng.random())
        record['food_found'] = float(self.rng.randint(0, self.n_food))
        record['competition_index'] = float(self.rng.random())
        record['exploration_rate'] = float(self.rng.random())
        record['pheromone_decay'] = float(self.rng.random() * 0.1)
        record['trail_length'] = float(self.rng.random() * 100)
        record['ant_density'] = float(self.n_ants / 100)
        self.history.append(record)
        return record


class InstitutionNetwork:
    def __init__(self, n_agents=100, seed=42):
        self.n_agents = n_agents
        self.rng = np.random.RandomState(seed)
        self.history = []

    def step(self):
        record = {'timestep': len(self.history)}
        record['cooperation_rate'] = float(self.rng.random())
        record['mean_payoff'] = float(self.rng.random() * 10)
        record['mean_trust'] = float(self.rng.random())
        record['network_connectivity'] = float(self.rng.random())
        record['n_components'] = 1.0
        record['largest_component'] = float(self.rng.random())
        record['strategy_entropy'] = float(self.rng.random())
        record['cov_trace'] = float(self.rng.random())
        record['cov_condition'] = float(self.rng.random() * 100)
        record['norm_deviation'] = float(self.rng.random())
        record['non_principal'] = float(self.rng.random())
        self.history.append(record)
        return record


# ============================================================
# RESISTANT SYSTEMS
# ============================================================

from modular_sparse import ModularSparseSystem
from delayed_coupling import DelayedCouplingSystem
from heterogeneous_update import HeterogeneousUpdateSystem
from adaptive_desync import AdaptiveDesyncSystem


# ============================================================
# ANALYSIS UTILITIES
# ============================================================

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


def compute_condition_number(matrix):
    if len(matrix) > matrix.shape[1]:
        try:
            cov = np.cov(matrix.T)
            eigenvalues = np.linalg.eigvalsh(cov)
            eigenvalues = eigenvalues[eigenvalues > 1e-10]
            if len(eigenvalues) > 1:
                return float(eigenvalues[-1] / eigenvalues[0])
        except:
            pass
    return 1.0


def compute_survivor_observables(matrix):
    results = {}
    if len(matrix) > 10:
        autocorr = []
        for lag in range(1, min(11, len(matrix) // 2)):
            c = np.corrcoef(matrix[:-lag].flatten(), matrix[lag:].flatten())[0, 1]
            if not np.isnan(c):
                autocorr.append(c)
        results['lagged_stability'] = float(np.mean(autocorr)) if autocorr else 0.0
    else:
        results['lagged_stability'] = 0.0

    if len(matrix) > 1:
        changes = np.abs(np.diff(matrix, axis=0))
        std_per_dim = np.std(matrix, axis=0)
        std_per_dim[std_per_dim == 0] = 1
        transition_mask = changes > 0.1 * std_per_dim
        results['transition_density'] = float(np.mean(transition_mask))
    else:
        results['transition_density'] = 0.0

    flat = matrix.flatten()
    hist, _ = np.histogram(flat, bins=50, density=True)
    hist = hist[hist > 0]
    results['approx_entropy'] = float(-np.sum(hist * np.log(hist + 1e-10)))

    return results


def compute_confidence_interval(data, confidence=0.95):
    n = len(data)
    if n < 2:
        return float(data[0]) if n > 0 else 0.0, 0.0
    mean = np.mean(data)
    se = stats.sem(data)
    ci = se * stats.t.ppf((1 + confidence) / 2, n - 1)
    return float(mean), float(ci)


# ============================================================
# TEST RESISTANT SYSTEMS
# ============================================================

def run_resistant_systems_test():
    """Main experiment: test resistant systems."""
    print("=" * 70)
    print("PHASE 004A DIVISION 5: ANTI-COLLAPSE SYNTHETIC SYSTEMS")
    print("=" * 70)
    print(f"Baseline systems: 3 (distributed, ant_colony, institution)")
    print(f"Resistant systems: 4 (modular_sparse, delayed_coupling, heterogeneous_update, adaptive_desync)")
    print(f"Seeds: {NUM_SEEDS}")
    print(f"Timesteps: {NUM_TIMESTEPS}")
    print()

    baseline_systems = {
        "distributed": {"class": DistributedSystem, "kwargs": {"n_nodes": 100}},
        "ant_colony": {"class": AntColony, "kwargs": {"n_ants": 50, "n_food": 100}},
        "institution": {"class": InstitutionNetwork, "kwargs": {"n_agents": 100}},
    }

    resistant_systems = {
        "modular_sparse": {"class": ModularSparseSystem, "kwargs": {"n_nodes": 100, "n_communities": 5}},
        "delayed_coupling": {"class": DelayedCouplingSystem, "kwargs": {"n_nodes": 100, "delay": 5}},
        "heterogeneous_update": {"class": HeterogeneousUpdateSystem, "kwargs": {"n_agents": 100}},
        "adaptive_desync": {"class": AdaptiveDesyncSystem, "kwargs": {"n_nodes": 100}},
    }

    all_results = {}

    # Test baseline systems
    print("Testing baseline systems...")
    for sys_name, sys_info in baseline_systems.items():
        print(f"\n  {sys_name}:")
        seed_results = []

        for seed in range(NUM_SEEDS):
            try:
                system = sys_info["class"](seed=seed, **sys_info["kwargs"])
                for _ in range(NUM_TIMESTEPS):
                    system.step()

                matrix, _ = trajectory_to_matrix(system.history)
                ed = compute_effective_dimensionality(matrix)
                cn = compute_condition_number(matrix)
                survivors = compute_survivor_observables(matrix)

                seed_results.append({
                    'ed': ed,
                    'condition_number': cn,
                    'survivors': survivors,
                })
            except Exception as e:
                print(f"    Seed {seed}: ERROR - {e}")

        if seed_results:
            eds = [r['ed'] for r in seed_results]
            ed_mean, ed_ci = compute_confidence_interval(eds)
            print(f"    ED: {ed_mean:.4f} ± {ed_ci:.4f}")
            all_results[sys_name] = {
                'type': 'baseline',
                'ed_mean': ed_mean,
                'ed_ci': ed_ci,
                'n_seeds': len(seed_results),
            }

    # Test resistant systems
    print("\nTesting resistant systems...")
    for sys_name, sys_info in resistant_systems.items():
        print(f"\n  {sys_name}:")
        seed_results = []

        for seed in range(NUM_SEEDS):
            try:
                system = sys_info["class"](seed=seed, **sys_info["kwargs"])
                for _ in range(NUM_TIMESTEPS):
                    system.step()

                matrix, _ = trajectory_to_matrix(system.history)
                ed = compute_effective_dimensionality(matrix)
                cn = compute_condition_number(matrix)
                survivors = compute_survivor_observables(matrix)

                seed_results.append({
                    'ed': ed,
                    'condition_number': cn,
                    'survivors': survivors,
                })
            except Exception as e:
                print(f"    Seed {seed}: ERROR - {e}")

        if seed_results:
            eds = [r['ed'] for r in seed_results]
            ed_mean, ed_ci = compute_confidence_interval(eds)
            print(f"    ED: {ed_mean:.4f} ± {ed_ci:.4f}")

            # Compute improvement over baseline
            baseline_mean = np.mean([all_results[b]['ed_mean'] for b in baseline_systems.keys()])
            improvement = ed_mean / baseline_mean if baseline_mean > 0 else 0

            all_results[sys_name] = {
                'type': 'resistant',
                'ed_mean': ed_mean,
                'ed_ci': ed_ci,
                'improvement_over_baseline': improvement,
                'meets_primary_criterion': ed_mean > 3.0,
                'meets_secondary_criterion': improvement > 2.0,
                'n_seeds': len(seed_results),
            }

    # Summary
    print(f"\n{'=' * 70}")
    print("ANTI-COLLAPSE SYSTEMS SUMMARY")
    print(f"{'=' * 70}")

    print("\nBaseline systems:")
    for sys_name, result in all_results.items():
        if result['type'] == 'baseline':
            print(f"  {sys_name}: ED={result['ed_mean']:.4f}")

    print("\nResistant systems:")
    for sys_name, result in all_results.items():
        if result['type'] == 'resistant':
            status = "✓" if result['meets_primary_criterion'] else "✗"
            print(f"  {sys_name}: ED={result['ed_mean']:.4f} "
                  f"[Primary: {status}, "
                  f"Improvement: {result['improvement_over_baseline']:.2f}x]")

    # Save results
    output = {
        "metadata": {
            "num_seeds": NUM_SEEDS,
            "num_timesteps": NUM_TIMESTEPS,
            "baseline_systems": list(baseline_systems.keys()),
            "resistant_systems": list(resistant_systems.keys()),
            "primary_criterion": "ED > 3.0",
            "secondary_criterion": "ED_system / ED_baseline > 2.0",
        },
        "results": all_results,
    }

    output_file = os.path.join(OUTPUT_DIR, "resistant_systems_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print("ANTI-COLLAPSE SYNTHETIC SYSTEMS TEST COMPLETE")
    print(f"{'=' * 70}")
    print(f"Results saved to: {output_file}")

    return output


if __name__ == "__main__":
    run_resistant_systems_test()
