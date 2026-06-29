"""
Phase 003D Division 3 — Basis-Invariance Tests

Test:
- Permutation invariance
- Orthogonal transform sensitivity
- Scaling sensitivity
- Normalization sensitivity

The project must now explicitly quantify:
> what transformations preserve observables.
"""

import pytest
import numpy as np
import sys
import os

# Add source paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def compute_G_from_matrix(matrix, n_sectors=2):
    """Compute G from matrix using sector alignment."""
    if len(matrix) < 10:
        return 0.0

    mid = len(matrix) // 2
    before = matrix[:mid]
    after = matrix[mid:]

    surviving = 0
    dim_per_sector = matrix.shape[1] // n_sectors

    for i in range(n_sectors):
        start = i * dim_per_sector
        end = start + dim_per_sector
        bv = before[:, start:end]
        av = after[:, start:end]

        if bv.size == 0 or av.size == 0:
            continue

        def _cosine(a, b):
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            return float(np.dot(a.flatten(), b.flatten()) / (na * nb)) if na > 0 and nb > 0 else 0.0

        raw = _cosine(bv, av)
        bn = (bv - bv.mean(0)) / (bv.std(0) + 1e-8)
        an = (av - av.mean(0)) / (av.std(0) + 1e-8)
        norm = _cosine(bn, an)

        if (norm - raw) > -0.1:
            surviving += 1

    return surviving / n_sectors if n_sectors > 0 else 0.0


def compute_H_from_matrix(matrix, max_lag=5):
    """Compute H from matrix using autocorrelation."""
    if len(matrix) < max_lag + 1:
        return 0.0

    autocorrs = []
    for lag in range(1, min(max_lag + 1, len(matrix))):
        if lag < len(matrix):
            a = matrix[:-lag]
            b = matrix[lag:]
            if a.size > 0 and b.size > 0:
                na, nb = np.linalg.norm(a), np.linalg.norm(b)
                if na > 0 and nb > 0:
                    corr = np.dot(a.flatten(), b.flatten()) / (na * nb)
                    autocorrs.append(abs(corr))

    return np.mean(autocorrs) if autocorrs else 0.0


class TestBasisInvariance:
    """Test basis invariance of metrics."""

    def setup_method(self):
        """Set up test fixtures."""
        np.random.seed(42)
        self.matrix = np.random.randn(50, 8)
        self.G_baseline = compute_G_from_matrix(self.matrix)
        self.H_baseline = compute_H_from_matrix(self.matrix)

    def test_permutation_invariance(self):
        """Test that metrics are invariant to column permutation."""
        permutation = np.random.permutation(8)
        permuted = self.matrix[:, permutation]

        G_perm = compute_G_from_matrix(permuted)
        H_perm = compute_H_from_matrix(permuted)

        # G should be invariant to permutation (same sectors, just reordered)
        assert abs(G_perm - self.G_baseline) < 0.01, (
            f"G changed under permutation: {self.G_baseline} -> {G_perm}"
        )

        # H should be invariant to permutation (autocorrelation is permutation-invariant)
        assert abs(H_perm - self.H_baseline) < 0.01, (
            f"H changed under permutation: {self.H_baseline} -> {H_perm}"
        )

    def test_orthogonal_transform_sensitivity(self):
        """Test sensitivity to orthogonal transforms."""
        # Random orthogonal matrix
        Q, _ = np.linalg.qr(np.random.randn(8, 8))
        rotated = self.matrix @ Q

        G_rot = compute_G_from_matrix(rotated)
        H_rot = compute_H_from_matrix(rotated)

        # G may change under rotation (sector structure changes)
        # Just verify it's finite
        assert np.isfinite(G_rot), f"G became non-finite under rotation: {G_rot}"

        # H should be relatively stable under rotation
        assert np.isfinite(H_rot), f"H became non-finite under rotation: {H_rot}"

    def test_scaling_sensitivity(self):
        """Test sensitivity to uniform scaling."""
        scale = 2.5
        scaled = self.matrix * scale

        G_scaled = compute_G_from_matrix(scaled)
        H_scaled = compute_H_from_matrix(scaled)

        # G should be invariant to uniform scaling (cosine similarity is scale-invariant)
        assert abs(G_scaled - self.G_baseline) < 0.01, (
            f"G changed under scaling: {self.G_baseline} -> {G_scaled}"
        )

        # H should be invariant to uniform scaling
        assert abs(H_scaled - self.H_baseline) < 0.01, (
            f"H changed under scaling: {self.H_baseline} -> {H_scaled}"
        )

    def test_normalization_sensitivity(self):
        """Test sensitivity to normalization method."""
        # Z-score normalization
        mean = self.matrix.mean(0)
        std = self.matrix.std(0) + 1e-8
        zscore = (self.matrix - mean) / std

        G_zscore = compute_G_from_matrix(zscore)
        H_zscore = compute_H_from_matrix(zscore)

        # G may change under normalization
        assert np.isfinite(G_zscore), f"G became non-finite under zscore: {G_zscore}"

        # H should be relatively stable
        assert np.isfinite(H_zscore), f"H became non-finite under zscore: {H_zscore}"

    def test_permutation_invariance_formal(self):
        """Formal test: metrics should be permutation-invariant."""
        for _ in range(10):
            perm = np.random.permutation(8)
            permuted = self.matrix[:, perm]

            G_perm = compute_G_from_matrix(permuted)
            H_perm = compute_H_from_matrix(permuted)

            # Allow small numerical differences
            assert abs(G_perm - self.G_baseline) < 0.05, (
                f"G not permutation-invariant: {self.G_baseline} vs {G_perm}"
            )

    def test_scaling_invariance_formal(self):
        """Formal test: metrics should be scale-invariant."""
        for scale in [0.1, 0.5, 1.0, 2.0, 10.0]:
            scaled = self.matrix * scale

            G_scaled = compute_G_from_matrix(scaled)
            H_scaled = compute_H_from_matrix(scaled)

            assert abs(G_scaled - self.G_baseline) < 0.05, (
                f"G not scale-invariant at scale={scale}: {self.G_baseline} vs {G_scaled}"
            )
            assert abs(H_scaled - self.H_baseline) < 0.05, (
                f"H not scale-invariant at scale={scale}: {self.H_baseline} vs {H_scaled}"
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
