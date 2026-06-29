#!/usr/bin/env python3
"""
Phase 003E Division 2 — Information-Carrying Capacity

Measure:
- Mutual information
- Entropy retention
- Signal-to-noise ratios
- Embedding compression loss
- Predictive information survival

Question: how much actual information survives the embedding pipeline?
"""

import numpy as np
import json
import os
import sys
import time
from scipy.special import digamma
from sklearn.neighbors import KernelDensity

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


def compute_entropy(x, k=3):
    """Compute differential entropy using k-NN estimator."""
    x = np.atleast_2d(x)
    n, d = x.shape
    if n < 2:
        return 0.0

    # Compute distances to k-th nearest neighbor
    from scipy.spatial.distance import cdist
    dists = cdist(x, x)
    np.fill_diagonal(dists, np.inf)
    kth_dists = np.sort(dists, axis=1)[:, min(k, n-1)]

    # Estimate entropy
    entropy = np.mean(np.log(kth_dists + 1e-10)) + digamma(n) - digamma(k)
    return float(entropy)


def compute_mutual_information(x, y, k=3):
    """Estimate mutual information using k-NN estimator (Kraskov et al.)."""
    x = np.atleast_2d(x)
    y = np.atleast_2d(y)
    n, dx = x.shape
    _, dy = y.shape

    if n < 2:
        return 0.0

    # Concatenate
    xy = np.hstack([x, y])

    # Compute distances
    from scipy.spatial.distance import cdist
    dists_x = cdist(x, x)
    dists_y = cdist(y, y)
    dists_xy = cdist(xy, xy)

    np.fill_diagonal(dists_x, np.inf)
    np.fill_diagonal(dists_y, np.inf)
    np.fill_diagonal(dists_xy, np.inf)

    # Find k-th nearest neighbor in joint space
    kth_dists = np.sort(dists_xy, axis=1)[:, min(k, n-1)]

    # Count neighbors within epsilon in marginal spaces
    eps = kth_dists
    nx = np.sum(dists_x < eps[:, None], axis=1) - 1
    ny = np.sum(dists_y < eps[:, None], axis=1) - 1

    # Estimate MI
    mi = digamma(k) - np.mean(digamma(nx + 1) + digamma(ny + 1)) + digamma(n)
    return float(max(0, mi))


def compute_signal_to_noise(matrix):
    """Compute signal-to-noise ratio."""
    signal = np.var(matrix, axis=0).mean()
    noise = np.mean([np.std(np.diff(matrix[:, i])) for i in range(matrix.shape[1])])
    return float(signal / (noise + 1e-10))


def compute_compression_loss(original, compressed):
    """Compute compression loss (variance retained)."""
    var_original = np.var(original, axis=0).sum()
    var_compressed = np.var(compressed, axis=0).sum()
    return float(1.0 - var_compressed / (var_original + 1e-10))


def compute_predictive_information(matrix, lag=1):
    """Compute predictive information I(X_t; X_{t+lag})."""
    if len(matrix) <= lag:
        return 0.0
    x_t = matrix[:-lag]
    x_t_lag = matrix[lag:]
    return compute_mutual_information(x_t, x_t_lag)


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003E Division 2 — Information-Carrying Capacity")
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

        print(f"  Matrix shape: {matrix.shape}")

        # Compute entropy
        entropy = compute_entropy(matrix)
        print(f"  Entropy: {entropy:.4f}")

        # Compute SNR
        snr = compute_signal_to_noise(matrix)
        print(f"  SNR: {snr:.4f}")

        # Compute predictive information
        pi = compute_predictive_information(matrix)
        print(f"  Predictive information: {pi:.4f}")

        # Compute compression loss (1D vs full)
        # Use first principal component as 1D compression
        U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
        compressed_1d = U[:, :1] * s[0]
        compression_loss = compute_compression_loss(matrix, compressed_1d)
        print(f"  Compression loss (1D): {compression_loss:.4f}")

        # Compute pairwise MI between dimensions
        n_dims = min(matrix.shape[1], 8)  # Limit to 8 dims for speed
        mi_matrix = np.zeros((n_dims, n_dims))
        for i in range(n_dims):
            for j in range(i+1, n_dims):
                mi = compute_mutual_information(
                    matrix[:, i:i+1], matrix[:, j:j+1]
                )
                mi_matrix[i, j] = mi
                mi_matrix[j, i] = mi

        avg_mi = mi_matrix.sum() / (n_dims * (n_dims - 1))
        print(f"  Average pairwise MI: {avg_mi:.4f}")

        results[sys_name] = {
            'matrix_shape': list(matrix.shape),
            'n_keys': len(keys),
            'keys': keys,
            'entropy': entropy,
            'snr': snr,
            'predictive_information': pi,
            'compression_loss_1d': compression_loss,
            'average_pairwise_mi': avg_mi,
            'mi_matrix': mi_matrix.tolist(),
        }

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
        'summary': {
            sys_name: {
                'entropy': r['entropy'],
                'snr': r['snr'],
                'predictive_information': r['predictive_information'],
                'compression_loss_1d': r['compression_loss_1d'],
                'average_pairwise_mi': r['average_pairwise_mi'],
            }
            for sys_name, r in results.items()
        },
    }

    outpath = os.path.join(os.path.dirname(__file__), 'information_capacity_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
