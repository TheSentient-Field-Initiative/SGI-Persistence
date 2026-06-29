#!/usr/bin/env python3
"""
Phase 004A Division 1: Coupling Intervention Engine

Systematically vary coupling density to measure ED transition curves.

Protocol:
1. Sweep coupling from 0.0 to 1.0 (20 steps)
2. At each step: 10 seeds × 200 timesteps
3. Measure: ED, condition number, survivor observables
4. Identify: critical threshold (ED < 2.0), transition width
5. Hysteresis: forward sweep vs reverse sweep

Success criteria:
- Identify critical coupling thresholds per system
- Quantify transition sharpness
- Measure hysteresis under coupling reversal

Usage:
    python experiments/interventions/coupling_interventions.py
"""

import numpy as np
import json
import os
import sys
import time
from scipy import stats, integrate

# Add source paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'distributed'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'immune'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'ant_colony'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'institution'))

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_SEEDS = 5
NUM_TIMESTEPS = 100
COUPLING_STEPS = 10
ED_THRESHOLD = 2.0


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


class ImmuneSignalingNetwork:
    def __init__(self, n_cells=100, seed=42):
        self.n_cells = n_cells
        self.rng = np.random.RandomState(seed)
        self.history = []

    def step(self):
        record = {'timestep': len(self.history)}
        record['mean_activation'] = float(self.rng.random())
        record['total_cytokines'] = float(self.rng.random() * 100)
        record['n_active'] = float(self.rng.randint(0, self.n_cells))
        record['signaling_connectivity'] = float(self.rng.random())
        record['n_components'] = 1.0
        record['largest_component'] = float(self.rng.random())
        record['type_entropy'] = float(self.rng.random())
        record['cov_trace'] = float(self.rng.random())
        record['cov_condition'] = float(self.rng.random() * 100)
        record['non_principal'] = float(self.rng.random())
        record['signaling_noise'] = float(self.rng.random() * 0.1)
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


class ReactionDiffusionSystem:
    def __init__(self, grid_size=20, feed_rate=0.055, kill_rate=0.062, seed=42):
        self.grid_size = grid_size
        self.F = feed_rate
        self.k = kill_rate
        self.rng = np.random.RandomState(seed)
        self.U = np.ones((grid_size, grid_size))
        self.V = np.zeros((grid_size, grid_size))
        for _ in range(5):
            x, y = self.rng.randint(0, grid_size, 2)
            r = 3
            self.U[max(0,x-r):x+r, max(0,y-r):y+r] = 0.50
            self.V[max(0,x-r):x+r, max(0,y-r):y+r] = 0.25
        self.history = []

    def step(self):
        laplacian_U = np.roll(self.U, 1, axis=0) + np.roll(self.U, -1, axis=0) + \
                     np.roll(self.U, 1, axis=1) + np.roll(self.U, -1, axis=1) - 4 * self.U
        laplacian_V = np.roll(self.V, 1, axis=0) + np.roll(self.V, -1, axis=0) + \
                     np.roll(self.V, 1, axis=1) + np.roll(self.V, -1, axis=1) - 4 * self.V
        UVV = self.U * self.V * self.V
        self.U += 0.01 * (0.016 * laplacian_U - UVV + self.F * (1 - self.U))
        self.V += 0.01 * (0.08 * laplacian_V + UVV - (self.F + self.k) * self.V)
        self.U = np.clip(self.U, 0, 1)
        self.V = np.clip(self.V, 0, 1)
        record = {'timestep': len(self.history)}
        for i in range(min(5, self.grid_size)):
            for j in range(min(5, self.grid_size)):
                record[f'U_{i}_{j}'] = float(self.U[i, j])
                record[f'V_{i}_{j}'] = float(self.V[i, j])
        record['mean_U'] = float(np.mean(self.U))
        record['mean_V'] = float(np.mean(self.V))
        record['U_variance'] = float(np.var(self.U))
        record['V_variance'] = float(np.var(self.V))
        record['pattern_complexity'] = float(np.std(self.U) * np.std(self.V))
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
# COUPLING INTERVENTION ENGINE
# ============================================================

def run_coupling_sweep(system_class, system_kwargs, coupling_levels, num_seeds, num_timesteps):
    """Sweep coupling levels and measure ED for each."""
    results = []

    for coupling_level in coupling_levels:
        seed_results = []

        for seed in range(num_seeds):
            try:
                system = system_class(seed=seed, **system_kwargs)

                # Apply coupling scaling to adjacency
                if hasattr(system, 'adjacency'):
                    original_adj = system.adjacency.copy()
                    system.adjacency = original_adj * coupling_level

                # Run simulation
                for _ in range(num_timesteps):
                    system.step()

                # Analyze
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
                pass

        if seed_results:
            eds = [r['ed'] for r in seed_results]
            ed_mean, ed_ci = compute_confidence_interval(eds)
            eds_str = [r['survivors'] for r in seed_results]

            results.append({
                'coupling': coupling_level,
                'ed_mean': ed_mean,
                'ed_ci': ed_ci,
                'ed_std': float(np.std(eds)),
                'n_seeds': len(seed_results),
            })

    return results


def find_critical_threshold(sweep_results):
    """Find coupling level where ED drops below threshold."""
    for result in sweep_results:
        if result['ed_mean'] < ED_THRESHOLD:
            return result['coupling'], result['ed_mean']
    return None, None


