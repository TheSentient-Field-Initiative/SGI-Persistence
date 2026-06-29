#!/usr/bin/env python3
"""
Phase 003G Division 3 — Representation Minimalism

Question: What is the smallest representation that preserves any legitimate observable?

Try:
- 1D
- 2D
- sparse coordinates
- orthogonal bases
- compressed embeddings

The goal is no longer richness. The goal is survival.
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


def corrupt_matrix(matrix, corruption_level, seed=42):
    """Apply corruption to matrix."""
    rng = np.random.RandomState(seed)
    noise = rng.randn(*matrix.shape) * corruption_level * matrix.std()
    return matrix + noise


def reduce_to_1d(matrix):
    """Reduce to 1D using PCA."""
    U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
    return (U[:, :1] * s[0])


def reduce_to_2d(matrix):
    """Reduce to 2D using PCA."""
    U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
    return (U[:, :2] * s[:2])


def reduce_to_sparse(matrix, sparsity=0.5):
    """Reduce to sparse representation."""
    rng = np.random.RandomState(42)
    mask = rng.random(matrix.shape) > sparsity
    return matrix * mask


def reduce_to_orthogonal(matrix):
    """Reduce to orthogonal basis."""
    Q, R = np.linalg.qr(matrix)
    return Q


def reduce_to_compressed(matrix, compression_ratio=0.5):
    """Reduce to compressed representation."""
    n_cols = max(1, int(matrix.shape[1] * compression_ratio))
    U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
    return (U[:, :n_cols] * s[:n_cols])


# ============================================================
# SURVIVOR OBSERVABLES (from Division 1)
# ============================================================

def obs_variance_mean(matrix):
    """Variance of column means."""
    return float(np.mean(np.var(matrix, axis=0)))


def obs_variance_total(matrix):
    """Total variance."""
    return float(np.var(matrix))


def obs_entropy_rate(matrix):
    """Entropy rate (autocorrelation decay)."""
    if len(matrix) < 3:
        return 0.0
    autocorrs = []
    for lag in range(1, min(4, len(matrix))):
        a = matrix[:-lag]
        b = matrix[lag:]
        if a.size > 0 and b.size > 0:
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            if na > 0 and nb > 0:
                corr = np.dot(a.flatten(), b.flatten()) / (na * nb)
                autocorrs.append(abs(corr))
    if len(autocorrs) < 2:
        return 0.0
    return float(-np.mean(np.diff(autocorrs)))


def obs_persistence(matrix):
    """Persistence: fraction of coordinates that remain stable."""
    if len(matrix) < 2:
        return 0.0
    mid = len(matrix) // 2
    before = matrix[:mid]
    after = matrix[mid:]
    stable = 0
    for col in range(matrix.shape[1]):
        b_col = before[:, col]
        a_col = after[:, col]
        if np.std(b_col) > 0 and np.std(a_col) > 0:
            corr = np.corrcoef(b_col, a_col)[0, 1]
            if not np.isnan(corr) and abs(corr) > 0.5:
                stable += 1
    return stable / matrix.shape[1] if matrix.shape[1] > 0 else 0.0


def obs_lagged_stability(matrix, lag=2):
    """Lagged stability: autocorrelation at given lag."""
    if len(matrix) <= lag:
        return 0.0
    a = matrix[:-lag]
    b = matrix[lag:]
    if a.size == 0 or b.size == 0:
        return 0.0
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na > 0 and nb > 0:
        return float(abs(np.dot(a.flatten(), b.flatten()) / (na * nb)))
    return 0.0


def obs_transition_density(matrix):
    """Transition density: fraction of non-zero transitions."""
    if len(matrix) < 2:
        return 0.0
    diff = np.diff(matrix, axis=0)
    non_zero = np.sum(np.abs(diff) > 1e-6)
    total = diff.size
    return non_zero / total if total > 0 else 0.0


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003G Division 3 — Representation Minimalism")
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

    # Representation methods
    representations = {
        'full': lambda m: m,
        '1d': reduce_to_1d,
        '2d': reduce_to_2d,
        'sparse_50': lambda m: reduce_to_sparse(m, 0.5),
        'sparse_75': lambda m: reduce_to_sparse(m, 0.75),
        'orthogonal': reduce_to_orthogonal,
        'compressed_50': lambda m: reduce_to_compressed(m, 0.5),
        'compressed_25': lambda m: reduce_to_compressed(m, 0.25),
    }

    # Survivor observables
    observables = {
        'variance_mean': obs_variance_mean,
        'variance_total': obs_variance_total,
        'entropy_rate': obs_entropy_rate,
        'persistence': obs_persistence,
        'lagged_stability': obs_lagged_stability,
        'transition_density': obs_transition_density,
    }

    results = {}

    for sys_name, config in systems.items():
        print(f"\n--- {sys_name} ---")

        # Run baseline simulation
        traj = run_simulation(config['class'], **config['kwargs'])
        matrix, keys = trajectory_to_matrix(traj, max_dim=64)

        sys_results = {}

        for rep_name, rep_func in representations.items():
            rep_matrix = rep_func(matrix)

            rep_results = {}
            for obs_name, obs_func in observables.items():
                # Compute canonical value
                canonical = obs_func(rep_matrix)

                # Compute under corruption
                corruption_levels = [0.0, 0.25, 0.5, 0.75, 1.0]
                corrupted_values = []
                for level in corruption_levels:
                    corrupted = corrupt_matrix(rep_matrix, level)
                    val = obs_func(corrupted)
                    corrupted_values.append(val)

                # Compute variance under corruption
                variance = np.var(corrupted_values)

                # Compute null controls
                null_values = []
                for i in range(5):
                    null_matrix = np.random.randn(*rep_matrix.shape) * rep_matrix.std() + rep_matrix.mean()
                    null_val = obs_func(null_matrix)
                    null_values.append(null_val)

                null_mean = np.mean(null_values)
                null_std = np.std(null_values)

                # Determine if canonical outperforms null
                if null_std > 0:
                    z_score = (canonical - null_mean) / null_std
                    outperforms_null = abs(z_score) > 2.0
                else:
                    z_score = 0.0
                    outperforms_null = abs(canonical - null_mean) > 0.1

                rep_results[obs_name] = {
                    'canonical': canonical,
                    'variance_under_corruption': float(variance),
                    'z_score': float(z_score),
                    'outperforms_null': bool(outperforms_null),
                }

            sys_results[rep_name] = rep_results

            # Print summary
            surviving = sum(1 for r in rep_results.values() if r['outperforms_null'])
            print(f"  {rep_name}: {surviving}/{len(observables)} observables survive")

        results[sys_name] = sys_results

    # Find minimal representation that preserves survivors
    print("\n" + "=" * 60)
    print("MINIMAL REPRESENTATION ANALYSIS")
    print("=" * 60)

    for obs_name in observables:
        print(f"\n{obs_name}:")
        for rep_name in representations:
            surviving_systems = 0
            for sys_name in systems:
                if results[sys_name][rep_name][obs_name]['outperforms_null']:
                    surviving_systems += 1
            status = "PASS" if surviving_systems >= 3 else "FAIL"
            print(f"  {rep_name}: {surviving_systems}/4 systems [{status}]")

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
    }

    outpath = os.path.join(os.path.dirname(__file__), 'minimal_representation_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
