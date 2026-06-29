#!/usr/bin/env python3
"""
Phase 003D Division 1 — Effective Dimensionality Analysis

Measure:
- Participation ratio
- Spectral entropy
- Covariance rank
- Stable rank
- Singular value decay
- Effective information dimension

Question: how many dimensions actually carry signal?
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


def compute_participation_ratio(singular_values):
    """Compute participation ratio: N_eff = (sum(s_i))^2 / sum(s_i^2)."""
    sv = singular_values[singular_values > 0]
    if len(sv) == 0:
        return 0.0
    return (np.sum(sv) ** 2) / np.sum(sv ** 2)


def compute_spectral_entropy(singular_values):
    """Compute spectral entropy: -sum(p_i * log(p_i)) where p_i = s_i / sum(s_j)."""
    sv = singular_values[singular_values > 0]
    if len(sv) == 0:
        return 0.0
    p = sv / np.sum(sv)
    return -np.sum(p * np.log(p + 1e-10))


def compute_covariance_rank(matrix, threshold=1e-10):
    """Compute rank of covariance matrix."""
    cov = np.cov(matrix.T)
    eigenvalues = np.linalg.eigvalsh(cov)
    return np.sum(eigenvalues > threshold)


def compute_stable_rank(singular_values):
    """Compute stable rank: ||A||_F^2 / ||A||_2^2."""
    sv = singular_values[singular_values > 0]
    if len(sv) == 0:
        return 0.0
    return np.sum(sv ** 2) / (sv[0] ** 2)


def compute_singular_value_decay(singular_values):
    """Compute rate of singular value decay."""
    sv = singular_values[singular_values > 0]
    if len(sv) < 2:
        return 0.0
    # Fit exponential decay: s_i = s_1 * exp(-alpha * i)
    i = np.arange(len(sv))
    log_sv = np.log(sv + 1e-10)
    coeffs = np.polyfit(i, log_sv, 1)
    return -coeffs[0]  # Decay rate


def compute_effective_information_dimension(singular_values):
    """Compute effective information dimension: D_eff = sum(p_i) / max(p_i)."""
    sv = singular_values[singular_values > 0]
    if len(sv) == 0:
        return 0.0
    p = sv / np.sum(sv)
    return np.sum(p) / np.max(p)


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003D Division 1 — Effective Dimensionality Analysis")
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

        # Compute SVD
        U, s, Vt = np.linalg.svd(matrix, full_matrices=False)

        # Compute dimensionality metrics
        participation_ratio = compute_participation_ratio(s)
        spectral_entropy = compute_spectral_entropy(s)
        covariance_rank = compute_covariance_rank(matrix)
        stable_rank = compute_stable_rank(s)
        sv_decay = compute_singular_value_decay(s)
        effective_info_dim = compute_effective_information_dimension(s)

        print(f"  Participation ratio: {participation_ratio:.4f}")
        print(f"  Spectral entropy: {spectral_entropy:.4f}")
        print(f"  Covariance rank: {covariance_rank}")
        print(f"  Stable rank: {stable_rank:.4f}")
        print(f"  SV decay rate: {sv_decay:.4f}")
        print(f"  Effective info dimension: {effective_info_dim:.4f}")

        # Singular values
        sv_normalized = s / s[0] if s[0] > 0 else s

        results[sys_name] = {
            'matrix_shape': list(matrix.shape),
            'n_keys': len(keys),
            'keys': keys,
            'participation_ratio': float(participation_ratio),
            'spectral_entropy': float(spectral_entropy),
            'covariance_rank': int(covariance_rank),
            'stable_rank': float(stable_rank),
            'sv_decay_rate': float(sv_decay),
            'effective_info_dimension': float(effective_info_dim),
            'singular_values': s.tolist(),
            'singular_values_normalized': sv_normalized.tolist(),
        }

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
        'summary': {
            sys_name: {
                'participation_ratio': r['participation_ratio'],
                'spectral_entropy': r['spectral_entropy'],
                'covariance_rank': r['covariance_rank'],
                'stable_rank': r['stable_rank'],
                'effective_info_dimension': r['effective_info_dimension'],
            }
            for sys_name, r in results.items()
        },
    }

    outpath = os.path.join(os.path.dirname(__file__), 'effective_dimensionality_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
