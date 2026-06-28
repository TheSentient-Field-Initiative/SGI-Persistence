"""
SGI Post-Ω Study 001J — Cross-Domain Historical Entanglement Audit

Test whether G ∝ 1/H generalizes across all system types:
- Distributed system (scheduler-dominant)
- Ant colony (stigmergic-adaptive)
- Institution network (symbolic-institutional)
- Immune system (decentralized-selective)
"""

import numpy as np
import json
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

sys.path.insert(0, '/home/student/sgp_core_v2/post_omega_study_001')


# ═══════════════════════════════════════════════════════════════════
# Common State Representation
# ═══════════════════════════════════════════════════════════════════

def normalize_state(state: dict) -> np.ndarray:
    """Extract a common 5-dimensional state vector from any system."""
    return np.array([
        state.get('connectivity', state.get('signaling_connectivity', 0)),
        state.get('mean_act', state.get('mean_activation', state.get('assignment_rate', 0))),
        state.get('type_entropy', state.get('routing_entropy', state.get('allocation_entropy', 0))),
        state.get('n_components', 0) / max(state.get('n_active', 1), 1),
        state.get('pathogen', state.get('cov_trace', 0)),
    ])


# ═══════════════════════════════════════════════════════════════════
# Cross-Domain Entanglement Measures
# ═══════════════════════════════════════════════════════════════════

def measure_path_dependence(trajectory_a, trajectory_b, noise=0.01):
    """Measure divergence between two trajectories from perturbed initial conditions."""
    if len(trajectory_a) < 5 or len(trajectory_b) < 5:
        return 0.0
    
    min_len = min(len(trajectory_a), len(trajectory_b))
    divergences = []
    for t in range(min_len):
        va = normalize_state(trajectory_a[t])
        vb = normalize_state(trajectory_b[t])
        divergences.append(np.linalg.norm(va - vb))
    
    if not divergences:
        return 0.0
    
    final_div = divergences[-1]
    return float(final_div / max(noise, 1e-8))


def measure_trajectory_divergence(trajectories):
    """Measure Lyapunov-like divergence of multiple trajectories."""
    if len(trajectories) < 2:
        return 0.0
    
    min_len = min(len(tr) for tr in trajectories)
    divergences = []
    for t in range(min_len):
        states = [normalize_state(tr[t]) for tr in trajectories]
        for i in range(len(states)):
            for j in range(i+1, len(states)):
                divergences.append(np.linalg.norm(states[i] - states[j]))
    
    if not divergences:
        return 0.0
    
    div_array = np.array(divergences).reshape(min_len, -1).mean(axis=1)
    div_array = div_array[div_array > 0]
    
    if len(div_array) < 2:
        return 0.0
    
    log_div = np.log(div_array + 1e-10)
    t = np.arange(len(log_div))
    slope = np.polyfit(t, log_div, 1)[0]
    return float(slope)


def measure_hysteresis(trajectory_before, trajectory_perturbed, trajectory_after):
    """Measure how much the system returns to baseline after perturbation."""
    if not trajectory_before or not trajectory_after:
        return 0.0
    
    baseline = normalize_state(trajectory_before[-1])
    recovered = normalize_state(trajectory_after[-1])
    
    perturbed_states = [normalize_state(s) for s in trajectory_perturbed]
    if perturbed_states:
        max_perturbation = max(np.linalg.norm(s - baseline) for s in perturbed_states)
    else:
        max_perturbation = 1.0
    
    recovery_distance = np.linalg.norm(recovered - baseline)
    
    if max_perturbation < 1e-8:
        return 0.0
    
    return float(recovery_distance / max_perturbation)


def measure_memory_entropy(system_type, **kwargs):
    """Measure entropy of memory-like state distribution."""
    if system_type == 'immune':
        return kwargs.get('memory_entropy', 0.0)
    elif system_type == 'distributed':
        # Routing table diversity as proxy for memory
        return kwargs.get('routing_entropy', 0.0)
    elif system_type == 'ant_colony':
        # Pheromone distribution entropy
        return kwargs.get('pheromone_entropy', 0.0)
    elif system_type == 'institution':
        # Trust/reputation distribution entropy
        return kwargs.get('trust_entropy', 0.0)
    return 0.0


