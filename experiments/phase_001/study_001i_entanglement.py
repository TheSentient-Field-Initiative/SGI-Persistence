"""
SGI Post-Ω Study 001I — Historical Entanglement Audit

Directly measure historical residue coupling:
- Path dependence
- State-history mutual information
- Trajectory divergence
- Memory entropy
- Hysteresis

Test: G ∝ 1/historical residue coupling
"""

import numpy as np
import json
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

sys.path.insert(0, '/home/student/sgp_core_v2/post_omega_study_001')


# ═══════════════════════════════════════════════════════════════════
# Parametric Immune System (same as 001H)
# ═══════════════════════════════════════════════════════════════════

@dataclass
class PCell:
    id: int
    cell_type: str
    activation: float = 0.0
    cytokine_level: float = 0.0
    active: bool = True
    receptors: Dict[str, float] = field(default_factory=dict)
    memory: float = 0.0
    clonal_amplification: float = 1.0
    suppression_level: float = 0.0


class ImmuneNet:
    def __init__(self, n=100, seed=42, md=0.5, fg=1.0):
        self.rng = np.random.RandomState(seed)
        self.n = n
        self.md = np.clip(md, 0.0, 1.0)
        self.fg = np.clip(fg, 0.0, 2.0)
        self.timestep = 0
        self.trajectory = []
        self.cell_snapshots = []
        
        probs = [0.30, 0.25, 0.25, 0.20]
        names = ['macrophage', 't_cell', 'b_cell', 'dendritic']
        
        self.cells: List[PCell] = []
        for i in range(n):
            ct = self.rng.choice(names, p=probs)
            c = PCell(id=i, cell_type=ct,
                     activation=self.rng.uniform(0, 0.1),
                     cytokine_level=self.rng.uniform(0, 0.05))
            if ct == 'macrophage':
                c.receptors = {'il1': 1.0, 'tnf': 0.8, 'il6': 0.6}
            elif ct == 't_cell':
                c.receptors = {'il2': 1.0, 'ifn': 0.8, 'il4': 0.5}
            elif ct == 'b_cell':
                c.receptors = {'il4': 1.0, 'il6': 0.8, 'il2': 0.5}
            else:
                c.receptors = {'il1': 0.8, 'il12': 1.0, 'ifn': 0.7}
            self.cells.append(c)
        
        self.adj = {}
        self._build()
        
        self.cyto = {k: np.zeros(n) for k in ['il1','il2','il4','il6','tnf','ifn','il12']}
        self.pathogen = 0.0
    
    def _build(self):
        for i in range(self.n):
            nc = self.rng.randint(3, 9)
            same = [j for j in range(self.n) if j != i and self.cells[j].cell_type == self.cells[i].cell_type]
            other = [j for j in range(self.n) if j != i and self.cells[j].cell_type != self.cells[i].cell_type]
            t = []
            if same and self.rng.random() < 0.7:
                ns = min(nc, len(same))
                t.extend(self.rng.choice(same, size=ns, replace=False))
                nc -= ns
            if other and nc > 0:
                no = min(nc, len(other))
                t.extend(self.rng.choice(other, size=no, replace=False))
            self.adj[i] = list(set(t))
    
    def inject_pathogen(self, sev=0.5):
        self.pathogen = sev
        for c in self.cells:
            if c.cell_type == 'macrophage' and self.rng.random() < sev:
                c.activation = 1.0
                c.cytokine_level = 1.0
    
    def step(self):
        for c in self.cells:
            if not c.active: continue
            for ck, s in c.receptors.items():
                self.cyto[ck][c.id] += c.activation * s * 0.1 * self.fg
        
        for c in self.cells:
            if not c.active: continue
            sig = 0
            for nid in self.adj.get(c.id, []):
                nb = self.cells[nid]
                if not nb.active: continue
                for ck, s in c.receptors.items():
                    sig += nb.cytokine_level * s * 0.01 * self.fg
            mb = c.memory * 0.05 * self.md
            c.activation = np.clip(c.activation * 0.9 + sig * 0.1 + mb, 0, 1)
            c.cytokine_level = c.activation * 0.5
            c.memory = c.memory * 0.95 + c.activation * 0.1 * self.md
        
        if self.pathogen > 0:
            ta = sum(c.activation for c in self.cells if c.active)
            cr = ta * 0.005
            self.pathogen = max(0, self.pathogen - cr)
            self.pathogen = min(1.0, self.pathogen + 0.02)
        
        for k in self.cyto:
            self.cyto[k] *= 0.95
        
        state = self._snap()
        self.trajectory.append(state)
        self.cell_snapshots.append(self._cell_state())
        self.timestep += 1
        return state
    
    def _cell_state(self):
        return np.array([(c.activation, c.memory, c.cytokine_level) for c in self.cells])
    
    def _snap(self):
        ac = [c for c in self.cells if c.active]
        n = len(ac)
        ma = sum(c.activation for c in ac) / max(n, 1)
        tc = sum(c.cytokine_level for c in ac)
        
        ae = 0
        te = 0
        for i, nbrs in self.adj.items():
            if not self.cells[i].active: continue
            for j in nbrs:
                te += 1
                if self.cells[j].active: ae += 1
        conn = ae / max(te, 1)
        
        nc, cs = self._comp()
        lc = max(cs) / max(n, 1) if cs else 0
        
        tc2 = {}
        for c in ac:
            tc2[c.cell_type] = tc2.get(c.cell_type, 0) + 1
        tp = np.array(list(tc2.values())) / max(sum(tc2.values()), 1)
        ent = -np.sum(tp * np.log2(tp + 1e-10))
        
        # Transport
        type_acts = {}
        for c in ac:
            type_acts.setdefault(c.cell_type, []).append(c.activation)
        types = list(type_acts.keys())
        if len(types) > 1:
            mat = np.zeros((len(types), max(len(v) for v in type_acts.values())))
            for i, t in enumerate(types):
                mat[i, :len(type_acts[t])] = type_acts[t]
            cov = np.cov(mat)
            ev = np.sort(np.abs(np.linalg.eigvalsh(cov)))[::-1]
            cov_trace = float(np.sum(ev))
            cov_cond = float(ev[0] / (ev[-1] + 1e-10)) if len(ev) > 1 else 1.0
        else:
            ev = np.array([0])
            cov_trace = 0
            cov_cond = 1.0
        
        if len(types) > 1 and len(ev) > 1:
            te2 = np.sum(ev)
            non_princ = float(np.sum(ev[1:]) / (te2 + 1e-10))
        else:
            non_princ = 0
        
        cyto_var = [c.cytokine_level ** 2 for c in ac]
        noise = np.sqrt(np.mean(cyto_var)) if cyto_var else 0
        
        return {'mean_act': ma, 'total_cyto': tc, 'n_active': n,
                'connectivity': conn, 'n_comp': nc, 'largest': lc,
                'type_entropy': ent, 'pathogen': self.pathogen,
                'cov_trace': cov_trace, 'cov_condition': cov_cond,
                'non_principal': non_princ, 'signaling_noise': noise}
    
    def _comp(self):
        v = set()
        cs = []
        for c in self.cells:
            if not c.active or c.id in v: continue
            s = 0
            q = [c.id]
            v.add(c.id)
            while q:
                cur = q.pop(0)
                s += 1
                for nid in self.adj.get(cur, []):
                    if nid not in v and self.cells[nid].active:
                        v.add(nid)
                        q.append(nid)
            cs.append(s)
        return len(cs), cs
    
    def copy_with_perturbation(self, noise=0.01):
        """Create a copy with slightly perturbed initial state."""
        import copy
        net2 = ImmuneNet(self.n, seed=self.rng.randint(10000), md=self.md, fg=self.fg)
        # Copy cell states with noise
        for c1, c2 in zip(self.cells, net2.cells):
            c2.activation = np.clip(c1.activation + self.rng.normal(0, noise), 0, 1)
            c2.memory = np.clip(c1.memory + self.rng.normal(0, noise), 0, 1)
            c2.cytokine_level = np.clip(c1.cytokine_level + self.rng.normal(0, noise), 0, 1)
        return net2


