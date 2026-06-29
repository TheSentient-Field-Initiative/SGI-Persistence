#!/usr/bin/env python3
"""
Phase 003 Division 5 — Stability Envelope Study

Measure:
- Embedding perturbation tolerance
- Sector corruption tolerance
- Dimensional dropout tolerance
- Normalization sensitivity

Output:
- Stability regions
- Collapse thresholds
- Confidence maps
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


def compute_G_canonical(trajectory, sector_definition):
    """Compute G using canonical sector alignment."""
    if len(trajectory) < 10:
        return 0.0

    mid = len(trajectory) // 2
    before = trajectory[:mid]
    after = trajectory[mid:]

    surviving = 0
    total = len(sector_definition)

    for sector_name, metrics in sector_definition.items():
        bv = np.array([[bm.get(m, 0) for bm in before] for m in metrics]).T
        av = np.array([[am.get(m, 0) for am in after] for m in metrics]).T

        if bv.size == 0 or av.size == 0:
            continue

        ml = min(len(bv), len(av))
        bv, av = bv[:ml], av[:ml]

        def _cosine(a, b):
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            return float(np.dot(a.flatten(), b.flatten()) / (na * nb)) if na > 0 and nb > 0 else 0.0

        raw = _cosine(bv, av)
        bn = (bv - bv.mean(0)) / (bv.std(0) + 1e-8)
        an = (av - av.mean(0)) / (av.std(0) + 1e-8)
        norm = _cosine(bn, an)

        if (norm - raw) > -0.1:
            surviving += 1

    return surviving / total if total > 0 else 0.0


def perturb_trajectory(trajectory, noise_level, seed=42):
    """Add Gaussian noise to trajectory."""
    rng = np.random.RandomState(seed)
    perturbed = []
    for state in trajectory:
        new_state = {}
        for k, v in state.items():
            if isinstance(v, (int, float)):
                noise = rng.randn() * noise_level * abs(v)
                new_state[k] = v + noise
            else:
                new_state[k] = v
        perturbed.append(new_state)
    return perturbed


def corrupt_sectors(sector_definition, corruption_fraction, seed=42):
    """Randomly remove metrics from sectors."""
    rng = np.random.RandomState(seed)
    corrupted = {}
    for sector, metrics in sector_definition.items():
        n_remove = int(len(metrics) * corruption_fraction)
        if n_remove > 0:
            indices = rng.choice(len(metrics), size=n_remove, replace=False)
            remaining = [m for i, m in enumerate(metrics) if i not in indices]
        else:
            remaining = metrics
        if remaining:
            corrupted[sector] = remaining
    return corrupted


def dropout_dimensions(trajectory, dropout_fraction, seed=42):
    """Randomly zero out dimensions in trajectory."""
    rng = np.random.RandomState(seed)
    all_keys = set()
    for state in trajectory[:5]:
        all_keys.update(state.keys())
    all_keys.discard('timestep')
    all_keys.discard('cov_eigenvalues')

    keys = sorted(all_keys)
    n_drop = int(len(keys) * dropout_fraction)
    if n_drop > 0:
        drop_keys = set(rng.choice(keys, size=n_drop, replace=False))
    else:
        drop_keys = set()

    dropped = []
    for state in trajectory:
        new_state = {}
        for k, v in state.items():
            if k in drop_keys:
                new_state[k] = 0.0
            else:
                new_state[k] = v
        dropped.append(new_state)
    return dropped, list(drop_keys)


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003 Division 5 — Stability Envelope Study")
    print("=" * 60)

    # System configurations
    from study_001 import DistributedSystem
    from study_001c_immune import ImmuneSignalingNetwork
    from study_001b_colony import AntColony
    from study_001d_institution import InstitutionNetwork

    systems = {
        'distributed': {
            'class': DistributedSystem,
            'kwargs': {'n_nodes': 100, 'seed': 42},
            'sectors': {
                'amplitude': ['n_active', 'connectivity'],
                'topology': ['routing_entropy', 'n_components'],
            },
        },
        'immune': {
            'class': ImmuneSignalingNetwork,
            'kwargs': {'n_cells': 100, 'seed': 42},
            'sectors': {
                'amplitude': ['mean_activation', 'n_active'],
                'topology': ['signaling_connectivity', 'type_entropy'],
            },
        },
        'ant_colony': {
            'class': AntColony,
            'kwargs': {'n_ants': 50, 'n_food': 100, 'seed': 42},
            'sectors': {
                'amplitude': ['total_pheromone', 'recruitment_rate'],
                'topology': ['trail_connectivity', 'path_redundancy'],
            },
        },
        'institution': {
            'class': InstitutionNetwork,
            'kwargs': {'n_agents': 100, 'seed': 42},
            'sectors': {
                'amplitude': ['cooperation_rate', 'mean_trust'],
                'topology': ['network_connectivity', 'strategy_entropy'],
            },
        },
    }

    results = {}

    for sys_name, config in systems.items():
        print(f"\n--- {sys_name} ---")

        # Run baseline simulation
        traj = run_simulation(config['class'], **config['kwargs'])
        g_baseline = compute_G_canonical(traj, config['sectors'])
        print(f"  Baseline G = {g_baseline:.4f}")

        sys_results = {'baseline_G': g_baseline}

        # 1. Embedding perturbation tolerance
        print("  Testing embedding perturbation...")
        noise_levels = [0.01, 0.05, 0.1, 0.2, 0.5, 1.0]
        perturbation_results = []
        for noise in noise_levels:
            perturbed = perturb_trajectory(traj, noise)
            g_perturbed = compute_G_canonical(perturbed, config['sectors'])
            stable = abs(g_perturbed - g_baseline) < 0.01
            perturbation_results.append({
                'noise_level': noise,
                'G': g_perturbed,
                'delta_G': g_perturbed - g_baseline,
                'stable': stable,
            })
        sys_results['perturbation'] = perturbation_results

        # Find collapse threshold
        collapse_threshold = None
        for r in perturbation_results:
            if not r['stable']:
                collapse_threshold = r['noise_level']
                break
        sys_results['perturbation_collapse_threshold'] = collapse_threshold
        print(f"    Collapse threshold: {collapse_threshold}")

        # 2. Sector corruption tolerance
        print("  Testing sector corruption...")
        corruption_fractions = [0.0, 0.25, 0.5, 0.75, 1.0]
        corruption_results = []
        for frac in corruption_fractions:
            corrupted = corrupt_sectors(config['sectors'], frac)
            if corrupted:
                g_corrupted = compute_G_canonical(traj, corrupted)
                stable = abs(g_corrupted - g_baseline) < 0.01
            else:
                g_corrupted = 0.0
                stable = False
            corruption_results.append({
                'corruption_fraction': frac,
                'G': g_corrupted,
                'delta_G': g_corrupted - g_baseline,
                'stable': stable,
                'n_sectors_remaining': len(corrupted),
            })
        sys_results['corruption'] = corruption_results

        # Find corruption threshold
        corruption_threshold = None
        for r in corruption_results:
            if not r['stable']:
                corruption_threshold = r['corruption_fraction']
                break
        sys_results['corruption_collapse_threshold'] = corruption_threshold
        print(f"    Corruption threshold: {corruption_threshold}")

        # 3. Dimensional dropout tolerance
        print("  Testing dimensional dropout...")
        dropout_fractions = [0.0, 0.25, 0.5, 0.75]
        dropout_results = []
        for frac in dropout_fractions:
            dropped, drop_keys = dropout_dimensions(traj, frac)
            g_dropped = compute_G_canonical(dropped, config['sectors'])
            stable = abs(g_dropped - g_baseline) < 0.01
            dropout_results.append({
                'dropout_fraction': frac,
                'G': g_dropped,
                'delta_G': g_dropped - g_baseline,
                'stable': stable,
                'dropped_keys': drop_keys,
            })
        sys_results['dropout'] = dropout_results

        # Find dropout threshold
        dropout_threshold = None
        for r in dropout_results:
            if not r['stable']:
                dropout_threshold = r['dropout_fraction']
                break
        sys_results['dropout_collapse_threshold'] = dropout_threshold
        print(f"    Dropout threshold: {dropout_threshold}")

        results[sys_name] = sys_results

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
        'summary': {
            sys_name: {
                'perturbation_collapse': r.get('perturbation_collapse_threshold'),
                'corruption_collapse': r.get('corruption_collapse_threshold'),
                'dropout_collapse': r.get('dropout_collapse_threshold'),
            }
            for sys_name, r in results.items()
        },
    }

    outpath = os.path.join(os.path.dirname(__file__), 'stability_envelope_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
