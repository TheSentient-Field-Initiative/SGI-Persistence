#!/usr/bin/env python3
"""
Phase 003F Division 3 — Embedding Singularity Analysis

Study:
- Covariance rank deficiency
- Singular-value collapse
- Jacobian conditioning
- Coordinate entropy collapse

Outputs:
- Singular spectra
- Condition-number evolution
- Rank-collapse trajectories
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


def compute_covariance_spectrum(matrix):
    """Compute covariance spectrum (eigenvalues of covariance matrix)."""
    if matrix.shape[0] < 2 or matrix.shape[1] < 2:
        return np.array([0.0])

    cov = np.cov(matrix, rowvar=False)
    eigenvalues = np.linalg.eigvalsh(cov)
    return np.sort(eigenvalues)[::-1]


def compute_condition_number(matrix):
    """Compute condition number of covariance matrix."""
    if matrix.shape[0] < 2 or matrix.shape[1] < 2:
        return 1.0

    cov = np.cov(matrix, rowvar=False)
    singular_values = np.linalg.svd(cov, compute_uv=False)

    if singular_values[-1] < 1e-10:
        return np.inf

    return float(singular_values[0] / singular_values[-1])


def compute_rank_deficiency(matrix, threshold=1e-6):
    """Compute rank deficiency of covariance matrix."""
    if matrix.shape[0] < 2 or matrix.shape[1] < 2:
        return matrix.shape[1]

    cov = np.cov(matrix, rowvar=False)
    singular_values = np.linalg.svd(cov, compute_uv=False)

    rank = np.sum(singular_values > threshold)
    deficiency = matrix.shape[1] - rank

    return int(deficiency)


def compute_coordinate_entropy(matrix):
    """Compute entropy of coordinate variances."""
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


def compute_participation_ratio(matrix):
    """Compute participation ratio of covariance spectrum."""
    if matrix.shape[0] < 2 or matrix.shape[1] < 2:
        return 1.0

    cov = np.cov(matrix, rowvar=False)
    eigenvalues = np.sort(np.linalg.eigvalsh(cov))[::-1]

    # Filter out negative eigenvalues
    eigenvalues = eigenvalues[eigenvalues > 0]

    if len(eigenvalues) == 0:
        return 1.0

    # Participation ratio
    total = np.sum(eigenvalues)
    if total < 1e-10:
        return 1.0

    pr = (np.sum(eigenvalues) ** 2) / np.sum(eigenvalues ** 2)
    return float(pr)


def corrupt_matrix(matrix, corruption_level, seed=42):
    """Apply corruption to matrix."""
    rng = np.random.RandomState(seed)
    noise = rng.randn(*matrix.shape) * corruption_level * matrix.std()
    return matrix + noise


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003F Division 3 — Embedding Singularity Analysis")
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
        cov_spectrum = compute_covariance_spectrum(matrix)
        condition_number = compute_condition_number(matrix)
        rank_deficiency = compute_rank_deficiency(matrix)
        coord_entropy = compute_coordinate_entropy(matrix)
        participation_ratio = compute_participation_ratio(matrix)

        print(f"  Matrix shape: {matrix.shape}")
        print(f"  Covariance spectrum (top 5): {cov_spectrum[:5]}")
        print(f"  Condition number: {condition_number:.4f}")
        print(f"  Rank deficiency: {rank_deficiency}")
        print(f"  Coordinate entropy: {coord_entropy:.4f}")
        print(f"  Participation ratio: {participation_ratio:.4f}")

        # Track metrics under corruption
        corruption_levels = np.linspace(0, 1, 20)
        condition_numbers = []
        rank_deficiencies = []
        coord_entropies = []
        participation_ratios = []

        for level in corruption_levels:
            corrupted = corrupt_matrix(matrix, level)
            cn = compute_condition_number(corrupted)
            rd = compute_rank_deficiency(corrupted)
            ce = compute_coordinate_entropy(corrupted)
            pr = compute_participation_ratio(corrupted)

            condition_numbers.append(cn if not np.isinf(cn) else 1e10)
            rank_deficiencies.append(rd)
            coord_entropies.append(ce)
            participation_ratios.append(pr)

        # Compute trajectories
        cn_trajectory = np.gradient(condition_numbers)
        rd_trajectory = np.gradient(rank_deficiencies)
        ce_trajectory = np.gradient(coord_entropies)
        pr_trajectory = np.gradient(participation_ratios)

        print(f"  Condition number trajectory: {cn_trajectory[:5]}")
        print(f"  Rank deficiency trajectory: {rd_trajectory[:5]}")
        print(f"  Coordinate entropy trajectory: {ce_trajectory[:5]}")
        print(f"  Participation ratio trajectory: {pr_trajectory[:5]}")

        results[sys_name] = {
            'matrix_shape': list(matrix.shape),
            'covariance_spectrum': cov_spectrum.tolist(),
            'condition_number': condition_number if not np.isinf(condition_number) else 1e10,
            'rank_deficiency': rank_deficiency,
            'coordinate_entropy': coord_entropy,
            'participation_ratio': participation_ratio,
            'condition_number_trajectory': cn_trajectory.tolist(),
            'rank_deficiency_trajectory': rd_trajectory.tolist(),
            'coordinate_entropy_trajectory': ce_trajectory.tolist(),
            'participation_ratio_trajectory': pr_trajectory.tolist(),
        }

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
    }

    outpath = os.path.join(os.path.dirname(__file__), 'embedding_singularity_analysis_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
