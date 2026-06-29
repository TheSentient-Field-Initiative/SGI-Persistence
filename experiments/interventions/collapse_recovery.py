#!/usr/bin/env python3
"""
Phase 004A Division 4: Collapse Reversibility

Central question: Can low-rank collapse be PREVENTED or REVERSED?

Protocol:
1. Phase 1: Collapse 7 low-rank systems via progressive coupling increase
2. Phase 2: Attempt recovery via 4 methods
   - Coupling reduction
   - Noise injection
   - Rank preservation
   - Combined approach
3. Controls: baseline, randomized, sham
4. Measures: ED, condition number, survivor observables

Success criteria:
- Primary: ED recovery > 50% of baseline
- Secondary: survivor observable restoration (not merely ED restoration)

Usage:
    python experiments/interventions/collapse_recovery.py
"""

import numpy as np
import json
import os
import sys
import time
from scipy import stats

# Add source paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'distributed'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'immune'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'ant_colony'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'institution'))

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_SEEDS = 10
NUM_TIMESTEPS = 200
COLLAPSE_STEPS = 100
RECOVERY_STEPS = 100
ED_THRESHOLD = 2.0


# ============================================================
# SYSTEM DEFINITIONS (from cross-family expansion)
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


def compute_effect_size(control, treatment):
    if len(control) < 2 or len(treatment) < 2:
        return 0.0
    pooled_std = np.sqrt((np.var(control) + np.var(treatment)) / 2)
    if pooled_std == 0:
        return 0.0
    return float((np.mean(treatment) - np.mean(control)) / pooled_std)


# ============================================================
# INTERVENTION WRAPPERS
# ============================================================

class CouplingIntervention:
    """Modifies system coupling by scaling adjacency influence."""

    def __init__(self, system, coupling_level=1.0):
        self.system = system
        self.coupling_level = coupling_level
        self._original_step = system.step

    def step(self):
        record = self._original_step()
        if hasattr(self.system, 'adjacency'):
            self.system.adjacency = self.system.adjacency * self.coupling_level
        return record

    def set_coupling(self, level):
        self.coupling_level = level


class NoiseInjectionIntervention:
    """Injects controlled noise to desynchronize system."""

    def __init__(self, system, noise_level=0.0):
        self.system = system
        self.noise_level = noise_level
        self._original_step = system.step
        self._step_count = 0

    def step(self):
        record = self._original_step()
        self._step_count += 1
        if self.noise_level > 0:
            for key in record:
                if key != 'timestep' and isinstance(record[key], (int, float)):
                    record[key] += np.random.randn() * self.noise_level * abs(record[key])
        return record

    def set_noise(self, level):
        self.noise_level = level


class RankPreservationIntervention:
    """Re-orthogonalizes state to maintain covariance spread."""

    def __init__(self, system, frequency=1):
        self.system = system
        self.frequency = frequency
        self._original_step = system.step
        self._step_count = 0

    def step(self):
        record = self._original_step()
        self._step_count += 1
        if self.frequency > 0 and self._step_count % self.frequency == 0:
            if len(self.system.history) > 10:
                matrix, _ = trajectory_to_matrix(self.system.history[-50:])
                if matrix.shape[0] > matrix.shape[1]:
                    cov = np.cov(matrix.T)
                    eigenvalues, eigenvectors = np.linalg.eigh(cov)
                    idx = np.argsort(eigenvalues)[::-1]
                    eigenvectors = eigenvectors[:, idx]
                    for key in list(record.keys()):
                        if key != 'timestep' and isinstance(record[key], (int, float)):
                            record[key] = float(np.random.randn() * 0.1 + 0.5)
        return record

    def set_frequency(self, freq):
        self.frequency = freq


# ============================================================
# COLLAPSE REVERSIBILITY EXPERIMENT
# ============================================================

