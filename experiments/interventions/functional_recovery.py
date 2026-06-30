#!/usr/bin/env python3
"""
Phase 004B Division 1: Functional Recovery Metrics (CRITICAL)

Central question: Can representational recovery restore FUNCTION, or only dimensional statistics?

Protocol:
1. Define functional metrics per system
2. Measure baseline function
3. Induce collapse
4. Apply recovery interventions
5. Compare ED recovery vs functional recovery
6. Identify systems where representation recovers but function does NOT

Required functional metrics:
- distributed: consensus accuracy
- immune: pathogen suppression
- epidemic: infection containment
- market: price stability
- neural: prediction consistency
- swarm: formation coherence
- reaction_diffusion: pattern persistence
- institution: decision stability

Success criteria:
- Compute functional_recovery_ratio = post_function / baseline_function
- Compute representational_recovery_ratio = post_ED / baseline_ED
- Identify systems where representation recovers BUT function does NOT

Usage:
    python experiments/interventions/functional_recovery.py
"""

import numpy as np
import json
import os
import sys
import time
from scipy import stats

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_SEEDS = 10
NUM_TIMESTEPS = 200
COLLAPSE_STEPS = 100
RECOVERY_STEPS = 100


# ============================================================
# SYSTEM DEFINITIONS WITH FUNCTIONAL METRICS
# ============================================================

class DistributedSystem:
    """Distributed system with consensus functionality."""

    def __init__(self, n_nodes=100, seed=42):
        self.n_nodes = n_nodes
        self.rng = np.random.RandomState(seed)
        self.adjacency = self._create_random_graph()
        self.history = []
        self.consensus_state = self.rng.choice([0, 1], size=n_nodes)
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
        # Consensus dynamics
        new_state = self.consensus_state.copy()
        for i in range(self.n_nodes):
            neighbors = np.where(self.adjacency[i] > 0)[0]
            if len(neighbors) > 0:
                neighbor_votes = self.consensus_state[neighbors]
                majority = np.mean(neighbor_votes)
                if majority > 0.5:
                    new_state[i] = 1
                elif majority < 0.5:
                    new_state[i] = 0
        self.consensus_state = new_state

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

    def compute_function(self):
        """Consensus accuracy: fraction of nodes matching target."""
        return float(np.mean(self.consensus_state == self.target_state))


class ImmuneSignalingNetwork:
    """Immune system with pathogen suppression functionality."""

    def __init__(self, n_cells=100, seed=42):
        self.n_cells = n_cells
        self.rng = np.random.RandomState(seed)
        self.history = []
        self.pathogen_load = 1.0
        self.immune_response = 0.0

    def step(self):
        # Immune dynamics
        self.immune_response = 0.9 * self.immune_response + 0.1 * np.mean([self.rng.random()])
        self.pathogen_load *= (1.0 - 0.1 * self.immune_response)
        self.pathogen_load = max(0.01, self.pathogen_load)

        record = {'timestep': len(self.history)}
        record['mean_activation'] = float(self.immune_response)
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

    def compute_function(self):
        """Pathogen suppression: 1 - normalized pathogen load."""
        return float(1.0 - self.pathogen_load / 1.0)


class EpidemicSystem:
    """Epidemic system with infection containment functionality."""

    def __init__(self, n_nodes=100, seed=42):
        self.n_nodes = n_nodes
        self.rng = np.random.RandomState(seed)
        self.history = []
        self.infected = n_nodes // 10
        self.recovered = 0

    def step(self):
        # SIR dynamics
        new_infections = int(0.3 * self.infected * (1 - self.infected / self.n_nodes))
        new_recoveries = int(0.1 * self.infected)
        self.infected = max(0, self.infected + new_infections - new_recoveries)
        self.recovered = min(self.n_nodes, self.recovered + new_recoveries)

        record = {'timestep': len(self.history)}
        for i in range(min(10, self.n_nodes)):
            record[f'node_{i}'] = float(self.rng.choice([0, 1, 2]))
        record['n_susceptible'] = float(self.n_nodes - self.infected - self.recovered)
        record['n_infected'] = float(self.infected)
        record['n_recovered'] = float(self.recovered)
        self.history.append(record)
        return record

    def compute_function(self):
        """Infection containment: 1 - normalized infection rate."""
        return float(1.0 - self.infected / self.n_nodes)


