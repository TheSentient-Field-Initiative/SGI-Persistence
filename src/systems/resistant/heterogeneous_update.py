"""
Heterogeneous Update System - Resistant to Low-Rank Collapse

Design principles:
- Agents with different update frequencies
- Asynchronous updates prevent coordination
- High heterogeneity in dynamics
- Random update schedules

Target: ED > 3.0
"""

import numpy as np
from typing import List, Dict


class HeterogeneousUpdateSystem:
    """System with agents having different update frequencies."""

    def __init__(self, n_agents=100, min_freq=1, max_freq=10, seed=42):
        self.n_agents = n_agents
        self.rng = np.random.RandomState(seed)
        self.history = []

        # Build sparse interaction graph
        self.adjacency = self._build_sparse_graph()

        # Heterogeneous update frequencies
        self.update_frequencies = self.rng.randint(min_freq, max_freq + 1, size=n_agents)
        self.update_counters = np.zeros(n_agents, dtype=int)

        # Agent states (heterogeneous)
        self.states = self.rng.randn(n_agents) * 0.5
        self.agent_types = self.rng.choice(['fast', 'medium', 'slow'], size=n_agents)

        # Type-specific dynamics
        self.type_multipliers = {'fast': 1.0, 'medium': 0.5, 'slow': 0.2}

    def _build_sparse_graph(self):
        adj = np.zeros((self.n_agents, self.n_agents))
        for i in range(self.n_agents):
            n_neighbors = self.rng.randint(1, 4)
            neighbors = self.rng.choice(self.n_agents, n_neighbors, replace=False)
            adj[i, neighbors] = 1
            adj[neighbors, i] = 1
        return adj

    def step(self):
        new_states = self.states.copy()
        self.update_counters += 1

        for i in range(self.n_agents):
            if self.update_counters[i] >= self.update_frequencies[i]:
                self.update_counters[i] = 0

                # Get neighbors' states
                neighbors = np.where(self.adjacency[i] > 0)[0]
                if len(neighbors) > 0:
                    neighbor_mean = np.mean(self.states[neighbors])
                    type_mult = self.type_multipliers[self.agent_types[i]]
                    noise = self.rng.randn() * 0.01
                    new_states[i] = (1 - 0.1 * type_mult) * self.states[i] + \
                                   0.1 * type_mult * neighbor_mean + noise

        self.states = new_states

        record = {'timestep': len(self.history)}
        record['n_active'] = float(self.n_agents)
        record['connectivity'] = float(np.mean(self.adjacency > 0))
        record['state_variance'] = float(np.var(self.states))
        record['frequency_variance'] = float(np.var(self.update_frequencies))
        record['frequency_mean'] = float(np.mean(self.update_frequencies))
        record['type_entropy'] = float(self._compute_type_entropy())
        record['asynchrony'] = float(self._compute_asynchrony())
        self.history.append(record)
        return record

    def _compute_type_entropy(self):
        type_counts = {}
        for t in self.agent_types:
            type_counts[t] = type_counts.get(t, 0) + 1
        probs = np.array(list(type_counts.values())) / self.n_agents
        return float(-np.sum(probs * np.log(probs + 1e-10)))

    def _compute_asynchrony(self):
        return float(np.std(self.update_counters) / (np.mean(self.update_frequencies) + 1e-10))

    def get_state(self):
        return {
            'states': self.states.copy(),
            'agent_types': self.agent_types.copy(),
            'update_frequencies': self.update_frequencies.copy(),
        }


# SECTORS definition
HETEROGENEOUS_UPDATE_SECTORS = {
    'amplitude': {
        'metrics': ['n_active', 'connectivity', 'state_variance'],
        'expected_survival': False,
    },
    'topology': {
        'metrics': ['frequency_variance', 'frequency_mean', 'type_entropy', 'asynchrony'],
        'expected_survival': True,
    },
}
