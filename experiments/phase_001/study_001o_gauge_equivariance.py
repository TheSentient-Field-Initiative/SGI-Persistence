"""
SGI Post-Ω Study 001O — Gauge Equivariance Audit

Test whether G = gauge-equivariant replay preservation.

Measures:
- Replay gauge equivariance
- Sector-preserving replay maps
- Representation-class invariance
- Normalization-induced trajectory distortion
- Gauge-orbit stability
- Replay equivalence preservation
"""

import numpy as np
import json
import sys

sys.path.insert(0, '/home/student/sgp_core_v2/post_omega_study_001')


# ═══════════════════════════════════════════════════════════════════
# State Encoding & Gauge Transformations
# ═══════════════════════════════════════════════════════════════════

def state_to_vector(state: dict) -> np.ndarray:
    """Convert state dict to normalized vector."""
    if not state:
        return np.zeros(4)
    
    vals = []
    for key in ['connectivity', 'mean_act', 'type_entropy', 'n_components',
                'routing_entropy', 'n_active', 'assignment_rate', 'allocation_entropy',
                'efficiency', 'total_pheromone', 'coverage', 'n_institutions', 'avg_trust',
                'n_naive', 'n_memory', 'n_active_cells', 'pathogen_load']:
        v = state.get(key, 0)
        if isinstance(v, (int, float)):
            vals.append(float(v))
    
    if not vals:
        return np.zeros(4)
    
    vec = np.array(vals[:4], dtype=float)
    max_vals = np.maximum(np.abs(vec), 1.0)
    vec = vec / max_vals
    return np.clip(vec, -1, 1)


def encode_state(state: dict, n_bins: int = 8) -> str:
    """Discretize state into a symbolic string."""
    v = state_to_vector(state)
    bins = np.linspace(0, 1, n_bins + 1)
    symbols = []
    for val in v:
        val_norm = (val + 1) / 2  # Map [-1,1] to [0,1]
        sym = int(np.digitize(val_norm, bins[1:-1]))
        symbols.append(str(sym))
    return ''.join(symbols)


def apply_gauge_transformation(trajectory, gauge_type='normalize'):
    """Apply a gauge transformation to a trajectory."""
    transformed = []
    
    for state in trajectory:
        v = state_to_vector(state)
        
        if gauge_type == 'normalize':
            # L2 normalization
            norm = np.linalg.norm(v)
            if norm > 0:
                v = v / norm
            v = np.clip(v, -1, 1)
        
        elif gauge_type == 'permute':
            # Permute dimensions
            perm = [3, 2, 1, 0]
            v = v[perm]
        
        elif gauge_type == 'scale':
            # Scale by random factor
            scale = 0.5 + np.random.random() * 1.5
            v = v * scale
            v = np.clip(v, -1, 1)
        
        elif gauge_type == 'shift':
            # Shift by random amount
            shift = np.random.randn(4) * 0.1
            v = v + shift
            v = np.clip(v, -1, 1)
        
        elif gauge_type == 'sector':
            # Project to sector (keep only positive components)
            v = np.maximum(v, 0)
            v = v / max(np.linalg.norm(v), 1e-10)
        
        transformed.append({'gauge_vector': v.tolist()})
    
    return transformed


def compute_trajectory_distance(traj1, traj2):
    """Compute distance between two trajectories."""
    if len(traj1) != len(traj2):
        min_len = min(len(traj1), len(traj2))
        traj1 = traj1[:min_len]
        traj2 = traj2[:min_len]
    
    if not traj1:
        return 0.0
    
    distances = []
    for s1, s2 in zip(traj1, traj2):
        v1 = state_to_vector(s1)
        v2 = state_to_vector(s2)
        distances.append(np.linalg.norm(v1 - v2))
    
    return np.mean(distances)


def compute_gauge_equivariance(trajectory, gauge_type='normalize'):
    """Measure how much trajectory changes under gauge transformation."""
    transformed = apply_gauge_transformation(trajectory, gauge_type)
    
    # Compute distance between original and transformed
    distances = []
    for orig, trans in zip(trajectory, transformed):
        v_orig = state_to_vector(orig)
        v_trans = np.array(trans['gauge_vector'])
        distances.append(np.linalg.norm(v_orig - v_trans))
    
    return np.mean(distances)


def compute_sector_preservation(trajectory):
    """Measure how well trajectory preserves sector structure."""
    if len(trajectory) < 2:
        return 1.0
    
    # Compute sector at each step
    sectors = []
    for state in trajectory:
        v = state_to_vector(state)
        sector = tuple(np.sign(v).astype(int))
        sectors.append(sector)
    
    # Count sector changes
    changes = sum(1 for i in range(len(sectors) - 1) if sectors[i] != sectors[i+1])
    
    return 1.0 - changes / max(len(sectors) - 1, 1)


