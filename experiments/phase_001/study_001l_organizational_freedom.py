"""
SGI Post-Ω Study 001L — Organizational Freedom Audit

Test whether high G = organizational freedom (broad state repertoire, 
reversible transitions) rather than organizational rigidity.

Measures:
- Reachable-state volume
- Transition reversibility graph
- Basin transition entropy
- Organizational branching factor
- State-space accessibility
- Canalization depth
"""

import numpy as np
import json
import sys
from collections import defaultdict

sys.path.insert(0, '/home/student/sgp_core_v2/post_omega_study_001')


# ═══════════════════════════════════════════════════════════════════
# State Encoding
# ═══════════════════════════════════════════════════════════════════

def encode_state(state: dict, n_bins: int = 8) -> str:
    """Discretize state into a symbolic string."""
    if not state:
        return '0' * 4
    
    vals = []
    for key in ['connectivity', 'mean_act', 'type_entropy', 'n_components', 'pathogen',
                'routing_entropy', 'n_active', 'assignment_rate', 'allocation_entropy',
                'efficiency', 'total_pheromone', 'coverage', 'n_institutions', 'avg_trust',
                'n_naive', 'n_memory', 'n_active_cells', 'pathogen_load']:
        v = state.get(key, 0)
        if isinstance(v, (int, float)):
            vals.append(float(v))
    
    if not vals:
        vals = [0.0] * 4
    
    vals = np.array(vals[:4], dtype=float)
    max_vals = np.maximum(np.abs(vals), 1.0)
    vals = vals / max_vals
    vals = np.clip(vals, 0, 1)
    
    bins = np.linspace(0, 1, n_bins + 1)
    symbols = []
    for v in vals:
        sym = int(np.digitize(v, bins[1:-1]))
        symbols.append(str(sym))
    
    return ''.join(symbols)


def build_transition_graph(trajectories):
    """Build a directed transition graph from trajectories."""
    transitions = defaultdict(lambda: defaultdict(int))
    
    for traj in trajectories:
        for i in range(len(traj) - 1):
            s1 = encode_state(traj[i])
            s2 = encode_state(traj[i + 1])
            transitions[s1][s2] += 1
    
    return transitions


# ═══════════════════════════════════════════════════════════════════
# Freedom Measures
# ═══════════════════════════════════════════════════════════════════

def measure_reachable_states(trajectories):
    """Count distinct states visited across all trajectories."""
    states = set()
    for traj in trajectories:
        for s in traj:
            states.add(encode_state(s))
    return len(states)


def measure_transition_entropy(transitions):
    """Average entropy of transition distributions from each state."""
    entropies = []
    for source, targets in transitions.items():
        if not targets:
            continue
        total = sum(targets.values())
        probs = [c / total for c in targets.values()]
        H = -sum(p * np.log2(p + 1e-10) for p in probs)
        entropies.append(H)
    
    return np.mean(entropies) if entropies else 0.0


def measure_reversibility(transitions):
    """Fraction of transitions that have a reverse transition."""
    if not transitions:
        return 0.0
    
    reversible = 0
    total = 0
    
    for source, targets in transitions.items():
        for target in targets:
            total += 1
            if target in transitions and source in transitions[target]:
                reversible += 1
    
    return reversible / max(total, 1)


def measure_branching_factor(transitions):
    """Average number of distinct next states from each state."""
    if not transitions:
        return 0.0
    
    branchings = [len(targets) for targets in transitions.values()]
    return np.mean(branchings) if branchings else 0.0


def measure_accessibility(trajectories, n_bins=8):
    """Fraction of possible states that are actually reachable."""
    reachable = measure_reachable_states(trajectories)
    total_possible = n_bins ** 4  # 4 state dimensions
    return reachable / total_possible


def measure_canalization_depth(trajectories, convergence_threshold=3):
    """Steps until trajectory converges to a fixed state (low variance)."""
    depths = []
    
    for traj in trajectories:
        if len(traj) < 5:
            depths.append(len(traj))
            continue
        
        # Check when trajectory becomes stable
        for i in range(len(traj) - 5):
            recent = traj[i:i+5]
            # Encode each state
            encoded = [encode_state(s) for s in recent]
            # Check if all same (converged)
            if len(set(encoded)) == 1:
                depths.append(i)
                break
        else:
            depths.append(len(traj))  # Never converged
    
    return np.mean(depths) if depths else 0.0


def measure_state_space_volume(trajectories):
    """Estimate volume of state space covered by trajectories."""
    # Collect all state values
    all_vals = []
    for traj in trajectories:
        for s in traj:
            vals = []
            for key in ['connectivity', 'mean_act', 'type_entropy', 'n_components']:
                v = s.get(key, 0)
                if isinstance(v, (int, float)):
                    vals.append(float(v))
            if vals:
                all_vals.append(vals)
    
    if not all_vals:
        return 0.0
    
    arr = np.array(all_vals)
    # Normalize to [0, 1]
    mins = arr.min(axis=0)
    maxs = arr.max(axis=0)
    ranges = maxs - mins
    ranges[ranges == 0] = 1.0
    
    # Volume = product of ranges
    volume = np.prod(ranges)
    return float(volume)