class MarketSystem:
    """Market system with price stability functionality."""

    def __init__(self, n_agents=100, seed=42):
        self.n_agents = n_agents
        self.rng = np.random.RandomState(seed)
        self.history = []
        self.price = 50.0
        self.price_history = [self.price]

    def step(self):
        # Market dynamics
        shock = self.rng.randn() * 2.0
        self.price = 0.95 * self.price + 0.05 * 50.0 + shock
        self.price_history.append(self.price)

        record = {'timestep': len(self.history)}
        for i in range(min(10, self.n_agents)):
            record[f'agent_{i}'] = float(self.rng.uniform(10, 100))
        record['price'] = float(self.price)
        record['mean_wealth'] = float(self.rng.uniform(10, 100))
        record['wealth_variance'] = float(self.rng.random() * 100)
        self.history.append(record)
        return record

    def compute_function(self):
        """Price stability: 1 - normalized price variance."""
        if len(self.price_history) < 10:
            return 1.0
        variance = np.var(self.price_history[-100:])
        return float(1.0 - min(1.0, variance / 100.0))


class NeuralSystem:
    """Neural system with prediction consistency functionality."""

    def __init__(self, n_neurons=100, seed=42):
        self.n_neurons = n_neurons
        self.rng = np.random.RandomState(seed)
        self.history = []
        self.activity = self.rng.randn(n_neurons) * 0.5
        self.prediction_error = 0.0

    def step(self):
        # Neural dynamics
        noise = self.rng.randn(self.n_neurons) * 0.01
        new_activity = np.tanh(self.activity + noise)
        self.prediction_error = 0.9 * self.prediction_error + 0.1 * np.mean(np.abs(new_activity - self.activity))
        self.activity = new_activity

        record = {'timestep': len(self.history)}
        for i in range(min(10, self.n_neurons)):
            record[f'neuron_{i}'] = float(self.activity[i])
        record['mean_activity'] = float(np.mean(self.activity))
        record['activity_variance'] = float(np.var(self.activity))
        self.history.append(record)
        return record

    def compute_function(self):
        """Prediction consistency: 1 - normalized prediction error."""
        return float(1.0 - min(1.0, self.prediction_error))


class SwarmCoordinationSystem:
    """Swarm system with formation coherence functionality."""

    def __init__(self, n_agents=100, seed=42):
        self.n_agents = n_agents
        self.rng = np.random.RandomState(seed)
        self.positions = self.rng.randn(n_agents, 2) * 10
        self.velocities = self.rng.randn(n_agents, 2) * 0.1
        self.history = []
        self.target_formation = self.rng.randn(n_agents, 2) * 5

    def step(self):
        # Swarm dynamics
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

    def compute_function(self):
        """Formation coherence: 1 - normalized formation error."""
        formation_error = np.mean(np.sqrt(np.sum((self.positions - self.target_formation)**2, axis=1)))
        return float(1.0 - min(1.0, formation_error / 10.0))


class ReactionDiffusionSystem:
    """Reaction-diffusion system with pattern persistence functionality."""

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
        self.initial_pattern = self.U.copy()

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

    def compute_function(self):
        """Pattern persistence: similarity to initial pattern."""
        return float(1.0 - np.mean(np.abs(self.U - self.initial_pattern)))


class InstitutionNetwork:
    """Institution system with decision stability functionality."""

    def __init__(self, n_agents=100, seed=42):
        self.n_agents = n_agents
        self.rng = np.random.RandomState(seed)
        self.history = []
        self.decisions = self.rng.choice([0, 1], size=n_agents)
        self.stability = 1.0

    def step(self):
        # Decision dynamics
        new_decisions = self.decisions.copy()
        for i in range(self.n_agents):
            if self.rng.random() < 0.1:
                new_decisions[i] = 1 - new_decisions[i]
        self.stability = 0.95 * self.stability + 0.05 * np.mean(new_decisions == self.decisions)
        self.decisions = new_decisions

        record = {'timestep': len(self.history)}
        record['cooperation_rate'] = float(np.mean(self.decisions))
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

    def compute_function(self):
        """Decision stability: normalized stability metric."""
        return float(self.stability)


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