# ═══════════════════════════════════════════════════════════════════
# Historical Entanglement Measures
# ═══════════════════════════════════════════════════════════════════

def measure_path_dependence(net, n_steps=50, noise=0.01):
    """Measure how much trajectories diverge from perturbed initial conditions."""
    net2 = net.copy_with_perturbation(noise)
    
    divergences = []
    for _ in range(n_steps):
        s1 = net.step()
        s2 = net2.step()
        # State distance
        v1 = np.array([s1['mean_act'], s1['connectivity'], s1['type_entropy']])
        v2 = np.array([s2['mean_act'], s2['connectivity'], s2['type_entropy']])
        div = np.linalg.norm(v1 - v2)
        divergences.append(div)
    
    # Path dependence = final divergence / initial perturbation
    final_div = divergences[-1] if divergences else 0
    return float(final_div / max(noise, 1e-8))


def measure_state_history_mi(net, n_steps=50):
    """Measure mutual information between current state and historical states."""
    # Run net to collect trajectory
    for _ in range(n_steps):
        net.step()
    
    if len(net.trajectory) < 10:
        return 0.0
    
    # Current state vector
    current = np.array([net.trajectory[-1]['mean_act'], 
                       net.trajectory[-1]['connectivity'],
                       net.trajectory[-1]['type_entropy']])
    
    # Historical states (average of past windows)
    window = 5
    hist_vectors = []
    for i in range(0, len(net.trajectory) - window, window):
        w = net.trajectory[i:i+window]
        hv = np.array([np.mean([s['mean_act'] for s in w]),
                       np.mean([s['connectivity'] for s in w]),
                       np.mean([s['type_entropy'] for s in w])])
        hist_vectors.append(hv)
    
    if not hist_vectors:
        return 0.0
    
    hist_matrix = np.array(hist_vectors)
    
    # Discretize for MI estimation
    n_bins = 5
    def discretize(arr, bins=n_bins):
        d = np.digitize(arr, np.linspace(arr.min(), arr.max() + 1e-8, bins))
        return d
    
    current_d = discretize(current)
    hist_d = discretize(hist_matrix)
    
    # Compute MI (simplified: correlation-based)
    mi = 0.0
    for dim in range(min(current_d.shape[0], hist_d.shape[1])):
        c_val = current_d[dim] if dim < len(current_d) else 0
        h_vals = hist_d[:, dim] if dim < hist_d.shape[1] else np.zeros(len(hist_d))
        if len(h_vals) > 0 and np.std(h_vals) > 0:
            mi += abs(np.corrcoef([c_val] * len(h_vals), h_vals)[0, 1])
    
    return float(mi / 3.0)  # Average over dimensions