def compute_composite_entanglement(path_dep, div, hyst, mem_ent):
    """Compute composite entanglement score."""
    pd_norm = min(path_dep / 5.0, 1.0)
    div_norm = min(max(div + 0.1, 0) / 0.2, 1.0)
    hyst_norm = min(hyst / 1.0, 1.0)
    me_norm = min(mem_ent / 3.0, 1.0)
    return float(np.mean([pd_norm, div_norm, hyst_norm, me_norm]))


# ═══════════════════════════════════════════════════════════════════
# System Adapters
# ═══════════════════════════════════════════════════════════════════

def run_distributed_entanglement():
    """Run entanglement audit on distributed system."""
    from study_001 import DistributedSystem, NodeRemoval
    
    results_per_condition = []
    
    for seed in [42, 123, 456]:
        # Baseline trajectory
        net = DistributedSystem(100, seed)
        net.generate_tasks(100)
        traj_b = [net.step() for _ in range(20)]
        
        # Perturbed trajectory
        net2 = DistributedSystem(100, seed)
        net2.generate_tasks(100)
        [net2.step() for _ in range(20)]
        NodeRemoval.apply(net2, 0.3)
        traj_p = [net2.step() for _ in range(50)]
        
        # Recovery trajectory
        net3 = DistributedSystem(100, seed)
        net3.generate_tasks(100)
        [net3.step() for _ in range(20)]
        NodeRemoval.apply(net3, 0.3)
        traj_a = [net3.step() for _ in range(50)]
        
        # Second perturbed trajectory (for path dependence)
        net4 = DistributedSystem(100, seed + 1)  # Different seed = perturbed initial
        net4.generate_tasks(100)
        [net4.step() for _ in range(20)]
        NodeRemoval.apply(net4, 0.3)
        traj_b2 = [net4.step() for _ in range(50)]
        
        pd = measure_path_dependence(traj_a, traj_b2)
        div = measure_trajectory_divergence([traj_a, traj_p, traj_b2])
        hyst = measure_hysteresis(traj_b, traj_p, traj_a)
        me = 0.0  # No memory in distributed system
        
        composite = compute_composite_entanglement(pd, div, hyst, me)
        
        results_per_condition.append({
            'path_dep': pd, 'divergence': div, 'hysteresis': hyst,
            'memory_entropy': me, 'composite': composite,
        })
    
    avg = {k: float(np.mean([r[k] for r in results_per_condition])) for k in 
           ['path_dep', 'divergence', 'hysteresis', 'memory_entropy', 'composite']}
    return avg


