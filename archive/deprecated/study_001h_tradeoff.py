"""
SGI Post-Ω Study 001H — Persistence–Adaptation Tradeoff

Explicitly vary memory depth and feedback gain.
Measure G and adaptation accuracy at each point.
Determine if a Pareto frontier exists between G and adaptation.
"""

import numpy as np
import json
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

sys.path.insert(0, '/home/student/sgp_core_v2/post_omega_study_001')


# ═══════════════════════════════════════════════════════════════════
# Parametric Immune System
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ParamCell:
    id: int
    cell_type: str
    activation: float = 0.0
    cytokine_level: float = 0.0
    active: bool = True
    receptors: Dict[str, float] = field(default_factory=dict)
    memory: float = 0.0
    clonal_amplification: float = 1.0
    suppression_level: float = 0.0


class ParametricImmuneNetwork:
    """Immune system with continuous memory_depth and feedback_gain parameters."""
    
    def __init__(self, n_cells: int = 100, seed: int = 42,
                 memory_depth: float = 0.5,
                 feedback_gain: float = 1.0):
        
        self.rng = np.random.RandomState(seed)
        self.n_cells = n_cells
        self.timestep = 0
        self.history = []
        
        # Continuous parameters
        self.memory_depth = np.clip(memory_depth, 0.0, 1.0)
        self.feedback_gain = np.clip(feedback_gain, 0.0, 2.0)
        
        # Cell types
        type_probs = [0.30, 0.25, 0.25, 0.20]
        type_names = ['macrophage', 't_cell', 'b_cell', 'dendritic']
        
        self.cells: List[ParamCell] = []
        for i in range(n_cells):
            ct = self.rng.choice(type_names, p=type_probs)
            cell = ParamCell(
                id=i,
                cell_type=ct,
                activation=self.rng.uniform(0.0, 0.1),
                cytokine_level=self.rng.uniform(0.0, 0.05),
            )
            if ct == 'macrophage':
                cell.receptors = {'il1': 1.0, 'tnf': 0.8, 'il6': 0.6}
            elif ct == 't_cell':
                cell.receptors = {'il2': 1.0, 'ifn': 0.8, 'il4': 0.5}
            elif ct == 'b_cell':
                cell.receptors = {'il4': 1.0, 'il6': 0.8, 'il2': 0.5}
            else:
                cell.receptors = {'il1': 0.8, 'il12': 1.0, 'ifn': 0.7}
            self.cells.append(cell)
        
        # Build network
        self.adjacency: Dict[int, List[int]] = {}
        self._build_network()
        
        # Cytokine field
        self.cytokine_field = {
            'il1': np.zeros(n_cells), 'il2': np.zeros(n_cells),
            'il4': np.zeros(n_cells), 'il6': np.zeros(n_cells),
            'tnf': np.zeros(n_cells), 'ifn': np.zeros(n_cells),
            'il12': np.zeros(n_cells),
        }
        
        # Adaptation tracking
        self.pathogen_load = 0.0
        self.adaptation_score = 0.0
        self.response_times = []
    
    def _build_network(self):
        for i in range(self.n_cells):
            n_connections = self.rng.randint(3, 9)
            same_type = [j for j in range(self.n_cells) if j != i and 
                        self.cells[j].cell_type == self.cells[i].cell_type]
            other_type = [j for j in range(self.n_cells) if j != i and 
                         self.cells[j].cell_type != self.cells[i].cell_type]
            targets = []
            if same_type and self.rng.random() < 0.7:
                n_same = min(n_connections, len(same_type))
                targets.extend(self.rng.choice(same_type, size=n_same, replace=False))
                n_connections -= n_same
            if other_type and n_connections > 0:
                n_other = min(n_connections, len(other_type))
                targets.extend(self.rng.choice(other_type, size=n_other, replace=False))
            self.adjacency[i] = list(set(targets))
    
    def introduce_pathogen(self, severity: float = 0.5):
        """Introduce pathogen and track system response."""
        self.pathogen_load = severity
        # Activate macrophages
        for cell in self.cells:
            if cell.cell_type == 'macrophage' and self.rng.random() < severity:
                cell.activation = 1.0
                cell.cytokine_level = 1.0
    
    def step(self) -> Dict:
        """Execute one signaling step."""
        # 1. Cytokine production (scaled by feedback_gain)
        for cell in self.cells:
            if not cell.active:
                continue
            for cytokine, sensitivity in cell.receptors.items():
                production = cell.activation * sensitivity * 0.1 * self.feedback_gain
                self.cytokine_field[cytokine][cell.id] += production
        
        # 2. Signal reception and activation update
        for cell in self.cells:
            if not cell.active:
                continue
            
            total_signal = 0
            for neighbor_id in self.adjacency.get(cell.id, []):
                neighbor = self.cells[neighbor_id]
                if not neighbor.active:
                    continue
                for cytokine, sensitivity in cell.receptors.items():
                    signal = neighbor.cytokine_level * sensitivity * 0.01 * self.feedback_gain
                    total_signal += signal
            
            # Memory effect (scaled by memory_depth)
            memory_boost = cell.memory * 0.05 * self.memory_depth
            
            # Update activation
            new_activation = cell.activation * 0.9 + total_signal * 0.1 + memory_boost
            
            # Threshold gating
            new_activation = np.clip(new_activation, 0, 1)
            
            cell.activation = new_activation
            cell.cytokine_level = cell.activation * 0.5
            
            # Update memory (scaled by memory_depth)
            cell.memory = cell.memory * 0.95 + cell.activation * 0.1 * self.memory_depth
        
        # 3. Pathogen clearance
        if self.pathogen_load > 0:
            total_activation = sum(c.activation for c in self.cells if c.active)
            clearance_rate = total_activation * 0.01
            self.pathogen_load = max(0, self.pathogen_load - clearance_rate)
            self.adaptation_score += clearance_rate
        
        # 4. Decay cytokine field
        for cytokine in self.cytokine_field:
            self.cytokine_field[cytokine] *= 0.95
        
        # 5. Measure
        state = self._measure()
        self.history.append(state)
        self.timestep += 1
        return state
    
    def _measure(self) -> Dict:
        active_cells = [c for c in self.cells if c.active]
        n_active = len(active_cells)
        
        # Amplitude
        mean_activation = sum(c.activation for c in active_cells) / max(n_active, 1)
        total_cytokines = sum(c.cytokine_level for c in active_cells)
        
        # Topology
        active_edges = 0
        total_edges = 0
        for i, neighbors in self.adjacency.items():
            if not self.cells[i].active:
                continue
            for j in neighbors:
                total_edges += 1
                if self.cells[j].active:
                    active_edges += 1
        signaling_connectivity = active_edges / max(total_edges, 1)
        
        n_components, component_sizes = self._find_components()
        largest_component = max(component_sizes) / max(n_active, 1) if component_sizes else 0
        
        type_counts = {}
        for c in active_cells:
            type_counts[c.cell_type] = type_counts.get(c.cell_type, 0) + 1
        type_probs = np.array(list(type_counts.values())) / max(sum(type_counts.values()), 1)
        type_entropy = -np.sum(type_probs * np.log2(type_probs + 1e-10))
        
        # Transport
        type_activations = {}
        for c in active_cells:
            if c.cell_type not in type_activations:
                type_activations[c.cell_type] = []
            type_activations[c.cell_type].append(c.activation)
        
        types = list(type_activations.keys())
        if len(types) > 1:
            act_matrix = np.zeros((len(types), max(len(v) for v in type_activations.values())))
            for i, t in enumerate(types):
                vals = type_activations[t]
                act_matrix[i, :len(vals)] = vals
            cov = np.cov(act_matrix)
            eigenvalues = np.sort(np.abs(np.linalg.eigvalsh(cov)))[::-1]
            cov_trace = float(np.sum(eigenvalues))
            cov_condition = float(eigenvalues[0] / (eigenvalues[-1] + 1e-10)) if len(eigenvalues) > 1 else 1.0
        else:
            eigenvalues = np.array([0])
            cov_trace = 0
            cov_condition = 1.0
        
        # Residual
        if len(types) > 1 and len(eigenvalues) > 1:
            total_energy = np.sum(eigenvalues)
            non_principal = float(np.sum(eigenvalues[1:]) / (total_energy + 1e-10))
        else:
            non_principal = 0
        
        cytokine_variances = [c.cytokine_level ** 2 for c in active_cells]
        signaling_noise = np.sqrt(np.mean(cytokine_variances)) if cytokine_variances else 0
        
        return {
            'timestep': self.timestep,
            'mean_activation': float(mean_activation),
            'total_cytokines': float(total_cytokines),
            'n_active': n_active,
            'signaling_connectivity': float(signaling_connectivity),
            'n_components': n_components,
            'largest_component': float(largest_component),
            'type_entropy': float(type_entropy),
            'cov_trace': cov_trace,
            'cov_condition': cov_condition,
            'cov_eigenvalues': eigenvalues.tolist(),
            'non_principal': non_principal,
            'signaling_noise': float(signaling_noise),
            'pathogen_load': float(self.pathogen_load),
            'adaptation_score': float(self.adaptation_score),
        }
    
    def _find_components(self) -> Tuple[int, List[int]]:
        visited = set()
        components = []
        for cell in self.cells:
            if not cell.active or cell.id in visited:
                continue
            component_size = 0
            queue = [cell.id]
            visited.add(cell.id)
            while queue:
                current = queue.pop(0)
                component_size += 1
                for neighbor_id in self.adjacency.get(current, []):
                    if neighbor_id not in visited and self.cells[neighbor_id].active:
                        visited.add(neighbor_id)
                        queue.append(neighbor_id)
            components.append(component_size)
        return len(components), components