def measure_trajectory_divergence(net, n_runs=3, n_steps=30):
    """Measure Lyapunov-like divergence of multiple trajectories."""
    trajectories = []
    for _ in range(n_runs):
        net_copy = ImmuneNet(net.n, seed=net.rng.randint(10000), md=net.md, fg=net.fg)
        # Inject same perturbation
        net_copy.inject_pathogen(0.5)
        traj = []
        for _ in range(n_steps):
            s = net_copy.step()
            traj.append(np.array([s['mean_act'], s['connectivity'], s['type_entropy']]))
        trajectories.append(np.array(traj))
    
    if len(trajectories) < 2:
        return 0.0
    
    # Average pairwise divergence over time
    divergences = []
    for t in range(min(len(tr) for tr in trajectories)):
        states = [tr[t] for tr in trajectories]
        for i in range(len(states)):
            for j in range(i+1, len(states)):
                divergences.append(np.linalg.norm(states[i] - states[j]))
    
    if not divergences:
        return 0.0
    
    # Divergence rate = slope of log divergence over time
    div_array = np.array(divergences).reshape(min(len(tr) for tr in trajectories), -1).mean(axis=1)
    div_array = div_array[div_array > 0]
    
    if len(div_array) < 2:
        return 0.0
    
    log_div = np.log(div_array + 1e-10)
    t = np.arange(len(log_div))
    slope = np.polyfit(t, log_div, 1)[0]
    
    return float(slope)


def measure_memory_entropy(net):
    """Measure entropy of memory distribution across cells."""
    memories = [c.memory for c in net.cells if c.active]
    if not memories:
        return 0.0
    
    mem_array = np.array(memories)
    n_bins = 10
    hist, _ = np.histogram(mem_array, bins=n_bins, range=(0, 1))
    hist = hist / max(hist.sum(), 1)
    entropy = -np.sum(hist[hist > 0] * np.log2(hist[hist > 0]))
    
    return float(entropy)


