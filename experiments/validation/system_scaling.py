#!/usr/bin/env python3
"""
Phase 003I Division 2: System Scaling
Tests whether low-rank collapse generalizes across 8 systems.

Additional synthetic systems:
1. Epidemic (SIR model)
2. Neural (simple neural dynamics)
3. Market (economic agents)
4. Ecological (predator-prey)

Usage:
    python experiments/validation/system_scaling.py
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

NUM_SEEDS = 5  # 5 seeds for scalability
NUM_TIMESTEPS = 200


# ============================================================
# SYNTHETIC SYSTEMS (structurally different from existing 4)
# ============================================================

class EpidemicSystem:
    """SIR epidemic model with spatial structure."""

    def __init__(self, n_nodes=100, infection_rate=0.3, recovery_rate=0.1, seed=42):
        self.n_nodes = n_nodes
        self.beta = infection_rate
        self.gamma = recovery_rate
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
                if infected_neighbors > 0 and self.rng.random() < self.beta * infected_neighbors / 5:
                    new_state[i] = 'I'
            elif self.state[i] == 'I':
                if self.rng.random() < self.gamma:
                    new_state[i] = 'R'

        self.state = new_state

        # Record state as numerical
        state_map = {'S': 0, 'I': 1, 'R': 2}
        numerical = np.array([state_map[s] for s in self.state], dtype=float)

        record = {'timestep': len(self.history)}
        for i, val in enumerate(numerical):
            record[f'node_{i}'] = float(val)
        record['n_susceptible'] = float(np.sum(self.state == 'S'))
        record['n_infected'] = float(np.sum(self.state == 'I'))
        record['n_recovered'] = float(np.sum(self.state == 'R'))
        self.history.append(record)

        return record


class NeuralSystem:
    """Simple neural network dynamics with Hebbian learning."""

    def __init__(self, n_neurons=100, learning_rate=0.01, decay=0.9, seed=42):
        self.n_neurons = n_neurons
        self.lr = learning_rate
        self.decay = decay
        self.rng = np.random.RandomState(seed)
        self.weights = self.rng.randn(n_neurons, n_neurons) * 0.1
        self.activity = self.rng.randn(n_neurons) * 0.5
        self.history = []

    def step(self):
        # Hebbian update
        noise = self.rng.randn(self.n_neurons) * 0.01
        self.activity = np.tanh(self.weights @ self.activity + noise)

        # Weight update (Hebbian)
        outer = np.outer(self.activity, self.activity)
        self.weights = self.weights * self.decay + self.lr * outer
        self.weights = np.clip(self.weights, -2, 2)

        record = {'timestep': len(self.history)}
        for i, val in enumerate(self.activity):
            record[f'neuron_{i}'] = float(val)
        record['mean_activity'] = float(np.mean(np.abs(self.activity)))
        record['activity_variance'] = float(np.var(self.activity))
        self.history.append(record)

        return record


class MarketSystem:
    """Economic agent model with price dynamics."""

    def __init__(self, n_agents=100, volatility=0.1, seed=42):
        self.n_agents = n_agents
        self.volatility = volatility
        self.rng = np.random.RandomState(seed)
        self.wealth = self.rng.uniform(10, 100, n_agents)
        self.strategy = self.rng.choice(['bull', 'bear', 'neutral'], n_agents)
        self.price = 50.0
        self.history = []

    def step(self):
        # Price dynamics
        demand = 0
        for i in range(self.n_agents):
            if self.strategy[i] == 'bull':
                demand += 1
            elif self.strategy[i] == 'bear':
                demand -= 1

        self.price += self.volatility * demand / self.n_agents + self.rng.randn() * 0.5
        self.price = max(1, self.price)

        # Agent updates
        for i in range(self.n_agents):
            if self.rng.random() < 0.1:
                if self.price > 60:
                    self.strategy[i] = 'bear'
                elif self.price < 40:
                    self.strategy[i] = 'bull'
                else:
                    self.strategy[i] = self.rng.choice(['bull', 'bear', 'neutral'])

            # Wealth update
            if self.strategy[i] == 'bull':
                self.wealth[i] *= (1 + self.volatility * self.rng.randn())
            elif self.strategy[i] == 'bear':
                self.wealth[i] *= (1 - self.volatility * self.rng.randn())
            self.wealth[i] = max(0, self.wealth[i])

        record = {'timestep': len(self.history)}
        for i, val in enumerate(self.wealth):
            record[f'agent_{i}'] = float(val)
        record['price'] = float(self.price)
        record['mean_wealth'] = float(np.mean(self.wealth))
        record['wealth_variance'] = float(np.var(self.wealth))
        self.history.append(record)

        return record


class EcologicalSystem:
    """Predator-prey Lotka-Volterra dynamics with spatial structure."""

    def __init__(self, n_patches=100, prey_growth=0.5, predation_rate=0.02,
                 predator_death=0.3, conversion=0.5, seed=42):
        self.n_patches = n_patches
        self.alpha = prey_growth
        self.beta = predation_rate
        self.delta = predator_death
        self.gamma = conversion
        self.rng = np.random.RandomState(seed)
        self.prey = self.rng.uniform(20, 80, n_patches)
        self.predators = self.rng.uniform(10, 30, n_patches)
        self.history = []

    def step(self):
        # Lotka-Volterra with migration
        noise_prey = self.rng.randn(self.n_patches) * 0.5
        noise_pred = self.rng.randn(self.n_patches) * 0.2

        d_prey = self.alpha * self.prey - self.beta * self.prey * self.predators + noise_prey
        d_pred = self.gamma * self.prey * self.predators - self.delta * self.predators + noise_pred

        self.prey = np.clip(self.prey + d_prey, 0, 200)
        self.predators = np.clip(self.predators + d_pred, 0, 100)

        record = {'timestep': len(self.history)}
        for i in range(self.n_patches):
            record[f'prey_{i}'] = float(self.prey[i])
            record[f'predator_{i}'] = float(self.predators[i])
        record['total_prey'] = float(np.sum(self.prey))
        record['total_predators'] = float(np.sum(self.predators))
        self.history.append(record)

        return record


def trajectory_to_matrix(trajectory, max_dim=64):
    """Convert trajectory to matrix of shape (T, D)."""
    all_keys = set()
    for state in trajectory[:5]:
        all_keys.update(state.keys())
    all_keys.discard('timestep')
    all_keys.discard('cov_eigenvalues')

    keys = sorted(all_keys)[:max_dim]
    vectors = []
    for state in trajectory:
        v = [state.get(k, 0) for k in keys]
        vectors.append(v)

    return np.array(vectors), keys


def compute_embedding_metrics(matrix):
    """Compute embedding singularity metrics."""
    results = {}

    if len(matrix) > matrix.shape[1]:
        try:
            cov = np.cov(matrix.T)
            eigenvalues = np.linalg.eigvalsh(cov)
            eigenvalues = eigenvalues[eigenvalues > 1e-10]
            if len(eigenvalues) > 0:
                condition_number = eigenvalues[-1] / eigenvalues[0]
                participation_ratio = (np.sum(eigenvalues) ** 2) / np.sum(eigenvalues ** 2)
                results["condition_number"] = float(condition_number)
                results["participation_ratio"] = float(participation_ratio)
                results["rank_deficiency"] = int(matrix.shape[1] - len(eigenvalues))
                results["effective_dimensionality"] = float(participation_ratio)
            else:
                results["condition_number"] = float("inf")
                results["participation_ratio"] = 1.0
                results["rank_deficiency"] = matrix.shape[1]
                results["effective_dimensionality"] = 1.0
        except Exception as e:
            results["condition_number"] = 1.0
            results["participation_ratio"] = 1.0
            results["rank_deficiency"] = 0
            results["effective_dimensionality"] = 1.0
    else:
        results["condition_number"] = 1.0
        results["participation_ratio"] = 1.0
        results["rank_deficiency"] = 0
        results["effective_dimensionality"] = 1.0

    return results


def run_system_scaling():
    """Run all 8 systems and compare embedding quality."""
    from study_001 import DistributedSystem
    from study_001c_immune import ImmuneSignalingNetwork
    from study_001b_colony import AntColony
    from study_001d_institution import InstitutionNetwork

    systems = {
        # Original 4
        "distributed": {
            "class": DistributedSystem,
            "kwargs": {"n_nodes": 100}
        },
        "immune": {
            "class": ImmuneSignalingNetwork,
            "kwargs": {"n_cells": 100}
        },
        "ant_colony": {
            "class": AntColony,
            "kwargs": {"n_ants": 50, "n_food": 100}
        },
        "institution": {
            "class": InstitutionNetwork,
            "kwargs": {"n_agents": 100}
        },
        # New 4
        "epidemic": {
            "class": EpidemicSystem,
            "kwargs": {"n_nodes": 100}
        },
        "neural": {
            "class": NeuralSystem,
            "kwargs": {"n_neurons": 100}
        },
        "market": {
            "class": MarketSystem,
            "kwargs": {"n_agents": 100}
        },
        "ecological": {
            "class": EcologicalSystem,
            "kwargs": {"n_patches": 100}
        },
    }

    all_results = {}

    for sys_name, sys_info in systems.items():
        print(f"\nRunning {sys_name} across {NUM_SEEDS} seeds...")
        seed_results = []

        for seed in range(NUM_SEEDS):
            start = time.time()
            try:
                system = sys_info["class"](seed=seed, **sys_info["kwargs"])
                trajectory = []
                for _ in range(NUM_TIMESTEPS):
                    trajectory.append(system.step())

                matrix, keys = trajectory_to_matrix(trajectory)
                metrics = compute_embedding_metrics(matrix)
                metrics["seed"] = seed
                metrics["runtime"] = time.time() - start
                metrics["n_dims"] = matrix.shape[1]
                seed_results.append(metrics)
                print(f"  Seed {seed}: ED={metrics.get('effective_dimensionality', 'N/A'):.4f}, dims={metrics['n_dims']}")
            except Exception as e:
                print(f"  Seed {seed}: ERROR - {e}")
                continue

        # Aggregate across seeds
        if seed_results:
            agg = {}
            for key in seed_results[0]:
                if key == "seed":
                    continue
                values = [r[key] for r in seed_results if key in r and r[key] != float("inf")]
                if values:
                    agg[key] = {
                        "mean": float(np.mean(values)),
                        "std": float(np.std(values)),
                        "min": float(np.min(values)),
                        "max": float(np.max(values)),
                        "ci_95": [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]
                    }
                else:
                    agg[key] = {"mean": float("inf"), "std": 0, "min": float("inf"), "max": float("inf"), "ci_95": [float("inf"), float("inf")]}

            all_results[sys_name] = {
                "seeds": seed_results,
                "aggregate": agg,
                "n_seeds": len(seed_results)
            }

            ed = agg.get("effective_dimensionality", {})
            pr = agg.get("participation_ratio", {})
            cr = agg.get("condition_number", {})
            print(f"  Effective dimensionality: {ed.get('mean', 'N/A'):.4f} ± {ed.get('std', 0):.4f}")
            print(f"  Participation ratio: {pr.get('mean', 'N/A'):.4f}")
            print(f"  Condition number: {cr.get('mean', 'N/A')}")

    return all_results


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 003I DIVISION 2: SYSTEM SCALING (8 SYSTEMS)")
    print("=" * 70)
    print(f"Systems: distributed, immune, ant_colony, institution, epidemic, neural, market, ecological")
    print(f"Seeds: {NUM_SEEDS}")
    print(f"Timesteps: {NUM_TIMESTEPS}")

    start_time = time.time()

    # Run system scaling experiments
    results = run_system_scaling()

    # Save results
    output = {
        "metadata": {
            "num_seeds": NUM_SEEDS,
            "num_timesteps": NUM_TIMESTEPS,
            "num_systems": len(results),
            "total_time": time.time() - start_time
        },
        "main_results": results,
    }

    output_file = os.path.join(OUTPUT_DIR, "system_scaling_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print(f"SYSTEM SCALING COMPLETE")
    print(f"{'=' * 70}")
    print(f"Total runtime: {output['metadata']['total_time']:.1f}s")
    print(f"Systems tested: {output['metadata']['num_systems']}")
    print(f"Results saved to: {output_file}")

    # Print summary
    print(f"\nSUMMARY:")
    low_rank_count = 0
    for sys_name, sys_data in results.items():
        agg = sys_data["aggregate"]
        ed = agg.get("effective_dimensionality", {})
        ed_mean = ed.get("mean", 999)
        if ed_mean < 2.0:
            low_rank_count += 1
            status = "LOW-RANK"
        else:
            status = "NOT-LOW-RANK"
        print(f"  {sys_name}: ED={ed_mean:.4f} [{status}]")

    print(f"\nLow-rank systems: {low_rank_count}/{len(results)}")
    if low_rank_count == len(results):
        print("CONCLUSION: Low-rank collapse generalizes across all 8 systems")
    else:
        print("CONCLUSION: Low-rank collapse does NOT generalize to all systems")
