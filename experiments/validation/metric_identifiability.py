#!/usr/bin/env python3
"""
Phase 003C Division 1 — Metric Identifiability Analysis

Measure when G becomes non-identifiable, sector collapse boundaries,
embedding degeneracy regions, coordinate dominance transitions,
and metric ambiguity regions.

Output:
- Identifiability heatmaps
- Collapse phase diagrams
- Ambiguity tables
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


def compute_H_autocorrelation(trajectory, max_lag=5):
    """Compute H using autocorrelation."""
    if len(trajectory) < max_lag + 1:
        return 0.0

    all_keys = set()
    for state in trajectory[:5]:
        all_keys.update(state.keys())
    all_keys.discard('timestep')
    all_keys.discard('cov_eigenvalues')

    keys = sorted(all_keys)
    vectors = []
    for state in trajectory:
        v = [state.get(k, 0) for k in keys]
        vectors.append(v)

    vectors = np.array(vectors)
    if vectors.std() == 0:
        return 0.0

    autocorrs = []
    for lag in range(1, min(max_lag + 1, len(vectors))):
        if lag < len(vectors):
            a = vectors[:-lag]
            b = vectors[lag:]
            if a.size > 0 and b.size > 0:
                na, nb = np.linalg.norm(a), np.linalg.norm(b)
                if na > 0 and nb > 0:
                    corr = np.dot(a.flatten(), b.flatten()) / (na * nb)
                    autocorrs.append(abs(corr))

    return np.mean(autocorrs) if autocorrs else 0.0


def check_identifiability(G, H, threshold=0.01):
    """Check if G and H are identifiable."""
    G_identifiable = G > threshold and G < (1.0 - threshold)
    H_identifiable = H > threshold and H < (1.0 - threshold)
    return G_identifiable, H_identifiable


def check_sector_collapse(trajectory, sector_definition, threshold=0.1):
    """Check if sectors collapse to identical behavior."""
    if len(trajectory) < 10:
        return True

    mid = len(trajectory) // 2
    before = trajectory[:mid]
    after = trajectory[mid:]

    sector_vectors = []
    for sector_name, metrics in sector_definition.items():
        bv = np.array([[bm.get(m, 0) for bm in before] for m in metrics]).T
        av = np.array([[am.get(m, 0) for am in after] for m in metrics]).T
        if bv.size > 0 and av.size > 0:
            ml = min(len(bv), len(av))
            diff = np.abs(bv[:ml] - av[:ml]).mean()
            sector_vectors.append(diff)

    if len(sector_vectors) < 2:
        return True

    max_diff = max(sector_vectors)
    min_diff = min(sector_vectors)
    return (max_diff - min_diff) < threshold


def check_embedding_degeneracy(trajectory, threshold=0.9):
    """Check if embedding is degenerate (one dimension dominates)."""
    all_keys = set()
    for state in trajectory[:5]:
        all_keys.update(state.keys())
    all_keys.discard('timestep')
    all_keys.discard('cov_eigenvalues')

    keys = sorted(all_keys)
    vectors = []
    for state in trajectory:
        v = [state.get(k, 0) for k in keys]
        vectors.append(v)

    vectors = np.array(vectors)
    if vectors.std() == 0:
        return True, {}

    # Check coordinate dominance
    norms = np.abs(vectors).mean(axis=0)
    total_norm = norms.sum()
    if total_norm == 0:
        return True, {}

    dominance = norms / total_norm
    max_dominance = dominance.max()

    return max_dominance > threshold, {k: float(d) for k, d in zip(keys, dominance)}


def compute_metric_ambiguity(G_values, H_values):
    """Compute metric ambiguity (how much G/H vary across conditions)."""
    G_range = max(G_values) - min(G_values) if G_values else 0
    H_range = max(H_values) - min(H_values) if H_values else 0
    return G_range, H_range


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003C Division 1 — Metric Identifiability Analysis")
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
        G = compute_G_canonical(traj, config['sectors'])
        H = compute_H_autocorrelation(traj)

        print(f"  G = {G:.4f}, H = {H:.4f}")

        # Check identifiability
        G_ident, H_ident = check_identifiability(G, H)
        print(f"  G identifiable: {G_ident}, H identifiable: {H_ident}")

        # Check sector collapse
        sector_collapsed = check_sector_collapse(traj, config['sectors'])
        print(f"  Sector collapsed: {sector_collapsed}")

        # Check embedding degeneracy
        degenerate, dominance = check_embedding_degeneracy(traj)
        print(f"  Embedding degenerate: {degenerate}")

        # Compute ambiguity across multiple runs
        G_values = []
        H_values = []
        for seed in range(10):
            try:
                if sys_name == 'distributed':
                    t = run_simulation(DistributedSystem, n_nodes=100, seed=seed)
                elif sys_name == 'immune':
                    t = run_simulation(ImmuneSignalingNetwork, n_cells=100, seed=seed)
                elif sys_name == 'ant_colony':
                    t = run_simulation(AntColony, n_ants=50, n_food=100, seed=seed)
                elif sys_name == 'institution':
                    t = run_simulation(InstitutionNetwork, n_agents=100, seed=seed)

                g = compute_G_canonical(t, config['sectors'])
                h = compute_H_autocorrelation(t)
                G_values.append(g)
                H_values.append(h)
            except Exception as e:
                print(f"  Warning: seed {seed} failed: {e}")

        G_range, H_range = compute_metric_ambiguity(G_values, H_values)
        print(f"  G range: {G_range:.4f}, H range: {H_range:.4f}")

        results[sys_name] = {
            'G': G,
            'H': H,
            'G_identifiable': G_ident,
            'H_identifiable': H_ident,
            'sector_collapsed': sector_collapsed,
            'embedding_degenerate': degenerate,
            'dominance': dominance,
            'G_values': G_values,
            'H_values': H_values,
            'G_range': G_range,
            'H_range': H_range,
        }

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
        'summary': {
            sys_name: {
                'G_identifiable': r['G_identifiable'],
                'H_identifiable': r['H_identifiable'],
                'sector_collapsed': r['sector_collapsed'],
                'embedding_degenerate': r['embedding_degenerate'],
                'G_range': r['G_range'],
                'H_range': r['H_range'],
            }
            for sys_name, r in results.items()
        },
    }

    outpath = os.path.join(os.path.dirname(__file__), 'metric_identifiability_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
