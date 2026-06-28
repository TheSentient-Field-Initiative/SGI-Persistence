"""
Phase 002A — Holonomy Experiment & Curvature Proxy

Test whether:
- immune systems exhibit lower organizational holonomy
- ant colonies accumulate larger replay defects
- curvature correlates with H and inversely with G
"""

import numpy as np
import json
import sys
import importlib

sys.path.insert(0, '/home/student/sgp_core_v2/post_omega_study_001')
sys.path.insert(0, '/home/student/sgp_core_v2/phase_002')

from organizational_bundle import (
    OrganizationalBundle, build_bundle_from_trajectory,
    compute_curvature_proxy, compute_replay_divergence,
    run_holonomy_experiment, state_to_vector
)


# ═══════════════════════════════════════════════════════════════════
# System Simulation
# ═══════════════════════════════════════════════════════════════════

def simulate_system(system_name, n_steps=50, seed=42):
    """Run a simulation and return the trajectory."""
    if system_name == 'distributed':
        from study_001 import DistributedSystem
        net = DistributedSystem(100, seed=seed)
        net.generate_tasks(100)
    elif system_name == 'ant_colony':
        spec = importlib.util.spec_from_file_location("colony",
            "/home/student/sgp_core_v2/post_omega_study_001/study_001b_colony.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        net = mod.AntColony(50, 100, seed=seed)
    elif system_name == 'institution':
        spec = importlib.util.spec_from_file_location("inst",
            "/home/student/sgp_core_v2/post_omega_study_001/study_001d_institution.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        net = mod.InstitutionNetwork(100, seed=seed)
    elif system_name == 'immune':
        from study_001c_immune import ImmuneSignalingNetwork
        net = ImmuneSignalingNetwork(100, seed=seed)
    else:
        raise ValueError(f"Unknown system: {system_name}")
    
    for _ in range(n_steps):
        net.step()
    
    return net.history


# ═══════════════════════════════════════════════════════════════════
# Bundle Construction & Experiment
# ═══════════════════════════════════════════════════════════════════

def build_and_test_bundle(system_name, n_steps=50, memory_depth=10):
    """Build a bundle and run geometric tests."""
    print(f"\n  Building bundle for {system_name}...")
    
    # Simulate
    trajectory = simulate_system(system_name, n_steps=n_steps)
    
    # Build bundle
    bundle = build_bundle_from_trajectory(
        trajectory, 
        name=system_name,
        memory_depth=memory_depth,
    )
    
    # Compute geometric measures
    curvature = compute_curvature_proxy(bundle, loop_length=4)
    replay_div = compute_replay_divergence(bundle, n_trajectories=5)
    holonomy_result = run_holonomy_experiment(bundle)
    
    # Additional measures
    fiber_entanglements = [f.entanglement() for f in bundle.fibers]
    avg_fiber_entanglement = np.mean(fiber_entanglements)
    max_fiber_entanglement = np.max(fiber_entanglements)
    
    # State manifold properties
    state_vectors = [s.vector for s in bundle.states]
    state_spread = np.mean([np.std(state_vectors, axis=0)])
    
    return {
        'curvature': curvature,
        'replay_divergence': replay_div,
        'holonomy': holonomy_result['holonomy'],
        'closure_error': holonomy_result['closure_error'],
        'fiber_entanglement': holonomy_result['fiber_entanglement'],
        'avg_fiber_entanglement': avg_fiber_entanglement,
        'max_fiber_entanglement': max_fiber_entanglement,
        'state_spread': state_spread,
        'n_states': len(bundle.states),
    }


# ═══════════════════════════════════════════════════════════════════
# Known Values
# ═══════════════════════════════════════════════════════════════════

KNOWN_G = {
    'distributed': 0.250,
    'ant_colony': 0.125,
    'institution': 0.250,
    'immune': 0.875,
}

KNOWN_H = {
    'distributed': 0.396,
    'ant_colony': 0.576,
    'institution': 0.497,
    'immune': 0.180,
}


# ═══════════════════════════════════════════════════════════════════
# Main Experiment
# ═══════════════════════════════════════════════════════════════════

def run_phase_002a():
    print("=" * 70)
    print("Phase 002A — Organizational Fiber Geometry")
    print("=" * 70)
    
    print("\n  Building organizational bundles...")
    print("  Testing: G ∝ 1/H has geometric meaning")
    
    systems = {}
    
    for name in ['distributed', 'ant_colony', 'institution', 'immune']:
        systems[name] = build_and_test_bundle(name, n_steps=50, memory_depth=10)
    
    # ─── Results Table ───
    print(f"\n{'=' * 70}")
    print("GEOMETRIC MEASURES")
    print(f"{'=' * 70}")
    
    print(f"\n  {'System':15s}  {'G':>5s}  {'H':>5s}  {'curv':>8s}  {'replay_div':>11s}  {'holonomy':>9s}  {'fiber_ent':>10s}  {'state_spread':>12s}")
    print(f"  {'─' * 85}")
    
    for name in systems:
        a = systems[name]
        G = KNOWN_G[name]
        H = KNOWN_H[name]
        print(f"  {name:15s}  {G:.3f}  {H:.3f}  {a['curvature']:.3f}  {a['replay_divergence']:.3f}  "
              f"{a['holonomy']:.3f}  {a['avg_fiber_entanglement']:.3f}  {a['state_spread']:.3f}")
    
    # ─── Correlation Analysis ───
    print(f"\n{'=' * 70}")
    print("CORRELATION: G vs Geometric Measures")
    print(f"{'=' * 70}")
    
    G_vals = np.array([KNOWN_G[name] for name in systems])
    H_vals = np.array([KNOWN_H[name] for name in systems])
    
    measures = {
        'curvature': np.array([systems[n]['curvature'] for n in systems]),
        'replay_divergence': np.array([systems[n]['replay_divergence'] for n in systems]),
        'holonomy': np.array([systems[n]['holonomy'] for n in systems]),
        'avg_fiber_entanglement': np.array([systems[n]['avg_fiber_entanglement'] for n in systems]),
        'state_spread': np.array([systems[n]['state_spread'] for n in systems]),
    }
    
    print(f"\n  {'Measure':25s}  {'Corr(G)':>10s}  {'Corr(H)':>10s}  {'Direction':>12s}")
    print(f"  {'─' * 65}")
    
    for name, vals in measures.items():
        if np.std(vals) > 1e-6 and np.std(G_vals) > 1e-6:
            corr_G = np.corrcoef(G_vals, vals)[0, 1]
            corr_H = np.corrcoef(H_vals, vals)[0, 1]
            direction = 'neg-G' if corr_G < 0 else 'pos-G'
            print(f"  {name:25s}  {corr_G:+.3f}  {corr_H:+.3f}  {direction:>12s}")
        else:
            print(f"  {name:25s}  {'N/A':>10s}  {'N/A':>10s}  {'N/A':>12s}")
    
    # ─── Central Anomaly Test ───
    print(f"\n{'=' * 70}")
    print("CENTRAL ANOMALY TEST")
    print(f"{'=' * 70}")
    
    print(f"\n  Do immune and distributed systems separate under geometry?")
    print(f"")
    
    for name in ['distributed', 'immune']:
        a = systems[name]
        G = KNOWN_G[name]
        print(f"  {name:15s}: G={G:.3f}, curvature={a['curvature']:.3f}, "
              f"holonomy={a['holonomy']:.3f}, fiber_ent={a['avg_fiber_entanglement']:.3f}")
    
    # ─── Success/Failure Assessment ───
    print(f"\n{'=' * 70}")
    print("SUCCESS/FAILURE ASSESSMENT")
    print(f"{'=' * 70}")
    
    # Check if geometric measures differentiate systems
    curvature_range = max(systems[n]['curvature'] for n in systems) - min(systems[n]['curvature'] for n in systems)
    holonomy_range = max(systems[n]['holonomy'] for n in systems) - min(systems[n]['holonomy'] for n in systems)
    
    print(f"\n  Curvature range: {curvature_range:.3f}")
    print(f"  Holonomy range: {holonomy_range:.3f}")
    
    if curvature_range > 0.01 or holonomy_range > 0.01:
        print(f"\n  → GEOMETRY DIFFERENTIATES SYSTEMS")
        print(f"  → Phase 002A succeeds on differentiation criterion")
    else:
        print(f"\n  → GEOMETRY DOES NOT DIFFERENTIATE SYSTEMS")
        print(f"  → Phase 002A fails on differentiation criterion")
    
    # Check if curvature correlates with H
    if 'curvature' in measures and np.std(measures['curvature']) > 1e-6:
        corr_curv_H = np.corrcoef(H_vals, measures['curvature'])[0, 1]
        print(f"\n  Corr(curvature, H) = {corr_curv_H:.3f}")
        if abs(corr_curv_H) > 0.5:
            print(f"  → CURVATURE CORRELATES WITH ENTANGLEMENT")
        else:
            print(f"  → CURVATURE DOES NOT CORRELATE WITH ENTANGLEMENT")
    
    # Save
    with open('/home/student/sgp_core_v2/phase_002/phase_002a_results.json', 'w') as f:
        json.dump({
            'systems': systems,
            'known_G': KNOWN_G,
            'known_H': KNOWN_H,
        }, f, indent=2, default=str)
    
    print(f"\nResults saved")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    run_phase_002a()