# ═══════════════════════════════════════════════════════════════════
# Perturbation Protocols
# ═══════════════════════════════════════════════════════════════════

class PathogenAttack:
    @staticmethod
    def apply(network: ParametricImmuneNetwork, severity: float) -> str:
        network.introduce_pathogen(severity)
        return f"Introduced pathogen (severity={severity})"

class Immunosuppression:
    @staticmethod
    def apply(network: ParametricImmuneNetwork, severity: float) -> str:
        suppressed = 0
        for cell in network.cells:
            if cell.active and network.rng.random() < severity:
                cell.activation *= (1 - severity)
                cell.cytokine_level *= (1 - severity)
                suppressed += 1
        return f"Immunosuppressed {suppressed} cells"

class CellDepletion:
    @staticmethod
    def apply(network: ParametricImmuneNetwork, severity: float) -> str:
        depleted = 0
        for cell in network.cells:
            if cell.active and network.rng.random() < severity:
                cell.active = False
                depleted += 1
        return f"Depleted {depleted} cells"

class ReceptorBlockade:
    @staticmethod
    def apply(network: ParametricImmuneNetwork, severity: float) -> str:
        blocked = 0
        for cell in network.cells:
            if cell.active:
                for receptor in cell.receptors:
                    if network.rng.random() < severity:
                        cell.receptors[receptor] *= 0.1
                        blocked += 1
        return f"Blocked {blocked} receptors"


