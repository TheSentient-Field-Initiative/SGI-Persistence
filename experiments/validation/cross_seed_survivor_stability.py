#!/usr/bin/env python3
"""
Phase 003I Division 4: Cross-seed Survivor Stability Quantification
Tests whether survivor observables remain stable across different seeds.

Usage:
    python experiments/validation/cross_seed_survivor_stability.py
"""

import numpy as np
import json
import os
import sys
import time

# Add source paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'distributed'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'immune'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'ant_colony'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'institution'))

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_SEEDS = 10
NUM_TIMESTEPS = 200


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


def compute_survivor_observables(matrix):
    """Compute all survivor observables on a matrix."""
    results = {}

    # Basic statistics
    results["variance_mean"] = float(np.mean(np.var(matrix, axis=0)))

    # Lagged stability (autocorrelation)
    if len(matrix) > 10:
        autocorr = []
        for lag in range(1, min(11, len(matrix) // 2)):
            c = np.corrcoef(matrix[:-lag].flatten(), matrix[lag:].flatten())[0, 1]
            if not np.isnan(c):
                autocorr.append(c)
        results["lagged_stability"] = float(np.mean(autocorr)) if autocorr else 0.0
    else:
        results["lagged_stability"] = 0.0

    # Persistence (fraction of variance retained)
    var_per_dim = np.var(matrix, axis=0)
    total_var = np.sum(var_per_dim)
    if total_var > 0:
        results["persistence"] = float(np.sum(var_per_dim > 0.01 * np.max(var_per_dim)) / len(var_per_dim))
    else:
        results["persistence"] = 0.0

    # Transition density (fraction of dimensions that change)
    if len(matrix) > 1:
        changes = np.abs(np.diff(matrix, axis=0))
        std_per_dim = np.std(matrix, axis=0)
        std_per_dim[std_per_dim == 0] = 1  # Avoid division by zero
        transition_mask = changes > 0.1 * std_per_dim
        results["transition_density"] = float(np.mean(transition_mask))
    else:
        results["transition_density"] = 0.0

    # Additional observables
    # Variance of variances
    var_of_var = np.var(np.var(matrix, axis=0))
    results["variance_of_variance"] = float(var_of_var)

    # Mean absolute difference
    if len(matrix) > 1:
        mad = np.mean(np.abs(np.diff(matrix, axis=0)))
        results["mean_absolute_difference"] = float(mad)
    else:
        results["mean_absolute_difference"] = 0.0

    # Entropy (approximate)
    flat = matrix.flatten()
    hist, _ = np.histogram(flat, bins=50, density=True)
    hist = hist[hist > 0]
    results["approx_entropy"] = float(-np.sum(hist * np.log(hist + 1e-10)))

    return results


def run_cross_seed_survivor_stability():
    """Test survivor observables across seeds and systems."""
    from study_001 import DistributedSystem
    from study_001c_immune import ImmuneSignalingNetwork
    from study_001b_colony import AntColony
    from study_001d_institution import InstitutionNetwork

    systems = {
        "distributed": {
            "class": DistributedSystem,
            "kwargs": {"n_nodes": 100}
        },
        "immune": {
            "class": ImmuneSignalingNetwork,
            "kwargs": {"n_cells": 100}
        },
        "ant_colony": {
            "class": AntColony,
            "kwargs": {"n_ants": 50, "n_food": 100}
        },
        "institution": {
            "class": InstitutionNetwork,
            "kwargs": {"n_agents": 100}
        },
    }

    all_results = {}

    for sys_name, sys_info in systems.items():
        print(f"\nRunning {sys_name} across {NUM_SEEDS} seeds...")
        seed_observables = []

        for seed in range(NUM_SEEDS):
            start = time.time()
            try:
                system = sys_info["class"](seed=seed, **sys_info["kwargs"])
                trajectory = []
                for _ in range(NUM_TIMESTEPS):
                    trajectory.append(system.step())

                matrix, keys = trajectory_to_matrix(trajectory)
                observables = compute_survivor_observables(matrix)
                observables["seed"] = seed
                observables["runtime"] = time.time() - start
                seed_observables.append(observables)
                print(f"  Seed {seed}: variance_mean={observables['variance_mean']:.4f}, "
                      f"lagged_stability={observables['lagged_stability']:.4f}")
            except Exception as e:
                print(f"  Seed {seed}: ERROR - {e}")
                continue

        # Compute cross-seed statistics
        if seed_observables:
            obs_stats = {}
            for obs_name in seed_observables[0]:
                if obs_name in ("seed", "runtime"):
                    continue
                values = [r[obs_name] for r in seed_observables if obs_name in r]
                if values:
                    cv = np.std(values) / np.mean(values) if np.mean(values) != 0 else float("inf")
                    obs_stats[obs_name] = {
                        "mean": float(np.mean(values)),
                        "std": float(np.std(values)),
                        "cv": float(cv),
                        "min": float(np.min(values)),
                        "max": float(np.max(values)),
                        "range": float(np.max(values) - np.min(values)),
                        "is_stable": cv < 0.2  # 20% CV threshold for stability
                    }

            all_results[sys_name] = {
                "seeds": seed_observables,
                "statistics": obs_stats,
                "n_seeds": len(seed_observables)
            }

            print(f"  Summary:")
            for obs_name, stats in obs_stats.items():
                status = "STABLE" if stats["is_stable"] else "UNSTABLE"
                print(f"    {obs_name}: CV={stats['cv']:.4f} [{status}]")

    return all_results


def compute_cross_system_stability(all_results):
    """Compute which observables are stable across ALL systems."""
    obs_names = []
    for sys_name, sys_data in all_results.items():
        obs_names = list(sys_data["statistics"].keys())
        break

    cross_system_stability = {}
    for obs_name in obs_names:
        systems_stable = 0
        total_cv = []
        for sys_name, sys_data in all_results.items():
            if obs_name in sys_data["statistics"]:
                stats = sys_data["statistics"][obs_name]
                if stats["is_stable"]:
                    systems_stable += 1
                total_cv.append(stats["cv"])

        cross_system_stability[obs_name] = {
            "n_stable_systems": systems_stable,
            "total_systems": len(all_results),
            "mean_cv": float(np.mean(total_cv)) if total_cv else float("inf"),
            "is_cross_system_stable": systems_stable == len(all_results)
        }

    return cross_system_stability


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 003I DIVISION 4: CROSS-SEED SURVIVOR STABILITY")
    print("=" * 70)
    print(f"Seeds: {NUM_SEEDS}")
    print(f"Timesteps: {NUM_TIMESTEPS}")
    print(f"Systems: distributed, immune, ant_colony, institution")

    start_time = time.time()

    # Run cross-seed survivor stability
    results = run_cross_seed_survivor_stability()

    # Compute cross-system stability
    print(f"\nCROSS-SYSTEM STABILITY ANALYSIS:")
    cross_stability = compute_cross_system_stability(results)

    for obs_name, stats in cross_stability.items():
        status = "CROSS-SYSTEM STABLE" if stats["is_cross_system_stable"] else "NOT CROSS-SYSTEM STABLE"
        print(f"  {obs_name}: {stats['n_stable_systems']}/{stats['total_systems']} systems stable [{status}]")

    # Save results
    output = {
        "metadata": {
            "num_seeds": NUM_SEEDS,
            "num_timesteps": NUM_TIMESTEPS,
            "total_time": time.time() - start_time
        },
        "main_results": results,
        "cross_system_stability": cross_stability
    }

    output_file = os.path.join(OUTPUT_DIR, "cross_seed_survivor_stability_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print(f"CROSS-SEED SURVIVOR STABILITY COMPLETE")
    print(f"{'=' * 70}")
    print(f"Total runtime: {output['metadata']['total_time']:.1f}s")
    print(f"Results saved to: {output_file}")

    # Print summary
    print(f"\nSUMMARY:")
    cross_stable_count = sum(1 for s in cross_stability.values() if s["is_cross_system_stable"])
    print(f"Cross-system stable observables: {cross_stable_count}/{len(cross_stability)}")
    for obs_name, stats in cross_stability.items():
        status = "STABLE" if stats["is_cross_system_stable"] else "UNSTABLE"
        print(f"  {obs_name}: {status} (mean CV={stats['mean_cv']:.4f})")
