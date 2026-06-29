"""
Modular Sparse System - Resistant to Low-Rank Collapse

Design principles:
- Community structure with sparse intra-community edges
- Low coupling density (< 0.1)
- High sparsity
- Modular dynamics that prevent synchronization

Target: ED > 3.0
"""

import numpy as np
from typing import List, Dict


class ModularSparseSystem:
    """Network with community structure and sparse connectivity."""

    def __init__(self, n_nodes=100, n_communities=5, intra_community_prob=0.3,
                 inter_community_prob=0.02, seed=42):
        self.n_nodes = n_nodes
        self.n_communities = n_communities
        self.rng = np.random.RandomState(seed)
        self.history = []

        # Build community structure
        self.community_sizes = [n_nodes // n_communities] * n_communities
        self.community_sizes[-1] += n_nodes % n_communities

        # Build adjacency with community structure
        self.adjacency = self._build_modular_graph(intra_community_prob, inter_community_prob)

        # Initialize node states (heterogeneous)
        self.states = self.rng.randn(n_nodes) * 0.5
        self.community_activity = self.rng.randn(n_communities) * 0.1

    def _build_modular_graph(self, intra_prob, inter_prob):
        adj = np.zeros((self.n_nodes, self.n_nodes))
        node_community = []
        for c, size in enumerate(self.community_sizes):
            node_community.extend([c] * size)

        for i in range(self.n_nodes):
            for j in range(i + 1, self.n_nodes):
                if node_community[i] == node_community[j]:
                    if self.rng.random() < intra_prob:
                        adj[i, j] = 1
                        adj[j, i] = 1
                else:
                    if self.rng.random() < inter_prob:
                        adj[i, j] = 1
                        adj[j, i] = 1
        return adj

    def step(self):
        # Heterogeneous dynamics per community
        new_states = self.states.copy()
        for c in range(self.n_communities):
            start = sum(self.community_sizes[:c])
            end = start + self.community_sizes[c]
            community_states = self.states[start:end]
            community_adj = self.adjacency[start:end, start:end]

            # Community-specific dynamics
            influence = community_adj @ community_states / (np.sum(community_adj, axis=1) + 1)
            noise = self.rng.randn(len(community_states)) * 0.01
            new_states[start:end] = 0.9 * community_states + 0.1 * influence + noise

            # Update community activity
            self.community_activity[c] = 0.95 * self.community_activity[c] + 0.05 * np.mean(community_states)

        self.states = new_states

        record = {'timestep': len(self.history)}
        record['n_active'] = float(self.n_nodes)
        record['connectivity'] = float(np.mean(self.adjacency > 0))
        record['community_activity_mean'] = float(np.mean(self.community_activity))
        record['community_activity_std'] = float(np.std(self.community_activity))
        record['state_variance'] = float(np.var(self.states))
        record['modularity'] = float(self._compute_modularity())
        self.history.append(record)
        return record

    def _compute_modularity(self):
        """Simple modularity estimate."""
        total_edges = np.sum(self.adjacency > 0) / 2
        if total_edges == 0:
            return 0.0
        in_community_edges = 0
        node_community = []
        for c, size in enumerate(self.community_sizes):
            node_community.extend([c] * size)
        for i in range(self.n_nodes):
            for j in range(i + 1, self.n_nodes):
                if self.adjacency[i, j] > 0 and node_community[i] == node_community[j]:
                    in_community_edges += 1
        return in_community_edges / total_edges

    def get_state(self):
        return {
            'states': self.states.copy(),
            'community_activity': self.community_activity.copy(),
        }


# SECTORS definition
MODULAR_SPARSE_SECTORS = {
    'amplitude': {
        'metrics': ['n_active', 'connectivity', 'state_variance'],
        'expected_survival': False,
    },
    'topology': {
        'metrics': ['community_activity_mean', 'community_activity_std', 'modularity'],
        'expected_survival': True,
    },
}