# ═══════════════════════════════════════════════════════════════════
# Sector Audit
# ═══════════════════════════════════════════════════════════════════

IMMUNE_SECTORS = {
    'amplitude': ['mean_activation', 'total_cytokines', 'n_active'],
    'topology': ['signaling_connectivity', 'n_components', 'largest_component', 'type_entropy'],
    'transport': ['cov_trace', 'cov_condition'],
    'residual': ['non_principal', 'signaling_noise'],
}


def extract_metrics(state: dict) -> dict:
    return {k: v for k, v in state.items() if k != 'timestep' and k != 'cov_eigenvalues'}


def compute_sector_alignment(before_metrics: list, after_metrics: list) -> dict:
    results = {}
    for sector_name, metrics in IMMUNE_SECTORS.items():
        before_vectors = []
        after_vectors = []
        for m in metrics:
            before_vals = [bm.get(m, 0) for bm in before_metrics]
            after_vals = [am.get(m, 0) for am in after_metrics]
            before_vectors.append(before_vals)
            after_vectors.append(after_vals)
        
        before_arr = np.array(before_vectors).T
        after_arr = np.array(after_vectors).T
        
        if before_arr.size == 0 or after_arr.size == 0:
            results[sector_name] = {'error': 'no data'}
            continue
        
        min_len = min(len(before_arr), len(after_arr))
        before_arr = before_arr[:min_len]
        after_arr = after_arr[:min_len]
        
        def cosine_sim(a, b):
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            if na == 0 or nb == 0:
                return 0.0
            return float(np.dot(a.flatten(), b.flatten()) / (na * nb))
        
        raw_sim = cosine_sim(before_arr, after_arr)
        before_norm = (before_arr - before_arr.mean(axis=0)) / (before_arr.std(axis=0) + 1e-8)
        after_norm = (after_arr - after_arr.mean(axis=0)) / (after_arr.std(axis=0) + 1e-8)
        norm_sim = cosine_sim(before_norm, after_norm)
        norm_survival = norm_sim - raw_sim
        
        results[sector_name] = {
            'raw_similarity': raw_sim,
            'normalized_similarity': norm_sim,
            'normalization_survival': norm_survival,
            'verdict': 'SURVIVES' if norm_survival > -0.1 else 'COLLAPSES',
        }
    return results


