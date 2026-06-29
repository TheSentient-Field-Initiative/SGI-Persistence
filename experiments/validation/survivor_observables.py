#!/usr/bin/env python3
"""
Phase 003G Division 1 — Survivor Observable Search

Construct and test extremely minimal observables.

Candidates:
- variance-only metrics
- entropy-rate metrics
- persistence metrics
- lagged stability metrics
- transition-density metrics

Requirements for survival:
- outperform null controls
- survive perturbations
- remain basis-stable
- remain identifiable
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


def generate_random_matrix(shape, seed=42):
    """Generate random matrix for null control."""
    rng = np.random.RandomState(seed)
    return rng.randn(*shape)


# ============================================================
# SURVIVOR OBSERVABLE CANDIDATES
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
    # Compute correlation per coordinate
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


def obs_coordinate_diversity(matrix):
    """Coordinate diversity: entropy of coordinate variances."""
    variances = np.var(matrix, axis=0)
    total_var = np.sum(variances)
    if total_var < 1e-10:
        return 0.0
    probs = variances / total_var
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log(probs + 1e-10)))


def obs_spectral_entropy(matrix):
    """Spectral entropy of covariance matrix."""
    if matrix.shape[0] < 2 or matrix.shape[1] < 2:
        return 0.0
    cov = np.cov(matrix, rowvar=False)
    eigenvalues = np.sort(np.linalg.eigvalsh(cov))[::-1]
    eigenvalues = eigenvalues[eigenvalues > 0]
    if len(eigenvalues) == 0:
        return 0.0
    total = np.sum(eigenvalues)
    if total < 1e-10:
        return 0.0
    probs = eigenvalues / total
    return float(-np.sum(probs * np.log(probs + 1e-10)))


def obs_mean_stability(matrix):
    """Mean stability: how stable is the global mean."""
    if len(matrix) < 2:
        return 0.0
    means = np.mean(matrix, axis=1)
    if np.std(means) < 1e-10:
        return 1.0
    return float(1.0 / (1.0 + np.std(means)))


def obs_local_variance(matrix):
    """Local variance: average variance within sliding windows."""
    if len(matrix) < 5:
        return 0.0
    window_size = len(matrix) // 5
    local_vars = []
    for i in range(0, len(matrix) - window_size + 1, window_size):
        window = matrix[i:i + window_size]
        local_vars.append(np.var(window))
    return float(np.mean(local_vars))


# ============================================================
# MAIN EXPERIMENT
# ============================================================

def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003G Division 1 — Survivor Observable Search")
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

    # Observable candidates
    observables = {
        'variance_mean': obs_variance_mean,
        'variance_total': obs_variance_total,
        'entropy_rate': obs_entropy_rate,
        'persistence': obs_persistence,
        'lagged_stability': obs_lagged_stability,
        'transition_density': obs_transition_density,
        'coordinate_diversity': obs_coordinate_diversity,
        'spectral_entropy': obs_spectral_entropy,
        'mean_stability': obs_mean_stability,
        'local_variance': obs_local_variance,
    }

    results = {}

    for sys_name, config in systems.items():
        print(f"\n--- {sys_name} ---")

        # Run baseline simulation
        traj = run_simulation(config['class'], **config['kwargs'])
        matrix, keys = trajectory_to_matrix(traj, max_dim=64)

        sys_results = {}

        for obs_name, obs_func in observables.items():
            # Compute canonical value
            canonical = obs_func(matrix)

            # Compute under corruption
            corruption_levels = [0.0, 0.25, 0.5, 0.75, 1.0]
            corrupted_values = []
            for level in corruption_levels:
                corrupted = corrupt_matrix(matrix, level)
                val = obs_func(corrupted)
                corrupted_values.append(val)

            # Compute variance under corruption
            variance = np.var(corrupted_values)

            # Compute null controls
            null_values = []
            for i in range(5):
                null_matrix = generate_random_matrix(matrix.shape, seed=i)
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

            # Determine if basis-stable
            rng = np.random.RandomState(42)
            perm = rng.permutation(matrix.shape[1])
            permuted = matrix[:, perm]
            permuted_val = obs_func(permuted)
            basis_stable = abs(canonical - permuted_val) < 0.1 * abs(canonical) + 1e-6

            # Survival score
            survival_score = 0
            if outperforms_null:
                survival_score += 1
            if basis_stable:
                survival_score += 1
            if variance < 0.1:
                survival_score += 1

            sys_results[obs_name] = {
                'canonical': canonical,
                'variance_under_corruption': float(variance),
                'null_mean': float(null_mean),
                'null_std': float(null_std),
                'z_score': float(z_score),
                'outperforms_null': bool(outperforms_null),
                'basis_stable': bool(basis_stable),
                'survival_score': survival_score,
                'corrupted_values': corrupted_values,
            }

            status = "PASS" if survival_score >= 2 else "FAIL"
            print(f"  {obs_name}: {canonical:.4f} (z={z_score:.2f}, score={survival_score}/3) [{status}]")

        results[sys_name] = sys_results

    # Find survivors across all systems
    print("\n" + "=" * 60)
    print("SURVIVOR ANALYSIS")
    print("=" * 60)

    survivor_counts = {obs_name: 0 for obs_name in observables}
    for sys_name, sys_results in results.items():
        for obs_name, obs_data in sys_results.items():
            if obs_data['survival_score'] >= 2:
                survivor_counts[obs_name] += 1

    print("\nSurvival counts across 4 systems:")
    for obs_name, count in sorted(survivor_counts.items(), key=lambda x: -x[1]):
        status = "SURVIVOR" if count >= 3 else "CONDITIONAL" if count >= 2 else "FAILED"
        print(f"  {obs_name}: {count}/4 [{status}]")

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'survivor_counts': survivor_counts,
        'runtime_seconds': round(elapsed, 1),
    }

    outpath = os.path.join(os.path.dirname(__file__), 'survivor_observables_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
