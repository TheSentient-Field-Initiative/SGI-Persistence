"""
Delayed Coupling System - Resistant to Low-Rank Collapse

Design principles:
- Configurable communication delays
- Temporal decoupling prevents synchronization
- High memory depth
- Delayed feedback loops

Target: ED > 3.0
"""

import numpy as np
from typing import List, Dict
from collections import deque


class DelayedCouplingSystem:
    """System with configurable communication delays."""

    def __init__(self, n_nodes=100, delay=5, coupling_strength=0.1, seed=42):
        self.n_nodes = n_nodes
        self.delay = delay
        self.coupling_strength = coupling_strength
        self.rng = np.random.RandomState(seed)
        self.history = []

        # Build sparse random graph
        self.adjacency = self._build_sparse_graph()

        # State buffer for delays
        self.state_buffer = deque(maxlen=delay + 1)
        self.states = self.rng.randn(n_nodes) * 0.5
        self.state_buffer.append(self.states.copy())

        # Heterogeneous update schedules
        self.update_frequencies = self.rng.choice([1, 2, 3], size=n_nodes)
        self.update_counters = np.zeros(n_nodes, dtype=int)

    def _build_sparse_graph(self):
        adj = np.zeros((self.n_nodes, self.n_nodes))
        for i in range(self.n_nodes):
            n_neighbors = self.rng.randint(1, 4)
            neighbors = self.rng.choice(self.n_nodes, n_neighbors, replace=False)
            adj[i, neighbors] = 1
            adj[neighbors, i] = 1
        return adj

    def step(self):
        # Get delayed state
        if len(self.state_buffer) > self.delay:
            delayed_state = self.state_buffer[0]
        else:
            delayed_state = self.state_buffer[-1]

        new_states = self.states.copy()
        self.update_counters += 1

        for i in range(self.n_nodes):
            if self.update_counters[i] >= self.update_frequencies[i]:
                self.update_counters[i] = 0
                # Use delayed coupling
                neighbors = np.where(self.adjacency[i] > 0)[0]
                if len(neighbors) > 0:
                    delayed_influence = np.mean(delayed_state[neighbors])
                    noise = self.rng.randn() * 0.01
                    new_states[i] = 0.9 * self.states[i] + self.coupling_strength * delayed_influence + noise

        self.states = new_states
        self.state_buffer.append(self.states.copy())

        record = {'timestep': len(self.history)}
        record['n_active'] = float(self.n_nodes)
        record['connectivity'] = float(np.mean(self.adjacency > 0))
        record['mean_delay'] = float(self.delay)
        record['state_variance'] = float(np.var(self.states))
        record['state_autocorrelation'] = float(self._compute_autocorrelation())
        record['update_heterogeneity'] = float(np.std(self.update_frequencies) / np.mean(self.update_frequencies))
        self.history.append(record)
        return record

    def _compute_autocorrelation(self):
        if len(self.state_buffer) < 2:
            return 0.0
        states = np.array(list(self.state_buffer))
        if states.shape[0] < 2:
            return 0.0
        autocorr = np.mean(np.corrcoef(states[:-1].T, states[1:].T)[:self.n_nodes, self.n_nodes:])
        return float(autocorr) if not np.isnan(autocorr) else 0.0

    def get_state(self):
        return {
            'states': self.states.copy(),
            'delayed_state': self.state_buffer[0].copy() if self.state_buffer else self.states.copy(),
        }


# SECTORS definition
DELAYED_COUPLING_SECTORS = {
    'amplitude': {
        'metrics': ['n_active', 'connectivity', 'state_variance'],
        'expected_survival': False,
    },
    'topology': {
        'metrics': ['mean_delay', 'state_autocorrelation', 'update_heterogeneity'],
        'expected_survival': True,
    },
}