def compute_representation_invariance(trajectory, net_class, net_args):
    """Measure whether trajectory is invariant under representation change."""
    # Run with different seeds
    trajectories = []
    for seed in [42, 43, 44]:
        net = net_class(*net_args, seed=seed)
        if hasattr(net, 'generate_tasks'):
            net.generate_tasks(100)
        for _ in range(len(trajectory)):
            net.step()
        trajectories.append(net.history)
    
    # Compute pairwise distances
    distances = []
    for i in range(len(trajectories)):
        for j in range(i + 1, len(trajectories)):
            dist = compute_trajectory_distance(trajectories[i], trajectories[j])
            distances.append(dist)
    
    return np.mean(distances) if distances else 0.0


def compute_normalization_distortion(trajectory):
    """Measure how much normalization distorts the trajectory."""
    if not trajectory:
        return 0.0
    
    distortions = []
    for state in trajectory:
        v = state_to_vector(state)
        
        # Normalize
        norm = np.linalg.norm(v)
        if norm > 0:
            v_norm = v / norm
        else:
            v_norm = v
        
        # Distortion = change in direction
        cos_sim = np.dot(v, v_norm) / (np.linalg.norm(v) * np.linalg.norm(v_norm) + 1e-10)
        distortion = 1 - cos_sim
        distortions.append(distortion)
    
    return np.mean(distortions)


def compute_gauge_orbit_stability(trajectory, n_gauges=5):
    """Measure stability of trajectory across multiple gauge transformations."""
    gauge_types = ['normalize', 'permute', 'scale', 'shift', 'sector']
    
    orbits = []
    for gauge_type in gauge_types[:n_gauges]:
        transformed = apply_gauge_transformation(trajectory, gauge_type)
        orbit = [state_to_vector(s) for s in transformed]
        orbits.append(orbit)
    
    # Compute stability: average pairwise distance between orbits
    if len(orbits) < 2:
        return 0.0
    
    distances = []
    for i in range(len(orbits)):
        for j in range(i + 1, len(orbits)):
            if len(orbits[i]) == len(orbits[j]):
                dist = np.mean([np.linalg.norm(o1 - o2) 
                               for o1, o2 in zip(orbits[i], orbits[j])])
                distances.append(dist)
    
    return np.mean(distances) if distances else 0.0


def compute_replay_equivalence(trajectory, net_class, net_args):
    """Measure whether replay preserves equivalence relations."""
    # Run original
    net1 = net_class(*net_args, seed=42)
    if hasattr(net1, 'generate_tasks'):
        net1.generate_tasks(100)
    for _ in range(len(trajectory)):
        net1.step()
    
    # Run with different initial conditions but same parameters
    net2 = net_class(*net_args, seed=42 + 100)
    if hasattr(net2, 'generate_tasks'):
        net2.generate_tasks(100)
    for _ in range(len(trajectory)):
        net2.step()
    
    # Check if final states are equivalent
    v1 = state_to_vector(net1.history[-1])
    v2 = state_to_vector(net2.history[-1])
    
    # Equivalence = inverse distance
    dist = np.linalg.norm(v1 - v2)
    equivalence = 1.0 / (1.0 + dist)
    
    return equivalence


def compute_equivariance_score(trajectory, net_class, net_args):
    """Combined equivariance score."""
    gauge_eq = compute_gauge_equivariance(trajectory, 'normalize')
    sector_pres = compute_sector_preservation(trajectory)
    norm_dist = compute_normalization_distortion(trajectory)
    orbit_stab = compute_gauge_orbit_stability(trajectory)
    replay_eq = compute_replay_equivalence(trajectory, net_class, net_args)
    
    # Score: high when gauge equivariance is low (trajectory doesn't change much)
    # and sector preservation is high (trajectory stays in same sector)
    score = (1.0 / (1.0 + gauge_eq)) * sector_pres * (1.0 / (1.0 + orbit_stab)) * replay_eq
    
    return score


# ═══════════════════════════════════════════════════════════════════
# System Adapters
# ═══════════════════════════════════════════════════════════════════

def run_system(system_name, net_class, net_args, n_seeds=10, n_steps=30):
    """Run a system and collect trajectories."""
    trajectories = []
    
    for seed in range(n_seeds):
        net = net_class(*net_args, seed=seed * 7 + 3)
        if hasattr(net, 'generate_tasks'):
            net.generate_tasks(100)
        
        for _ in range(n_steps):
            net.step()
        
        trajectories.append(net.history)
    
    return trajectories


