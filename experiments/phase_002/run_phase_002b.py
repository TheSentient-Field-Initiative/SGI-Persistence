"""
Phase 002B — Validation: Organizational Connection Formalism

Test whether true geometric observables (holonomy, curvature, fiber twist)
separate systems that scalar metrics collapsed.
"""

import sys
import os
import numpy as np
import json

# Add source paths
sys.path.insert(0, '/home/student/SGI-Persistence/src')
sys.path.insert(0, '/home/student/SGI-Persistence/src/systems')
sys.path.insert(0, '/home/student/SGI-Persistence/src/systems/distributed')
sys.path.insert(0, '/home/student/SGI-Persistence/src/systems/immune')
sys.path.insert(0, '/home/student/SGI-Persistence/src/systems/ant_colony')
sys.path.insert(0, '/home/student/SGI-Persistence/src/systems/institution')

from geometry.connection_formalism import (
    OrganizationalState, HistoricalFiber, ConnectionOperator,
    CurvatureTensor, HolonomySpectrum, FiberTwist,
    RepresentationCovarianceTest, build_bundle, state_to_vector
)


# ═══════════════════════════════════════════════════════════════════
# Simulation Wrappers
# ═══════════════════════════════════════════════════════════════════

def simulate_distributed(n_steps=50, seed=42):
    """Run distributed system simulation."""
    from study_001 import DistributedSystem
    system = DistributedSystem(n_nodes=100, seed=seed)
    system.generate_tasks(n_tasks=100)
    for _ in range(n_steps):
        system.step()
    return system.history


def simulate_immune(n_steps=50, seed=42):
    """Run immune system simulation."""
    from study_001c_immune import ImmuneSignalingNetwork
    network = ImmuneSignalingNetwork(n_cells=100, seed=seed)
    for _ in range(n_steps):
        network.step()
    return network.history


def simulate_ant_colony(n_steps=50, seed=42):
    """Run ant colony simulation."""
    from study_001b_colony import AntColony
    colony = AntColony(n_ants=50, n_food=100, seed=seed)
    for _ in range(n_steps):
        colony.step()
    return colony.history


def simulate_institution(n_steps=50, seed=42):
    """Run institution simulation."""
    from study_001d_institution import InstitutionNetwork
    inst = InstitutionNetwork(n_agents=100, seed=seed)
    for _ in range(n_steps):
        inst.step()
    return inst.history


# ═══════════════════════════════════════════════════════════════════
# Bundle Analysis
# ═══════════════════════════════════════════════════════════════════

def analyze_bundle(system_name, trajectory, memory_depth=10):
    """Build bundle and compute all geometric observables."""
    print(f"\n  Analyzing {system_name}...")
    
    # Build bundle
    states, fibers, connection = build_bundle(trajectory, memory_depth=memory_depth)
    
    # Compute connection coefficients
    manifold_points = [s.vector for s in states]
    connection.compute_connection_coefficients(manifold_points)
    
    # ─── Curvature ───
    curvature = CurvatureTensor(connection)
    if len(states) > 0:
        curvature.compute_curvature(states[0].vector, [np.eye(connection.dimension)])
    curv_mag = curvature.curvature_magnitude()
    ricci = curvature.ricci_scalar()
    
    # ─── Holonomy Spectrum ───
    holonomy = HolonomySpectrum(connection)
    spectrum = holonomy.compute_spectrum(states, fibers, n_loops=50, loop_length=4)
    
    # ─── Fiber Twist ───
    twist = FiberTwist(connection)
    torsions = [twist.compute_fiber_torsion(f) for f in fibers]
    phase_drift = twist.compute_replay_phase_drift(fibers)
    winding = twist.compute_winding_number(fibers)
    
    # ─── State manifold spread ───
    state_vectors = [s.vector for s in states]
    state_spread = float(np.mean(np.std(state_vectors, axis=0)))
    
    # ─── Fiber entanglement ───
    fiber_entanglements = [f.entanglement() for f in fibers]
    avg_fiber_entanglement = np.mean(fiber_entanglements)
    max_fiber_entanglement = np.max(fiber_entanglements)
    
    # ─── Transport inconsistency ───
    transport_errors = []
    for i in range(len(states) - 1):
        error = connection.compute_transport_error(fibers[i], fibers[i+1])
        transport_errors.append(error)
    avg_transport_error = np.mean(transport_errors) if transport_errors else 0.0
    
    return {
        'system': system_name,
        'n_states': len(states),
        'state_spread': state_spread,
        # Curvature
        'curvature_magnitude': curv_mag,
        'ricci_scalar': ricci,
        # Holonomy
        'mean_holonomy': spectrum['mean_holonomy'],
        'std_holonomy': spectrum['std_holonomy'],
        'max_holonomy': spectrum['max_holonomy'],
        'loop_instability': spectrum['loop_instability'],
        # Fiber twist
        'mean_torsion': float(np.mean(torsions)),
        'max_torsion': float(np.max(torsions)),
        'phase_drift': phase_drift,
        'winding_number': winding,
        # Fiber entanglement
        'avg_fiber_entanglement': float(avg_fiber_entanglement),
        'max_fiber_entanglement': float(max_fiber_entanglement),
        # Transport
        'avg_transport_error': float(avg_transport_error),
    }


