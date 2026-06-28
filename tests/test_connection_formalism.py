"""
Tests for connection_formalism.py — Phase 002B core geometry.

Covers:
- OrganizationalState construction and distance
- HistoricalFiber construction and entanglement
- ConnectionOperator parallel transport
- CurvatureTensor computation
- build_bundle determinism
- state_to_vector normalization
"""

import numpy as np
import pytest
import sys
sys.path.insert(0, '/home/student/SGI-Persistence/src')

from geometry.connection_formalism import (
    OrganizationalState, HistoricalFiber, ConnectionOperator,
    CurvatureTensor, HolonomySpectrum, FiberTwist,
    build_bundle, state_to_vector
)


class TestOrganizationalState:
    def test_construction(self):
        vec = np.array([1.0, 2.0, 3.0])
        state = OrganizationalState(vector=vec, timestamp=5)
        np.testing.assert_array_equal(state.vector, vec)
        assert state.timestamp == 5

    def test_distance_to_self(self):
        vec = np.array([1.0, 2.0])
        state = OrganizationalState(vector=vec)
        assert state.distance_to(state) == 0.0

    def test_distance_symmetry(self):
        s1 = OrganizationalState(vector=np.array([0.0, 0.0]))
        s2 = OrganizationalState(vector=np.array([3.0, 4.0]))
        assert s1.distance_to(s2) == pytest.approx(s2.distance_to(s1))

    def test_interpolate_endpoint(self):
        s1 = OrganizationalState(vector=np.array([0.0]))
        s2 = OrganizationalState(vector=np.array([10.0]))
        mid = s1.interpolate(s2, 0.5)
        np.testing.assert_array_almost_equal(mid.vector, [5.0])


class TestHistoricalFiber:
    def test_entanglement_zero(self):
        fiber = HistoricalFiber(residue=np.zeros(4), basis=np.eye(4))
        assert fiber.entanglement() == 0.0

    def test_entanglement_positive(self):
        fiber = HistoricalFiber(residue=np.array([1.0, 0.0, 0.0, 0.0]), basis=np.eye(4))
        assert fiber.entanglement() == pytest.approx(1.0)

    def test_twist_angle(self):
        fiber = HistoricalFiber(residue=np.array([1.0, 0.0]), basis=np.eye(2))
        angle = fiber.twist_angle()
        assert 0.0 <= angle <= np.pi


class TestConnectionOperator:
    def test_parallel_transport_identity(self):
        conn = ConnectionOperator(dimension=4)
        fiber = HistoricalFiber(residue=np.array([1.0, 0.0, 0.0, 0.0]), basis=np.eye(4))
        p1 = np.zeros(4)
        p2 = np.zeros(4)
        transported = conn.parallel_transport(fiber, p1, p2)
        np.testing.assert_array_almost_equal(transported.residue, fiber.residue)

    def test_transport_error_zero_for_identical(self):
        conn = ConnectionOperator(dimension=4)
        fiber = HistoricalFiber(residue=np.array([1.0, 0.0, 0.0, 0.0]), basis=np.eye(4))
        assert conn.compute_transport_error(fiber, fiber) == 0.0


class TestStateToVector:
    def test_empty_state(self):
        vec = state_to_vector({})
        assert len(vec) == 8
        np.testing.assert_array_equal(vec, np.zeros(8))

    def test_normalization(self):
        state = {'connectivity': 100.0, 'n_active': 50.0}
        vec = state_to_vector(state)
        assert np.max(np.abs(vec)) <= 1.0

    def test_deterministic(self):
        state = {'connectivity': 1.0, 'routing_entropy': 2.0}
        v1 = state_to_vector(state)
        v2 = state_to_vector(state)
        np.testing.assert_array_equal(v1, v2)


class TestBuildBundle:
    def test_deterministic(self):
        trajectory = [{'connectivity': float(i), 'n_active': float(i * 2)} for i in range(20)]
        s1, f1, c1 = build_bundle(trajectory, memory_depth=5)
        s2, f2, c2 = build_bundle(trajectory, memory_depth=5)
        for a, b in zip(s1, s2):
            np.testing.assert_array_equal(a.vector, b.vector)
        for a, b in zip(f1, f2):
            np.testing.assert_array_equal(a.residue, b.residue)

    def test_no_nans(self):
        trajectory = [{'connectivity': float(i), 'n_active': float(i)} for i in range(15)]
        states, fibers, _ = build_bundle(trajectory)
        for s in states:
            assert not np.any(np.isnan(s.vector))
        for f in fibers:
            assert not np.any(np.isnan(f.residue))
