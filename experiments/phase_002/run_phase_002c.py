"""
Phase 002C — Transport Geometry Stress Test

Central target: H ≡ transport noncommutativity
Test: G ∝ 1/T vs G ∝ 1/H
"""

import sys
import os
import numpy as np
import json

sys.path.insert(0, '/home/student/SGI-Persistence/src')
sys.path.insert(0, '/home/student/SGI-Persistence/src/systems')
sys.path.insert(0, '/home/student/SGI-Persistence/src/systems/distributed')
sys.path.insert(0, '/home/student/SGI-Persistence/src/systems/immune')
sys.path.insert(0, '/home/student/SGI-Persistence/src/systems/ant_colony')
sys.path.insert(0, '/home/student/SGI-Persistence/src/systems/institution')

from geometry.connection_formalism import (
    OrganizationalState, HistoricalFiber, ConnectionOperator,
    build_bundle, state_to_vector
)
from geometry.discrete_transport import (
    DiscreteTransportAlgebra, TransportPerturbationSuite,
    TransportPhaseDiagram, DiscreteHolonomy,
    TransportCanonicalization, OrganizationalCategory
)


# ═══════════════════════════════════════════════════════════════════
# Simulation
# ═══════════════════════════════════════════════════════════════════

def simulate_system(system_name, n_steps=50, seed=42):
    """Run simulation and return trajectory."""
    if system_name == 'distributed':
        from study_001 import DistributedSystem
        system = DistributedSystem(n_nodes=100, seed=seed)
        system.generate_tasks(n_tasks=100)
    elif system_name == 'immune':
        from study_001c_immune import ImmuneSignalingNetwork
        system = ImmuneSignalingNetwork(n_cells=100, seed=seed)
    elif system_name == 'ant_colony':
        from study_001b_colony import AntColony
        system = AntColony(n_ants=50, n_food=100, seed=seed)
    elif system_name == 'institution':
        from study_001d_institution import InstitutionNetwork
        system = InstitutionNetwork(n_agents=100, seed=seed)
    else:
        raise ValueError(f"Unknown system: {system_name}")
    
    for _ in range(n_steps):
        system.step()
    
    return system.history


# ═══════════════════════════════════════════════════════════════════
# Analysis Functions
# ═══════════════════════════════════════════════════════════════════

def analyze_system_transport(system_name, trajectory, memory_depth=10):
    """Full transport analysis for a single system."""
    print(f"\n  Analyzing {system_name}...")
    
    # Build bundle
    states, fibers, connection = build_bundle(trajectory, memory_depth=memory_depth)
    
    # Build discrete transport algebra
    algebra = DiscreteTransportAlgebra(dimension=8)
    algebra.build_transports(states, fibers, connection)
    
    # 1. Transport instability T
    T_result = algebra.compute_transport_path_divergence(
        states, fibers, n_pairs=30, path_length=5
    )
    
    # 2. Discrete holonomy
    holonomy = DiscreteHolonomy(algebra)
    holo_spectrum = holonomy.compute_holonomy_spectrum(
        n_states=len(states), n_loops=30, loop_length=5
    )
    
    # 3. Transport error (from Phase 002B)
    transport_errors = []
    for i in range(len(states) - 1):
        te = connection.compute_transport_error(fibers[i], fibers[i+1])
        transport_errors.append(te)
    avg_transport_error = np.mean(transport_errors) if transport_errors else 0.0
    
    # 4. Fiber entanglement
    fiber_entanglements = [f.entanglement() for f in fibers]
    avg_fiber_entanglement = np.mean(fiber_entanglements)
    
    # 5. Noncommutativity (sample random path pairs)
    nc_results = []
    for _ in range(10):
        n = len(states)
        if n >= 8:
            idx1 = sorted(np.random.choice(n, 4, replace=False).tolist())
            idx2 = sorted(np.random.choice(n, 4, replace=False).tolist())
            nc = algebra.compute_noncommutativity(idx1, idx2)
            nc_results.append(nc)
    
    avg_nc = np.mean([r['relative_noncommutativity'] for r in nc_results]) if nc_results else 0.0
    max_nc = np.max([r['relative_noncommutativity'] for r in nc_results]) if nc_results else 0.0
    
    # 6. Replay divergence
    replay_div = TransportCanonicalization(algebra).compute_replay_divergence(
        states, fibers, n_trajectories=10
    )
    
    # 7. Category structure
    category = OrganizationalCategory()
    category.build_from_bundle(states, fibers, algebra)
    cat_summary = category.summary()
    
    return {
        'system': system_name,
        'n_states': len(states),
        # Transport instability
        'T': T_result['T'],
        'T_std': T_result.get('T_std', 0.0),
        # Discrete holonomy
        'mean_holonomy': holo_spectrum['mean_holonomy'],
        'std_holonomy': holo_spectrum['std_holonomy'],
        'max_holonomy': holo_spectrum['max_holonomy'],
        'mean_det': holo_spectrum['mean_det'],
        'mean_spectral_radius': holo_spectrum['mean_spectral_radius'],
        # Phase 002B metrics
        'transport_error': float(avg_transport_error),
        'fiber_entanglement': float(avg_fiber_entanglement),
        # Noncommutativity
        'avg_noncommutativity': float(avg_nc),
        'max_noncommutativity': float(max_nc),
        # Replay divergence
        'replay_divergence': replay_div['replay_divergence'],
        # Category
        'n_objects': cat_summary['n_objects'],
        'n_morphisms': cat_summary['n_morphisms'],
        'commutativity_fraction': cat_summary['commutativity_fraction'],
        'mean_commutator_norm': cat_summary['mean_commutator_norm'],
    }