# ═══════════════════════════════════════════════════════════════════
# Main Validation
# ═══════════════════════════════════════════════════════════════════

def run_validation():
    print("=" * 70)
    print("Phase 002B — Organizational Connection Formalism Validation")
    print("=" * 70)
    
    # ─── Known values from Phase 001 ───
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
    
    # ─── Simulate all systems ───
    print("\n[Step 1] Simulating systems...")
    
    trajectories = {}
    
    print("\n  Distributed system...")
    try:
        trajectories['distributed'] = simulate_distributed(n_steps=50, seed=42)
        print(f"    OK: {len(trajectories['distributed'])} steps")
    except Exception as e:
        print(f"    FAILED: {e}")
    
    print("\n  Immune system...")
    try:
        trajectories['immune'] = simulate_immune(n_steps=50, seed=42)
        print(f"    OK: {len(trajectories['immune'])} steps")
    except Exception as e:
        print(f"    FAILED: {e}")
    
    print("\n  Ant colony...")
    try:
        trajectories['ant_colony'] = simulate_ant_colony(n_steps=50, seed=42)
        print(f"    OK: {len(trajectories['ant_colony'])} steps")
    except Exception as e:
        print(f"    FAILED: {e}")
    
    print("\n  Institution...")
    try:
        trajectories['institution'] = simulate_institution(n_steps=50, seed=42)
        print(f"    OK: {len(trajectories['institution'])} steps")
    except Exception as e:
        print(f"    FAILED: {e}")
    
    # ─── Analyze bundles ───
    print("\n[Step 2] Building organizational bundles...")
    
    results = {}
    for name, traj in trajectories.items():
        results[name] = analyze_bundle(name, traj, memory_depth=10)
    
    # ─── Results Table ───
    print(f"\n{'=' * 70}")
    print("GEOMETRIC OBSERVABLES")
    print(f"{'=' * 70}")
    
    header = f"  {'System':15s}  {'G':>5s}  {'H':>5s}  {'curv':>8s}  {'holonomy':>9s}  {'instab':>7s}  {'torsion':>8s}  {'wind':>6s}  {'fiber_e':>8s}  {'trans_e':>8s}"
    print(f"\n{header}")
    print(f"  {'─' * 95}")
    
    for name in results:
        r = results[name]
        G = KNOWN_G[name]
        H = KNOWN_H[name]
        print(f"  {name:15s}  {G:.3f}  {H:.3f}  {r['curvature_magnitude']:.3f}  "
              f"{r['mean_holonomy']:.3f}  {r['loop_instability']:.3f}  "
              f"{r['mean_torsion']:.3f}  {r['winding_number']:+.2f}  "
              f"{r['avg_fiber_entanglement']:.3f}  {r['avg_transport_error']:.3f}")
    
    # ─── Correlation Analysis ───
    print(f"\n{'=' * 70}")
    print("CORRELATION: G vs Geometric Observables")
    print(f"{'=' * 70}")
    
    G_vals = np.array([KNOWN_G[name] for name in results])
    H_vals = np.array([KNOWN_H[name] for name in results])
    
    measures = {
        'curvature_magnitude': np.array([results[n]['curvature_magnitude'] for n in results]),
        'mean_holonomy': np.array([results[n]['mean_holonomy'] for n in results]),
        'loop_instability': np.array([results[n]['loop_instability'] for n in results]),
        'mean_torsion': np.array([results[n]['mean_torsion'] for n in results]),
        'winding_number': np.array([results[n]['winding_number'] for n in results]),
        'avg_fiber_entanglement': np.array([results[n]['avg_fiber_entanglement'] for n in results]),
        'avg_transport_error': np.array([results[n]['avg_transport_error'] for n in results]),
        'state_spread': np.array([results[n]['state_spread'] for n in results]),
    }
    
    print(f"\n  {'Observable':25s}  {'Corr(G)':>10s}  {'Corr(H)':>10s}  {'Separates?':>12s}")
    print(f"  {'─' * 65}")
    
    separation_scores = {}
    for name, vals in measures.items():
        if np.std(vals) > 1e-6 and np.std(G_vals) > 1e-6:
            corr_G = np.corrcoef(G_vals, vals)[0, 1]
            corr_H = np.corrcoef(H_vals, vals)[0, 1]
            # Separation: range of normalized values
            vals_norm = (vals - np.min(vals)) / (np.max(vals) - np.min(vals) + 1e-10)
            separation = float(np.max(vals_norm) - np.min(vals_norm))
            separation_scores[name] = separation
            separates = "YES" if separation > 0.1 else "NO"
            print(f"  {name:25s}  {corr_G:+.3f}  {corr_H:+.3f}  {separates:>12s}")
        else:
            print(f"  {name:25s}  {'N/A':>10s}  {'N/A':>10s}  {'N/A':>12s}")
    
    # ─── Central Anomaly Test ───
    print(f"\n{'=' * 70}")
    print("CENTRAL ANOMALY: Immune vs Distributed Separation")
    print(f"{'=' * 70}")
    
    if 'distributed' in results and 'immune' in results:
        d = results['distributed']
        im = results['immune']
        
        print(f"\n  {'Observable':25s}  {'Distributed':>12s}  {'Immune':>12s}  {'Ratio':>10s}")
        print(f"  {'─' * 65}")
        
        for obs in ['curvature_magnitude', 'mean_holonomy', 'loop_instability',
                    'mean_torsion', 'winding_number', 'avg_fiber_entanglement',
                    'avg_transport_error']:
            dv = d[obs]
            iv = im[obs]
            ratio = iv / (dv + 1e-10)
            print(f"  {obs:25s}  {dv:12.4f}  {iv:12.4f}  {ratio:10.2f}x")
    
    # ─── Representation Covariance Test ───
    print(f"\n{'=' * 70}")
    print("REPRESENTATION COVARIANCE TEST")
    print(f"{'=' * 70}")
    
    cov_test = RepresentationCovarianceTest()
    
    # Test on immune system (highest G)
    if 'immune' in trajectories:
        print("\n  Testing immune system under gauge transformations...")
        
        states, fibers, connection = build_bundle(trajectories['immune'], memory_depth=10)
        connection.compute_connection_coefficients([s.vector for s in states])
        
        cov_results = cov_test.test_covariance(states, fibers, connection)
        
        print(f"\n  {'Gauge':15s}  {'curv_inv':>10s}  {'holo_inv':>10s}  {'tors_inv':>10s}  {'inv_score':>10s}")
        print(f"  {'─' * 60}")
        
        for gauge_name, gauge_data in cov_results.items():
            if gauge_name == 'original':
                continue
            inv = gauge_data.get('invariance', {})
            inv_scores = [v for v in inv.values() if isinstance(v, (int, float))]
            avg_inv = np.mean(inv_scores) if inv_scores else 0.0
            
            curv_inv = inv.get('curvature_magnitude', 0)
            holo_inv = inv.get('mean_holonomy', 0)
            tors_inv = inv.get('mean_torsion', 0)
            
            print(f"  {gauge_name:15s}  {curv_inv:10.4f}  {holo_inv:10.4f}  {tors_inv:10.4f}  {avg_inv:10.4f}")
    
    # ─── Phase 002A Comparison ───
    print(f"\n{'=' * 70}")
    print("COMPARISON: Phase 002A vs Phase 002B")
    print(f"{'=' * 70}")
    
    # Phase 002A results (from prior run)
    phase_002a = {
        'distributed': {'curvature': 0.102, 'holonomy': 0.361, 'fiber_entanglement': 0.157},
        'ant_colony': {'curvature': 0.112, 'holonomy': 0.333, 'fiber_entanglement': 0.163},
        'institution': {'curvature': 0.108, 'holonomy': 0.352, 'fiber_entanglement': 0.159},
        'immune': {'curvature': 0.118, 'holonomy': 0.320, 'fiber_entanglement': 0.165},
    }
    
    print(f"\n  Phase 002A (scalar proxies):")
    print(f"  {'System':15s}  {'curv':>8s}  {'holonomy':>9s}  {'fiber_e':>8s}")
    for name in phase_002a:
        p = phase_002a[name]
        print(f"  {name:15s}  {p['curvature']:.3f}  {p['holonomy']:.3f}  {p['fiber_entanglement']:.3f}")
    
    print(f"\n  Phase 002B (true connection formalism):")
    print(f"  {'System':15s}  {'curv':>8s}  {'holonomy':>9s}  {'fiber_e':>8s}")
    for name in results:
        r = results[name]
        print(f"  {name:15s}  {r['curvature_magnitude']:.3f}  {r['mean_holonomy']:.3f}  {r['avg_fiber_entanglement']:.3f}")
    
    # ─── Separation Improvement ───
    print(f"\n  SEPARATION IMPROVEMENT:")
    
    for metric_key, phase_002a_key in [('curvature_magnitude', 'curvature'), 
                                        ('mean_holonomy', 'holonomy'),
                                        ('avg_fiber_entanglement', 'fiber_entanglement')]:
        a_vals = np.array([phase_002a[n][phase_002a_key] for n in phase_002a])
        b_vals = np.array([results[n][metric_key] for n in results])
        
        a_range = np.max(a_vals) - np.min(a_vals)
        b_range = np.max(b_vals) - np.min(b_vals)
        
        improvement = b_range / (a_range + 1e-10)
        print(f"  {metric_key:25s}: range {a_range:.4f} → {b_range:.4f} ({improvement:.2f}x)")
    
    # ─── Success/Failure Assessment ───
    print(f"\n{'=' * 70}")
    print("SUCCESS/FAILURE ASSESSMENT")
    print(f"{'=' * 70}")
    
    # Check if new observables separate systems
    best_separation = max(separation_scores.values()) if separation_scores else 0
    bestObservable = max(separation_scores, key=separation_scores.get) if separation_scores else "none"
    
    print(f"\n  Best separation: {bestObservable} = {best_separation:.3f}")
    
    # Check immune vs distributed separation
    if 'distributed' in results and 'immune' in results:
        d_holo = results['distributed']['mean_holonomy']
        i_holo = results['immune']['mean_holonomy']
        holo_ratio = i_holo / (d_holo + 1e-10)
        
        print(f"  Immune/Distributed holonomy ratio: {holo_ratio:.2f}x")
        
        if abs(holo_ratio - 1.0) > 0.1:
            print(f"\n  → GEOMETRY SEPARATES IMMUNE FROM DISTRIBUTED")
            print(f"  → Phase 002B SUCCEEDS on central anomaly")
        else:
            print(f"\n  → GEOMETRY DOES NOT SEPARATE IMMUNE FROM DISTRIBUTED")
            print(f"  → Phase 002B FAILS on central anomaly")
    
    # Overall verdict
    n_separated = sum(1 for s in separation_scores.values() if s > 0.1)
    total_measures = len(separation_scores)
    
    print(f"\n  Measures that separate systems: {n_separated}/{total_measures}")
    
    if n_separated >= total_measures * 0.5:
        print(f"\n  → OVERALL: Phase 002B SUCCEEDS")
        print(f"  → True geometric observables reveal structure hidden from scalar proxies")
    else:
        print(f"\n  → OVERALL: Phase 002B PARTIALLY SUCCEEDS")
        print(f"  → Some geometric observables separate, others don't")
    
    # ─── Save Results ───
    output = {
        'results': results,
        'known_G': KNOWN_G,
        'known_H': KNOWN_H,
        'separation_scores': separation_scores,
        'phase_002a_comparison': phase_002a,
    }
    
    with open('/home/student/SGI-Persistence/experiments/phase_002/phase_002b_results.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\nResults saved to phase_002b_results.json")
    print(f"{'=' * 70}")
    
    return output


if __name__ == '__main__':
    run_validation()
