#!/usr/bin/env python3
"""
Phase 003H Division 1 — Survivor Stability Atlas

Map survivor observables across:
- Corruption
- Dimensionality
- Sparsity
- Basis transforms
- Temporal shuffling
- Stochastic injection
- Sample truncation

Output:
- Survival surfaces
- Robustness rankings
- Failure manifolds
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


def reduce_to_dim(matrix, dim):
    """Reduce to specified dimensionality."""
    if dim >= matrix.shape[1]:
        return matrix
    U, s, Vt = np.linalg.svd(matrix, full_matrices=False)
    return (U[:, :dim] * s[:dim])


def apply_sparsity(matrix, sparsity):
    """Apply sparsity mask."""
    rng = np.random.RandomState(42)
    mask = rng.random(matrix.shape) > sparsity
    return matrix * mask


def apply_basis_transform(matrix, transform_type):
    """Apply basis transform."""
    rng = np.random.RandomState(42)
    if transform_type == 'permutation':
        perm = rng.permutation(matrix.shape[1])
        return matrix[:, perm]
    elif transform_type == 'rotation':
        Q, R = np.linalg.qr(rng.randn(matrix.shape[1], matrix.shape[1]))
        return matrix @ Q
    elif transform_type == 'scaling':
        scales = rng.uniform(0.5, 2.0, matrix.shape[1])
        return matrix * scales
    return matrix


def apply_temporal_shuffle(matrix, shuffle_fraction):
    """Apply temporal shuffling."""
    rng = np.random.RandomState(42)
    n_shuffle = int(len(matrix) * shuffle_fraction)
    indices = rng.choice(len(matrix), size=n_shuffle, replace=False)
    shuffled = matrix.copy()
    rng.shuffle(shuffled[indices])
    return shuffled


def apply_stochastic_injection(matrix, injection_level):
    """Apply stochastic injection."""
    rng = np.random.RandomState(42)
    noise = rng.randn(*matrix.shape) * injection_level * matrix.std()
    return matrix + noise


def apply_sample_truncation(matrix, truncation_fraction):
    """Apply sample truncation."""
    n_keep = int(len(matrix) * (1 - truncation_fraction))
    return matrix[:n_keep]


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
    # Ensure both halves have same length
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


def compute_survival_score(canonical, null_matrices, obs_func):
    """Compute survival score (0-1)."""
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
    print("Phase 003H Division 1 — Survivor Stability Atlas")
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

        sys_results = {}

        for obs_name, obs_func in observables.items():
            print(f"\n  {obs_name}:")

            obs_results = {}

            # 1. Corruption stability
            corruption_levels = np.linspace(0, 1, 20)
            corruption_scores = []
            for level in corruption_levels:
                corrupted = corrupt_matrix(matrix, level)
                canonical = obs_func(corrupted)
                score = compute_survival_score(canonical, null_matrices, obs_func)
                corruption_scores.append(score)
            obs_results['corruption'] = {
                'levels': corruption_levels.tolist(),
                'scores': corruption_scores,
            }
            corruption_boundary = corruption_levels[np.argmax(np.array(corruption_scores) == 0)] if 0 in corruption_scores else 1.0
            print(f"    Corruption boundary: {corruption_boundary:.2f}")

            # 2. Dimensionality stability
            dim_levels = [1, 2, 3, 5, 8, 13, 21, 34]
            dim_scores = []
            for dim in dim_levels:
                reduced = reduce_to_dim(matrix, dim)
                canonical = obs_func(reduced)
                score = compute_survival_score(canonical, null_matrices, obs_func)
                dim_scores.append(score)
            obs_results['dimensionality'] = {
                'levels': dim_levels,
                'scores': dim_scores,
            }
            dim_boundary = dim_levels[np.argmax(np.array(dim_scores) == 0)] if 0 in dim_scores else dim_levels[-1]
            print(f"    Dimensionality boundary: {dim_boundary}")

            # 3. Sparsity stability
            sparsity_levels = np.linspace(0, 0.9, 10)
            sparsity_scores = []
            for sparsity in sparsity_levels:
                sparse = apply_sparsity(matrix, sparsity)
                canonical = obs_func(sparse)
                score = compute_survival_score(canonical, null_matrices, obs_func)
                sparsity_scores.append(score)
            obs_results['sparsity'] = {
                'levels': sparsity_levels.tolist(),
                'scores': sparsity_scores,
            }
            sparsity_boundary = sparsity_levels[np.argmax(np.array(sparsity_scores) == 0)] if 0 in sparsity_scores else 1.0
            print(f"    Sparsity boundary: {sparsity_boundary:.2f}")

            # 4. Basis transform stability
            basis_types = ['permutation', 'rotation', 'scaling']
            basis_scores = []
            for basis_type in basis_types:
                transformed = apply_basis_transform(matrix, basis_type)
                canonical = obs_func(transformed)
                score = compute_survival_score(canonical, null_matrices, obs_func)
                basis_scores.append(score)
            obs_results['basis_transform'] = {
                'types': basis_types,
                'scores': basis_scores,
            }
            basis_pass = sum(basis_scores)
            print(f"    Basis transform pass: {basis_pass}/3")

            # 5. Temporal shuffle stability
            shuffle_fractions = np.linspace(0, 0.9, 10)
            shuffle_scores = []
            for frac in shuffle_fractions:
                shuffled = apply_temporal_shuffle(matrix, frac)
                canonical = obs_func(shuffled)
                score = compute_survival_score(canonical, null_matrices, obs_func)
                shuffle_scores.append(score)
            obs_results['temporal_shuffle'] = {
                'fractions': shuffle_fractions.tolist(),
                'scores': shuffle_scores,
            }
            shuffle_boundary = shuffle_fractions[np.argmax(np.array(shuffle_scores) == 0)] if 0 in shuffle_scores else 1.0
            print(f"    Temporal shuffle boundary: {shuffle_boundary:.2f}")

            # 6. Stochastic injection stability
            injection_levels = np.linspace(0, 1, 20)
            injection_scores = []
            for level in injection_levels:
                injected = apply_stochastic_injection(matrix, level)
                canonical = obs_func(injected)
                score = compute_survival_score(canonical, null_matrices, obs_func)
                injection_scores.append(score)
            obs_results['stochastic_injection'] = {
                'levels': injection_levels.tolist(),
                'scores': injection_scores,
            }
            injection_boundary = injection_levels[np.argmax(np.array(injection_scores) == 0)] if 0 in injection_scores else 1.0
            print(f"    Stochastic injection boundary: {injection_boundary:.2f}")

            # 7. Sample truncation stability
            truncation_fractions = np.linspace(0, 0.9, 10)
            truncation_scores = []
            for frac in truncation_fractions:
                truncated = apply_sample_truncation(matrix, frac)
                if len(truncated) > 5:
                    canonical = obs_func(truncated)
                    score = compute_survival_score(canonical, null_matrices, obs_func)
                else:
                    score = 0
                truncation_scores.append(score)
            obs_results['sample_truncation'] = {
                'fractions': truncation_fractions.tolist(),
                'scores': truncation_scores,
            }
            truncation_boundary = truncation_fractions[np.argmax(np.array(truncation_scores) == 0)] if 0 in truncation_scores else 1.0
            print(f"    Sample truncation boundary: {truncation_boundary:.2f}")

            # Compute robustness score
            robustness_score = np.mean([
                corruption_boundary,
                dim_boundary / 34.0,
                sparsity_boundary,
                basis_pass / 3.0,
                shuffle_boundary,
                injection_boundary,
                truncation_boundary,
            ])
            obs_results['robustness_score'] = float(robustness_score)
            print(f"    Overall robustness score: {robustness_score:.3f}")

            sys_results[obs_name] = obs_results

        results[sys_name] = sys_results

    # Compute rankings
    print("\n" + "=" * 60)
    print("ROBUSTNESS RANKINGS")
    print("=" * 60)

    rankings = {}
    for obs_name in observables:
        scores = []
        for sys_name in systems:
            scores.append(results[sys_name][obs_name]['robustness_score'])
        mean_score = np.mean(scores)
        rankings[obs_name] = {
            'mean_score': float(mean_score),
            'scores': {sys_name: results[sys_name][obs_name]['robustness_score'] for sys_name in systems},
        }
        print(f"  {obs_name}: {mean_score:.3f}")

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'rankings': rankings,
        'runtime_seconds': round(elapsed, 1),
    }

    outpath = os.path.join(os.path.dirname(__file__), 'survivor_stability_atlas_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
