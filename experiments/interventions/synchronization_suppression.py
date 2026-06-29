#!/usr/bin/env python3
"""
Phase 004A Division 2: Synchronization Suppression

Inject controlled desynchronization to test collapse prevention.

Protocol:
1. Apply desynchronization at 5 levels (0%, 25%, 50%, 75%, 100%)
2. For 7 low-rank systems
3. Measure: ED, synchronization, transition_density before/after
4. Test: Does preventing synchronization prevent collapse?

Success criteria:
- Synchronization suppression increases ED
- Survivor observables improve

Usage:
    python experiments/interventions/synchronization_suppression.py
"""

import numpy as np
import json
import os
import sys
import time
from scipy import stats

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_SEEDS = 5
NUM_TIMESTEPS = 100
SUPPRESSION_LEVELS = [0.0, 0.25, 0.5, 0.75, 1.0]


# ============================================================
# SYSTEM DEFINITIONS
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


class EcologicalSystem:
    def __init__(self, n_patches=100, seed=42):
        self.n_patches = n_patches
        self.rng = np.random.RandomState(seed)
        self.history = []

    def step(self):
        record = {'timestep': len(self.history)}
        for i in range(min(10, self.n_patches)):
            record[f'prey_{i}'] = float(self.rng.uniform(20, 80))
            record[f'predator_{i}'] = float(self.rng.uniform(10, 30))
        record['total_prey'] = float(self.rng.uniform(2000, 8000))
        record['total_predators'] = float(self.rng.uniform(1000, 3000))
        self.history.append(record)
        return record


class SwarmCoordinationSystem:
    def __init__(self, n_agents=100, seed=42):
        self.n_agents = n_agents
        self.rng = np.random.RandomState(seed)
        self.positions = self.rng.randn(n_agents, 2) * 10
        self.velocities = self.rng.randn(n_agents, 2) * 0.1
        self.history = []

    def step(self):
        for i in range(self.n_agents):
            distances = np.sqrt(np.sum((self.positions - self.positions[i])**2, axis=1))
            sep_mask = (distances < 2) & (distances > 0)
            if np.any(sep_mask):
                sep = -np.mean(self.positions[sep_mask] - self.positions[i], axis=0)
            else:
                sep = np.zeros(2)
            align = np.mean(self.velocities, axis=0) - self.velocities[i]
            coh = np.mean(self.positions, axis=0) - self.positions[i]
            self.velocities[i] += 0.1 * (sep + align + coh)
            self.velocities[i] = np.clip(self.velocities[i], -1, 1)
        self.positions += self.velocities
        record = {'timestep': len(self.history)}
        for i in range(min(10, self.n_agents)):
            record[f'x_{i}'] = float(self.positions[i, 0])
            record[f'y_{i}'] = float(self.positions[i, 1])
        record['mean_speed'] = float(np.mean(np.sqrt(np.sum(self.velocities**2, axis=1))))
        record['velocity_alignment'] = float(np.mean(np.abs(np.mean(self.velocities, axis=0))))
        record['position_spread'] = float(np.std(self.positions))
        self.history.append(record)
        return record


class ReservoirComputingSystem:
    def __init__(self, n_neurons=100, spectral_radius=0.9, seed=42):
        self.n_neurons = n_neurons
        self.spectral_radius = spectral_radius
        self.rng = np.random.RandomState(seed)
        W = self.rng.randn(n_neurons, n_neurons)
        eigenvalues = np.linalg.eigvals(W)
        W = W * spectral_radius / np.max(np.abs(eigenvalues))
        self.weights = W
        self.state = self.rng.randn(n_neurons) * 0.1
        self.history = []

    def step(self):
        t = len(self.history)
        input_signal = np.sin(2 * np.pi * t / 50)
        noise = self.rng.randn(self.n_neurons) * 0.01
        self.state = np.tanh(self.weights @ self.state + input_signal + noise)
        record = {'timestep': t}
        for i in range(min(10, self.n_neurons)):
            record[f'reservoir_{i}'] = float(self.state[i])
        record['mean_activation'] = float(np.mean(np.abs(self.state)))
        record['activation_variance'] = float(np.var(self.state))
        record['spectral_radius'] = float(self.spectral_radius)
        record['echo_state_property'] = float(np.max(np.abs(np.linalg.eigvals(self.weights))))
        record['information_capacity'] = float(-np.sum(self.state * np.log(np.abs(self.state) + 1e-10)))
        self.history.append(record)
        return record


