#!/usr/bin/env python3
"""
Phase 003I Division 1: Multi-seed replication
Runs all major experiments across 10+ random seeds to establish statistical confidence.

Usage:
    python experiments/validation/multi_seed_replication.py
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


def run_simulation(system_class, **kwargs):
    """Run a simulation and return trajectory."""
    system = system_class(**kwargs)
    for _ in range(NUM_TIMESTEPS):
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


def compute_metrics(matrix):
    """Compute all metrics on a matrix."""
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

    # Embedding singularity
    if len(matrix) > matrix.shape[1]:
        try:
            cov = np.cov(matrix.T)
            eigenvalues = np.linalg.eigvalsh(cov)
            eigenvalues = eigenvalues[eigenvalues > 1e-10]
            if len(eigenvalues) > 0:
                condition_number = eigenvalues[-1] / eigenvalues[0]
                participation_ratio = (np.sum(eigenvalues) ** 2) / np.sum(eigenvalues ** 2)
                results["condition_number"] = float(condition_number)
                results["participation_ratio"] = float(participation_ratio)
                results["rank_deficiency"] = int(matrix.shape[1] - len(eigenvalues))
                results["effective_dimensionality"] = float(participation_ratio)
            else:
                results["condition_number"] = float("inf")
                results["participation_ratio"] = 1.0
                results["rank_deficiency"] = matrix.shape[1]
                results["effective_dimensionality"] = 1.0
        except Exception as e:
            results["condition_number"] = 1.0
            results["participation_ratio"] = 1.0
            results["rank_deficiency"] = 0
            results["effective_dimensionality"] = 1.0
    else:
        results["condition_number"] = 1.0
        results["participation_ratio"] = 1.0
        results["rank_deficiency"] = 0
        results["effective_dimensionality"] = 1.0

    return results


def run_multi_seed_replication():
    """Run all experiments across multiple seeds."""
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
        }
    }

    all_results = {}

    for sys_name, sys_info in systems.items():
        print(f"\nRunning {sys_name} across {NUM_SEEDS} seeds...")
        seed_results = []

        for seed in range(NUM_SEEDS):
            start = time.time()
            try:
                trajectory = run_simulation(sys_info["class"], seed=seed, **sys_info["kwargs"])
                matrix, keys = trajectory_to_matrix(trajectory)
                metrics = compute_metrics(matrix)
                metrics["seed"] = seed
                metrics["runtime"] = time.time() - start
                seed_results.append(metrics)
                print(f"  Seed {seed}: runtime={metrics['runtime']:.2f}s, ED={metrics.get('effective_dimensionality', 'N/A'):.4f}")
            except Exception as e:
                print(f"  Seed {seed}: ERROR - {e}")
                continue

        # Aggregate across seeds
        if seed_results:
            agg = {}
            for key in seed_results[0]:
                if key == "seed":
                    continue
                values = [r[key] for r in seed_results if key in r and r[key] != float("inf")]
                if values:
                    agg[key] = {
                        "mean": float(np.mean(values)),
                        "std": float(np.std(values)),
                        "min": float(np.min(values)),
                        "max": float(np.max(values)),
                        "ci_95": [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]
                    }
                else:
                    agg[key] = {"mean": float("inf"), "std": 0, "min": float("inf"), "max": float("inf"), "ci_95": [float("inf"), float("inf")]}

            all_results[sys_name] = {
                "seeds": seed_results,
                "aggregate": agg,
                "n_seeds": len(seed_results)
            }

            ed = agg.get("effective_dimensionality", {})
            pr = agg.get("participation_ratio", {})
            print(f"  Effective dimensionality: {ed.get('mean', 'N/A'):.4f} ± {ed.get('std', 0):.4f}")
            print(f"  Participation ratio: {pr.get('mean', 'N/A'):.4f}")

    return all_results


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 003I DIVISION 1: MULTI-SEED REPLICATION")
    print("=" * 70)
    print(f"Seeds: {NUM_SEEDS}")
    print(f"Timesteps: {NUM_TIMESTEPS}")
    print(f"Systems: distributed, immune, ant_colony, institution")

    start_time = time.time()

    # Run multi-seed experiments
    results = run_multi_seed_replication()

    # Save results
    output = {
        "metadata": {
            "num_seeds": NUM_SEEDS,
            "num_timesteps": NUM_TIMESTEPS,
            "total_time": time.time() - start_time
        },
        "main_results": results,
    }

    output_file = os.path.join(OUTPUT_DIR, "multi_seed_replication.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print(f"MULTI-SEED REPLICATION COMPLETE")
    print(f"{'=' * 70}")
    print(f"Total runtime: {output['metadata']['total_time']:.1f}s")
    print(f"Results saved to: {output_file}")

    # Print summary
    print(f"\nSUMMARY:")
    for sys_name, sys_data in results.items():
        agg = sys_data["aggregate"]
        ed = agg.get("effective_dimensionality", {})
        pr = agg.get("participation_ratio", {})
        print(f"  {sys_name}:")
        print(f"    Effective dimensionality: {ed.get('mean', 'N/A'):.4f} ± {ed.get('std', 0):.4f}")
        print(f"    Participation ratio: {pr.get('mean', 'N/A'):.4f} ± {pr.get('std', 0):.4f}")
        print(f"    Seeds completed: {sys_data.get('n_seeds', 0)}/{NUM_SEEDS}")
