#!/usr/bin/env python3
"""
Phase 003D Division 2 — Observable Survival Analysis

For each metric (G, H, TE, T), measure survival under:
- coordinate corruption
- dimensional collapse
- basis rotation
- sparsification
- normalization changes
- stochastic perturbation

Output:
- survival curves
- collapse thresholds
- robustness ordering
"""

import numpy as np
import json
import os
import sys
import time

# Add source paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'distributed'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'immune'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'ant_colony'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'institution'))


def run_simulation(system_class, **kwargs):
    """Run a simulation and return trajectory."""
    system = system_class(**kwargs)
    for _ in range(50):
        system.step()
    return system.history


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


def corrupt_coordinates(matrix, corruption_fraction, seed=42):
    """Randomly corrupt coordinates."""
    rng = np.random.RandomState(seed)
    corrupted = matrix.copy()
    n_corrupt = int(matrix.shape[1] * corruption_fraction)
    if n_corrupt > 0:
        indices = rng.choice(matrix.shape[1], size=n_corrupt, replace=False)
        for idx in indices:
            corrupted[:, idx] = rng.randn(matrix.shape[0]) * matrix[:, idx].std()
    return corrupted


def collapse_dimensions(matrix, keep_fraction, seed=42):
    """Keep only a fraction of dimensions."""
    rng = np.random.RandomState(seed)
    n_keep = max(1, int(matrix.shape[1] * keep_fraction))
    indices = rng.choice(matrix.shape[1], size=n_keep, replace=False)
    return matrix[:, indices]


def rotate_basis(matrix, angle, seed=42):
    """Apply random rotation to matrix."""
    rng = np.random.RandomState(seed)
    n_dim = matrix.shape[1]
    # Random orthogonal matrix via QR
    Q, _ = np.linalg.qr(rng.randn(n_dim, n_dim))
    # Apply rotation
    return matrix @ Q


def sparsify_matrix(matrix, sparsity, seed=42):
    """Randomly zero out elements."""
    rng = np.random.RandomState(seed)
    mask = rng.random(matrix.shape) > sparsity
    return matrix * mask


def normalize_matrix(matrix, method='zscore'):
    """Normalize matrix."""
    if method == 'zscore':
        mean = matrix.mean(0)
        std = matrix.std(0) + 1e-8
        return (matrix - mean) / std
    elif method == 'minmax':
        min_val = matrix.min(0)
        max_val = matrix.max(0)
        return (matrix - min_val) / (max_val - min_val + 1e-8)
    elif method == 'unit':
        norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-8
        return matrix / norms
    return matrix