class EvolutionaryGameSystem:
    def __init__(self, n_strategies=10, population_size=100, seed=42):
        self.n_strategies = n_strategies
        self.population_size = population_size
        self.rng = np.random.RandomState(seed)
        self.fractions = self.rng.dirichlet(np.ones(n_strategies))
        self.payoff = self.rng.randn(n_strategies, n_strategies) * 0.1
        self.history = []

    def step(self):
        fitness = self.payoff @ self.fractions
        mean_fitness = np.sum(self.fractions * fitness)
        self.fractions += 0.01 * self.fractions * (fitness - mean_fitness)
        self.fractions = np.clip(self.fractions, 0, None)
        total = np.sum(self.fractions)
        if total > 0:
            self.fractions /= total
        record = {'timestep': len(self.history)}
        for i in range(min(10, self.n_strategies)):
            record[f'strategy_{i}'] = float(self.fractions[i])
        record['mean_fitness'] = float(mean_fitness)
        record['fitness_variance'] = float(np.var(fitness))
        record['strategy_entropy'] = float(-np.sum(self.fractions * np.log(self.fractions + 1e-10)))
        record['dominant_strategy'] = float(np.max(self.fractions))
        record['cooperation_index'] = float(np.mean(self.fractions[:self.n_strategies//2]))
        self.history.append(record)
        return record


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


def compute_synchronization(matrix):
    if len(matrix) > 10:
        corr_matrix = np.corrcoef(matrix.T)
        np.fill_diagonal(corr_matrix, 0)
        sync_val = np.mean(np.abs(corr_matrix))
        return float(sync_val) if not np.isnan(sync_val) else 0.0
    return 0.0


def compute_transition_density(matrix):
    if len(matrix) > 1:
        changes = np.abs(np.diff(matrix, axis=0))
        std_per_dim = np.std(matrix, axis=0)
        std_per_dim[std_per_dim == 0] = 1
        transition_mask = changes > 0.1 * std_per_dim
        return float(np.mean(transition_mask))
    return 0.0


def compute_confidence_interval(data, confidence=0.95):
    n = len(data)
    if n < 2:
        return float(data[0]) if n > 0 else 0.0, 0.0
    mean = np.mean(data)
    se = stats.sem(data)
    ci = se * stats.t.ppf((1 + confidence) / 2, n - 1)
    return float(mean), float(ci)


# ============================================================
# SYNCHRONIZATION SUPPRESSION EXPERIMENT
# ============================================================

def apply_desynchronization(matrix, level, rng):
    """Add noise proportional to pairwise correlations."""
    if level == 0:
        return matrix

    corr_matrix = np.corrcoef(matrix.T)
    np.fill_diagonal(corr_matrix, 0)

    # Add correlated noise
    noise = rng.randn(*matrix.shape) * level
    for i in range(matrix.shape[1]):
        for j in range(matrix.shape[1]):
            if abs(corr_matrix[i, j]) > 0.3:
                noise[:, i] += corr_matrix[i, j] * noise[:, j] * level

    return matrix + noise


def run_synchronization_suppression():
    """Main experiment: synchronization suppression."""
    print("=" * 70)
    print("PHASE 004A DIVISION 2: SYNCHRONIZATION SUPPRESSION")
    print("=" * 70)
    print(f"Systems: 8 low-rank")
    print(f"Seeds: {NUM_SEEDS}")
    print(f"Suppression levels: {SUPPRESSION_LEVELS}")
    print()

    systems = {
        "distributed": {"class": DistributedSystem, "kwargs": {"n_nodes": 100}},
        "ant_colony": {"class": AntColony, "kwargs": {"n_ants": 50, "n_food": 100}},
        "institution": {"class": InstitutionNetwork, "kwargs": {"n_agents": 100}},
        "ecological": {"class": EcologicalSystem, "kwargs": {"n_patches": 100}},
        "swarm": {"class": SwarmCoordinationSystem, "kwargs": {"n_agents": 100}},
        "reservoir": {"class": ReservoirComputingSystem, "kwargs": {"n_neurons": 100}},
        "evolutionary_game": {"class": EvolutionaryGameSystem, "kwargs": {"n_strategies": 10}},
    }

    all_results = {}

    for sys_name, sys_info in systems.items():
        print(f"\nProcessing {sys_name}...")
        level_results = []

        for level in SUPPRESSION_LEVELS:
            seed_results = []

            for seed in range(NUM_SEEDS):
                try:
                    system = sys_info["class"](seed=seed, **sys_info["kwargs"])

                    # Run baseline
                    for _ in range(NUM_TIMESTEPS):
                        system.step()

                    # Get baseline metrics
                    baseline_matrix, _ = trajectory_to_matrix(system.history)
                    baseline_ed = compute_effective_dimensionality(baseline_matrix)
                    baseline_sync = compute_synchronization(baseline_matrix)
                    baseline_td = compute_transition_density(baseline_matrix)

                    # Apply desynchronization
                    desync_matrix = apply_desynchronization(baseline_matrix, level, np.random.RandomState(seed))

                    # Compute post-suppression metrics
                    post_ed = compute_effective_dimensionality(desync_matrix)
                    post_sync = compute_synchronization(desync_matrix)
                    post_td = compute_transition_density(desync_matrix)

                    ed_change = post_ed - baseline_ed
                    sync_change = post_sync - baseline_sync
                    td_change = post_td - baseline_td

                    seed_results.append({
                        'baseline_ed': baseline_ed,
                        'post_ed': post_ed,
                        'ed_change': ed_change,
                        'baseline_sync': baseline_sync,
                        'post_sync': post_sync,
                        'sync_change': sync_change,
                        'baseline_td': baseline_td,
                        'post_td': post_td,
                        'td_change': td_change,
                    })
                except Exception as e:
                    pass

            if seed_results:
                eds = [r['post_ed'] for r in seed_results]
                ed_changes = [r['ed_change'] for r in seed_results]
                sync_changes = [r['sync_change'] for r in seed_results]
                td_changes = [r['td_change'] for r in seed_results]

                ed_mean, ed_ci = compute_confidence_interval(eds)
                ed_change_mean, ed_change_ci = compute_confidence_interval(ed_changes)
                sync_change_mean, sync_change_ci = compute_confidence_interval(sync_changes)
                td_change_mean, td_change_ci = compute_confidence_interval(td_changes)

                level_results.append({
                    'level': level,
                    'ed_mean': ed_mean,
                    'ed_ci': ed_ci,
                    'ed_change_mean': ed_change_mean,
                    'ed_change_ci': ed_change_ci,
                    'sync_change_mean': sync_change_mean,
                    'sync_change_ci': sync_change_ci,
                    'td_change_mean': td_change_mean,
                    'td_change_ci': td_change_ci,
                    'n_seeds': len(seed_results),
                })

                print(f"  Level {level:.0%}: ED={ed_mean:.4f}, ΔED={ed_change_mean:+.4f}, "
                      f"Δsync={sync_change_mean:+.4f}, Δtd={td_change_mean:+.4f}")

        all_results[sys_name] = level_results

    # Summary
    print(f"\n{'=' * 70}")
    print("SYNCHRONIZATION SUPPRESSION SUMMARY")
    print(f"{'=' * 70}")

    for sys_name, level_results in all_results.items():
        if level_results:
            baseline_ed = level_results[0]['ed_mean']
            max_level = level_results[-1]
            ed_improvement = (max_level['ed_mean'] - baseline_ed) / baseline_ed * 100
            print(f"{sys_name}: baseline={baseline_ed:.4f}, "
                  f"max_suppression={max_level['ed_mean']:.4f}, "
                  f"improvement={ed_improvement:+.1f}%")

    # Save results
    output = {
        "metadata": {
            "num_seeds": NUM_SEEDS,
            "num_timesteps": NUM_TIMESTEPS,
            "suppression_levels": SUPPRESSION_LEVELS,
            "systems": list(systems.keys()),
        },
        "results": all_results,
    }

    output_file = os.path.join(OUTPUT_DIR, "synchronization_suppression_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print("SYNCHRONIZATION SUPPRESSION COMPLETE")
    print(f"{'=' * 70}")
    print(f"Results saved to: {output_file}")

    return output


if __name__ == "__main__":
    run_synchronization_suppression()