class SynchronizationSuppressionIntervention:
    """Suppresses synchronization in the system."""

    def __init__(self, system, suppression_level=0.0):
        self.system = system
        self.suppression_level = suppression_level
        self._original_step = system.step

    def step(self):
        record = self._original_step()
        if self.suppression_level > 0 and hasattr(self.system, 'consensus_state'):
            noise = np.random.randn(len(self.system.consensus_state)) * self.suppression_level
            self.system.consensus_state = np.clip(self.system.consensus_state + noise, 0, 1)
        return record

    def set_suppression(self, level):
        self.suppression_level = level


# ============================================================
# FUNCTIONAL RECOVERY EXPERIMENT
# ============================================================

def run_functional_recovery():
    """Main experiment: functional vs representational recovery."""
    print("=" * 70)
    print("PHASE 004B DIVISION 1: FUNCTIONAL RECOVERY METRICS")
    print("=" * 70)
    print(f"Systems: 8 (with functional metrics)")
    print(f"Seeds: {NUM_SEEDS}")
    print(f"Collapse steps: {COLLAPSE_STEPS}")
    print(f"Recovery steps: {RECOVERY_STEPS}")
    print()

    systems = {
        "distributed": {"class": DistributedSystem, "kwargs": {"n_nodes": 100}},
        "immune": {"class": ImmuneSignalingNetwork, "kwargs": {"n_cells": 100}},
        "epidemic": {"class": EpidemicSystem, "kwargs": {"n_nodes": 100}},
        "market": {"class": MarketSystem, "kwargs": {"n_agents": 100}},
        "neural": {"class": NeuralSystem, "kwargs": {"n_neurons": 100}},
        "swarm": {"class": SwarmCoordinationSystem, "kwargs": {"n_agents": 100}},
        "reaction_diffusion": {"class": ReactionDiffusionSystem, "kwargs": {"grid_size": 20}},
        "institution": {"class": InstitutionNetwork, "kwargs": {"n_agents": 100}},
    }

    recovery_methods = [
        "coupling_reduction",
        "synchronization_suppression",
        "noise_injection",
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
                baseline_function = system.compute_function()
                baseline_survivors = compute_survivor_observables(baseline_matrix)

                sys_results["baseline"].append({
                    "ed": baseline_ed,
                    "function": baseline_function,
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
                collapse_function = system.compute_function()
                collapse_survivors = compute_survivor_observables(collapse_matrix)

                sys_results["collapsed"].append({
                    "ed": collapse_ed,
                    "function": collapse_function,
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
                    elif method == "synchronization_suppression":
                        intervention = SynchronizationSuppressionIntervention(system, suppression_level=0.5)
                        for step in range(RECOVERY_STEPS):
                            intervention.set_suppression(0.5 * (1 - step / RECOVERY_STEPS))
                            intervention.step()
                    elif method == "noise_injection":
                        intervention = NoiseInjectionIntervention(system, noise_level=0.3)
                        for step in range(RECOVERY_STEPS):
                            intervention.set_noise(0.3 * (1 - step / RECOVERY_STEPS))
                            intervention.step()
                    elif method == "combined":
                        intervention = CouplingIntervention(system, coupling_level=1.0)
                        noise_intervention = NoiseInjectionIntervention(system, noise_level=0.2)
                        sync_intervention = SynchronizationSuppressionIntervention(system, suppression_level=0.2)
                        for step in range(RECOVERY_STEPS):
                            intervention.set_coupling(1.0 - step / RECOVERY_STEPS)
                            noise_intervention.set_noise(0.2 * (1 - step / RECOVERY_STEPS))
                            sync_intervention.set_suppression(0.2 * (1 - step / RECOVERY_STEPS))
                            intervention.step()

                    recovery_matrix, _ = trajectory_to_matrix(system.history)
                    recovery_ed = compute_effective_dimensionality(recovery_matrix)
                    recovery_function = system.compute_function()
                    recovery_survivors = compute_survivor_observables(recovery_matrix)

                    # Compute recovery ratios
                    ed_recovery = (recovery_ed - collapse_ed) / (baseline_ed - collapse_ed) if baseline_ed != collapse_ed else 0.0
                    function_recovery = (recovery_function - collapse_function) / (baseline_function - collapse_function) if baseline_function != collapse_function else 0.0

                    sys_results["recovery"][method].append({
                        "ed": recovery_ed,
                        "function": recovery_function,
                        "survivors": recovery_survivors,
                        "ed_recovery_ratio": ed_recovery,
                        "function_recovery_ratio": function_recovery,
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
                control_function = system.compute_function()
                control_survivors = compute_survivor_observables(control_matrix)
                sys_results["controls"]["randomized"].append({
                    "ed": control_ed,
                    "function": control_function,
                    "survivors": control_survivors,
                })

                # Sham control
                system = sys_info["class"](seed=seed, **sys_info["kwargs"])
                for _ in range(RECOVERY_STEPS):
                    system.step()
                sham_matrix, _ = trajectory_to_matrix(system.history)
                sham_ed = compute_effective_dimensionality(sham_matrix)
                sham_function = system.compute_function()
                sham_survivors = compute_survivor_observables(sham_matrix)
                sys_results["controls"]["sham"].append({
                    "ed": sham_ed,
                    "function": sham_function,
                    "survivors": sham_survivors,
                })

            except Exception as e:
                print(f"  Seed {seed}: ERROR - {e}")

        all_results[sys_name] = sys_results

    # Aggregate results
    print(f"\n{'=' * 70}")
    print("FUNCTIONAL RECOVERY RESULTS SUMMARY")
    print(f"{'=' * 70}")

    for sys_name, sys_results in all_results.items():
        baseline_eds = [r['ed'] for r in sys_results['baseline']]
        baseline_functions = [r['function'] for r in sys_results['baseline']]
        collapsed_eds = [r['ed'] for r in sys_results['collapsed']]
        collapsed_functions = [r['function'] for r in sys_results['collapsed']]

        baseline_ed_mean, baseline_ed_ci = compute_confidence_interval(baseline_eds)
        baseline_func_mean, baseline_func_ci = compute_confidence_interval(baseline_functions)
        collapsed_ed_mean, collapsed_ed_ci = compute_confidence_interval(collapsed_eds)
        collapsed_func_mean, collapsed_func_ci = compute_confidence_interval(collapsed_functions)

        print(f"\n{sys_name}:")
        print(f"  Baseline: ED={baseline_ed_mean:.4f}, Function={baseline_func_mean:.4f}")
        print(f"  Collapsed: ED={collapsed_ed_mean:.4f}, Function={collapsed_func_mean:.4f}")

        for method in recovery_methods:
            method_eds = [r['ed'] for r in sys_results['recovery'][method]]
            method_functions = [r['function'] for r in sys_results['recovery'][method]]
            method_ed_recovery = [r['ed_recovery_ratio'] for r in sys_results['recovery'][method]]
            method_func_recovery = [r['function_recovery_ratio'] for r in sys_results['recovery'][method]]

            ed_mean, ed_ci = compute_confidence_interval(method_eds)
            func_mean, func_ci = compute_confidence_interval(method_functions)
            ed_recovery_mean, ed_recovery_ci = compute_confidence_interval(method_ed_recovery)
            func_recovery_mean, func_recovery_ci = compute_confidence_interval(method_func_recovery)

            # KEY ANALYSIS: Does representation recover but function does NOT?
            representation_recovers = ed_recovery_mean > 0.5
            function_recovers = func_recovery_mean > 0.5
            dissociation = representation_recovers and not function_recovers

            print(f"  {method}:")
            print(f"    ED={ed_mean:.4f}, Function={func_mean:.4f}")
            print(f"    ED recovery={ed_recovery_mean:.1%}, Function recovery={func_recovery_mean:.1%}")
            if dissociation:
                print(f"    *** DISSOCIATION: Representation recovers but function does NOT ***")

    # Save results
    output = {
        "metadata": {
            "num_seeds": NUM_SEEDS,
            "num_timesteps": NUM_TIMESTEPS,
            "collapse_steps": COLLAPSE_STEPS,
            "recovery_steps": RECOVERY_STEPS,
            "systems": list(systems.keys()),
            "recovery_methods": recovery_methods,
        },
        "results": all_results,
    }

    output_file = os.path.join(OUTPUT_DIR, "functional_recovery_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print("FUNCTIONAL RECOVERY EXPERIMENT COMPLETE")
    print(f"{'=' * 70}")
    print(f"Results saved to: {output_file}")

    return output


if __name__ == "__main__":
    run_functional_recovery()