def compute_gauge_fraction(sector_data: dict) -> float:
    sectors = ['amplitude', 'topology', 'transport', 'residual']
    surviving = 0
    total = 0
    for sector in sectors:
        data = sector_data.get(sector, {})
        if 'error' in data:
            continue
        total += 1
        if data.get('verdict') == 'SURVIVES':
            surviving += 1
    return surviving / max(total, 1)


# ═══════════════════════════════════════════════════════════════════
# Main Experiment: Parameter Sweep
# ═══════════════════════════════════════════════════════════════════

def run_single_condition(memory_depth: float, feedback_gain: float, seed: int = 42) -> dict:
    """Run a single (memory_depth, feedback_gain) condition."""
    perturbations = [
        ('P1_pathogen', PathogenAttack, 0.3),
        ('P2_immunosuppression', Immunosuppression, 0.5),
        ('P3_depletion', CellDepletion, 0.4),
        ('P4_blockade', ReceptorBlockade, 0.5),
    ]
    
    all_sectors = []
    adaptation_scores = []
    
    for pname, protocol, severity in perturbations:
        network = ParametricImmuneNetwork(
            n_cells=100, seed=seed,
            memory_depth=memory_depth,
            feedback_gain=feedback_gain
        )
        
        # Baseline
        history_before = []
        for _ in range(20):
            state = network.step()
            history_before.append(extract_metrics(state))
        
        # Perturb
        protocol.apply(network, severity)
        
        # Recovery
        history_after = []
        for _ in range(50):
            state = network.step()
            history_after.append(extract_metrics(state))
        
        # Sector audit
        before_m = [extract_metrics(h) for h in history_before]
        after_m = [extract_metrics(h) for h in history_after]
        sector_results = compute_sector_alignment(before_m, after_m)
        all_sectors.append(sector_results)
        
        # Adaptation score: pathogen clearance efficiency
        final_pathogen = history_after[-1].get('pathogen_load', 0) if history_after else 0
        initial_pathogen = 0.3  # severity
        adaptation_scores.append(1.0 - final_pathogen / max(initial_pathogen, 1e-8))
    
    avg_G = np.mean([compute_gauge_fraction(s) for s in all_sectors])
    avg_adaptation = np.mean(adaptation_scores)
    
    return {
        'memory_depth': memory_depth,
        'feedback_gain': feedback_gain,
        'G': float(avg_G),
        'adaptation': float(avg_adaptation),
    }