def run_perturbation_stress_test(system_name, trajectory, n_perturbations=5):
    """Run perturbation stress test on a system."""
    print(f"\n  Stress testing {system_name}...")
    
    suite = TransportPerturbationSuite()
    results = []
    
    # Define perturbation families
    perturbations = [
        # Temporal
        ("async_replay_0.2", lambda t: suite.temporal_async_replay(t, 0.2)),
        ("memory_truncation_0.5", lambda t: suite.temporal_memory_truncation(t, 0.5)),
        ("replay_scramble_0.3", lambda t: suite.temporal_replay_scramble(t, 0.3)),
        # Structural
        ("node_deletion_0.2", lambda t: suite.structural_node_deletion(t, 0.2)),
        ("routing_mutation_0.3", lambda t: suite.structural_routing_mutation(t, 0.3)),
        ("topology_rewire_0.2", lambda t: suite.structural_topology_rewire(t, 0.2)),
        # Gauge
        ("basis_rotation", lambda t: suite.gauge_basis_rotation(t, 0.3)),
        ("nonlinear_normalize", lambda t: suite.gauge_nonlinear_normalize(t)),
        ("random_projection_0.3", lambda t: suite.gauge_random_projection(t, 0.3)),
        # Historical
        ("memory_overwrite_0.2", lambda t: suite.historical_memory_overwrite(t, 0.2)),
        ("residue_injection_0.1", lambda t: suite.historical_residue_injection(t, 0.1)),
        ("counterfactual_0.2", lambda t: suite.historical_counterfactual_replay(t, 0.2)),
    ]
    
    # Baseline
    baseline = analyze_system_transport(system_name, trajectory)
    results.append({'perturbation': 'baseline', **baseline})
    
    # Apply each perturbation
    for pname, perturb_fn in perturbations:
        try:
            perturbed_traj = perturb_fn(list(trajectory))
            obs = analyze_system_transport(system_name, perturbed_traj)
            
            # Compute stability: how much did T change?
            T_change = abs(obs['T'] - baseline['T']) / (baseline['T'] + 1e-10)
            TE_change = abs(obs['transport_error'] - baseline['transport_error']) / (baseline['transport_error'] + 1e-10)
            
            results.append({
                'perturbation': pname,
                'T': obs['T'],
                'T_change': float(T_change),
                'transport_error': obs['transport_error'],
                'TE_change': float(TE_change),
                'fiber_entanglement': obs['fiber_entanglement'],
                'noncommutativity': obs['avg_noncommutativity'],
            })
        except Exception as e:
            results.append({
                'perturbation': pname,
                'T': 0.0,
                'T_change': 1.0,
                'error': str(e),
            })
    
    return results


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def run_phase_002c():
    print("=" * 70)
    print("Phase 002C — Transport Geometry Stress Test")
    print("=" * 70)
    
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
    
    # ─── Simulate ───
    print("\n[Step 1] Simulating systems...")
    trajectories = {}
    for name in ['distributed', 'immune', 'ant_colony', 'institution']:
        try:
            trajectories[name] = simulate_system(name, n_steps=50, seed=42)
            print(f"  {name}: {len(trajectories[name])} steps")
        except Exception as e:
            print(f"  {name}: FAILED ({e})")
    
    # ─── Analyze Transport ───
    print("\n[Step 2] Computing transport observables...")
    transport_results = {}
    for name, traj in trajectories.items():
        transport_results[name] = analyze_system_transport(name, traj)
    
    # ─── Results Table ───
    print(f"\n{'=' * 70}")
    print("TRANSPORT OBSERVABLES")
    print(f"{'=' * 70}")
    
    header = f"  {'System':12s}  {'G':>5s}  {'H':>5s}  {'T':>8s}  {'TE':>8s}  {'FE':>8s}  {'NC':>8s}  {'holonomy':>9s}  {'replay_div':>11s}"
    print(f"\n{header}")
    print(f"  {'─' * 95}")
    
    for name in transport_results:
        r = transport_results[name]
        print(f"  {name:12s}  {KNOWN_G[name]:.3f}  {KNOWN_H[name]:.3f}  "
              f"{r['T']:.4f}  {r['transport_error']:.4f}  "
              f"{r['fiber_entanglement']:.4f}  {r['avg_noncommutativity']:.4f}  "
              f"{r['mean_holonomy']:.4f}  {r['replay_divergence']:.4f}")
    
    # ─── G ∝ 1/T vs G ∝ 1/H ───
    print(f"\n{'=' * 70}")
    print("CENTRAL TEST: G ∝ 1/T vs G ∝ 1/H")
    print(f"{'=' * 70}")
    
    systems_data = {}
    for name in transport_results:
        systems_data[name] = {
            'G': KNOWN_G[name],
            'H': KNOWN_H[name],
            'T': transport_results[name]['T'],
        }
    
    canonicalizer = TransportCanonicalization(DiscreteTransportAlgebra(8))
    comparison = canonicalizer.compare_G_T_vs_G_H(systems_data)
    
    print(f"\n  Corr(G, H)     = {comparison['corr_G_H']:+.3f}")
    print(f"  Corr(G, T)     = {comparison['corr_G_T']:+.3f}")
    print(f"  Corr(G, 1/H)   = {comparison['corr_G_invH']:+.3f}")
    print(f"  Corr(G, 1/T)   = {comparison['corr_G_invT']:+.3f}")
    print(f"\n  Better predictor of G: {comparison['better_predictor']}")
    
    if comparison['better_predictor'] == 'T':
        print(f"\n  → TRANSPORT INSTABILITY OUTPREDICTS HISTORICAL ENTANGLEMENT")
        print(f"  → H ≈ T hypothesis SUPPORTED")
    else:
        print(f"\n  → HISTORICAL ENTANGLEMENT REMAINS STRONGER")
        print(f"  → H ≡ T hypothesis NOT YET CONFIRMED")
    
    # ─── Noncommutativity Results ───
    print(f"\n{'=' * 70}")
    print("LOOP NONCOMMUTATIVITY")
    print(f"{'=' * 70}")
    
    for name in transport_results:
        r = transport_results[name]
        print(f"  {name:12s}: avg_nc={r['avg_noncommutativity']:.4f}  "
              f"max_nc={r['max_noncommutativity']:.4f}  "
              f"commutativity_frac={r['commutativity_fraction']:.3f}")
    
    # ─── Perturbation Stress Test ───
    print(f"\n{'=' * 70}")
    print("PERTURBATION STRESS TEST")
    print(f"{'=' * 70}")
    
    stress_results = {}
    for name, traj in trajectories.items():
        stress_results[name] = run_perturbation_stress_test(name, traj)
    
    # Print stress test summary
    for name in stress_results:
        print(f"\n  {name}:")
        for sr in stress_results[name]:
            if sr['perturbation'] == 'baseline':
                continue
            T_change = sr.get('T_change', 0)
            TE_change = sr.get('TE_change', 0)
            stability = "STABLE" if T_change < 0.5 and TE_change < 0.5 else "UNSTABLE"
            print(f"    {sr['perturbation']:30s}: T_change={T_change:.2f}  TE_change={TE_change:.2f}  → {stability}")
    
    # ─── Discrete Holonomy Summary ───
    print(f"\n{'=' * 70}")
    print("DISCRETE HOLONOMY SUMMARY")
    print(f"{'=' * 70}")
    
    for name in transport_results:
        r = transport_results[name]
        print(f"  {name:12s}: mean_holonomy={r['mean_holonomy']:.4f}  "
              f"det={r['mean_det']:.4f}  "
              f"spectral_radius={r['mean_spectral_radius']:.4f}")
    
    # ─── Category Structure ───
    print(f"\n{'=' * 70}")
    print("ORGANIZATIONAL CATEGORY STRUCTURE")
    print(f"{'=' * 70}")
    
    for name in transport_results:
        r = transport_results[name]
        print(f"  {name:12s}: objects={r['n_objects']}  morphisms={r['n_morphisms']}  "
              f"commutativity={r['commutativity_fraction']:.3f}  "
              f"mean_commutator={r['mean_commutator_norm']:.4f}")
    
    # ─── Save ───
    output = {
        'transport_results': transport_results,
        'known_G': KNOWN_G,
        'known_H': KNOWN_H,
        'G_T_comparison': comparison,
        'stress_results': stress_results,
    }
    
    with open('/home/student/SGI-Persistence/experiments/phase_002/phase_002c_results.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\nResults saved to phase_002c_results.json")
    print(f"{'=' * 70}")
    
    return output


if __name__ == '__main__':
    run_phase_002c()
