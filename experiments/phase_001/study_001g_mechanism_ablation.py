"""
SGI Post-Ω Study 001G — Mechanism Ablation Protocol

Reverse-causal dissection of immune persistence.
Remove one mechanism at a time, measure G.

Ablations:
1. No memory (activation decays instantly)
2. No receptor specificity (all cells respond equally)
3. No clonal expansion (no amplification of successful responses)
4. No compartmentalization (flat network, no type-preferential connectivity)
5. No threshold gating (activation unbounded)
6. No cytokine feedback (no cell-cell signaling)
7. No suppression (no regulatory mechanisms)

Starting point: full immune system (G=0.875)
"""

import numpy as np
import json
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

sys.path.insert(0, '/home/student/sgp_core_v2/post_omega_study_001')


# ═══════════════════════════════════════════════════════════════════
# Ablatable Immune System
# ═══════════════════════════════════════════════════════════════════

@dataclass
class AblatableCell:
    id: int
    cell_type: str
    activation: float = 0.0
    cytokine_level: float = 0.0
    active: bool = True
    receptors: Dict[str, float] = field(default_factory=dict)
    # Memory
    memory: float = 0.0
    memory_decay: float = 0.95
    # Clonal expansion
    clonal_amplification: float = 1.0
    # Suppression
    suppression_level: float = 0.0