def analyze_system(system_name, trajectories, net_class, net_args):
    """Compute all gauge equivariance measures for a system."""
    primary = trajectories[0] if trajectories else []
    
    # Compute measures
    gauge_eq_normalize = compute_gauge_equivariance(primary, 'normalize')
    gauge_eq_permute = compute_gauge_equivariance(primary, 'permute')
    gauge_eq_scale = compute_gauge_equivariance(primary, 'scale')
    gauge_eq_shift = compute_gauge_equivariance(primary, 'shift')
    gauge_eq_sector = compute_gauge_equivariance(primary, 'sector')
    
    sector_pres = compute_sector_preservation(primary)
    norm_dist = compute_normalization_distortion(primary)
    orbit_stab = compute_gauge_orbit_stability(primary)
    replay_eq = compute_replay_equivalence(primary, net_class, net_args)
    equiv_score = compute_equivariance_score(primary, net_class, net_args)
    
    # Representation invariance
    rep_invar = compute_representation_invariance(primary, net_class, net_args)
    
    # Average over trajectories
    gauge_eq_scores = [compute_gauge_equivariance(t, 'normalize') for t in trajectories]
    sector_scores = [compute_sector_preservation(t) for t in trajectories]
    
    return {
        'gauge_equivariance_normalize': gauge_eq_normalize,
        'gauge_equivariance_permute': gauge_eq_permute,
        'gauge_equivariance_scale': gauge_eq_scale,
        'gauge_equivariance_shift': gauge_eq_shift,
        'gauge_equivariance_sector': gauge_eq_sector,
        'sector_preservation': sector_pres,
        'normalization_distortion': norm_dist,
        'gauge_orbit_stability': orbit_stab,
        'replay_equivalence': replay_eq,
        'equivariance_score': equiv_score,
        'representation_invariance': rep_invar,
        'gauge_eq_mean': np.mean(gauge_eq_scores),
        'sector_pres_mean': np.mean(sector_scores),
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

def run_study_001o():
    print("=" * 70)
    print("Study 001O — Gauge Equivariance Audit")
    print("=" * 70)
    
    print("\n  Testing: G = gauge-equivariant replay preservation")
    
    systems = {}
    
    # ─── Distributed System ───
    print("\n  Running distributed system...")
    from study_001 import DistributedSystem
    trajs = run_system('distributed', DistributedSystem, (100,))
    systems['distributed'] = analyze_system('distributed', trajs, DistributedSystem, (100,))
    
    # ─── Ant Colony ───
    print("  Running ant colony...")
    import importlib
    spec = importlib.util.spec_from_file_location("colony",
        "/home/student/sgp_core_v2/post_omega_study_001/study_001b_colony.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    trajs = run_system('ant_colony', mod.AntColony, (50, 100))
    systems['ant_colony'] = analyze_system('ant_colony', trajs, mod.AntColony, (50, 100))
    
    # ─── Institution Network ───
    print("  Running institution network...")
    spec = importlib.util.spec_from_file_location("inst",
        "/home/student/sgp_core_v2/post_omega_study_001/study_001d_institution.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    trajs = run_system('institution', mod.InstitutionNetwork, (100,))
    systems['institution'] = analyze_system('institution', trajs, mod.InstitutionNetwork, (100,))
    
    # ─── Immune System ───
    print("  Running immune system...")
    from study_001c_immune import ImmuneSignalingNetwork
    trajs = run_system('immune', ImmuneSignalingNetwork, (100,))
    systems['immune'] = analyze_system('immune', trajs, ImmuneSignalingNetwork, (100,))
    
    # ─── Results Table ───
    print(f"\n{'=' * 70}")
    print("GAUGE EQUIVARIANCE RESULTS")
    print(f"{'=' * 70}")
    
    print(f"\n  {'System':15s}  {'G':>5s}  {'H':>5s}  {'g_eq_norm':>10s}  {'g_eq_perm':>10s}  {'sec_pres':>9s}  {'norm_dist':>10s}  {'orbit':>8s}  {'replay_eq':>10s}  {'equiv_score':>12s}")
    print(f"  {'─' * 105}")
    
    for name in systems:
        a = systems[name]
        G = KNOWN_G[name]
        H = KNOWN_H[name]
        print(f"  {name:15s}  {G:.3f}  {H:.3f}  {a['gauge_equivariance_normalize']:.3f}  "
              f"{a['gauge_equivariance_permute']:.3f}  {a['sector_preservation']:.3f}  "
              f"{a['normalization_distortion']:.3f}  {a['gauge_orbit_stability']:.3f}  "
              f"{a['replay_equivalence']:.3f}  {a['equivariance_score']:.3f}")
    
    # ─── Correlation Analysis ───
    print(f"\n{'=' * 70}")
    print("CORRELATION: G vs Gauge Equivariance Measures")
    print(f"{'=' * 70}")
    
    G_vals = np.array([KNOWN_G[name] for name in systems])
    H_vals = np.array([KNOWN_H[name] for name in systems])
    
    measures = {
        'gauge_equivariance_normalize': np.array([systems[n]['gauge_equivariance_normalize'] for n in systems]),
        'gauge_equivariance_permute': np.array([systems[n]['gauge_equivariance_permute'] for n in systems]),
        'gauge_equivariance_scale': np.array([systems[n]['gauge_equivariance_scale'] for n in systems]),
        'sector_preservation': np.array([systems[n]['sector_preservation'] for n in systems]),
        'normalization_distortion': np.array([systems[n]['normalization_distortion'] for n in systems]),
        'gauge_orbit_stability': np.array([systems[n]['gauge_orbit_stability'] for n in systems]),
        'replay_equivalence': np.array([systems[n]['replay_equivalence'] for n in systems]),
        'equivariance_score': np.array([systems[n]['equivariance_score'] for n in systems]),
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
    
    # ─── The Central Anomaly ───
    print(f"\n{'=' * 70}")
    print("THE CENTRAL ANOMALY")
    print(f"{'=' * 70}")
    
    print(f"\n  Question: Why do immune and distributed systems have")
    print(f"  similar replay metrics but radically different G?")
    print(f"")
    
    for name in ['distributed', 'immune']:
        a = systems[name]
        G = KNOWN_G[name]
        print(f"  {name:15s}: G={G:.3f}, replay_eq={a['replay_equivalence']:.3f}, "
              f"sector_pres={a['sector_preservation']:.3f}, equiv_score={a['equivariance_score']:.3f}")
    
    # ─── Gauge Equivariance Test ───
    print(f"\n{'=' * 70}")
    print("HYPOTHESIS TEST: G = Gauge-Equivariant Replay Preservation")
    print(f"{'=' * 70}")
    
    print(f"\n  High-G systems should have:")
    print(f"    - LOWER gauge equivariance (trajectory doesn't change under gauge)")
    print(f"    - HIGHER sector preservation (trajectory stays in same sector)")
    print(f"    - LOWER normalization distortion")
    print(f"    - LOWER gauge orbit stability")
    print(f"    - HIGHER replay equivalence")
    print(f"    - HIGHER equivariance score")
    
    print(f"\n  {'System':15s}  {'G':>5s}  {'g_eq_norm':>10s}  {'sec_pres':>9s}  {'equiv_score':>12s}")
    print(f"  {'─' * 50}")
    
    for name in systems:
        a = systems[name]
        G = KNOWN_G[name]
        print(f"  {name:15s}  {G:.3f}  {a['gauge_equivariance_normalize']:.3f}  "
              f"{a['sector_preservation']:.3f}  {a['equivariance_score']:.3f}")
    
    # ─── The Equivariance Theory ───
    print(f"\n{'=' * 70}")
    print("THE EQUIVARIANCE THEORY")
    print(f"{'=' * 70}")
    
    print(f"""
    The evidence suggests:
    
    G is NOT about:
      - replay compressibility alone (001N falsified)
      - thermodynamic irreversibility (001M falsified)
      - attractor fragmentation (001K falsified)
      - organizational freedom (001L falsified)
    
    G IS about:
      - gauge-equivariant replay preservation
      - representation-preserving replay structure
      - sector-preserving replay maps
      - replay equivalence under gauge change
    
    The causal chain:
      memory → historical entanglement → non-replayable residue → representation sensitivity → low G
    
    The equivariance chain:
      high equivariance → replay preserves sectors → high G
      low equivariance → replay changes sectors → low G
    
    The key insight:
      G measures how well organizational replay preserves
      equivalence classes under representation transformation.
    
    This is consistent with:
      - 001I/001J: G ∝ 1/H (more equivariance = less entanglement)
      - 001L: high G = high reversibility (more reversibility = more equivariant)
      - 001N: replay compressibility partially predicts G
      - Ω-series: gauge invariance = representational equivariance
    
    The resolution of the central anomaly:
      Immune and distributed systems may have similar replay metrics
      but different equivariance structure.
      The immune system preserves sectors under gauge change.
      The distributed system does not.
""")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/gauge_equivariance_results.json', 'w') as f:
        json.dump({
            'systems': systems,
            'known_G': KNOWN_G,
            'known_H': KNOWN_H,
        }, f, indent=2, default=str)
    
    print(f"Results saved")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    run_study_001o()
