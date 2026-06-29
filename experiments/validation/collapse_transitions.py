#!/usr/bin/env python3
"""
Phase 003E Division 1 — Collapse Transition Analysis

Study:
- Abrupt vs gradual observable collapse
- Phase-transition-like behavior
- Critical corruption thresholds
- Hysteresis effects under recovery

Output:
- Collapse transition curves
- Bifurcation-style diagrams
- Stability landscapes

Question: do replay observables fail smoothly or catastrophically?
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


def corrupt_coordinates(matrix, corruption_fraction, seed=42):
    """Randomly corrupt coordinates."""
    rng = np.random.RandomState(seed)
    corrupted = matrix.copy()
    n_corrupt = int(matrix.shape[1] * corruption_fraction)
    if n_corrupt > 0:
        indices = rng.choice(matrix.shape[1], size=n_corrupt, replace=False)
        for idx in indices:
            corrupted[:, idx] = rng.randn(matrix.shape[0]) * matrix[:, idx].std()
    return corrupted


def analyze_collapse_curve(G_values, H_values, corruption_fractions):
    """Analyze collapse curve for abruptness."""
    G_values = np.array(G_values)
    H_values = np.array(H_values)
    corruption_fractions = np.array(corruption_fractions)

    # Compute gradient (rate of change)
    G_gradient = np.gradient(G_values, corruption_fractions)
    H_gradient = np.gradient(H_values, corruption_fractions)

    # Find critical threshold (steepest descent)
    G_critical_idx = np.argmin(G_gradient)
    H_critical_idx = np.argmin(H_gradient)

    # Compute collapse abruptness (max gradient magnitude)
    G_abruptness = np.max(np.abs(G_gradient))
    H_abruptness = np.max(np.abs(H_gradient))

    # Determine if collapse is abrupt or gradual
    # Abrupt: high gradient magnitude at critical point
    # Gradual: low gradient magnitude throughout
    G_abrupt = G_abruptness > 0.5
    H_abrupt = H_abruptness > 0.5

    return {
        'G_gradient': G_gradient.tolist(),
        'H_gradient': H_gradient.tolist(),
        'G_critical_threshold': float(corruption_fractions[G_critical_idx]),
        'H_critical_threshold': float(corruption_fractions[H_critical_idx]),
        'G_abruptness': float(G_abruptness),
        'H_abruptness': float(H_abruptness),
        'G_abrupt': bool(G_abrupt),
        'H_abrupt': bool(H_abrupt),
    }


def analyze_hysteresis(matrix, compute_func, corruption_range, seed=42):
    """Analyze hysteresis effects under recovery."""
    forward_values = []
    backward_values = []

    # Forward: increasing corruption
    for frac in corruption_range:
        corrupted = corrupt_coordinates(matrix, frac, seed=seed)
        val = compute_func(corrupted)
        forward_values.append(val)

    # Backward: decreasing corruption (recovery)
    for frac in reversed(corruption_range):
        corrupted = corrupt_coordinates(matrix, frac, seed=seed + 1)
        val = compute_func(corrupted)
        backward_values.append(val)

    backward_values = list(reversed(backward_values))

    # Compute hysteresis (difference between forward and backward)
    hysteresis = np.mean(np.abs(np.array(forward_values) - np.array(backward_values)))

    return {
        'forward': forward_values,
        'backward': backward_values,
        'hysteresis': float(hysteresis),
    }


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003E Division 1 — Collapse Transition Analysis")
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

    # Corruption range for fine-grained analysis
    corruption_fractions = np.linspace(0.0, 1.0, 21)

    results = {}

    for sys_name, config in systems.items():
        print(f"\n--- {sys_name} ---")

        # Run baseline simulation
        traj = run_simulation(config['class'], **config['kwargs'])
        matrix, keys = trajectory_to_matrix(traj, max_dim=64)

        # Compute baseline metrics
        G_baseline = compute_G_from_matrix(matrix)
        H_baseline = compute_H_from_matrix(matrix)

        print(f"  Baseline: G={G_baseline:.4f}, H={H_baseline:.4f}")

        # Compute collapse curves
        G_values = []
        H_values = []
        for frac in corruption_fractions:
            corrupted = corrupt_coordinates(matrix, frac)
            G = compute_G_from_matrix(corrupted)
            H = compute_H_from_matrix(corrupted)
            G_values.append(G)
            H_values.append(H)

        # Analyze collapse characteristics
        collapse_analysis = analyze_collapse_curve(G_values, H_values, corruption_fractions)

        print(f"  G critical threshold: {collapse_analysis['G_critical_threshold']:.2f}")
        print(f"  H critical threshold: {collapse_analysis['H_critical_threshold']:.2f}")
        print(f"  G abrupt: {collapse_analysis['G_abrupt']}")
        print(f"  H abrupt: {collapse_analysis['H_abrupt']}")

        # Analyze hysteresis
        hysteresis_G = analyze_hysteresis(
            matrix,
            compute_G_from_matrix,
            corruption_fractions[::2],  # Use every other point for speed
        )
        hysteresis_H = analyze_hysteresis(
            matrix,
            compute_H_from_matrix,
            corruption_fractions[::2],
        )

        print(f"  G hysteresis: {hysteresis_G['hysteresis']:.4f}")
        print(f"  H hysteresis: {hysteresis_H['hysteresis']:.4f}")

        results[sys_name] = {
            'baseline': {'G': G_baseline, 'H': H_baseline},
            'corruption_fractions': corruption_fractions.tolist(),
            'G_values': G_values,
            'H_values': H_values,
            'collapse_analysis': collapse_analysis,
            'hysteresis_G': hysteresis_G,
            'hysteresis_H': hysteresis_H,
        }

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
        'summary': {
            sys_name: {
                'G_critical_threshold': r['collapse_analysis']['G_critical_threshold'],
                'H_critical_threshold': r['collapse_analysis']['H_critical_threshold'],
                'G_abrupt': r['collapse_analysis']['G_abrupt'],
                'H_abrupt': r['collapse_analysis']['H_abrupt'],
                'G_hysteresis': r['hysteresis_G']['hysteresis'],
                'H_hysteresis': r['hysteresis_H']['hysteresis'],
            }
            for sys_name, r in results.items()
        },
    }

    outpath = os.path.join(os.path.dirname(__file__), 'collapse_transitions_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
