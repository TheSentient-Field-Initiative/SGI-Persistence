"""
Tests for reproducibility — seed determinism and JSON schema.

Covers:
- Bundle construction is deterministic with same seed
- Transport algebra is deterministic with same seed
- JSON result files are valid
- All metrics are finite
"""

import numpy as np
import pytest
import json
import os
import sys
sys.path.insert(0, '/home/student/SGI-Persistence/src')

from geometry.connection_formalism import build_bundle
from geometry.discrete_transport import DiscreteTransportAlgebra


DATA_DIR = '/home/student/SGI-Persistence/data/canonical'
EXPERIMENT_DIR = '/home/student/SGI-Persistence/experiments/phase_002'


def _make_trajectory(seed=42, n=25):
    rng = np.random.RandomState(seed)
    trajectory = []
    for i in range(n):
        trajectory.append({
            'connectivity': float(rng.random()),
            'n_active': float(rng.random() * 10),
            'routing_entropy': float(rng.random()),
            'assignment_rate': float(rng.random()),
            'allocation_entropy': float(rng.random()),
            'mean_activation': float(rng.random()),
            'type_entropy': float(rng.random()),
            'efficiency': float(rng.random()),
        })
    return trajectory


class TestSeedReproducibility:
    def test_bundle_deterministic(self):
        t1 = _make_trajectory(seed=42)
        t2 = _make_trajectory(seed=42)
        s1, f1, _ = build_bundle(t1)
        s2, f2, _ = build_bundle(t2)
        for a, b in zip(s1, s2):
            np.testing.assert_array_equal(a.vector, b.vector)
        for a, b in zip(f1, f2):
            np.testing.assert_array_equal(a.residue, b.residue)

    def test_algebra_deterministic(self):
        t1 = _make_trajectory(seed=42)
        t2 = _make_trajectory(seed=42)
        s1, f1, c1 = build_bundle(t1)
        s2, f2, c2 = build_bundle(t2)
        a1 = DiscreteTransportAlgebra(dimension=8)
        a2 = DiscreteTransportAlgebra(dimension=8)
        ops1 = a1.build_transports(s1, f1, c1)
        ops2 = a2.build_transports(s2, f2, c2)
        for key in ops1:
            np.testing.assert_array_almost_equal(ops1[key].matrix, ops2[key].matrix)


class TestJSONSchema:
    def _load_json_files(self):
        results = []
        for fn in os.listdir(DATA_DIR):
            if fn.endswith('.json'):
                with open(os.path.join(DATA_DIR, fn)) as f:
                    results.append((fn, json.load(f)))
        return results

    def test_all_json_valid(self):
        results = self._load_json_files()
        assert len(results) > 0, "No JSON files found"
        for fn, data in results:
            assert isinstance(data, (dict, list)), f"{fn} is not a dict or list"

    def test_experiment_json_valid(self):
        for subdir in ['phase_001', 'phase_002']:
            path = os.path.join(EXPERIMENT_DIR, subdir, 'metadata.json')
            if os.path.exists(path):
                with open(path) as f:
                    data = json.load(f)
                assert 'experiment_suite' in data
                assert 'seed' in data


class TestFiniteMetrics:
    def test_transport_algebra_finite(self):
        trajectory = _make_trajectory(seed=42, n=20)
        states, fibers, connection = build_bundle(trajectory)
        algebra = DiscreteTransportAlgebra(dimension=8)
        algebra.build_transports(states, fibers, connection)
        for key, op in algebra.transport_operators.items():
            assert np.all(np.isfinite(op.matrix)), f"Non-finite in operator {key}"

    def test_transport_divergence_finite(self):
        trajectory = _make_trajectory(seed=42, n=20)
        states, fibers, connection = build_bundle(trajectory)
        algebra = DiscreteTransportAlgebra(dimension=8)
        algebra.build_transports(states, fibers, connection)
        result = algebra.compute_transport_path_divergence(states, fibers, n_pairs=5, path_length=3)
        assert np.isfinite(result['T'])
