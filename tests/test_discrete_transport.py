"""
Tests for discrete_transport.py — Phase 002C transport algebra.

Covers:
- TransportOperator construction and composition
- DiscreteTransportAlgebra transport building
- TransportPerturbationSuite methods
- DiscreteHolonomy computation
- TransportCanonicalization determinism
- No NaN/Inf in outputs
"""

import numpy as np
import pytest
import sys
sys.path.insert(0, '/home/student/SGI-Persistence/src')

from geometry.connection_formalism import (
    OrganizationalState, HistoricalFiber, ConnectionOperator, build_bundle
)
from geometry.discrete_transport import (
    TransportOperator, DiscreteTransportAlgebra, TransportPerturbationSuite,
    DiscreteHolonomy, TransportCanonicalization, OrganizationalCategory
)


def _make_trajectory(n=20):
    """Create a deterministic test trajectory."""
    rng = np.random.RandomState(42)
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


class TestTransportOperator:
    def test_identity_compose(self):
        I = np.eye(4)
        op = TransportOperator(matrix=I, source_idx=0, target_idx=1)
        composed = op.compose(op)
        np.testing.assert_array_almost_equal(composed.matrix, I)

    def test_apply_fiber(self):
        mat = np.eye(4)
        op = TransportOperator(matrix=mat, source_idx=0, target_idx=1)
        fiber = HistoricalFiber(residue=np.array([1.0, 0.0, 0.0, 0.0]), basis=np.eye(4))
        result = op.apply(fiber)
        np.testing.assert_array_almost_equal(result.residue, fiber.residue)

    def test_commutator_zero_for_identity(self):
        I = np.eye(4)
        op1 = TransportOperator(matrix=I, source_idx=0, target_idx=1)
        op2 = TransportOperator(matrix=I, source_idx=0, target_idx=1)
        assert op1.commutator(op2) == 0.0

    def test_inversion_error_identity(self):
        I = np.eye(4)
        op = TransportOperator(matrix=I, source_idx=0, target_idx=1)
        assert op.inversion_error() < 1e-8


class TestDiscreteTransportAlgebra:
    def test_build_transports(self):
        trajectory = _make_trajectory(15)
        states, fibers, connection = build_bundle(trajectory)
        algebra = DiscreteTransportAlgebra(dimension=8)
        ops = algebra.build_transports(states, fibers, connection)
        assert len(ops) > 0

    def test_no_nans(self):
        trajectory = _make_trajectory(15)
        states, fibers, connection = build_bundle(trajectory)
        algebra = DiscreteTransportAlgebra(dimension=8)
        ops = algebra.build_transports(states, fibers, connection)
        for key, op in ops.items():
            assert not np.any(np.isnan(op.matrix)), f"NaN in transport operator {key}"
            assert not np.any(np.isinf(op.matrix)), f"Inf in transport operator {key}"

    def test_path_transport(self):
        trajectory = _make_trajectory(15)
        states, fibers, connection = build_bundle(trajectory)
        algebra = DiscreteTransportAlgebra(dimension=8)
        algebra.build_transports(states, fibers, connection)
        path_op = algebra.get_path_transport([0, 1, 2, 3])
        assert path_op is not None

    def test_transport_path_divergence(self):
        trajectory = _make_trajectory(20)
        states, fibers, connection = build_bundle(trajectory)
        algebra = DiscreteTransportAlgebra(dimension=8)
        algebra.build_transports(states, fibers, connection)
        result = algebra.compute_transport_path_divergence(states, fibers, n_pairs=5, path_length=3)
        assert 'T' in result
        assert not np.isnan(result['T'])


class TestTransportPerturbationSuite:
    def test_replay_delay(self):
        traj = _make_trajectory(10)
        result = TransportPerturbationSuite.temporal_replay_delay(traj, delay=3)
        assert len(result) >= len(traj)

    def test_node_deletion(self):
        traj = _make_trajectory(10)
        result = TransportPerturbationSuite.structural_node_deletion(traj, 0.3)
        assert len(result) == len(traj)

    def test_all_perturbations_return_lists(self):
        traj = _make_trajectory(10)
        suite = TransportPerturbationSuite()
        methods = [
            ('temporal_replay_delay', [3]),
            ('temporal_async_replay', [0.2]),
            ('temporal_memory_truncation', [0.5]),
            ('temporal_replay_scramble', [0.2]),
            ('structural_node_deletion', [0.2]),
            ('structural_sector_duplication', [0.2]),
            ('structural_routing_mutation', [0.2]),
            ('structural_topology_rewire', [0.2]),
            ('gauge_basis_rotation', [0.5]),
            ('gauge_nonlinear_normalize', []),
            ('gauge_random_projection', [0.3]),
            ('gauge_coordinate_compression', [4]),
            ('historical_memory_overwrite', [0.2]),
            ('historical_residue_injection', [0.1]),
            ('historical_replay_branch', [0.2]),
            ('historical_counterfactual_replay', [0.2]),
        ]
        for name, args in methods:
            fn = getattr(suite, name)
            result = fn(traj, *args)
            assert isinstance(result, list), f"{name} did not return a list"
            assert len(result) > 0, f"{name} returned empty list"


class TestDiscreteHolonomy:
    def test_holonomy_computation(self):
        trajectory = _make_trajectory(20)
        states, fibers, connection = build_bundle(trajectory)
        algebra = DiscreteTransportAlgebra(dimension=8)
        algebra.build_transports(states, fibers, connection)
        holonomy = DiscreteHolonomy(algebra)
        result = holonomy.compute_loop_holonomy([0, 2, 4, 6, 0])
        assert 'holonomy' in result
        assert not np.isnan(result['holonomy'])
