#!/usr/bin/env python3
"""
Phase 004B Division 5: Resistant Systems V2

Test hybrid architectures combining multiple resistance mechanisms.
"""

import numpy as np
import json
import os
import sys
import time
from pathlib import Path

# Add resistant systems to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'resistant'))

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_SEEDS = 10
NUM_TIMESTEPS = 200


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
# HYBRID RESISTANT SYSTEMS
# ============================================================

class ModularHeterogeneousSystem:
    """Combines community structure + heterogeneous update frequencies."""

    def __init__(self, n_nodes=100, n_communities=5, seed=42):
        self.n_nodes = n_nodes
        self.n_communities = n_communities
        self.rng = np.random.RandomState(seed)
        self.history = []

        # Community structure
        self.community_sizes = [n_nodes // n_communities] * n_communities
        self.community_sizes[-1] += n_nodes % n_communities
        self.node_community = []
        for c, size in enumerate(self.community_sizes):
            self.node_community.extend([c] * size)

        # Sparse modular graph
        self.adjacency = self._build_modular_graph()

        # Heterogeneous update frequencies
        self.update_frequencies = self.rng.randint(1, 10, size=n_nodes)
        self.update_counters = np.zeros(n_nodes, dtype=int)

        # Agent states
        self.states = self.rng.randn(n_nodes) * 0.5

    def _build_modular_graph(self):
        adj = np.zeros((self.n_nodes, self.n_nodes))
        for i in range(self.n_nodes):
            for j in range(i + 1, self.n_nodes):
                if self.node_community[i] == self.node_community[j]:
                    if self.rng.random() < 0.3:
                        adj[i, j] = 1
                        adj[j, i] = 1
                else:
                    if self.rng.random() < 0.02:
                        adj[i, j] = 1
                        adj[j, i] = 1
        return adj

    def step(self):
        new_states = self.states.copy()
        self.update_counters += 1

        for i in range(self.n_nodes):
            if self.update_counters[i] >= self.update_frequencies[i]:
                self.update_counters[i] = 0
                neighbors = np.where(self.adjacency[i] > 0)[0]
                if len(neighbors) > 0:
                    neighbor_mean = np.mean(self.states[neighbors])
                    new_states[i] = self.states[i] * 0.7 + neighbor_mean * 0.3
                new_states[i] += self.rng.normal(0, 0.01)

        self.states = new_states
        record = {'timestep': len(self.history)}
        record['state_variance'] = float(np.var(self.states))
        record['mean_state'] = float(np.mean(self.states))
        self.history.append(record)
        return record

    def compute_function(self):
        return float(1.0 / (1.0 + np.var(self.states)))


class DelayedHeterogeneousSystem:
    """Combines time delays + heterogeneous update frequencies."""

    def __init__(self, n_nodes=100, max_delay=5, seed=42):
        self.n_nodes = n_nodes
        self.max_delay = max_delay
        self.rng = np.random.RandomState(seed)
        self.history = []

        # Sparse graph
        self.adjacency = self._build_sparse_graph()

        # Heterogeneous update frequencies
        self.update_frequencies = self.rng.randint(1, 10, size=n_nodes)
        self.update_counters = np.zeros(n_nodes, dtype=int)

        # Time delays
        self.delays = self.rng.randint(0, max_delay + 1, size=n_nodes)

        # State history for delays
        self.state_history = []

        # Agent states
        self.states = self.rng.randn(n_nodes) * 0.5

    def _build_sparse_graph(self):
        adj = np.zeros((self.n_nodes, self.n_nodes))
        for i in range(self.n_nodes):
            n_neighbors = self.rng.randint(1, 4)
            neighbors = self.rng.choice(self.n_nodes, n_neighbors, replace=False)
            adj[i, neighbors] = 1
            adj[neighbors, i] = 1
        return adj

    def step(self):
        self.state_history.append(self.states.copy())
        if len(self.state_history) > self.max_delay + 1:
            self.state_history.pop(0)

        new_states = self.states.copy()
        self.update_counters += 1

        for i in range(self.n_nodes):
            if self.update_counters[i] >= self.update_frequencies[i]:
                self.update_counters[i] = 0
                neighbors = np.where(self.adjacency[i] > 0)[0]
                if len(neighbors) > 0:
                    delay = min(self.delays[i], len(self.state_history) - 1)
                    if delay > 0:
                        neighbor_mean = np.mean(self.state_history[-delay - 1][neighbors])
                    else:
                        neighbor_mean = np.mean(self.states[neighbors])
                    new_states[i] = self.states[i] * 0.7 + neighbor_mean * 0.3
                new_states[i] += self.rng.normal(0, 0.01)

        self.states = new_states
        record = {'timestep': len(self.history)}
        record['state_variance'] = float(np.var(self.states))
        record['mean_state'] = float(np.mean(self.states))
        self.history.append(record)
        return record

    def compute_function(self):
        return float(1.0 / (1.0 + np.var(self.states)))


class AdaptiveModularSystem:
    """Combines adaptive desynchronization + community structure."""

    def __init__(self, n_nodes=100, n_communities=5, seed=42):
        self.n_nodes = n_nodes
        self.n_communities = n_communities
        self.rng = np.random.RandomState(seed)
        self.history = []

        # Community structure
        self.community_sizes = [n_nodes // n_communities] * n_communities
        self.community_sizes[-1] += n_nodes % n_communities
        self.node_community = []
        for c, size in enumerate(self.community_sizes):
            self.node_community.extend([c] * size)

        # Sparse modular graph
        self.adjacency = self._build_modular_graph()

        # Adaptive desynchronization
        self.sync_threshold = 0.8
        self.desync_strength = 0.1

        # Agent states
        self.states = self.rng.randn(n_nodes) * 0.5

    def _build_modular_graph(self):
        adj = np.zeros((self.n_nodes, self.n_nodes))
        for i in range(self.n_nodes):
            for j in range(i + 1, self.n_nodes):
                if self.node_community[i] == self.node_community[j]:
                    if self.rng.random() < 0.3:
                        adj[i, j] = 1
                        adj[j, i] = 1
                else:
                    if self.rng.random() < 0.02:
                        adj[i, j] = 1
                        adj[j, i] = 1
        return adj

    def step(self):
        new_states = self.states.copy()

        for i in range(self.n_nodes):
            neighbors = np.where(self.adjacency[i] > 0)[0]
            if len(neighbors) > 0:
                neighbor_mean = np.mean(self.states[neighbors])
                # Check for synchronization
                sync_level = 1.0 - np.std(self.states[neighbors])
                if sync_level > self.sync_threshold:
                    # Desynchronize
                    desync_noise = self.rng.normal(0, self.desync_strength)
                    new_states[i] = self.states[i] * 0.7 + neighbor_mean * 0.1 + desync_noise
                else:
                    new_states[i] = self.states[i] * 0.7 + neighbor_mean * 0.3
            new_states[i] += self.rng.normal(0, 0.01)

        self.states = new_states
        record = {'timestep': len(self.history)}
        record['state_variance'] = float(np.var(self.states))
        record['mean_state'] = float(np.mean(self.states))
        self.history.append(record)
        return record

    def compute_function(self):
        return float(1.0 / (1.0 + np.var(self.states)))


# ============================================================
# BASELINE SYSTEMS
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
        self.history.append(record)
        return record

    def compute_function(self):
        return float(1.0 / (1.0 + np.var(self.consensus_state)))


# ============================================================
# BENCHMARK
# ============================================================

def run_resistant_systems_v2():
    print("=" * 70)
    print("PHASE 004B DIVISION 5: RESISTANT SYSTEMS V2")
    print("=" * 70)
    print()

    systems = {
        'distributed': lambda seed: DistributedSystem(n_nodes=100, seed=seed),
        'modular_heterogeneous': lambda seed: ModularHeterogeneousSystem(n_nodes=100, seed=seed),
        'delayed_heterogeneous': lambda seed: DelayedHeterogeneousSystem(n_nodes=100, seed=seed),
        'adaptive_modular': lambda seed: AdaptiveModularSystem(n_nodes=100, seed=seed),
    }

    all_results = {}

    for name, create_fn in systems.items():
        print(f"Processing {name}...")
        eds = []
        functions = []
        for seed in range(NUM_SEEDS):
            system = create_fn(seed)
            for _ in range(NUM_TIMESTEPS):
                system.step()
            matrix, _ = trajectory_to_matrix(system.history)
            ed = compute_effective_dimensionality(matrix)
            func = system.compute_function()
            eds.append(ed)
            functions.append(func)

        all_results[name] = {
            'ED_mean': float(np.mean(eds)),
            'ED_std': float(np.std(eds)),
            'function_mean': float(np.mean(functions)),
            'function_std': float(np.std(functions)),
        }

    print()
    print("=" * 70)
    print("RESISTANT SYSTEMS V2 RESULTS")
    print("=" * 70)
    print()

    print(f"  {'System':<30} {'ED':<20} {'Function':<20}")
    print(f"  {'-'*30} {'-'*20} {'-'*20}")
    for name, data in all_results.items():
        ed_str = f"{data['ED_mean']:.3f} ± {data['ED_std']:.3f}"
        func_str = f"{data['function_mean']:.3f} ± {data['function_std']:.3f}"
        print(f"  {name:<30} {ed_str:<20} {func_str:<20}")

    output_path = Path(OUTPUT_DIR) / 'resistant_systems_v2_results.json'
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")
    return all_results


if __name__ == '__main__':
    run_resistant_systems_v2()