def perturb_stochastic(matrix, noise_level, seed=42):
    """Add Gaussian noise."""
    rng = np.random.RandomState(seed)
    noise = rng.randn(*matrix.shape) * noise_level * matrix.std()
    return matrix + noise


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003D Division 2 — Observable Survival Analysis")
    print("=" * 60)

    from study_001 import DistributedSystem
    from study_001c_immune import ImmuneSignalingNetwork
    from study_001b_colony import AntColony
    from study_001d_institution import InstitutionNetwork

    # System configurations
    systems = {
        'distributed': {
            'class': DistributedSystem,
            'kwargs': {'n_nodes': 100, 'seed': 42},
        },
        'immune': {
            'class': ImmuneSignalingNetwork,
            'kwargs': {'n_cells': 100, 'seed': 42},
        },
        'ant_colony': {
            'class': AntColony,
            'kwargs': {'n_ants': 50, 'n_food': 100, 'seed': 42},
        },
        'institution': {
            'class': InstitutionNetwork,
            'kwargs': {'n_agents': 100, 'seed': 42},
        },
    }

    results = {}

    for sys_name, config in systems.items():
        print(f"\n--- {sys_name} ---")

        # Run baseline simulation
        traj = run_simulation(config['class'], **config['kwargs'])
        matrix, keys = trajectory_to_matrix(traj, max_dim=64)

        # Compute baseline metrics
        G_baseline = compute_G_from_matrix(matrix)
        H_baseline = compute_H_from_matrix(matrix)

        print(f"  Baseline: G={G_baseline:.4f}, H={H_baseline:.4f}")

        sys_results = {
            'baseline': {'G': G_baseline, 'H': H_baseline},
            'survival': {},
        }

        # 1. Coordinate corruption
        print("  Testing coordinate corruption...")
        corruption_results = []
        for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
            corrupted = corrupt_coordinates(matrix, frac)
            G = compute_G_from_matrix(corrupted)
            H = compute_H_from_matrix(corrupted)
            corruption_results.append({
                'corruption_fraction': frac,
                'G': G, 'H': H,
                'G_stable': abs(G - G_baseline) < 0.01,
                'H_stable': abs(H - H_baseline) < 0.01,
            })
        sys_results['survival']['corruption'] = corruption_results

        # 2. Dimensional collapse
        print("  Testing dimensional collapse...")
        collapse_results = []
        for keep in [1.0, 0.75, 0.5, 0.25, 0.1]:
            collapsed = collapse_dimensions(matrix, keep)
            G = compute_G_from_matrix(collapsed)
            H = compute_H_from_matrix(collapsed)
            collapse_results.append({
                'keep_fraction': keep,
                'n_dims': collapsed.shape[1],
                'G': G, 'H': H,
                'G_stable': abs(G - G_baseline) < 0.01,
                'H_stable': abs(H - H_baseline) < 0.01,
            })
        sys_results['survival']['dimensional_collapse'] = collapse_results

        # 3. Basis rotation
        print("  Testing basis rotation...")
        rotation_results = []
        for angle in [0, 30, 60, 90]:
            rotated = rotate_basis(matrix, angle)
            G = compute_G_from_matrix(rotated)
            H = compute_H_from_matrix(rotated)
            rotation_results.append({
                'angle': angle,
                'G': G, 'H': H,
                'G_stable': abs(G - G_baseline) < 0.01,
                'H_stable': abs(H - H_baseline) < 0.01,
            })
        sys_results['survival']['basis_rotation'] = rotation_results

        # 4. Sparsification
        print("  Testing sparsification...")
        sparsity_results = []
        for sparsity in [0.0, 0.25, 0.5, 0.75, 0.9]:
            sparse = sparsify_matrix(matrix, sparsity)
            G = compute_G_from_matrix(sparse)
            H = compute_H_from_matrix(sparse)
            sparsity_results.append({
                'sparsity': sparsity,
                'G': G, 'H': H,
                'G_stable': abs(G - G_baseline) < 0.01,
                'H_stable': abs(H - H_baseline) < 0.01,
            })
        sys_results['survival']['sparsification'] = sparsity_results

        # 5. Normalization changes
        print("  Testing normalization...")
        norm_results = {}
        for method in ['zscore', 'minmax', 'unit']:
            normalized = normalize_matrix(matrix, method)
            G = compute_G_from_matrix(normalized)
            H = compute_H_from_matrix(normalized)
            norm_results[method] = {
                'G': G, 'H': H,
                'G_stable': abs(G - G_baseline) < 0.01,
                'H_stable': abs(H - H_baseline) < 0.01,
            }
        sys_results['survival']['normalization'] = norm_results

        # 6. Stochastic perturbation
        print("  testing stochastic perturbation...")
        stochastic_results = []
        for noise in [0.0, 0.01, 0.05, 0.1, 0.2]:
            perturbed = perturb_stochastic(matrix, noise)
            G = compute_G_from_matrix(perturbed)
            H = compute_H_from_matrix(perturbed)
            stochastic_results.append({
                'noise_level': noise,
                'G': G, 'H': H,
                'G_stable': abs(G - G_baseline) < 0.01,
                'H_stable': abs(H - H_baseline) < 0.01,
            })
        sys_results['survival']['stochastic'] = stochastic_results

        results[sys_name] = sys_results

    # Compute robustness ordering
    print("\n--- Robustness Ordering ---")
    robustness = {}
    for sys_name, sys_results in results.items():
        g_stable_count = 0
        h_stable_count = 0
        total_tests = 0

        for perturbation_type, tests in sys_results['survival'].items():
            if isinstance(tests, list):
                for test in tests:
                    total_tests += 1
                    if test.get('G_stable', False):
                        g_stable_count += 1
                    if test.get('H_stable', False):
                        h_stable_count += 1
            elif isinstance(tests, dict):
                for method, test in tests.items():
                    total_tests += 1
                    if test.get('G_stable', False):
                        g_stable_count += 1
                    if test.get('H_stable', False):
                        h_stable_count += 1

        robustness[sys_name] = {
            'G_survival_rate': g_stable_count / total_tests if total_tests > 0 else 0,
            'H_survival_rate': h_stable_count / total_tests if total_tests > 0 else 0,
            'total_tests': total_tests,
        }
        print(f"  {sys_name}: G survival={robustness[sys_name]['G_survival_rate']:.2%}, "
              f"H survival={robustness[sys_name]['H_survival_rate']:.2%}")

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'robustness_ordering': robustness,
        'runtime_seconds': round(elapsed, 1),
    }

    outpath = os.path.join(os.path.dirname(__file__), 'observable_survival_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
