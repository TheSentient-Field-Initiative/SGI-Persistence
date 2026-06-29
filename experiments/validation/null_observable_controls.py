#!/usr/bin/env python3
"""
Phase 003E Division 4 — Null Observable Controls

Generate:
- Random observables
- Shuffled observables
- Synthetic degenerate metrics
- Coordinate-noise observables

Goal: determine whether canonical metrics outperform null metrics.
This is mandatory now.
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


def generate_random_observable(matrix, seed=42):
    """Generate random observable (same shape as matrix)."""
    rng = np.random.RandomState(seed)
    return rng.randn(*matrix.shape) * matrix.std() + matrix.mean()


def generate_shuffled_observable(matrix, seed=42):
    """Generate shuffled observable (rows shuffled)."""
    rng = np.random.RandomState(seed)
    shuffled = matrix.copy()
    for col in range(shuffled.shape[1]):
        rng.shuffle(shuffled[:, col])
    return shuffled


def generate_coordinate_noise_observable(matrix, noise_fraction=0.5, seed=42):
    """Generate coordinate-noise observable."""
    rng = np.random.RandomState(seed)
    noisy = matrix.copy()
    n_noisy = int(matrix.shape[1] * noise_fraction)
    if n_noisy > 0:
        indices = rng.choice(matrix.shape[1], size=n_noisy, replace=False)
        for idx in indices:
            noisy[:, idx] = rng.randn(matrix.shape[0]) * matrix[:, idx].std()
    return noisy


def generate_constant_observable(matrix, value=0.0):
    """Generate constant observable."""
    return np.full_like(matrix, value)


def generate_linear_trend_observable(matrix):
    """Generate linear trend observable."""
    trend = np.linspace(0, 1, matrix.shape[0]).reshape(-1, 1)
    return trend * matrix.std() + matrix.mean()


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003E Division 4 — Null Observable Controls")
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

        # Compute canonical metrics
        G_canonical = compute_G_from_matrix(matrix)
        H_canonical = compute_H_from_matrix(matrix)

        print(f"  Canonical: G={G_canonical:.4f}, H={H_canonical:.4f}")

        # Generate null observables
        null_results = {}

        # 1. Random observable
        random_obs = generate_random_observable(matrix)
        G_random = compute_G_from_matrix(random_obs)
        H_random = compute_H_from_matrix(random_obs)
        null_results['random'] = {'G': G_random, 'H': H_random}

        # 2. Shuffled observable
        shuffled_obs = generate_shuffled_observable(matrix)
        G_shuffled = compute_G_from_matrix(shuffled_obs)
        H_shuffled = compute_H_from_matrix(shuffled_obs)
        null_results['shuffled'] = {'G': G_shuffled, 'H': H_shuffled}

        # 3. Coordinate noise observable
        noise_obs = generate_coordinate_noise_observable(matrix)
        G_noise = compute_G_from_matrix(noise_obs)
        H_noise = compute_H_from_matrix(noise_obs)
        null_results['coordinate_noise'] = {'G': G_noise, 'H': H_noise}

        # 4. Constant observable
        constant_obs = generate_constant_observable(matrix, value=matrix.mean())
        G_constant = compute_G_from_matrix(constant_obs)
        H_constant = compute_H_from_matrix(constant_obs)
        null_results['constant'] = {'G': G_constant, 'H': H_constant}

        # 5. Linear trend observable
        trend_obs = generate_linear_trend_observable(matrix)
        G_trend = compute_G_from_matrix(trend_obs)
        H_trend = compute_H_from_matrix(trend_obs)
        null_results['linear_trend'] = {'G': G_trend, 'H': H_trend}

        # Compute statistics
        null_G_values = [v['G'] for v in null_results.values()]
        null_H_values = [v['H'] for v in null_results.values()]

        print(f"  Null G range: [{min(null_G_values):.4f}, {max(null_G_values):.4f}]")
        print(f"  Null H range: [{min(null_H_values):.4f}, {max(null_H_values):.4f}]")

        # Determine if canonical metrics outperform null
        G_outperforms = G_canonical > max(null_G_values) or G_canonical < min(null_G_values)
        H_outperforms = H_canonical > max(null_H_values) or H_canonical < min(null_H_values)

        print(f"  G outperforms null: {G_outperforms}")
        print(f"  H outperforms null: {H_outperforms}")

        results[sys_name] = {
            'canonical': {'G': G_canonical, 'H': H_canonical},
            'null_observables': null_results,
            'null_G_range': [min(null_G_values), max(null_G_values)],
            'null_H_range': [min(null_H_values), max(null_H_values)],
            'G_outperforms_null': bool(G_outperforms),
            'H_outperforms_null': bool(H_outperforms),
        }

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
        'summary': {
            sys_name: {
                'G_outperforms_null': r['G_outperforms_null'],
                'H_outperforms_null': r['H_outperforms_null'],
            }
            for sys_name, r in results.items()
        },
    }

    outpath = os.path.join(os.path.dirname(__file__), 'null_observable_controls_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
