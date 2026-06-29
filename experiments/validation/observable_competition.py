#!/usr/bin/env python3
"""
Phase 003F Division 4 — Observable Competition Tests

Compare canonical observables against:
- random observables
- PCA components
- autoencoder latents
- simple variance metrics
- entropy-only metrics

Question: Do the canonical observables outperform trivial alternatives?
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


def compute_random_observable(matrix, seed=42):
    """Compute random observable (baseline)."""
    rng = np.random.RandomState(seed)
    return float(np.mean(rng.randn(*matrix.shape)))


def compute_pca_observable(matrix):
    """Compute PCA-based observable (first principal component variance)."""
    if matrix.shape[0] < 2 or matrix.shape[1] < 2:
        return 0.0

    U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
    # Variance explained by first component
    var_explained = s[0] ** 2 / np.sum(s ** 2)
    return float(var_explained)


def compute_variance_observable(matrix):
    """Compute variance-based observable (total variance)."""
    return float(np.var(matrix))


def compute_entropy_observable(matrix):
    """Compute entropy-based observable (coordinate entropy)."""
    if matrix.shape[0] < 2 or matrix.shape[1] < 2:
        return 0.0

    variances = np.var(matrix, axis=0)
    total_var = np.sum(variances)

    if total_var < 1e-10:
        return 0.0

    probs = variances / total_var
    probs = probs[probs > 0]

    entropy = -np.sum(probs * np.log(probs + 1e-10))
    return float(entropy)


def compute_mean_observable(matrix):
    """Compute mean-based observable (global mean)."""
    return float(np.mean(matrix))


def compute_std_observable(matrix):
    """Compute std-based observable (global std)."""
    return float(np.std(matrix))


def compute_max_observable(matrix):
    """Compute max-based observable (global max)."""
    return float(np.max(matrix))


def compute_min_observable(matrix):
    """Compute min-based observable (global min)."""
    return float(np.min(matrix))


def corrupt_matrix(matrix, corruption_level, seed=42):
    """Apply corruption to matrix."""
    rng = np.random.RandomState(seed)
    noise = rng.randn(*matrix.shape) * corruption_level * matrix.std()
    return matrix + noise


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003F Division 4 — Observable Competition Tests")
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

        # Compute canonical metrics
        G_canonical = compute_G_from_matrix(matrix)

        # Compute alternative observables
        alternatives = {
            'random': compute_random_observable(matrix),
            'pca': compute_pca_observable(matrix),
            'variance': compute_variance_observable(matrix),
            'entropy': compute_entropy_observable(matrix),
            'mean': compute_mean_observable(matrix),
            'std': compute_std_observable(matrix),
            'max': compute_max_observable(matrix),
            'min': compute_min_observable(matrix),
        }

        print(f"  Canonical G: {G_canonical:.4f}")
        for name, value in alternatives.items():
            print(f"  {name}: {value:.4f}")

        # Test under corruption
        corruption_levels = [0.0, 0.25, 0.5, 0.75, 1.0]
        corruption_results = {}

        for level in corruption_levels:
            corrupted = corrupt_matrix(matrix, level)
            G_corrupted = compute_G_from_matrix(corrupted)
            alt_corrupted = {
                'random': compute_random_observable(corrupted),
                'pca': compute_pca_observable(corrupted),
                'variance': compute_variance_observable(corrupted),
                'entropy': compute_entropy_observable(corrupted),
                'mean': compute_mean_observable(corrupted),
                'std': compute_std_observable(corrupted),
                'max': compute_max_observable(corrupted),
                'min': compute_min_observable(corrupted),
            }
            corruption_results[level] = {
                'canonical_G': G_corrupted,
                **alt_corrupted,
            }

        # Determine if canonical outperforms alternatives
        # Use variance under corruption as metric of robustness
        canonical_variance = np.var([corruption_results[l]['canonical_G'] for l in corruption_levels])
        alt_variances = {}
        for name in alternatives.keys():
            alt_var = np.var([corruption_results[l][name] for l in corruption_levels])
            alt_variances[name] = alt_var

        print(f"\n  Variance under corruption:")
        print(f"    Canonical G: {canonical_variance:.6f}")
        for name, var in alt_variances.items():
            print(f"    {name}: {var:.6f}")

        # Determine winners
        all_variances = {'canonical_G': canonical_variance, **alt_variances}
        sorted_variances = sorted(all_variances.items(), key=lambda x: x[1])
        winner = sorted_variances[0][0]

        print(f"\n  Winner (lowest variance): {winner}")

        results[sys_name] = {
            'canonical_G': G_canonical,
            'alternatives': alternatives,
            'corruption_results': {str(k): v for k, v in corruption_results.items()},
            'canonical_variance': canonical_variance,
            'alternative_variances': alt_variances,
            'winner': winner,
        }

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
    }

    outpath = os.path.join(os.path.dirname(__file__), 'observable_competition_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