# ═══════════════════════════════════════════════════════════════════
# System Adapters
# ═══════════════════════════════════════════════════════════════════

def run_system(system_name, net_class, net_args, n_seeds=15, n_steps=30):
    """Run a system from multiple initial conditions and collect trajectories."""
    trajectories = []
    
    for seed in range(n_seeds):
        net = net_class(*net_args, seed=seed * 7 + 3)
        
        # Some systems need task generation
        if hasattr(net, 'generate_tasks'):
            net.generate_tasks(100)
        
        for _ in range(n_steps):
            net.step()
        
        trajectories.append(net.history)
    
    return trajectories


def analyze_system(system_name, trajectories):
    """Compute all freedom measures for a system."""
    transitions = build_transition_graph(trajectories)
    
    reachable = measure_reachable_states(trajectories)
    trans_entropy = measure_transition_entropy(transitions)
    reversibility = measure_reversibility(transitions)
    branching = measure_branching_factor(transitions)
    accessibility = measure_accessibility(trajectories)
    canalization = measure_canalization_depth(trajectories)
    volume = measure_state_space_volume(trajectories)
    
    return {
        'reachable_states': reachable,
        'transition_entropy': trans_entropy,
        'reversibility': reversibility,
        'branching_factor': branching,
        'accessibility': accessibility,
        'canalization_depth': canalization,
        'state_space_volume': volume,
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

def run_study_001l():
    print("=" * 70)
    print("Study 001L — Organizational Freedom Audit")
    print("=" * 70)
    
    print("\n  Testing: high G = organizational freedom")
    print("  vs. low G = historical canalization")
    
    systems = {}
    
    # ─── Distributed System ───
    print("\n  Running distributed system...")
    from study_001 import DistributedSystem
    trajs = run_system('distributed', DistributedSystem, (100,))
    systems['distributed'] = analyze_system('distributed', trajs)
    
    # ─── Ant Colony ───
    print("  Running ant colony...")
    import importlib
    spec = importlib.util.spec_from_file_location("colony",
        "/home/student/sgp_core_v2/post_omega_study_001/study_001b_colony.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    trajs = run_system('ant_colony', mod.AntColony, (50, 100))
    systems['ant_colony'] = analyze_system('ant_colony', trajs)
    
    # ─── Institution Network ───
    print("  Running institution network...")
    spec = importlib.util.spec_from_file_location("inst",
        "/home/student/sgp_core_v2/post_omega_study_001/study_001d_institution.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    trajs = run_system('institution', mod.InstitutionNetwork, (100,))
    systems['institution'] = analyze_system('institution', trajs)
    
    # ─── Immune System ───
    print("  Running immune system...")
    from study_001c_immune import ImmuneSignalingNetwork
    trajs = run_system('immune', ImmuneSignalingNetwork, (100,))
    systems['immune'] = analyze_system('immune', trajs)
    
    # ─── Results Table ───
    print(f"\n{'=' * 70}")
    print("ORGANIZATIONAL FREEDOM RESULTS")
    print(f"{'=' * 70}")
    
    print(f"\n  {'System':15s}  {'G':>5s}  {'H':>5s}  {'reach':>6s}  {'H_trans':>8s}  {'revers':>8s}  {'branch':>8s}  {'access':>8s}  {'canal':>8s}  {'vol':>6s}")
    print(f"  {'─' * 95}")
    
    for name in systems:
        a = systems[name]
        G = KNOWN_G[name]
        H = KNOWN_H[name]
        print(f"  {name:15s}  {G:.3f}  {H:.3f}  {a['reachable_states']:>6d}  {a['transition_entropy']:.3f}  "
              f"{a['reversibility']:.3f}  {a['branching_factor']:.3f}  {a['accessibility']:.3f}  "
              f"{a['canalization_depth']:.1f}  {a['state_space_volume']:.3f}")
    
    # ─── Correlation Analysis ───
    print(f"\n{'=' * 70}")
    print("CORRELATION: G vs Freedom Measures")
    print(f"{'=' * 70}")
    
    G_vals = np.array([KNOWN_G[name] for name in systems])
    H_vals = np.array([KNOWN_H[name] for name in systems])
    
    measures = {
        'reachable_states': np.array([systems[n]['reachable_states'] for n in systems], dtype=float),
        'transition_entropy': np.array([systems[n]['transition_entropy'] for n in systems]),
        'reversibility': np.array([systems[n]['reversibility'] for n in systems]),
        'branching_factor': np.array([systems[n]['branching_factor'] for n in systems]),
        'accessibility': np.array([systems[n]['accessibility'] for n in systems]),
        'canalization_depth': np.array([systems[n]['canalization_depth'] for n in systems]),
        'state_space_volume': np.array([systems[n]['state_space_volume'] for n in systems]),
    }
    
    print(f"\n  {'Measure':20s}  {'Corr(G)':>10s}  {'Corr(H)':>10s}  {'Prediction':>12s}")
    print(f"  {'─' * 58}")
    
    for name, vals in measures.items():
        if np.std(vals) > 1e-6 and np.std(G_vals) > 1e-6:
            corr_G = np.corrcoef(G_vals, vals)[0, 1]
            corr_H = np.corrcoef(H_vals, vals)[0, 1]
            
            # Prediction: if high G = freedom, then positive correlation with freedom measures
            if name == 'canalization_depth':
                prediction = 'neg-G (canalized=low G)' if corr_G < 0 else 'pos-G (unexpected)'
            else:
                prediction = 'pos-G (free=high G)' if corr_G > 0 else 'neg-G (rigid=high G)'
            
            print(f"  {name:20s}  {corr_G:+.3f}  {corr_H:+.3f}  {prediction}")
    
    # ─── Hypothesis Test ───
    print(f"\n{'=' * 70}")
    print("HYPOTHESIS TEST: High G = Organizational Freedom")
    print(f"{'=' * 70}")
    
    print(f"\n  Hypothesis A: High G = broader state repertoire")
    print(f"    Immune (G=0.875) should have MORE reachable states")
    print(f"    Ant colony (G=0.125) should have FEWER reachable states")
    
    immune_reach = systems['immune']['reachable_states']
    ant_reach = systems['ant_colony']['reachable_states']
    print(f"    Immune: {immune_reach} states, Ant colony: {ant_reach} states")
    print(f"    {'CONFIRMED' if immune_reach > ant_reach else 'FALSIFIED'}")
    
    print(f"\n  Hypothesis B: High G = more reversible transitions")
    print(f"    Immune should have MORE reversible transitions")
    
    immune_rev = systems['immune']['reversibility']
    ant_rev = systems['ant_colony']['reversibility']
    print(f"    Immune: {immune_rev:.3f}, Ant colony: {ant_rev:.3f}")
    print(f"    {'CONFIRMED' if immune_rev > ant_rev else 'FALSIFIED'}")
    
    print(f"\n  Hypothesis C: High G = less canalized")
    print(f"    Immune should converge MORE SLOWLY (higher canalization depth)")
    
    immune_can = systems['immune']['canalization_depth']
    ant_can = systems['ant_colony']['canalization_depth']
    print(f"    Immune: {immune_can:.1f} steps, Ant colony: {ant_can:.1f} steps")
    print(f"    {'CONFIRMED' if immune_can > ant_can else 'FALSIFIED'}")
    
    # ─── The Freedom-Canalization Axis ───
    print(f"\n{'=' * 70}")
    print("THE FREEDOM-CANALIZATION AXIS")
    print(f"{'=' * 70}")
    
    print(f"\n  Proposed organizational principle:")
    print(f"    High G = reversible access to multiple configurations")
    print(f"    Low G = historically canalized into narrow repertoire")
    print(f"")
    print(f"  Freedom score (reachable × reversibility / canalization):")
    
    for name in systems:
        a = systems[name]
        freedom = (a['reachable_states'] * a['reversibility'] / 
                   max(a['canalization_depth'], 1))
        G = KNOWN_G[name]
        print(f"    {name:15s}: freedom={freedom:.2f}, G={G:.3f}")
    
    # ─── Unified Theory ───
    print(f"\n{'=' * 70}")
    print("UNIFIED THEORY (revised)")
    print(f"{'=' * 70}")
    
    print(f"""
    G is NOT about:
      - attractor fragmentation (001K falsified)
      - trajectory incompressibility (001K falsified)
      - dynamical irreversibility (001K falsified)
    
    G IS about:
      - organizational freedom (001L tests this)
      - reversible access to multiple configurations
      - weak historical lock-in
      - low canalization depth
    
    The causal chain:
      memory → historical entanglement → canalization → representation sensitivity → low G
    
    The organizational chain:
      reversible transitions → broad state repertoire → high G
      irreversible transitions → narrow state repertoire → low G
    
    The separation:
      H = degree of historical lock-in (measured)
      B = attractor richness (measured in 001K)
      F = organizational freedom (measured here)
    
    The prediction:
      G = f(F, 1/H) — gauge stability is a function of freedom and inverse entanglement
""")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/organizational_freedom_results.json', 'w') as f:
        json.dump({
            'systems': systems,
            'known_G': KNOWN_G,
            'known_H': KNOWN_H,
        }, f, indent=2, default=str)
    
    print(f"Results saved")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    run_study_001l()