class AblatableImmuneNetwork:
    """Immune network with individually removable mechanisms."""
    
    def __init__(self, n_cells: int = 100, seed: int = 42,
                 enable_memory: bool = True,
                 enable_receptor_specificity: bool = True,
                 enable_clonal_expansion: bool = True,
                 enable_compartmentalization: bool = True,
                 enable_threshold_gating: bool = True,
                 enable_cytokine_feedback: bool = True,
                 enable_suppression: bool = True):
        
        self.rng = np.random.RandomState(seed)
        self.n_cells = n_cells
        self.timestep = 0
        self.history = []
        
        # Mechanism flags
        self.enable_memory = enable_memory
        self.enable_receptor_specificity = enable_receptor_specificity
        self.enable_clonal_expansion = enable_clonal_expansion
        self.enable_compartmentalization = enable_compartmentalization
        self.enable_threshold_gating = enable_threshold_gating
        self.enable_cytokine_feedback = enable_cytokine_feedback
        self.enable_suppression = enable_suppression
        
        # Cell types
        type_probs = [0.30, 0.25, 0.25, 0.20]
        type_names = ['macrophage', 't_cell', 'b_cell', 'dendritic']
        
        self.cells: List[AblatableCell] = []
        for i in range(n_cells):
            ct = self.rng.choice(type_names, p=type_probs)
            cell = AblatableCell(
                id=i,
                cell_type=ct,
                activation=self.rng.uniform(0.0, 0.1),
                cytokine_level=self.rng.uniform(0.0, 0.05),
            )
            
            # Receptors (only if receptor specificity enabled)
            if self.enable_receptor_specificity:
                if ct == 'macrophage':
                    cell.receptors = {'il1': 1.0, 'tnf': 0.8, 'il6': 0.6}
                elif ct == 't_cell':
                    cell.receptors = {'il2': 1.0, 'ifn': 0.8, 'il4': 0.5}
                elif ct == 'b_cell':
                    cell.receptors = {'il4': 1.0, 'il6': 0.8, 'il2': 0.5}
                else:
                    cell.receptors = {'il1': 0.8, 'il12': 1.0, 'ifn': 0.7}
            else:
                # No specificity: all cells respond to all signals equally
                cell.receptors = {'il1': 1.0, 'il2': 1.0, 'il4': 1.0, 
                                  'il6': 1.0, 'tnf': 1.0, 'ifn': 1.0, 'il12': 1.0}
            
            self.cells.append(cell)
        
        # Build network
        self.adjacency: Dict[int, List[int]] = {}
        self._build_network()
        
        # Cytokine field
        self.cytokine_field = {
            'il1': np.zeros(n_cells),
            'il2': np.zeros(n_cells),
            'il4': np.zeros(n_cells),
            'il6': np.zeros(n_cells),
            'tnf': np.zeros(n_cells),
            'ifn': np.zeros(n_cells),
            'il12': np.zeros(n_cells),
        }
    
    def _build_network(self):
        """Build network with optional compartmentalization."""
        for i in range(self.n_cells):
            n_connections = self.rng.randint(3, 9)
            
            if self.enable_compartmentalization:
                # Compartmentalized: prefer same cell type (70%)
                same_type = [j for j in range(self.n_cells) if j != i and 
                            self.cells[j].cell_type == self.cells[i].cell_type]
                other_type = [j for j in range(self.n_cells) if j != i and 
                             self.cells[j].cell_type != self.cells[i].cell_type]
            else:
                # Not compartmentalized: random connectivity
                same_type = [j for j in range(self.n_cells) if j != i]
                other_type = []
            
            targets = []
            if same_type and self.rng.random() < 0.7:
                n_same = min(n_connections, len(same_type))
                targets.extend(self.rng.choice(same_type, size=n_same, replace=False))
                n_connections -= n_same
            
            if other_type and n_connections > 0:
                n_other = min(n_connections, len(other_type))
                targets.extend(self.rng.choice(other_type, size=n_other, replace=False))
            
            self.adjacency[i] = list(set(targets))
    
    def step(self) -> Dict:
        """Execute one signaling step with ablation-aware dynamics."""
        
        # 1. Cytokine production (only if feedback enabled)
        if self.enable_cytokine_feedback:
            for cell in self.cells:
                if not cell.active:
                    continue
                for cytokine, sensitivity in cell.receptors.items():
                    production = cell.activation * sensitivity * 0.1
                    self.cytokine_field[cytokine][cell.id] += production
        
        # 2. Signal reception and activation update
        for cell in self.cells:
            if not cell.active:
                continue
            
            total_signal = 0
            
            if self.enable_cytokine_feedback:
                for neighbor_id in self.adjacency.get(cell.id, []):
                    neighbor = self.cells[neighbor_id]
                    if not neighbor.active:
                        continue
                    for cytokine, sensitivity in cell.receptors.items():
                        signal = neighbor.cytokine_level * sensitivity * 0.01
                        total_signal += signal
            
            # Memory effect
            memory_boost = 0
            if self.enable_memory:
                memory_boost = cell.memory * 0.05
                cell.memory = cell.memory * cell.memory_decay + cell.activation * 0.1
            
            # Clonal expansion effect
            clonal_boost = 0
            if self.enable_clonal_expansion:
                clonal_boost = cell.activation * (cell.clonal_amplification - 1.0) * 0.1
                # Amplify based on recent success
                if cell.activation > 0.5:
                    cell.clonal_amplification = min(3.0, cell.clonal_amplification * 1.05)
                else:
                    cell.clonal_amplification = max(0.5, cell.clonal_amplification * 0.95)
            
            # Suppression effect
            suppression = 0
            if self.enable_suppression:
                suppression = cell.suppression_level * cell.activation * 0.2
                # Regulatory cells suppress overactive neighbors
                if cell.activation > 0.7:
                    cell.suppression_level = min(1.0, cell.suppression_level + 0.05)
                else:
                    cell.suppression_level = max(0.0, cell.suppression_level - 0.02)
            
            # Update activation
            new_activation = cell.activation * 0.9 + total_signal * 0.1 + memory_boost + clonal_boost - suppression
            
            # Threshold gating
            if self.enable_threshold_gating:
                new_activation = np.clip(new_activation, 0, 1)
            else:
                new_activation = max(0, new_activation)  # Only lower bound
            
            cell.activation = new_activation
            cell.cytokine_level = cell.activation * 0.5
        
        # 3. Decay cytokine field
        for cytokine in self.cytokine_field:
            self.cytokine_field[cytokine] *= 0.95
        
        # 4. Measure
        state = self._measure()
        self.history.append(state)
        self.timestep += 1
        return state
    
    def _measure(self) -> Dict:
        """Measure all observables."""
        active_cells = [c for c in self.cells if c.active]
        n_active = len(active_cells)
        
        # Amplitude
        total_activation = sum(c.activation for c in active_cells)
        total_cytokines = sum(c.cytokine_level for c in active_cells)
        mean_activation = total_activation / max(n_active, 1)
        
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
# Perturbation Protocols (same as 001C)
# ═══════════════════════════════════════════════════════════════════

