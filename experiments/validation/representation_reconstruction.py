#!/usr/bin/env python3
"""
Phase 003E Division 5 — Representation Reconstruction Tests

Question: can we reconstruct original dynamics from compressed embeddings?

If embeddings are 1D, can we still predict system behavior?
This tests whether the embedding loss is meaningful.
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


def reconstruct_from_1d(compressed_1d, original_matrix):
    """Reconstruct full matrix from 1D compression using PCA inverse."""
    # PCA inverse: x_reconstructed = compressed_1d * Vt[0]
    U, s, Vt = np.linalg.svd(original_matrix, full_matrices=False)
    # compressed_1d should be U[:, 0] * s[0]
    # Reconstruction: U[:, :1] * Vt[:1, :] * s[0]
    reconstructed = U[:, :1] @ np.diag(s[:1]) @ Vt[:1, :]
    return reconstructed


def compute_reconstruction_error(original, reconstructed):
    """Compute reconstruction error (MSE)."""
    return float(np.mean((original - reconstructed) ** 2))


def compute_prediction_from_1d(matrix, lag=1):
    """Predict next state from 1D representation."""
    if len(matrix) <= lag:
        return 0.0

    # Get 1D representation
    U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
    compressed = (U[:, :1] * s[0]).flatten()

    # Simple linear prediction
    x_t = compressed[:-lag]
    x_t_lag = compressed[lag:]

    if len(x_t) < 2:
        return 0.0

    # Fit linear model
    A = np.vstack([x_t, np.ones(len(x_t))]).T
    try:
        coeffs = np.linalg.lstsq(A, x_t_lag, rcond=None)[0]
        # Compute prediction error
        predicted = A @ coeffs
        error = np.mean((predicted - x_t_lag) ** 2)
        return float(error)
    except:
        return 0.0


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003E Division 5 — Representation Reconstruction Tests")
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

        # Get 1D representation
        U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
        compressed_1d = U[:, :1] * s[0]

        # Reconstruction error
        reconstructed = reconstruct_from_1d(compressed_1d, matrix)
        recon_error = compute_reconstruction_error(matrix, reconstructed)
        print(f"  Reconstruction error (MSE): {recon_error:.6f}")

        # Prediction error from 1D
        pred_error = compute_prediction_from_1d(matrix)
        print(f"  Prediction error from 1D: {pred_error:.6f}")

        # Variance explained by 1D
        var_explained = s[0] ** 2 / np.sum(s ** 2)
        print(f"  Variance explained by 1D: {var_explained:.4f}")

        # Correlation between 1D and original
        correlations = []
        for col in range(matrix.shape[1]):
            corr = np.corrcoef(compressed_1d.flatten(), matrix[:, col])[0, 1]
            if not np.isnan(corr):
                correlations.append(abs(corr))

        avg_corr = np.mean(correlations) if correlations else 0.0
        print(f"  Average correlation with original: {avg_corr:.4f}")

        # Information loss
        var_original = np.var(matrix, axis=0).sum()
        var_reconstructed = np.var(reconstructed, axis=0).sum()
        info_loss = 1.0 - var_reconstructed / (var_original + 1e-10)
        print(f"  Information loss: {info_loss:.4f}")

        results[sys_name] = {
            'matrix_shape': list(matrix.shape),
            'reconstruction_error_mse': recon_error,
            'prediction_error_1d': pred_error,
            'variance_explained_1d': float(var_explained),
            'average_correlation_1d': float(avg_corr),
            'information_loss': float(info_loss),
            'svd_values': s[:5].tolist(),
        }

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
        'summary': {
            sys_name: {
                'reconstruction_error': r['reconstruction_error_mse'],
                'variance_explained': r['variance_explained_1d'],
                'information_loss': r['information_loss'],
            }
            for sys_name, r in results.items()
        },
    }

    outpath = os.path.join(os.path.dirname(__file__), 'representation_reconstruction_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