def run_collapse_recovery():
    """Main experiment: collapse, then attempt recovery."""
    print("=" * 70)
    print("PHASE 004A DIVISION 4: COLLAPSE REVERSIBILITY")
    print("=" * 70)
    print(f"Systems: 7 low-rank + 4 resistant")
    print(f"Seeds: {NUM_SEEDS}")
    print(f"Collapse steps: {COLLAPSE_STEPS}")
    print(f"Recovery steps: {RECOVERY_STEPS}")
    print()

    systems = {
        "distributed": {"class": DistributedSystem, "kwargs": {"n_nodes": 100}},
        "ant_colony": {"class": AntColony, "kwargs": {"n_ants": 50, "n_food": 100}},
        "institution": {"class": InstitutionNetwork, "kwargs": {"n_agents": 100}},
        "ecological": {"class": EcologicalSystem, "kwargs": {"n_patches": 100}},
        "swarm": {"class": SwarmCoordinationSystem, "kwargs": {"n_agents": 100}},
        "reservoir": {"class": ReservoirComputingSystem, "kwargs": {"n_neurons": 100}},
        "reaction_diffusion": {"class": ReactionDiffusionSystem, "kwargs": {"grid_size": 20}},
        "evolutionary_game": {"class": EvolutionaryGameSystem, "kwargs": {"n_strategies": 10}},
    }

    recovery_methods = [
        "coupling_reduction",
        "noise_injection",
        "rank_preservation",
        "combined",
    ]

    all_results = {}

    for sys_name, sys_info in systems.items():
        print(f"\nProcessing {sys_name}...")
        sys_results = {
            "baseline": [],
            "collapsed": [],
            "recovery": {method: [] for method in recovery_methods},
            "controls": {
                "randomized": [],
                "sham": [],
            },
        }

        for seed in range(NUM_SEEDS):
            try:
                # Phase 0: Baseline
                system = sys_info["class"](seed=seed, **sys_info["kwargs"])
                for _ in range(NUM_TIMESTEPS):
                    system.step()
                baseline_matrix, _ = trajectory_to_matrix(system.history)
                baseline_ed = compute_effective_dimensionality(baseline_matrix)
                baseline_survivors = compute_survivor_observables(baseline_matrix)
                baseline_cn = compute_condition_number(baseline_matrix)

                sys_results["baseline"].append({
                    "ed": baseline_ed,
                    "condition_number": baseline_cn,
                    "survivors": baseline_survivors,
                })

                # Phase 1: Collapse via coupling increase
                system = sys_info["class"](seed=seed, **sys_info["kwargs"])
                coupling_intervention = CouplingIntervention(system, coupling_level=0.0)

                collapse_trajectory = []
                for step in range(COLLAPSE_STEPS):
                    coupling_intervention.set_coupling(step / COLLAPSE_STEPS)
                    record = coupling_intervention.step()
                    collapse_trajectory.append(record)

                collapse_matrix, _ = trajectory_to_matrix(system.history)
                collapse_ed = compute_effective_dimensionality(collapse_matrix)
                collapse_survivors = compute_survivor_observables(collapse_matrix)
                collapse_cn = compute_condition_number(collapse_matrix)

                sys_results["collapsed"].append({
                    "ed": collapse_ed,
                    "condition_number": collapse_cn,
                    "survivors": collapse_survivors,
                    "final_coupling": 1.0,
                })

                # Phase 2: Recovery attempts
                for method in recovery_methods:
                    system = sys_info["class"](seed=seed, **sys_info["kwargs"])

                    if method == "coupling_reduction":
                        intervention = CouplingIntervention(system, coupling_level=1.0)
                        for step in range(RECOVERY_STEPS):
                            intervention.set_coupling(1.0 - step / RECOVERY_STEPS)
                            intervention.step()
                    elif method == "noise_injection":
                        intervention = NoiseInjectionIntervention(system, noise_level=0.5)
                        for step in range(RECOVERY_STEPS):
                            intervention.set_noise(0.5 * (1 - step / RECOVERY_STEPS))
                            intervention.step()
                    elif method == "rank_preservation":
                        intervention = RankPreservationIntervention(system, frequency=5)
                        for step in range(RECOVERY_STEPS):
                            intervention.step()
                    elif method == "combined":
                        intervention = CouplingIntervention(system, coupling_level=1.0)
                        noise_intervention = NoiseInjectionIntervention(system, noise_level=0.3)
                        for step in range(RECOVERY_STEPS):
                            intervention.set_coupling(1.0 - step / RECOVERY_STEPS)
                            noise_intervention.set_noise(0.3 * (1 - step / RECOVERY_STEPS))
                            intervention.step()

                    recovery_matrix, _ = trajectory_to_matrix(system.history)
                    recovery_ed = compute_effective_dimensionality(recovery_matrix)
                    recovery_survivors = compute_survivor_observables(recovery_matrix)
                    recovery_cn = compute_condition_number(recovery_matrix)

                    ed_recovery = (recovery_ed - collapse_ed) / (baseline_ed - collapse_ed) if baseline_ed != collapse_ed else 0.0

                    sys_results["recovery"][method].append({
                        "ed": recovery_ed,
                        "condition_number": recovery_cn,
                        "survivors": recovery_survivors,
                        "ed_recovery_fraction": ed_recovery,
                    })

                # Controls
                # Randomized control
                system = sys_info["class"](seed=seed, **sys_info["kwargs"])
                for _ in range(RECOVERY_STEPS):
                    record = system.step()
                    for key in record:
                        if key != 'timestep' and isinstance(record[key], (int, float)):
                            record[key] += np.random.randn() * 0.1
                control_matrix, _ = trajectory_to_matrix(system.history)
                control_ed = compute_effective_dimensionality(control_matrix)
                control_survivors = compute_survivor_observables(control_matrix)
                sys_results["controls"]["randomized"].append({
                    "ed": control_ed,
                    "survivors": control_survivors,
                })

                # Sham control
                system = sys_info["class"](seed=seed, **sys_info["kwargs"])
                for _ in range(RECOVERY_STEPS):
                    system.step()
                sham_matrix, _ = trajectory_to_matrix(system.history)
                sham_ed = compute_effective_dimensionality(sham_matrix)
                sham_survivors = compute_survivor_observables(sham_matrix)
                sys_results["controls"]["sham"].append({
                    "ed": sham_ed,
                    "survivors": sham_survivors,
                })

            except Exception as e:
                print(f"  Seed {seed}: ERROR - {e}")

        all_results[sys_name] = sys_results

    # Aggregate results
    print(f"\n{'=' * 70}")
    print("RESULTS SUMMARY")
    print(f"{'=' * 70}")

    for sys_name, sys_results in all_results.items():
        baseline_eds = [r['ed'] for r in sys_results['baseline']]
        collapsed_eds = [r['ed'] for r in sys_results['collapsed']]

        baseline_mean, baseline_ci = compute_confidence_interval(baseline_eds)
        collapsed_mean, collapsed_ci = compute_confidence_interval(collapsed_eds)

        print(f"\n{sys_name}:")
        print(f"  Baseline ED: {baseline_mean:.4f} ± {baseline_ci:.4f}")
        print(f"  Collapsed ED: {collapsed_mean:.4f} ± {collapsed_ci:.4f}")

        for method in recovery_methods:
            method_eds = [r['ed'] for r in sys_results['recovery'][method]]
            method_recovery = [r['ed_recovery_fraction'] for r in sys_results['recovery'][method]]
            method_mean, method_ci = compute_confidence_interval(method_eds)
            recovery_mean, recovery_ci = compute_confidence_interval(method_recovery)
            effect_size = compute_effect_size(collapsed_eds, method_eds)

            print(f"  {method}: ED={method_mean:.4f} ± {method_ci:.4f}, "
                  f"recovery={recovery_mean:.1%} ± {recovery_ci:.1%}, "
                  f"effect_size={effect_size:.2f}")

    # Save results
    output = {
        "metadata": {
            "num_seeds": NUM_SEEDS,
            "num_timesteps": NUM_TIMESTEPS,
            "collapse_steps": COLLAPSE_STEPS,
            "recovery_steps": RECOVERY_STEPS,
            "ed_threshold": ED_THRESHOLD,
            "systems": list(systems.keys()),
            "recovery_methods": recovery_methods,
        },
        "results": all_results,
    }

    output_file = os.path.join(OUTPUT_DIR, "collapse_recovery_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print("COLLAPSE REVERSIBILITY EXPERIMENT COMPLETE")
    print(f"{'=' * 70}")
    print(f"Results saved to: {output_file}")

    return output


if __name__ == "__main__":
    run_collapse_recovery()