def measure_hysteresis(net, n_steps=30, sev=0.5):
    """Measure how much the system returns to original state after perturbation cycle."""
    # Run to baseline
    for _ in range(n_steps):
        net.step()
    
    baseline = net.trajectory[-1].copy()
    baseline_vec = np.array([baseline['mean_act'], baseline['connectivity'], baseline['type_entropy']])
    
    # Apply perturbation
    net.inject_pathogen(sev)
    for _ in range(n_steps):
        net.step()
    
    perturbed = net.trajectory[-1].copy()
    perturbed_vec = np.array([perturbed['mean_act'], perturbed['connectivity'], perturbed['type_entropy']])
    
    # Let system recover (pathogen cleared naturally)
    for _ in range(n_steps * 2):
        net.step()
    
    recovered = net.trajectory[-1].copy()
    recovered_vec = np.array([recovered['mean_act'], recovered['connectivity'], recovered['type_entropy']])
    
    # Hysteresis = distance from baseline after recovery / distance at perturbation
    perturbation_distance = np.linalg.norm(perturbed_vec - baseline_vec)
    recovery_distance = np.linalg.norm(recovered_vec - baseline_vec)
    
    if perturbation_distance < 1e-8:
        return 0.0
    
    return float(recovery_distance / perturbation_distance)


def measure_historical_entanglement(net):
    """Compute composite historical residue coupling score."""
    path_dep = measure_path_dependence(net)
    mi = measure_state_history_mi(net)
    div = measure_trajectory_divergence(net)
    mem_ent = measure_memory_entropy(net)
    hyst = measure_hysteresis(net)
    
    # Normalize each to [0, 1] approximately
    # Higher values = more entanglement
    scores = {
        'path_dependence': path_dep,
        'state_history_mi': mi,
        'trajectory_divergence': div,
        'memory_entropy': mem_ent,
        'hysteresis': hyst,
    }
    
    # Composite score (weighted average)
    # Normalize path dependence (typical range 0-10)
    pd_norm = min(path_dep / 5.0, 1.0)
    # MI already ~[0,1]
    # Divergence (typical range -0.1 to 0.1)
    div_norm = min(max(div + 0.1, 0) / 0.2, 1.0)
    # Memory entropy (typical range 0-3)
    me_norm = min(mem_ent / 3.0, 1.0)
    # Hysteresis (typical range 0-2)
    hyst_norm = min(hyst / 1.0, 1.0)
    
    composite = np.mean([pd_norm, mi, div_norm, me_norm, hyst_norm])
    
    scores['composite'] = float(composite)
    
    return scores


# ═══════════════════════════════════════════════════════════════════
# G Measurement
# ═══════════════════════════════════════════════════════════════════

SECTORS = {
    'amplitude': ['mean_act', 'total_cyto', 'n_active'],
    'topology': ['connectivity', 'n_comp', 'largest', 'type_entropy'],
    'transport': ['cov_trace', 'cov_condition'],
    'residual': ['non_principal', 'signaling_noise'],
}

def extract_m(s):
    return {k: v for k, v in s.items() if k != 'timestep' and k != 'cov_eigenvalues'}

def sector_align(before, after):
    results = {}
    for sn, metrics in SECTORS.items():
        bv = np.array([[bm.get(m, 0) for bm in before] for m in metrics]).T
        av = np.array([[am.get(m, 0) for am in after] for m in metrics]).T
        if bv.size == 0 or av.size == 0:
            results[sn] = {'error': 'no data'}
            continue
        ml = min(len(bv), len(av))
        bv, av = bv[:ml], av[:ml]
        def cs(a, b):
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            return float(np.dot(a.flatten(), b.flatten()) / (na * nb)) if na > 0 and nb > 0 else 0.0
        raw = cs(bv, av)
        bn = (bv - bv.mean(0)) / (bv.std(0) + 1e-8)
        an = (av - av.mean(0)) / (av.std(0) + 1e-8)
        norm = cs(bn, an)
        results[sn] = {'verdict': 'SURVIVES' if norm - raw > -0.1 else 'COLLAPSES',
                       'norm_survival': norm - raw}
    return results

def gauge_frac(sd):
    surv = sum(1 for s in ['amplitude', 'topology', 'transport', 'residual'] 
               if sd.get(s, {}).get('verdict') == 'SURVIVES')
    return surv / 4.0


