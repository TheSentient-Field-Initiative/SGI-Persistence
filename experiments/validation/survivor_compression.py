#!/usr/bin/env python3
"""
Phase 003H Division 3 — Survivor Compression Study

Test: How aggressively can survivor observables be compressed before failure?

Include:
- PCA compression
- Random projection
- Quantization
- Binarization

Goal: Determine minimum information budget required for observability.
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


def pca_compress(matrix, n_components):
    """Compress using PCA."""
    if n_components >= matrix.shape[1]:
        return matrix
    U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
    return (U[:, :n_components] * s[:n_components])


def random_project(matrix, n_components, seed=42):
    """Compress using random projection."""
    rng = np.random.RandomState(seed)
    projection = rng.randn(matrix.shape[1], n_components)
    return matrix @ projection


def quantize(matrix, n_levels):
    """Quantize to n_levels."""
    min_val = np.min(matrix)
    max_val = np.max(matrix)
    if max_val - min_val < 1e-10:
        return matrix
    normalized = (matrix - min_val) / (max_val - min_val)
    quantized = np.round(normalized * (n_levels - 1)) / (n_levels - 1)
    return quantized * (max_val - min_val) + min_val


def binarize(matrix, threshold=0.0):
    """Binarize using threshold."""
    return (matrix > threshold).astype(float)


# ============================================================
# SURVIVOR OBSERVABLES
# ============================================================

def obs_variance_mean(matrix):
    """Variance of column means."""
    return float(np.mean(np.var(matrix, axis=0)))


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


def obs_persistence(matrix):
    """Persistence: fraction of coordinates that remain stable."""
    if len(matrix) < 2:
        return 0.0
    mid = len(matrix) // 2
    before = matrix[:mid]
    after = matrix[mid:]
    min_len = min(len(before), len(after))
    before = before[:min_len]
    after = after[:min_len]
    stable = 0
    for col in range(matrix.shape[1]):
        b_col = before[:, col]
        a_col = after[:, col]
        if np.std(b_col) > 0 and np.std(a_col) > 0:
            corr = np.corrcoef(b_col, a_col)[0, 1]
            if not np.isnan(corr) and abs(corr) > 0.5:
                stable += 1
    return stable / matrix.shape[1] if matrix.shape[1] > 0 else 0.0


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
    print("Phase 003H Division 3 — Survivor Compression Study")
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

    # Survivor observables
    observables = {
        'variance_mean': obs_variance_mean,
        'lagged_stability': obs_lagged_stability,
        'persistence': obs_persistence,
        'transition_density': obs_transition_density,
    }

    results = {}

    for sys_name, config in systems.items():
        print(f"\n--- {sys_name} ---")

        # Run baseline simulation
        traj = run_simulation(config['class'], **config['kwargs'])
        matrix, keys = trajectory_to_matrix(traj, max_dim=64)

        # Compute baseline values
        baseline_values = {}
        for obs_name, obs_func in observables.items():
            baseline_values[obs_name] = obs_func(matrix)

        sys_results = {
            'baseline': baseline_values,
            'compression_results': {},
        }

        # Test PCA compression
        print(f"\n  PCA Compression:")
        pca_results = {}
        for n_comp in [1, 2, 3, 5, 8, 13]:
            compressed = pca_compress(matrix, n_comp)
            obs_values = {}
            for obs_name, obs_func in observables.items():
                obs_values[obs_name] = obs_func(compressed)
            pca_results[n_comp] = obs_values
            print(f"    {n_comp} components: {obs_values}")
        sys_results['compression_results']['pca'] = pca_results

        # Test random projection
        print(f"\n  Random Projection:")
        rp_results = {}
        for n_comp in [1, 2, 3, 5, 8, 13]:
            projected = random_project(matrix, n_comp)
            obs_values = {}
            for obs_name, obs_func in observables.items():
                obs_values[obs_name] = obs_func(projected)
            rp_results[n_comp] = obs_values
            print(f"    {n_comp} components: {obs_values}")
        sys_results['compression_results']['random_projection'] = rp_results

        # Test quantization
        print(f"\n  Quantization:")
        quant_results = {}
        for n_levels in [2, 4, 8, 16, 32, 64]:
            quantized = quantize(matrix, n_levels)
            obs_values = {}
            for obs_name, obs_func in observables.items():
                obs_values[obs_name] = obs_func(quantized)
            quant_results[n_levels] = obs_values
            print(f"    {n_levels} levels: {obs_values}")
        sys_results['compression_results']['quantization'] = quant_results

        # Test binarization
        print(f"\n  Binarization:")
        bin_results = {}
        for threshold in [-0.5, 0.0, 0.5]:
            binarized = binarize(matrix, threshold)
            obs_values = {}
            for obs_name, obs_func in observables.items():
                obs_values[obs_name] = obs_func(binarized)
            bin_results[threshold] = obs_values
            print(f"    threshold={threshold}: {obs_values}")
        sys_results['compression_results']['binarization'] = bin_results

        results[sys_name] = sys_results

    # Compute compression tolerance
    print("\n" + "=" * 60)
    print("COMPRESSION TOLERANCE")
    print("=" * 60)

    for obs_name in observables:
        print(f"\n{obs_name}:")
        for sys_name in systems:
            baseline = results[sys_name]['baseline'][obs_name]

            # Find minimum PCA components that preserve value
            pca_results = results[sys_name]['compression_results']['pca']
            min_pca = 1
            for n_comp, values in sorted(pca_results.items()):
                if abs(values[obs_name] - baseline) < 0.1 * abs(baseline) + 1e-6:
                    min_pca = n_comp
                    break

            # Find minimum quantization levels
            quant_results = results[sys_name]['compression_results']['quantization']
            min_quant = 2
            for n_levels, values in sorted(quant_results.items()):
                if abs(values[obs_name] - baseline) < 0.1 * abs(baseline) + 1e-6:
                    min_quant = n_levels
                    break

            print(f"  {sys_name}: min_PCA={min_pca}, min_quant={min_quant}")

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
    }

    outpath = os.path.join(os.path.dirname(__file__), 'survivor_compression_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
