#!/usr/bin/env python3
"""
Phase 003F Division 2 — Collapse Mechanics Model

Model collapse itself:
- collapse rates
- collapse acceleration
- critical exponents
- recovery dynamics
- metastability regions

Question: Is collapse mathematically structured or merely numerical instability?
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


def compute_G_from_matrix(matrix, n_sectors=2):
    """Compute G from matrix using sector alignment."""
    if len(matrix) < 10:
        return 0.0

    mid = len(matrix) // 2
    before = matrix[:mid]
    after = matrix[mid:]

    surviving = 0
    dim_per_sector = matrix.shape[1] // n_sectors

    for i in range(n_sectors):
        start = i * dim_per_sector
        end = start + dim_per_sector
        bv = before[:, start:end]
        av = after[:, start:end]

        if bv.size == 0 or av.size == 0:
            continue

        def _cosine(a, b):
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            return float(np.dot(a.flatten(), b.flatten()) / (na * nb)) if na > 0 and nb > 0 else 0.0

        raw = _cosine(bv, av)
        bn = (bv - bv.mean(0)) / (bv.std(0) + 1e-8)
        an = (av - av.mean(0)) / (av.std(0) + 1e-8)
        norm = _cosine(bn, an)

        if (norm - raw) > -0.1:
            surviving += 1

    return surviving / n_sectors if n_sectors > 0 else 0.0


def compute_H_from_matrix(matrix, max_lag=5):
    """Compute H from matrix using autocorrelation."""
    if len(matrix) < max_lag + 1:
        return 0.0

    autocorrs = []
    for lag in range(1, min(max_lag + 1, len(matrix))):
        if lag < len(matrix):
            a = matrix[:-lag]
            b = matrix[lag:]
            if a.size > 0 and b.size > 0:
                na, nb = np.linalg.norm(a), np.linalg.norm(b)
                if na > 0 and nb > 0:
                    corr = np.dot(a.flatten(), b.flatten()) / (na * nb)
                    autocorrs.append(abs(corr))

    return np.mean(autocorrs) if autocorrs else 0.0


def corrupt_matrix(matrix, corruption_level, seed=42):
    """Apply corruption to matrix."""
    rng = np.random.RandomState(seed)
    noise = rng.randn(*matrix.shape) * corruption_level * matrix.std()
    return matrix + noise


def compute_collapse_rate(G_values, corruption_levels):
    """Compute collapse rate (derivative at collapse point)."""
    if len(G_values) < 2:
        return 0.0

    dG = np.diff(G_values)
    dc = np.diff(corruption_levels)

    # Find maximum derivative (steepest descent)
    rates = np.abs(dG / (dc + 1e-10))
    return float(np.max(rates))


def compute_collapse_acceleration(G_values, corruption_levels):
    """Compute collapse acceleration (second derivative)."""
    if len(G_values) < 3:
        return 0.0

    dG = np.diff(G_values)
    dc = np.diff(corruption_levels)

    d2G = np.diff(dG)
    # Use the mean step size for the denominator
    dc_mean = np.mean(dc[:-1])
    accelerations = np.abs(d2G / (dc_mean + 1e-10))
    return float(np.max(accelerations))


def find_critical_exponent(G_values, corruption_levels):
    """Estimate critical exponent near collapse."""
    if len(G_values) < 3:
        return 0.0

    # Find collapse point
    mid = len(G_values) // 2
    pre_collapse = G_values[:mid]
    post_collapse = G_values[mid:]

    if len(pre_collapse) < 2 or len(post_collapse) < 2:
        return 0.0

    # Fit power law: G ~ |c - c_crit|^beta
    # Use log-log fit near collapse
    c_crit = corruption_levels[mid]
    delta_c = np.abs(corruption_levels[mid+1:] - c_crit) + 1e-10
    G_near = G_values[mid+1:]

    if len(delta_c) < 2 or len(G_near) < 2:
        return 0.0

    # Filter out zeros
    mask = G_near > 0
    if mask.sum() < 2:
        return 0.0

    log_delta = np.log(delta_c[mask])
    log_G = np.log(G_near[mask])

    # Linear fit
    A = np.vstack([log_delta, np.ones(len(log_delta))]).T
    try:
        coeffs = np.linalg.lstsq(A, log_G, rcond=None)[0]
        return float(abs(coeffs[0]))  # Beta exponent
    except:
        return 0.0


def compute_recovery_rate(G_values, corruption_levels):
    """Compute recovery rate after corruption removal."""
    if len(G_values) < 3:
        return 0.0

    # Find minimum G
    min_idx = np.argmin(G_values)
    if min_idx >= len(G_values) - 1:
        return 0.0

    # Compute recovery slope
    recovery = G_values[min_idx:]
    recovery_levels = corruption_levels[min_idx:]

    if len(recovery) < 2:
        return 0.0

    dG = np.diff(recovery)
    dc = np.diff(recovery_levels)

    rates = dG / (dc + 1e-10)
    return float(np.mean(rates))


def compute_metastability_region(G_values, corruption_levels, threshold=0.1):
    """Compute metastability region (where G fluctuates around threshold)."""
    if len(G_values) < 3:
        return 0.0

    # Find region where G is near threshold
    near_threshold = np.abs(G_values - threshold) < 0.05
    if not np.any(near_threshold):
        return 0.0

    # Compute width of metastable region
    indices = np.where(near_threshold)[0]
    if len(indices) < 2:
        return 0.0

    width = corruption_levels[indices[-1]] - corruption_levels[indices[0]]
    return float(width)


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003F Division 2 — Collapse Mechanics Model")
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

        # Test corruption levels
        corruption_levels = np.linspace(0, 1, 50)
        G_values = []
        H_values = []

        for level in corruption_levels:
            corrupted = corrupt_matrix(matrix, level)
            G = compute_G_from_matrix(corrupted)
            H = compute_H_from_matrix(corrupted)
            G_values.append(G)
            H_values.append(H)

        G_values = np.array(G_values)
        H_values = np.array(H_values)

        # Compute collapse mechanics
        G_collapse_rate = compute_collapse_rate(G_values, corruption_levels)
        G_collapse_accel = compute_collapse_acceleration(G_values, corruption_levels)
        G_critical_exponent = find_critical_exponent(G_values, corruption_levels)
        G_recovery_rate = compute_recovery_rate(G_values, corruption_levels)
        G_metastability = compute_metastability_region(G_values, corruption_levels)

        H_collapse_rate = compute_collapse_rate(H_values, corruption_levels)
        H_collapse_accel = compute_collapse_acceleration(H_values, corruption_levels)
        H_critical_exponent = find_critical_exponent(H_values, corruption_levels)
        H_recovery_rate = compute_recovery_rate(H_values, corruption_levels)
        H_metastability = compute_metastability_region(H_values, corruption_levels)

        print(f"  G collapse rate: {G_collapse_rate:.4f}")
        print(f"  G collapse acceleration: {G_collapse_accel:.4f}")
        print(f"  G critical exponent: {G_critical_exponent:.4f}")
        print(f"  G recovery rate: {G_recovery_rate:.4f}")
        print(f"  G metastability region: {G_metastability:.4f}")
        print(f"  H collapse rate: {H_collapse_rate:.4f}")
        print(f"  H collapse acceleration: {H_collapse_accel:.4f}")
        print(f"  H critical exponent: {H_critical_exponent:.4f}")
        print(f"  H recovery rate: {H_recovery_rate:.4f}")
        print(f"  H metastability region: {H_metastability:.4f}")

        results[sys_name] = {
            'G_collapse_rate': G_collapse_rate,
            'G_collapse_acceleration': G_collapse_accel,
            'G_critical_exponent': G_critical_exponent,
            'G_recovery_rate': G_recovery_rate,
            'G_metastability_region': G_metastability,
            'H_collapse_rate': H_collapse_rate,
            'H_collapse_acceleration': H_collapse_accel,
            'H_critical_exponent': H_critical_exponent,
            'H_recovery_rate': H_recovery_rate,
            'H_metastability_region': H_metastability,
        }

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
    }

    outpath = os.path.join(os.path.dirname(__file__), 'collapse_mechanics_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