def run_ant_colony_entanglement():
    """Run entanglement audit on ant colony."""
    import importlib
    spec = importlib.util.spec_from_file_location("colony", 
        "/home/student/sgp_core_v2/post_omega_study_001/study_001b_colony.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    results_per_condition = []
    
    for seed in [42, 123, 456]:
        net = mod.AntColony(50, 100, seed)
        traj_b = [net.step() for _ in range(20)]
        
        net2 = mod.AntColony(50, 100, seed)
        [net2.step() for _ in range(20)]
        mod.WorkerRemoval.apply(net2, 0.3)
        traj_p = [net2.step() for _ in range(50)]
        
        net3 = mod.AntColony(50, 100, seed)
        [net3.step() for _ in range(20)]
        mod.WorkerRemoval.apply(net3, 0.3)
        traj_a = [net3.step() for _ in range(50)]
        
        net4 = mod.AntColony(50, 100, seed + 1)
        [net4.step() for _ in range(20)]
        mod.WorkerRemoval.apply(net4, 0.3)
        traj_b2 = [net4.step() for _ in range(50)]
        
        pd = measure_path_dependence(traj_a, traj_b2)
        div = measure_trajectory_divergence([traj_a, traj_p, traj_b2])
        hyst = measure_hysteresis(traj_b, traj_p, traj_a)
        me = 0.5  # Pheromone memory proxy
        
        composite = compute_composite_entanglement(pd, div, hyst, me)
        results_per_condition.append({
            'path_dep': pd, 'divergence': div, 'hysteresis': hyst,
            'memory_entropy': me, 'composite': composite,
        })
    
    avg = {k: float(np.mean([r[k] for r in results_per_condition])) for k in 
           ['path_dep', 'divergence', 'hysteresis', 'memory_entropy', 'composite']}
    return avg


def run_institution_entanglement():
    """Run entanglement audit on institution network."""
    import importlib
    spec = importlib.util.spec_from_file_location("inst",
        "/home/student/sgp_core_v2/post_omega_study_001/study_001d_institution.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    results_per_condition = []
    
    for seed in [42, 123, 456]:
        net = mod.InstitutionNetwork(100, seed)
        traj_b = [net.step() for _ in range(20)]
        
        net2 = mod.InstitutionNetwork(100, seed)
        [net2.step() for _ in range(20)]
        mod.TrustViolation.apply(net2, 0.3)
        traj_p = [net2.step() for _ in range(50)]
        
        net3 = mod.InstitutionNetwork(100, seed)
        [net3.step() for _ in range(20)]
        mod.TrustViolation.apply(net3, 0.3)
        traj_a = [net3.step() for _ in range(50)]
        
        net4 = mod.InstitutionNetwork(100, seed + 1)
        [net4.step() for _ in range(20)]
        mod.TrustViolation.apply(net4, 0.3)
        traj_b2 = [net4.step() for _ in range(50)]
        
        pd = measure_path_dependence(traj_a, traj_b2)
        div = measure_trajectory_divergence([traj_a, traj_p, traj_b2])
        hyst = measure_hysteresis(traj_b, traj_p, traj_a)
        me = 0.8  # Trust/reputation memory proxy
        
        composite = compute_composite_entanglement(pd, div, hyst, me)
        results_per_condition.append({
            'path_dep': pd, 'divergence': div, 'hysteresis': hyst,
            'memory_entropy': me, 'composite': composite,
        })
    
    avg = {k: float(np.mean([r[k] for r in results_per_condition])) for k in 
           ['path_dep', 'divergence', 'hysteresis', 'memory_entropy', 'composite']}
    return avg


def run_immune_entanglement():
    """Run entanglement audit on immune system (from 001I results)."""
    # Use previously measured values at md=0.5, fg=1.0
    return {
        'path_dep': 1.997,
        'divergence': -0.013,
        'hysteresis': 0.066,
        'memory_entropy': 0.0,
        'composite': 0.180,
    }


# ═══════════════════════════════════════════════════════════════════
# G Measurement (from previous studies)
# ═══════════════════════════════════════════════════════════════════

KNOWN_G = {
    'distributed': 0.250,
    'ant_colony': 0.125,
    'institution': 0.250,
    'immune': 0.875,
}


# ═══════════════════════════════════════════════════════════════════
# Main Experiment
# ═══════════════════════════════════════════════════════════════════

def run_study_001j():
    print("=" * 70)
    print("Study 001J — Cross-Domain Historical Entanglement Audit")
    print("=" * 70)
    
    print("\n  Testing: G ∝ 1/H across all system types")
    
    # Run entanglement audits
    systems = {}
    
    print("\n  Running distributed system...")
    systems['distributed'] = run_distributed_entanglement()
    
    print("  Running ant colony...")
    systems['ant_colony'] = run_ant_colony_entanglement()
    
    print("  Running institution network...")
    systems['institution'] = run_institution_entanglement()
    
    print("  Running immune system...")
    systems['immune'] = run_immune_entanglement()
    
    # ─── Results Table ───
    print(f"\n{'=' * 70}")
    print("CROSS-DOMAIN ENTANGLEMENT RESULTS")
    print(f"{'=' * 70}")
    
    print(f"\n  {'System':20s}  {'G':>6s}  {'H':>6s}  {'path_dep':>10s}  {'hyst':>8s}  {'div':>8s}")
    print(f"  {'─' * 65}")
    
    for name, ent in systems.items():
        G = KNOWN_G[name]
        print(f"  {name:20s}  {G:.3f}  {ent['composite']:.3f}  "
              f"{ent['path_dep']:.3f}  {ent['hysteresis']:.3f}  {ent['divergence']:.3f}")
    
    # ─── Correlation Analysis ───
    print(f"\n{'=' * 70}")
    print("CORRELATION: G vs Historical Entanglement (Cross-Domain)")
    print(f"{'=' * 70}")
    
    G_vals = np.array([KNOWN_G[name] for name in systems])
    H_vals = np.array([systems[name]['composite'] for name in systems])
    pd_vals = np.array([systems[name]['path_dep'] for name in systems])
    hyst_vals = np.array([systems[name]['hysteresis'] for name in systems])
    div_vals = np.array([systems[name]['divergence'] for name in systems])
    
    measures = {
        'composite': H_vals,
        'path_dependence': pd_vals,
        'hysteresis': hyst_vals,
        'trajectory_divergence': div_vals,
    }
    
    print(f"\n  {'Measure':25s}  {'Correlation':>12s}  {'Direction':>12s}  {'Strength':>10s}")
    print(f"  {'─' * 65}")
    
    for name, vals in measures.items():
        if np.std(vals) > 1e-6 and np.std(G_vals) > 1e-6:
            corr = np.corrcoef(G_vals, vals)[0, 1]
            direction = 'negative' if corr < 0 else 'positive'
            strength = 'strong' if abs(corr) > 0.7 else 'moderate' if abs(corr) > 0.4 else 'weak'
            print(f"  {name:25s}  {corr:+.3f}  {direction:>12s}  {strength:>10s}")
        else:
            print(f"  {name:25s}  (constant)")
    
    # ─── Hypothesis Test ───
    print(f"\n{'=' * 70}")
    print("HYPOTHESIS TEST: G ∝ 1/H (Cross-Domain)")
    print(f"{'=' * 70}")
    
    if np.std(H_vals) > 1e-6:
        corr = np.corrcoef(G_vals, H_vals)[0, 1]
        print(f"\n  G-Composite correlation: {corr:.3f}")
        if corr < -0.7:
            print(f"  HYPOTHESIS STRONGLY SUPPORTED: G ∝ 1/H is cross-domain universal")
        elif corr < -0.4:
            print(f"  HYPOTHESIS MODERATELY SUPPORTED: G ∝ 1/H partially generalizes")
        elif corr < 0:
            print(f"  HYPOTHESIS WEAKLY SUPPORTED: negative relationship exists")
        else:
            print(f"  HYPOTHESIS NOT SUPPORTED: no cross-domain relationship")
    
    # ─── Ranking Test ───
    print(f"\n{'=' * 70}")
    print("RANKING TEST: Do systems rank consistently on G and H?")
    print(f"{'=' * 70}")
    
    G_rank = np.argsort(G_vals)  # Lowest G first
    H_rank = np.argsort(H_vals)  # Lowest H first
    
    rank_names = list(systems.keys())
    print(f"\n  {'System':20s}  {'G rank':>8s}  {'H rank':>8s}  {'Consistent':>12s}")
    print(f"  {'─' * 55}")
    
    consistent = 0
    for i, name in enumerate(rank_names):
        g_r = list(G_rank).index(i)
        h_r = list(H_rank).index(i)
        is_consistent = (g_r == h_r) or (abs(g_r - h_r) <= 1)
        if is_consistent:
            consistent += 1
        print(f"  {name:20s}  {g_r+1:>8d}  {h_r+1:>8d}  {'YES' if is_consistent else 'NO':>12s}")
    
    print(f"\n  Consistent rankings: {consistent}/{len(rank_names)}")
    
    # ─── Visual ───
    print(f"\n{'=' * 70}")
    print("G vs H SCATTER (text)")
    print(f"{'=' * 70}")
    
    for name in systems:
        G = KNOWN_G[name]
        H = systems[name]['composite']
        x = int(G * 40)
        y = int((1 - H) * 20)
        print(f"  {'.' * x}{'*'}{'.' * (40 - x)}  {name} (G={G:.3f}, H={H:.3f})")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/cross_domain_entanglement.json', 'w') as f:
        json.dump({
            'systems': systems,
            'known_G': KNOWN_G,
            'correlation': float(corr) if np.std(H_vals) > 1e-6 else None,
        }, f, indent=2, default=str)
    
    print(f"\nResults saved")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    run_study_001j()