class PathogenAttack:
    @staticmethod
    def apply(network: AblatableImmuneNetwork, severity: float) -> str:
        activated = 0
        for cell in network.cells:
            if cell.cell_type == 'macrophage' and network.rng.random() < severity:
                cell.activation = 1.0
                cell.cytokine_level = 1.0
                activated += 1
        return f"Pathogen activated {activated} macrophages"

class Immunosuppression:
    @staticmethod
    def apply(network: AblatableImmuneNetwork, severity: float) -> str:
        suppressed = 0
        for cell in network.cells:
            if cell.active and network.rng.random() < severity:
                cell.activation *= (1 - severity)
                cell.cytokine_level *= (1 - severity)
                suppressed += 1
        return f"Immunosuppressed {suppressed} cells"

class CellDepletion:
    @staticmethod
    def apply(network: AblatableImmuneNetwork, severity: float) -> str:
        depleted = 0
        for cell in network.cells:
            if cell.active and network.rng.random() < severity:
                cell.active = False
                depleted += 1
        return f"Depleted {depleted} cells"

class ReceptorBlockade:
    @staticmethod
    def apply(network: AblatableImmuneNetwork, severity: float) -> str:
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
# Ablation Protocol
# ═══════════════════════════════════════════════════════════════════

ABLATION_CONDITIONS = [
    ('full', 'Full immune system (baseline)', {}),
    ('no_memory', 'Memory removed', {'enable_memory': False}),
    ('no_receptor_specificity', 'Receptor specificity removed', {'enable_receptor_specificity': False}),
    ('no_clonal_expansion', 'Clonal expansion removed', {'enable_clonal_expansion': False}),
    ('no_compartmentalization', 'Compartmentalization removed', {'enable_compartmentalization': False}),
    ('no_threshold_gating', 'Threshold gating removed', {'enable_threshold_gating': False}),
    ('no_cytokine_feedback', 'Cytokine feedback removed', {'enable_cytokine_feedback': False}),
    ('no_suppression', 'Suppression removed', {'enable_suppression': False}),
]

PERTURBATIONS = [
    ('P1_pathogen', PathogenAttack, 0.3),
    ('P2_immunosuppression', Immunosuppression, 0.5),
    ('P3_depletion', CellDepletion, 0.4),
    ('P4_blockade', ReceptorBlockade, 0.5),
]


def run_ablation(condition_name: str, description: str, kwargs: dict) -> dict:
    """Run a single ablation condition."""
    print(f"\n{'─' * 50}")
    print(f"Condition: {condition_name}")
    print(f"Description: {description}")
    print(f"{'─' * 50}")
    
    all_sectors = []
    
    for pname, protocol, severity in PERTURBATIONS:
        # Create network with ablation
        network = AblatableImmuneNetwork(n_cells=100, seed=42, **kwargs)
        
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
    
    # Aggregate
    avg_G = np.mean([compute_gauge_fraction(s) for s in all_sectors])
    
    sector_survival = {'amplitude': 0, 'topology': 0, 'transport': 0, 'residual': 0}
    for sd in all_sectors:
        for sector in sector_survival:
            if sd.get(sector, {}).get('verdict') == 'SURVIVES':
                sector_survival[sector] += 1
    
    print(f"  G = {avg_G:.3f}")
    for sector, count in sector_survival.items():
        print(f"    {sector:12s}: {count}/4 perturbations")
    
    return {
        'condition': condition_name,
        'description': description,
        'G': float(avg_G),
        'sector_survival': sector_survival,
    }


