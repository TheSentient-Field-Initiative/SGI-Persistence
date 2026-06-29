#!/usr/bin/env python3
"""
Phase 003G Division 4 — Failure Boundary Mapping

Map:
- Corruption boundaries
- Singularity boundaries
- Null indistinguishability boundaries
- Reconstruction-failure boundaries

Produce:
- Phase maps
- Collapse surfaces
- Legitimacy regions
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


def reduce_to_2d(matrix):
    """Reduce to 2D using PCA."""
    U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
    return (U[:, :2] * s[:2])


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


def compute_legitimacy_score(matrix, obs_func, null_matrices):
    """Compute legitimacy score for an observable."""
    canonical = obs_func(matrix)

    # Null distribution
    null_values = [obs_func(nm) for nm in null_matrices]
    null_mean = np.mean(null_values)
    null_std = np.std(null_values)

    if null_std > 0:
        z_score = (canonical - null_mean) / null_std
        outperforms_null = abs(z_score) > 2.0
    else:
        outperforms_null = False

    return 1 if outperforms_null else 0


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003G Division 4 — Failure Boundary Mapping")
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

        # Generate null matrices
        null_matrices = [
            np.random.randn(*matrix.shape) * matrix.std() + matrix.mean()
            for _ in range(10)
        ]

        # Map corruption boundaries
        corruption_levels = np.linspace(0, 1, 50)
        dim_levels = [1, 2, 3, 5, 8, 13, 21, 34]

        sys_results = {
            'corruption_boundaries': {},
            'dimensionality_boundaries': {},
            'phase_maps': {},
        }

        for obs_name, obs_func in observables.items():
            print(f"\n  {obs_name}:")

            # Corruption boundary
            corruption_scores = []
            for level in corruption_levels:
                corrupted = corrupt_matrix(matrix, level)
                score = compute_legitimacy_score(corrupted, obs_func, null_matrices)
                corruption_scores.append(score)

            # Find corruption boundary (where score drops to 0)
            corruption_boundary = 1.0
            for i, score in enumerate(corruption_scores):
                if score == 0:
                    corruption_boundary = corruption_levels[i]
                    break

            print(f"    Corruption boundary: {corruption_boundary:.2f}")
            sys_results['corruption_boundaries'][obs_name] = float(corruption_boundary)

            # Dimensionality boundary
            dim_scores = []
            for dim in dim_levels:
                # Reduce to dim dimensions
                if dim < matrix.shape[1]:
                    U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
                    reduced = (U[:, :dim] * s[:dim])
                else:
                    reduced = matrix

                score = compute_legitimacy_score(reduced, obs_func, null_matrices)
                dim_scores.append(score)

            # Find dimensionality boundary (where score drops to 0)
            dim_boundary = dim_levels[-1]
            for i, score in enumerate(dim_scores):
                if score == 0:
                    dim_boundary = dim_levels[i]
                    break

            print(f"    Dimensionality boundary: {dim_boundary}")
            sys_results['dimensionality_boundaries'][obs_name] = int(dim_boundary)

            # Phase map (corruption x dimensionality)
            phase_map = np.zeros((len(corruption_levels), len(dim_levels)))
            for i, level in enumerate(corruption_levels):
                for j, dim in enumerate(dim_levels):
                    corrupted = corrupt_matrix(matrix, level)
                    if dim < corrupted.shape[1]:
                        U, s, Vt = np.linalg.svd(corrupted, full_matrices=False)
                        reduced = (U[:, :dim] * s[:dim])
                    else:
                        reduced = corrupted
                    score = compute_legitimacy_score(reduced, obs_func, null_matrices)
                    phase_map[i, j] = score

            sys_results['phase_maps'][obs_name] = phase_map.tolist()

        results[sys_name] = sys_results

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
    }

    outpath = os.path.join(os.path.dirname(__file__), 'failure_boundary_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