def measure_G(md, fg, seed=42):
    """Measure G for a given (memory_depth, feedback_gain)."""
    net = ImmuneNet(100, seed, md, fg)
    
    # Baseline
    hist_b = []
    for _ in range(20):
        s = net.step()
        hist_b.append(extract_m(s))
    
    # Perturb
    net.inject_pathogen(0.5)
    
    # Recovery
    hist_a = []
    for _ in range(50):
        s = net.step()
        hist_a.append(extract_m(s))
    
    sr = sector_align(hist_b, hist_a)
    return gauge_frac(sr)


# ═══════════════════════════════════════════════════════════════════
# Main Experiment
# ═══════════════════════════════════════════════════════════════════

def run_study_001i():
    print("=" * 70)
    print("Study 001I — Historical Entanglement Audit")
    print("=" * 70)
    
    print("\n  Testing: G ∝ 1/historical residue coupling")
    
    # Sweep memory_depth
    md_values = np.linspace(0.0, 1.0, 6)
    fg_fixed = 1.0
    
    results = []
    
    for md in md_values:
        print(f"\n  md={md:.1f}...")
        
        net = ImmuneNet(100, 42, md, fg_fixed)
        
        # Measure entanglement
        entanglement = measure_historical_entanglement(net)
        
        # Measure G
        G = measure_G(md, fg_fixed)
        
        result = {
            'memory_depth': float(md),
            'feedback_gain': fg_fixed,
            'G': G,
            'entanglement': entanglement,
        }
        results.append(result)
        
        print(f"    G={G:.3f}  composite_entanglement={entanglement['composite']:.3f}")
        print(f"    path_dep={entanglement['path_dependence']:.3f}  "
              f"MI={entanglement['state_history_mi']:.3f}  "
              f"div={entanglement['trajectory_divergence']:.3f}  "
              f"mem_ent={entanglement['memory_entropy']:.3f}  "
              f"hyst={entanglement['hysteresis']:.3f}")
    
    # ─── Correlation Analysis ───
    print(f"\n{'=' * 70}")
    print("CORRELATION: G vs Historical Entanglement")
    print(f"{'=' * 70}")
    
    G_vals = np.array([r['G'] for r in results])
    ent_composite = np.array([r['entanglement']['composite'] for r in results])
    ent_pd = np.array([r['entanglement']['path_dependence'] for r in results])
    ent_mi = np.array([r['entanglement']['state_history_mi'] for r in results])
    ent_div = np.array([r['entanglement']['trajectory_divergence'] for r in results])
    ent_me = np.array([r['entanglement']['memory_entropy'] for r in results])
    ent_hyst = np.array([r['entanglement']['hysteresis'] for r in results])
    
    measures = {
        'composite': ent_composite,
        'path_dependence': ent_pd,
        'state_history_mi': ent_mi,
        'trajectory_divergence': ent_div,
        'memory_entropy': ent_me,
        'hysteresis': ent_hyst,
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
            print(f"  {name:25s}  (constant — no variance)")
    
    # ─── Test Hypothesis ───
    print(f"\n{'=' * 70}")
    print("HYPOTHESIS TEST: G ∝ 1/historical residue coupling")
    print(f"{'=' * 70}")
    
    if np.std(ent_composite) > 1e-6:
        corr = np.corrcoef(G_vals, ent_composite)[0, 1]
        print(f"\n  G-Composite correlation: {corr:.3f}")
        if corr < -0.7:
            print(f"  HYPOTHESIS STRONGLY SUPPORTED: G ∝ 1/entanglement")
        elif corr < -0.4:
            print(f"  HYPOTHESIS MODERATELY SUPPORTED: G ∝ 1/entanglement")
        elif corr < 0:
            print(f"  HYPOTHESIS WEAKLY SUPPORTED: negative relationship exists")
        else:
            print(f"  HYPOTHESIS NOT SUPPORTED: no negative relationship")
    else:
        print(f"\n  Composite entanglement has no variance — cannot test")
    
    # ─── Landscape ───
    print(f"\n{'=' * 70}")
    print("ENTANGLEMENT-G RELATIONSHIP")
    print(f"{'=' * 70}")
    
    for r in results:
        md = r['memory_depth']
        G = r['G']
        ent = r['entanglement']['composite']
        bar_g = '█' * int(G * 30)
        bar_e = '░' * int(ent * 30)
        print(f"  md={md:.1f}  G={G:.3f} {bar_g:30s}  ent={ent:.3f} {bar_e:30s}")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/entanglement_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    run_study_001i()
