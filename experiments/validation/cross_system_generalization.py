#!/usr/bin/env python3
"""
Phase 003H Division 2 — Cross-System Generalization Audit

Goal: Train thresholds/parameters on one system, evaluate on another.

Question: Do survivor observables generalize across adaptive-system classes?
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
    print("Phase 003H Division 2 — Cross-System Generalization Audit")
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

    # Run all simulations
    matrices = {}
    for sys_name, config in systems.items():
        traj = run_simulation(config['class'], **config['kwargs'])
        matrix, keys = trajectory_to_matrix(traj, max_dim=64)
        matrices[sys_name] = matrix

    results = {}

    for obs_name, obs_func in observables.items():
        print(f"\n--- {obs_name} ---")

        # Compute values for all systems
        values = {}
        for sys_name, matrix in matrices.items():
            values[sys_name] = obs_func(matrix)

        print(f"  Values: {values}")

        # Cross-system generalization test
        generalization_matrix = np.zeros((len(systems), len(systems)))

        for i, train_system in enumerate(systems):
            for j, test_system in enumerate(systems):
                if i == j:
                    generalization_matrix[i, j] = 1.0
                    continue

                # Train: compute threshold from training system
                train_matrix = matrices[train_system]
                train_values = []
                for seed in range(10):
                    rng = np.random.RandomState(seed)
                    noise = rng.randn(*train_matrix.shape) * 0.1 * train_matrix.std()
                    noisy = train_matrix + noise
                    train_values.append(obs_func(noisy))

                train_mean = np.mean(train_values)
                train_std = np.std(train_values)

                # Test: evaluate on test system
                test_matrix = matrices[test_system]
                test_values = []
                for seed in range(10):
                    rng = np.random.RandomState(seed)
                    noise = rng.randn(*test_matrix.shape) * 0.1 * test_matrix.std()
                    noisy = test_matrix + noise
                    test_values.append(obs_func(noisy))

                test_mean = np.mean(test_values)

                # Check if test value is within train range (within 2 std)
                if train_std > 0:
                    z_score = abs(test_mean - train_mean) / train_std
                    generalization_score = 1.0 if z_score < 2.0 else 0.0
                else:
                    generalization_score = 1.0 if abs(test_mean - train_mean) < 0.1 else 0.0

                generalization_matrix[i, j] = generalization_score

        # Compute generalization statistics
        off_diagonal = generalization_matrix[np.triu_indices(len(systems), k=1)]
        mean_generalization = np.mean(off_diagonal)
        min_generalization = np.min(off_diagonal)

        print(f"  Mean generalization: {mean_generalization:.3f}")
        print(f"  Min generalization: {min_generalization:.3f}")

        results[obs_name] = {
            'values': values,
            'generalization_matrix': generalization_matrix.tolist(),
            'mean_generalization': float(mean_generalization),
            'min_generalization': float(min_generalization),
        }

    # Compute rankings
    print("\n" + "=" * 60)
    print("GENERALIZATION RANKINGS")
    print("=" * 60)

    rankings = {}
    for obs_name in observables:
        mean_gen = results[obs_name]['mean_generalization']
        rankings[obs_name] = mean_gen
        print(f"  {obs_name}: {mean_gen:.3f}")

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'rankings': rankings,
        'runtime_seconds': round(elapsed, 1),
    }

    outpath = os.path.join(os.path.dirname(__file__), 'cross_system_generalization_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
