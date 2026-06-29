"""
Adaptive Desynchronization System - Resistant to Low-Rank Collapse

Design principles:
- Active synchronization suppression
- Feedback that prevents coordination
- Adaptive coupling based on synchronization level
- Self-organizing desynchronization

Target: ED > 3.0
"""

import numpy as np
from typing import List, Dict


class AdaptiveDesyncSystem:
    """System with active synchronization suppression."""

    def __init__(self, n_nodes=100, base_coupling=0.1, desync_strength=0.5, seed=42):
        self.n_nodes = n_nodes
        self.base_coupling = base_coupling
        self.desync_strength = desync_strength
        self.rng = np.random.RandomState(seed)
        self.history = []

        # Build sparse graph
        self.adjacency = self._build_sparse_graph()

        # Node states
        self.states = self.rng.randn(n_nodes) * 0.5
        self.synchronization_level = 0.0

        # Adaptive coupling strengths
        self.coupling_strengths = np.ones(n_nodes) * base_coupling

    def _build_sparse_graph(self):
        adj = np.zeros((self.n_nodes, self.n_nodes))
        for i in range(self.n_nodes):
            n_neighbors = self.rng.randint(1, 4)
            neighbors = self.rng.choice(self.n_nodes, n_neighbors, replace=False)
            adj[i, neighbors] = 1
            adj[neighbors, i] = 1
        return adj

    def _compute_synchronization(self):
        """Compute current synchronization level."""
        if self.n_nodes < 2:
            return 0.0
        try:
            # Reshape for correlation computation
            states_2d = self.states.reshape(1, -1)
            if np.std(self.states) < 1e-10:
                return 0.0
            corr_matrix = np.corrcoef(states_2d)
            np.fill_diagonal(corr_matrix, 0)
            return float(np.mean(np.abs(corr_matrix)))
        except:
            return 0.0

    def step(self):
        # Compute current synchronization
        self.synchronization_level = self._compute_synchronization()

        # Adaptive coupling: reduce coupling when synchronization is high
        sync_factor = np.exp(-self.desync_strength * self.synchronization_level)
        self.coupling_strengths = np.ones(self.n_nodes) * self.base_coupling * sync_factor

        new_states = self.states.copy()

        for i in range(self.n_nodes):
            neighbors = np.where(self.adjacency[i] > 0)[0]
            if len(neighbors) > 0:
                # Compute influence with adaptive coupling
                neighbor_diff = self.states[neighbors] - self.states[i]
                influence = np.mean(neighbor_diff) * self.coupling_strengths[i]

                # Add desynchronization noise
                desync_noise = self.rng.randn() * self.desync_strength * 0.1

                # Update state
                noise = self.rng.randn() * 0.01
                new_states[i] = self.states[i] + influence + desync_noise + noise

        self.states = new_states

        record = {'timestep': len(self.history)}
        record['n_active'] = float(self.n_nodes)
        record['connectivity'] = float(np.mean(self.adjacency > 0))
        record['state_variance'] = float(np.var(self.states))
        record['synchronization_level'] = float(self.synchronization_level)
        record['mean_coupling'] = float(np.mean(self.coupling_strengths))
        record['coupling_variance'] = float(np.var(self.coupling_strengths))
        record['desync_effectiveness'] = float(self._compute_desync_effectiveness())
        self.history.append(record)
        return record

    def _compute_desync_effectiveness(self):
        """How effective is the desynchronization at preventing sync."""
        if self.synchronization_level < 0.1:
            return 1.0
        return float(1.0 - self.synchronization_level)

    def get_state(self):
        return {
            'states': self.states.copy(),
            'synchronization_level': self.synchronization_level,
            'coupling_strengths': self.coupling_strengths.copy(),
        }


# SECTORS definition
ADAPTIVE_DESYNC_SECTORS = {
    'amplitude': {
        'metrics': ['n_active', 'connectivity', 'state_variance'],
        'expected_survival': False,
    },
    'topology': {
        'metrics': ['synchronization_level', 'mean_coupling', 'coupling_variance', 'desync_effectiveness'],
        'expected_survival': True,
    },
}