def run_study_001g():
    print("=" * 70)
    print("Study 001G — Mechanism Ablation Protocol")
    print("=" * 70)
    
    print("\n  REVERSE-CAUSAL IMMUNE DISSECTION")
    print("  Remove one mechanism at a time, measure G")
    
    results = []
    
    for condition_name, description, kwargs in ABLATION_CONDITIONS:
        result = run_ablation(condition_name, description, kwargs)
        results.append(result)
    
    # ─── Degradation Profile ───
    print(f"\n{'=' * 70}")
    print("DEGRADATION PROFILE")
    print(f"{'=' * 70}")
    
    full_G = results[0]['G']
    
    print(f"\n  {'Condition':30s}  {'G':>6s}  {'ΔG':>8s}  {'Degradation':>12s}")
    print(f"  {'─' * 60}")
    
    for r in results:
        delta_G = r['G'] - full_G
        degradation = 'none' if r['condition'] == 'full' else (
            'catastrophic' if r['G'] < 0.2 else
            'severe' if r['G'] < 0.4 else
            'moderate' if r['G'] < 0.6 else
            'mild' if r['G'] < 0.8 else
            'none'
        )
        print(f"  {r['condition']:30s}  {r['G']:.3f}  {delta_G:+.3f}  {degradation}")
    
    # ─── Critical Mechanism Identification ───
    print(f"\n{'=' * 70}")
    print("CRITICAL MECHANISM IDENTIFICATION")
    print(f"{'=' * 70}")
    
    # Sort by G impact
    sorted_results = sorted(results[1:], key=lambda x: x['G'])
    
    print(f"\n  Mechanisms ranked by G impact (lowest G = most critical):")
    for i, r in enumerate(sorted_results):
        impact = full_G - r['G']
        print(f"  {i+1}. {r['condition']:30s}  G={r['G']:.3f}  impact={impact:.3f}")
    
    # ─── Degradation Type ───
    print(f"\n{'=' * 70}")
    print("DEGRADATION TYPE ANALYSIS")
    print(f"{'=' * 70}")
    
    G_values = [r['G'] for r in results[1:]]  # exclude full
    
    # Check for catastrophic drop (single mechanism causes >50% G loss)
    catastrophic = [r for r in results[1:] if r['G'] < full_G * 0.5]
    gradual = [r for r in results[1:] if 0.5 <= r['G'] < full_G * 0.8]
    
    print(f"\n  Full system G: {full_G:.3f}")
    print(f"  Catastrophic drops (>50% loss): {len(catastrophic)}")
    for r in catastrophic:
        print(f"    - {r['condition']}: G={r['G']:.3f}")
    print(f"  Gradual degradation (20-50% loss): {len(gradual)}")
    for r in gradual:
        print(f"    - {r['condition']}: G={r['G']:.3f}")
    
    if len(catastrophic) > 0:
        print(f"\n  DEGRADATION TYPE: SYNERGISTIC")
        print(f"  Immune persistence depends on a closed mechanism ensemble.")
        print(f"  Removing any critical mechanism causes catastrophic G loss.")
    else:
        print(f"\n  DEGRADATION TYPE: ADDITIVE")
        print(f"  Each mechanism contributes independently to G.")
    
    # ─── Landscape Update ───
    print(f"\n{'=' * 70}")
    print("PERSISTENCE ALLOCATION LANDSCAPE (all conditions)")
    print(f"{'=' * 70}")
    
    with open('/home/student/sgp_core_v2/post_omega_study_001/gauge_geometry_results.json', 'r') as f:
        geometry = json.load(f)
    
    for r in results:
        key = f"Immune-{r['condition']}"
        geometry[key] = {
            'S': 0.5,  # Approximate
            'F': 0.5,
            'G': r['G'],
            'regime': 'ablated',
        }
    
    # Print landscape
    immune_results = [(r['condition'], r['G']) for r in results]
    for name, G in immune_results:
        print(f"  Immune-{name:25s}: G={G:.3f}")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/ablation_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    with open('/home/student/sgp_core_v2/post_omega_study_001/gauge_geometry_results.json', 'w') as f:
        json.dump(geometry, f, indent=2)
    
    print(f"\nResults saved")
    print(f"{'=' * 70}")
    
    return results


if __name__ == '__main__':
    run_study_001g()
