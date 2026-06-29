#!/usr/bin/env python3
"""
Phase 003I Division 3: Simulation Length Scaling
Tests whether embedding quality degrades with longer simulations.

Usage:
    python experiments/validation/simulation_length_scaling.py
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

# Test different simulation lengths
SIM_LENGTHS = [100, 200, 300, 500, 750, 1000]
NUM_SEEDS = 5
SYSTEM_CLASS = None  # Will be set in main


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


def compute_embedding_metrics(matrix):
    """Compute embedding singularity metrics."""
    results = {}

    # Basic shape
    results["n_timesteps"] = matrix.shape[0]
    results["n_dims"] = matrix.shape[1]

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

    # Information content (variance explained by first component)
    if len(matrix) > 1:
        try:
            cov = np.cov(matrix.T)
            eigenvalues = np.linalg.eigvalsh(cov)
            eigenvalues = eigenvalues[eigenvalues > 1e-10]
            total_var = np.sum(eigenvalues)
            if total_var > 0:
                results["variance_explained_pc1"] = float(eigenvalues[-1] / total_var)
            else:
                results["variance_explained_pc1"] = 1.0
        except:
            results["variance_explained_pc1"] = 1.0
    else:
        results["variance_explained_pc1"] = 1.0

    return results


def run_simulation_length_scaling():
    """Run simulations at different lengths and compare embedding quality."""
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
        print(f"\nRunning {sys_name} across simulation lengths...")
        length_results = {}

        for sim_length in SIM_LENGTHS:
            seed_metrics = []
            for seed in range(NUM_SEEDS):
                start = time.time()
                try:
                    system = sys_info["class"](seed=seed, **sys_info["kwargs"])
                    trajectory = []
                    for _ in range(sim_length):
                        trajectory.append(system.step())

                    matrix, keys = trajectory_to_matrix(trajectory)
                    metrics = compute_embedding_metrics(matrix)
                    metrics["seed"] = seed
                    metrics["runtime"] = time.time() - start
                    seed_metrics.append(metrics)
                except Exception as e:
                    print(f"  Seed {seed} (T={sim_length}): ERROR - {e}")
                    continue

            # Aggregate across seeds
            if seed_metrics:
                agg = {}
                for key in seed_metrics[0]:
                    if key == "seed":
                        continue
                    values = [r[key] for r in seed_metrics if key in r and r[key] != float("inf")]
                    if values:
                        agg[key] = {
                            "mean": float(np.mean(values)),
                            "std": float(np.std(values)),
                            "min": float(np.min(values)),
                            "max": float(np.max(values)),
                            "ci_95": [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]
                        }

                length_results[sim_length] = {
                    "seeds": seed_metrics,
                    "aggregate": agg,
                    "n_seeds": len(seed_metrics)
                }

                ed = agg.get("effective_dimensionality", {})
                print(f"  T={sim_length}: ED={ed.get('mean', 'N/A'):.4f} ± {ed.get('std', 0):.4f}")

        all_results[sys_name] = length_results

    return all_results


def analyze_length_trends(results):
    """Analyze how embedding quality changes with simulation length."""
    trends = {}

    for sys_name, length_data in results.items():
        ed_values = []
        lengths = []
        for sim_length, data in length_data.items():
            if "aggregate" in data and "effective_dimensionality" in data["aggregate"]:
                ed_values.append(data["aggregate"]["effective_dimensionality"]["mean"])
                lengths.append(sim_length)

        if len(ed_values) > 1:
            # Compute trend (slope)
            slope = np.polyfit(lengths, ed_values, 1)[0]
            # Compute stability (coefficient of variation)
            cv = np.std(ed_values) / np.mean(ed_values) if np.mean(ed_values) > 0 else 0

            trends[sys_name] = {
                "slope": float(slope),
                "cv": float(cv),
                "ed_values": ed_values,
                "lengths": lengths,
                "is_stable": abs(slope) < 0.001 and cv < 0.1
            }

            status = "STABLE" if trends[sys_name]["is_stable"] else "UNSTABLE"
            print(f"  {sys_name}: slope={slope:.6f}, cv={cv:.4f} [{status}]")

    return trends


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 003I DIVISION 3: SIMULATION LENGTH SCALING")
    print("=" * 70)
    print(f"Simulation lengths: {SIM_LENGTHS}")
    print(f"Seeds: {NUM_SEEDS}")
    print(f"Systems: distributed, immune, ant_colony, institution")

    start_time = time.time()

    # Run simulation length scaling
    results = run_simulation_length_scaling()

    # Analyze trends
    print(f"\nTREND ANALYSIS:")
    trends = analyze_length_trends(results)

    # Save results
    output = {
        "metadata": {
            "sim_lengths": SIM_LENGTHS,
            "num_seeds": NUM_SEEDS,
            "total_time": time.time() - start_time
        },
        "main_results": results,
        "trends": trends
    }

    output_file = os.path.join(OUTPUT_DIR, "simulation_length_scaling_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print(f"SIMULATION LENGTH SCALING COMPLETE")
    print(f"{'=' * 70}")
    print(f"Total runtime: {output['metadata']['total_time']:.1f}s")
    print(f"Results saved to: {output_file}")

    # Print summary
    print(f"\nSUMMARY:")
    stable_count = sum(1 for t in trends.values() if t["is_stable"])
    print(f"Stable systems: {stable_count}/{len(trends)}")
    for sys_name, trend in trends.items():
        status = "STABLE" if trend["is_stable"] else "UNSTABLE"
        print(f"  {sys_name}: {status}")