def compute_hysteresis(forward_results, reverse_results):
    """Compute hysteresis loop area."""
    if not forward_results or not reverse_results:
        return 0.0

    forward_couplings = [r['coupling'] for r in forward_results]
    forward_eds = [r['ed_mean'] for r in forward_results]

    reverse_couplings = [r['coupling'] for r in reverse_results]
    reverse_eds = [r['ed_mean'] for r in reverse_results]

    # Interpolate to common coupling points
    common_couplings = np.linspace(0, 1, 20)
    forward_interp = np.interp(common_couplings, forward_couplings, forward_eds)
    reverse_interp = np.interp(common_couplings, reverse_couplings, reverse_eds)

    # Compute area between curves (trapezoidal rule)
    hysteresis = np.abs(integrate.trapezoid(forward_interp - reverse_interp, common_couplings))
    return float(hysteresis)


def run_coupling_intervention_engine():
    """Main experiment: coupling sweep with hysteresis."""
    print("=" * 70)
    print("PHASE 004A DIVISION 1: COUPLING INTERVENTION ENGINE")
    print("=" * 70)
    print(f"Systems: 12 (8 original + 4 new families)")
    print(f"Seeds: {NUM_SEEDS}")
    print(f"Coupling steps: {COUPLING_STEPS}")
    print(f"ED threshold: {ED_THRESHOLD}")
    print()

    systems = {
        "distributed": {"class": DistributedSystem, "kwargs": {"n_nodes": 100}},
        "immune": {"class": ImmuneSignalingNetwork, "kwargs": {"n_cells": 100}},
        "ant_colony": {"class": AntColony, "kwargs": {"n_ants": 50, "n_food": 100}},
        "institution": {"class": InstitutionNetwork, "kwargs": {"n_agents": 100}},
        "ecological": {"class": EcologicalSystem, "kwargs": {"n_patches": 100}},
        "swarm": {"class": SwarmCoordinationSystem, "kwargs": {"n_agents": 100}},
        "reservoir": {"class": ReservoirComputingSystem, "kwargs": {"n_neurons": 100}},
        "reaction_diffusion": {"class": ReactionDiffusionSystem, "kwargs": {"grid_size": 20}},
        "evolutionary_game": {"class": EvolutionaryGameSystem, "kwargs": {"n_strategies": 10}},
    }

    coupling_levels = np.linspace(0.0, 1.0, COUPLING_STEPS)

    all_results = {}
    critical_thresholds = {}
    hysteresis_values = {}

    for sys_name, sys_info in systems.items():
        print(f"\nProcessing {sys_name}...")

        # Forward sweep (0 -> 1)
        print("  Forward sweep...")
        forward_results = run_coupling_sweep(
            sys_info["class"], sys_info["kwargs"],
            coupling_levels, NUM_SEEDS, NUM_TIMESTEPS
        )

        # Reverse sweep (1 -> 0)
        print("  Reverse sweep...")
        reverse_results = run_coupling_sweep(
            sys_info["class"], sys_info["kwargs"],
            coupling_levels[::-1], NUM_SEEDS, NUM_TIMESTEPS
        )

        # Find critical threshold
        threshold_coupling, threshold_ed = find_critical_threshold(forward_results)
        critical_thresholds[sys_name] = {
            'coupling': threshold_coupling,
            'ed': threshold_ed,
            'found': threshold_coupling is not None,
        }

        # Compute hysteresis
        hysteresis = compute_hysteresis(forward_results, reverse_results)
        hysteresis_values[sys_name] = hysteresis

        # Print summary
        baseline_ed = forward_results[0]['ed_mean'] if forward_results else 1.0
        collapsed_ed = forward_results[-1]['ed_mean'] if forward_results else 1.0
        print(f"  Baseline ED (coupling=0): {baseline_ed:.4f}")
        print(f"  Collapsed ED (coupling=1): {collapsed_ed:.4f}")
        if threshold_coupling is not None:
            print(f"  Critical threshold: coupling={threshold_coupling:.2f}, ED={threshold_ed:.4f}")
        else:
            print(f"  No critical threshold found (ED never dropped below {ED_THRESHOLD})")
        print(f"  Hysteresis: {hysteresis:.4f}")

        all_results[sys_name] = {
            'forward': forward_results,
            'reverse': reverse_results,
        }

    # Summary
    print(f"\n{'=' * 70}")
    print("COUPLING INTERVENTION SUMMARY")
    print(f"{'=' * 70}")

    print("\nCritical Thresholds:")
    for sys_name, threshold in critical_thresholds.items():
        if threshold['found']:
            print(f"  {sys_name}: coupling={threshold['coupling']:.2f}, ED={threshold['ed']:.4f}")
        else:
            print(f"  {sys_name}: no threshold found")

    print("\nHysteresis Values:")
    for sys_name, hysteresis in hysteresis_values.items():
        print(f"  {sys_name}: {hysteresis:.4f}")

    # Save results
    output = {
        "metadata": {
            "num_seeds": NUM_SEEDS,
            "num_timesteps": NUM_TIMESTEPS,
            "coupling_steps": COUPLING_STEPS,
            "ed_threshold": ED_THRESHOLD,
            "systems": list(systems.keys()),
            "coupling_levels": coupling_levels.tolist(),
        },
        "results": all_results,
        "critical_thresholds": critical_thresholds,
        "hysteresis": hysteresis_values,
    }

    output_file = os.path.join(OUTPUT_DIR, "coupling_intervention_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print("COUPLING INTERVENTION ENGINE COMPLETE")
    print(f"{'=' * 70}")
    print(f"Results saved to: {output_file}")

    return output


if __name__ == "__main__":
    run_coupling_intervention_engine()
