#!/usr/bin/env python3
"""External review verification script.

Reproduce key findings and verify metric implementations.
"""

import json
import os
import sys
import time
import numpy as np

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


def main():
    print("=" * 60)
    print("SGI PERSISTENCE — EXTERNAL REVIEW VERIFICATION")
    print("=" * 60)

    results = {}

    # 1. Test distributed system
    print("\n[1/4] Testing distributed system...")
    from study_001 import DistributedSystem
    traj = run_simulation(DistributedSystem, n_nodes=100, seed=42)
    sectors = {
        'amplitude': ['n_active', 'connectivity'],
        'topology': ['routing_entropy', 'n_components'],
    }
    g = compute_G_canonical(traj, sectors)
    results['distributed_G'] = {'value': g, 'tolerance': 0.01}
    print(f"  G = {g:.4f}")

    # 2. Test immune system
    print("\n[2/4] Testing immune system...")
    from study_001c_immune import ImmuneSignalingNetwork
    traj = run_simulation(ImmuneSignalingNetwork, n_cells=100, seed=42)
    sectors = {
        'amplitude': ['mean_activation', 'n_active'],
        'topology': ['signaling_connectivity', 'type_entropy'],
    }
    g = compute_G_canonical(traj, sectors)
    results['immune_G'] = {'value': g, 'tolerance': 0.01}
    print(f"  G = {g:.4f}")

    # 3. Test ant colony
    print("\n[3/4] Testing ant colony...")
    from study_001b_colony import AntColony
    traj = run_simulation(AntColony, n_ants=50, n_food=100, seed=42)
    sectors = {
        'amplitude': ['total_pheromone', 'recruitment_rate'],
        'topology': ['trail_connectivity', 'path_redundancy'],
    }
    g = compute_G_canonical(traj, sectors)
    results['ant_colony_G'] = {'value': g, 'tolerance': 0.01}
    print(f"  G = {g:.4f}")

    # 4. Test institution
    print("\n[4/4] Testing institution...")
    from study_001d_institution import InstitutionNetwork
    traj = run_simulation(InstitutionNetwork, n_agents=100, seed=42)
    sectors = {
        'amplitude': ['cooperation_rate', 'mean_trust'],
        'topology': ['network_connectivity', 'strategy_entropy'],
    }
    g = compute_G_canonical(traj, sectors)
    results['institution_G'] = {'value': g, 'tolerance': 0.01}
    print(f"  G = {g:.4f}")

    # Save results
    out_path = os.path.join(os.path.dirname(__file__), 'verification_results.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {out_path}")
    print("\n=== Verification Complete ===")


if __name__ == "__main__":
    main()