def run_study_001h():
    print("=" * 70)
    print("Study 001H — Persistence–Adaptation Tradeoff")
    print("=" * 70)
    
    print("\n  MAPPING THE TRADEOFF SURFACE")
    print("  Sweep memory_depth × feedback_gain")
    print("  Measure G and adaptation accuracy")
    
    # Parameter sweep
    memory_values = np.linspace(0.0, 1.0, 6)  # 0, 0.2, 0.4, 0.6, 0.8, 1.0
    feedback_values = np.linspace(0.0, 2.0, 6)  # 0, 0.4, 0.8, 1.2, 1.6, 2.0
    
    results = []
    
    print(f"\n  Sweeping {len(memory_values)} × {len(feedback_values)} = {len(memory_values) * len(feedback_values)} conditions")
    
    for md in memory_values:
        for fg in feedback_values:
            result = run_single_condition(md, fg)
            results.append(result)
    
    # ─── Print Grid ───
    print(f"\n{'=' * 70}")
    print("G(memory_depth, feedback_gain)")
    print(f"{'=' * 70}")
    
    # Reshape into grid
    n_md = len(memory_values)
    n_fg = len(feedback_values)
    
    G_grid = np.zeros((n_md, n_fg))
    A_grid = np.zeros((n_md, n_fg))
    
    for r in results:
        md_idx = np.argmin(np.abs(memory_values - r['memory_depth']))
        fg_idx = np.argmin(np.abs(feedback_values - r['feedback_gain']))
        G_grid[md_idx, fg_idx] = r['G']
        A_grid[md_idx, fg_idx] = r['adaptation']
    
    # Print G grid
    header = "  md\\fg  " + "  ".join([f"{fg:.1f}" for fg in feedback_values])
    print(f"\n  {header}")
    print(f"  {'─' * len(header)}")
    for i, md in enumerate(memory_values):
        row = "  " + f"{md:.1f}   " + "  ".join([f"{G_grid[i,j]:.3f}" for j in range(n_fg)])
        print(row)
    
    # Print A grid
    print(f"\n  ADAPTATION(memory_depth, feedback_gain)")
    print(f"\n  {header}")
    print(f"  {'─' * len(header)}")
    for i, md in enumerate(memory_values):
        row = "  " + f"{md:.1f}   " + "  ".join([f"{A_grid[i,j]:.3f}" for j in range(n_fg)])
        print(row)
    
    # ─── Tradeoff Analysis ───
    print(f"\n{'=' * 70}")
    print("TRADEOFF ANALYSIS")
    print(f"{'=' * 70}")
    
    # Find Pareto-optimal points (maximize both G and adaptation)
    pareto_points = []
    for r in results:
        is_pareto = True
        for r2 in results:
            if r2['G'] >= r['G'] and r2['adaptation'] >= r['adaptation']:
                if r2['G'] > r['G'] or r2['adaptation'] > r['adaptation']:
                    is_pareto = False
                    break
        if is_pareto:
            pareto_points.append(r)
    
    pareto_points.sort(key=lambda x: x['G'])
    
    print(f"\n  Pareto-optimal points ({len(pareto_points)}):")
    for p in pareto_points:
        print(f"    md={p['memory_depth']:.1f}  fg={p['feedback_gain']:.1f}  G={p['G']:.3f}  A={p['adaptation']:.3f}")
    
    # Tradeoff correlation
    G_vals = [r['G'] for r in results]
    A_vals = [r['adaptation'] for r in results]
    correlation = np.corrcoef(G_vals, A_vals)[0, 1]
    
    print(f"\n  G-Adaptation correlation: {correlation:.3f}")
    if correlation < -0.3:
        print(f"  TRADEOFF CONFIRMED: G and adaptation are negatively correlated")
    elif correlation > 0.3:
        print(f"  NO TRADEOFF: G and adaptation are positively correlated")
    else:
        print(f"  WEAK RELATIONSHIP: G and adaptation are weakly correlated")
    
    # ─── Extreme Points ───
    print(f"\n{'=' * 70}")
    print("EXTREME POINTS")
    print(f"{'=' * 70}")
    
    max_G = max(results, key=lambda x: x['G'])
    max_A = max(results, key=lambda x: x['adaptation'])
    
    print(f"\n  Highest G:  md={max_G['memory_depth']:.1f}  fg={max_G['feedback_gain']:.1f}  G={max_G['G']:.3f}  A={max_G['adaptation']:.3f}")
    print(f"  Highest A:  md={max_A['memory_depth']:.1f}  fg={max_A['feedback_gain']:.1f}  G={max_A['G']:.3f}  A={max_A['adaptation']:.3f}")
    
    # ─── Landscape ───
    print(f"\n{'=' * 70}")
    print("PERSISTENCE ALLOCATION LANDSCAPE")
    print(f"{'=' * 70}")
    
    with open('/home/student/sgp_core_v2/post_omega_study_001/gauge_geometry_results.json', 'r') as f:
        geometry = json.load(f)
    
    # Add tradeoff points
    geometry['Immune-max-G'] = {
        'S': 0.5, 'F': 0.5, 'G': max_G['G'],
        'regime': 'tradeoff-optimal',
    }
    geometry['Immune-max-A'] = {
        'S': 0.5, 'F': 0.5, 'G': max_A['G'],
        'regime': 'tradeoff-optimal',
    }
    
    for name, data in geometry.items():
        if 'regime' in data:
            print(f"  {name:25s}: G={data['G']:.3f}  regime={data['regime']}")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/tradeoff_results.json', 'w') as f:
        json.dump({
            'results': results,
            'pareto_points': pareto_points,
            'correlation': float(correlation),
            'max_G': max_G,
            'max_A': max_A,
        }, f, indent=2, default=str)
    
    with open('/home/student/sgp_core_v2/post_omega_study_001/gauge_geometry_results.json', 'w') as f:
        json.dump(geometry, f, indent=2)
    
    print(f"\nResults saved")
    print(f"{'=' * 70}")
    
    return results, pareto_points


if __name__ == '__main__':
    run_study_001h()
