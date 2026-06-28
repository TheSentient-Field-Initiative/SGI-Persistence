"""
SGI Post-Ω Study 001B.R2 + 001C: Persistence Allocation Geometry + Immune Signaling Network

001B.R2: Formalize P=(S,F) phase space, classify existing systems
001C: Immune signaling network, test H1, place on persistence landscape
"""

import numpy as np
import json
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

sys.path.insert(0, '/home/student/sgp_core_v2/post_omega_study_001')


# ═══════════════════════════════════════════════════════════════════
# PART 1: Persistence Allocation Geometry (001B.R2)
# ═══════════════════════════════════════════════════════════════════

def classify_persistence_regime(S: float, F: float, threshold: float = 0.3) -> str:
    """Classify system into persistence allocation regime.
    
    P = (S, F) where:
    S = structural persistence (topology survival under normalization)
    F = functional persistence (throughput/coordination survival)
    
    Regimes:
    - high S, low F: rigid persistence
    - low S, high F: adaptive persistence
    - high S, high F: resilient persistence
    - low S, low F: collapse regime
    """
    high_S = S > threshold
    high_F = F > threshold
    
    if high_S and high_F:
        return "resilient"
    elif high_S and not high_F:
        return "rigid"
    elif not high_S and high_F:
        return "adaptive"
    else:
        return "collapse"


def compute_coupling_trajectory(S: float, F: float) -> float:
    """Compute coupling direction in P=(S,F) space.
    
    Returns angle from diagonal:
    - positive = favors structural persistence
    - negative = favors functional persistence
    """
    return S - F


def run_persistence_geometry():
    """Run persistence allocation geometry analysis."""
    print("=" * 70)
    print("Study 001B.R2: Persistence Allocation Geometry")
    print("=" * 70)
    
    # Load existing results
    with open('/home/student/sgp_core_v2/post_omega_study_001/dissociation_audit_results.json', 'r') as f:
        dissociation = json.load(f)
    
    systems = {}
    
    for system_name in ['Distributed System', 'Ant Colony']:
        data = dissociation.get(system_name, {})
        structural_scores = data.get('structural_scores', [])
        functional_scores = data.get('functional_scores', [])
        
        if not structural_scores or not functional_scores:
            continue
        
        S = np.mean(structural_scores)
        F = np.mean(functional_scores)
        
        # Normalize F to [0,1] for geometry (ant colony F can exceed 1)
        F_normalized = min(F, 1.0)
        
        regime = classify_persistence_regime(S, F_normalized)
        coupling = compute_coupling_trajectory(S, F_normalized)
        
        systems[system_name] = {
            'S': float(S),
            'F': float(F),
            'F_normalized': float(F_normalized),
            'regime': regime,
            'coupling': float(coupling),
        }
        
        print(f"\n  {system_name}:")
        print(f"    S (structural) = {S:.3f}")
        print(f"    F (functional) = {F:.3f} (normalized: {F_normalized:.3f})")
        print(f"    Regime: {regime}")
        print(f"    Coupling direction: {coupling:+.3f}")
    
    # Phase space visualization (text-based)
    print(f"\n{'─' * 50}")
    print("PERSISTENCE ALLOCATION LANDSCAPE")
    print(f"{'─' * 50}")
    print("  F (functional)")
    print("  ↑")
    print("  │")
    print("  │  adaptive    resilient")
    print("  │  (low S,     (high S,")
    print("  │   high F)     high F)")
    print("  │")
    print("  ├──────────────────────────→ S (structural)")
    print("  │")
    print("  │  collapse    rigid")
    print("  │  (low S,     (high S,")
    print("  │   low F)      low F)")
    print("  │")
    
    for name, data in systems.items():
        S, F = data['S'], data['F_normalized']
        # Map to grid position
        col = int(S * 20)
        row = int((1 - F) * 10)
        marker = "★" if "Distributed" in name else "●"
        print(f"  {marker} = {name[:15]}")
    
    print(f"\n  Legend: ★ = Distributed System, ● = Ant Colony")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/persistence_geometry_results.json', 'w') as f:
        json.dump(systems, f, indent=2)
    
    print(f"\nResults saved to persistence_geometry_results.json")
    print(f"{'=' * 70}")
    
    return systems


# ═══════════════════════════════════════════════════════════════════
# PART 2: Immune Signaling Network (001C)
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ImmuneCell:
    id: int
    cell_type: str  # 'macrophage', 't_cell', 'b_cell', 'dendritic'
    activation: float = 0.0
    cytokine_level: float = 0.0
    active: bool = True
    receptors: Dict[str, float] = field(default_factory=dict)


class ImmuneSignalingNetwork:
    """Simplified immune signaling network with cytokine-mediated coordination."""
    
    def __init__(self, n_cells: int = 100, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.n_cells = n_cells
        self.timestep = 0
        self.history = []
        
        # Cell types: 30% macrophage, 25% t_cell, 25% b_cell, 20% dendritic
        type_probs = [0.30, 0.25, 0.25, 0.20]
        type_names = ['macrophage', 't_cell', 'b_cell', 'dendritic']
        
        self.cells: List[ImmuneCell] = []
        for i in range(n_cells):
            ct = self.rng.choice(type_names, p=type_probs)
            cell = ImmuneCell(
                id=i,
                cell_type=ct,
                activation=self.rng.uniform(0.0, 0.1),
                cytokine_level=self.rng.uniform(0.0, 0.05),
            )
            # Receptors: different cell types respond to different signals
            if ct == 'macrophage':
                cell.receptors = {'il1': 1.0, 'tnf': 0.8, 'il6': 0.6}
            elif ct == 't_cell':
                cell.receptors = {'il2': 1.0, 'ifn': 0.8, 'il4': 0.5}
            elif ct == 'b_cell':
                cell.receptors = {'il4': 1.0, 'il6': 0.8, 'il2': 0.5}
            else:  # dendritic
                cell.receptors = {'il1': 0.8, 'il12': 1.0, 'ifn': 0.7}
            
            self.cells.append(cell)
        
        # Signaling network: adjacency based on proximity
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
        """Build signaling network: each cell connects to 3-8 neighbors."""
        for i in range(self.n_cells):
            n_connections = self.rng.randint(3, 9)
            # Prefer same cell type (70%)
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
    
    def step(self) -> Dict:
        """Execute one signaling step."""
        # 1. Cells produce cytokines based on activation
        for cell in self.cells:
            if not cell.active:
                continue
            # Cytokine production proportional to activation
            for cytokine, sensitivity in cell.receptors.items():
                production = cell.activation * sensitivity * 0.1
                self.cytokine_field[cytokine][cell.id] += production
        
        # 2. Cells receive cytokine signals from neighbors
        for cell in self.cells:
            if not cell.active:
                continue
            total_signal = 0
            for neighbor_id in self.adjacency.get(cell.id, []):
                neighbor = self.cells[neighbor_id]
                if not neighbor.active:
                    continue
                # Signal = neighbor's cytokine * receptor sensitivity
                for cytokine, sensitivity in cell.receptors.items():
                    signal = neighbor.cytokine_level * sensitivity * 0.01
                    total_signal += signal
            
            # Update activation
            cell.activation = np.clip(
                cell.activation * 0.9 + total_signal * 0.1,
                0, 1
            )
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
        
        # ─── Amplitude Sector ───
        total_activation = sum(c.activation for c in active_cells)
        total_cytokines = sum(c.cytokine_level for c in active_cells)
        mean_activation = total_activation / max(n_active, 1)
        
        # ─── Topology Sector ───
        # Signaling connectivity: fraction of active edges
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
        
        # Component structure
        n_components, component_sizes = self._find_components()
        largest_component = max(component_sizes) / max(n_active, 1) if component_sizes else 0
        
        # Type distribution entropy
        type_counts = {}
        for c in active_cells:
            type_counts[c.cell_type] = type_counts.get(c.cell_type, 0) + 1
        type_probs = np.array(list(type_counts.values())) / max(sum(type_counts.values()), 1)
        type_entropy = -np.sum(type_probs * np.log2(type_probs + 1e-10))
        
        # ─── Transport Sector ───
        # Activation covariance across cell types
        type_activations = {}
        for c in active_cells:
            if c.cell_type not in type_activations:
                type_activations[c.cell_type] = []
            type_activations[c.cell_type].append(c.activation)
        
        # Compute covariance between types
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
        
        # ─── Residual Sector ───
        # Non-principal activation modes
        if len(types) > 1 and len(eigenvalues) > 1:
            total_energy = np.sum(eigenvalues)
            non_principal = float(np.sum(eigenvalues[1:]) / (total_energy + 1e-10))
        else:
            non_principal = 0
        
        # Signaling noise: variance of cytokine levels within types
        cytokine_variances = []
        for c in active_cells:
            cytokine_variances.append(c.cytokine_level ** 2)
        signaling_noise = np.sqrt(np.mean(cytokine_variances)) if cytokine_variances else 0
        
        return {
            'timestep': self.timestep,
            # Amplitude
            'mean_activation': float(mean_activation),
            'total_cytokines': float(total_cytokines),
            'n_active': n_active,
            # Topology
            'signaling_connectivity': float(signaling_connectivity),
            'n_components': n_components,
            'largest_component': float(largest_component),
            'type_entropy': float(type_entropy),
            # Transport
            'cov_trace': cov_trace,
            'cov_condition': cov_condition,
            'cov_eigenvalues': eigenvalues.tolist(),
            # Residual
            'non_principal': non_principal,
            'signaling_noise': float(signaling_noise),
        }
    
    def _find_components(self) -> Tuple[int, List[int]]:
        """Find connected components in active subgraph."""
        visited = set()
        components = []
        
        for cell in self.cells:
            if not cell.active or cell.id in visited:
                continue
            # BFS
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


# ─── Immune Perturbation Protocols ───

class ImmunePerturbation:
    @staticmethod
    def apply(network: ImmuneSignalingNetwork, severity: float) -> str:
        raise NotImplementedError

class PathogenAttack(ImmunePerturbation):
    """P1: Introduce pathogen that activates macrophages."""
    @staticmethod
    def apply(network: ImmuneSignalingNetwork, severity: float) -> str:
        activated = 0
        for cell in network.cells:
            if cell.cell_type == 'macrophage' and network.rng.random() < severity:
                cell.activation = 1.0
                cell.cytokine_level = 1.0
                activated += 1
        return f"Pathogen activated {activated} macrophages"

class Immunosuppression(ImmunePerturbation):
    """P2: Suppress cell activation."""
    @staticmethod
    def apply(network: ImmuneSignalingNetwork, severity: float) -> str:
        suppressed = 0
        for cell in network.cells:
            if cell.active and network.rng.random() < severity:
                cell.activation *= (1 - severity)
                cell.cytokine_level *= (1 - severity)
                suppressed += 1
        return f"Immunosuppressed {suppressed} cells"

class CellDepletion(ImmunePerturbation):
    """P3: Remove immune cells."""
    @staticmethod
    def apply(network: ImmuneSignalingNetwork, severity: float) -> str:
        depleted = 0
        for cell in network.cells:
            if cell.active and network.rng.random() < severity:
                cell.active = False
                depleted += 1
        return f"Depleted {depleted} cells"

class ReceptorBlockade(ImmunePerturbation):
    """P4: Block cytokine receptors."""
    @staticmethod
    def apply(network: ImmuneSignalingNetwork, severity: float) -> str:
        blocked = 0
        for cell in network.cells:
            if cell.active:
                for receptor in cell.receptors:
                    if network.rng.random() < severity:
                        cell.receptors[receptor] *= 0.1
                        blocked += 1
        return f"Blocked {blocked} receptors"


# ─── Sector Audit for Immune System ───

IMMUNE_SECTORS = {
    'amplitude': {
        'metrics': ['mean_activation', 'total_cytokines', 'n_active'],
        'expected_survival': False,
    },
    'topology': {
        'metrics': ['signaling_connectivity', 'n_components', 'largest_component', 'type_entropy'],
        'expected_survival': True,
    },
    'transport': {
        'metrics': ['cov_trace', 'cov_condition'],
        'expected_survival': True,
    },
    'residual': {
        'metrics': ['non_principal', 'signaling_noise'],
        'expected_survival': True,
    },
}


def extract_immune_metrics(state: dict) -> dict:
    """Extract sector metrics from immune state."""
    return {k: v for k, v in state.items() if k != 'timestep' and k != 'cov_eigenvalues'}


def compute_immune_sector_alignment(before_metrics: list, after_metrics: list) -> dict:
    """Compute sector alignment for immune metrics."""
    results = {}
    
    for sector_name, sector_def in IMMUNE_SECTORS.items():
        metrics = sector_def['metrics']
        
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
        
        before_range = before_arr.max(axis=0) - before_arr.min(axis=0)
        after_range = after_arr.max(axis=0) - after_arr.min(axis=0)
        range_ratio = float(np.mean(after_range / (before_range + 1e-10)))
        
        results[sector_name] = {
            'raw_similarity': raw_sim,
            'normalized_similarity': norm_sim,
            'normalization_survival': norm_survival,
            'range_preservation': range_ratio,
            'expected_survival': sector_def['expected_survival'],
            'verdict': 'SURVIVES' if norm_survival > -0.1 else 'COLLAPSES',
        }
    
    return results


def run_immune_study():
    """Run complete immune signaling network study."""
    print(f"\n{'=' * 70}")
    print("Study 001C: Immune Signaling Network")
    print(f"{'=' * 70}")
    
    # Pre-registered hypothesis
    print("\n  PRE-REGISTERED HYPOTHESIS H1:")
    print("  Immune systems will exhibit:")
    print("  - moderate-to-high functional persistence")
    print("  - moderate structural persistence")
    print("  - weaker anti-coupling than ant colonies")
    
    all_results = {}
    
    perturbations = {
        'P1_pathogen_attack': (PathogenAttack, 0.3),
        'P2_immunosuppression': (Immunosuppression, 0.5),
        'P3_cell_depletion': (CellDepletion, 0.4),
        'P4_receptor_blockade': (ReceptorBlockade, 0.5),
    }
    
    for pname, (protocol, severity) in perturbations.items():
        print(f"\n{'─' * 50}")
        print(f"Perturbation: {pname} (severity={severity})")
        print(f"{'─' * 50}")
        
        # Reset network
        network = ImmuneSignalingNetwork(n_cells=100, seed=42)
        
        # Establish baseline (20 timesteps)
        history_before = []
        for _ in range(20):
            state = network.step()
            history_before.append(extract_immune_metrics(state))
        
        # Apply perturbation
        description = protocol.apply(network, severity)
        print(f"  Applied: {description}")
        
        # Measure recovery (50 timesteps)
        history_after = []
        for _ in range(50):
            state = network.step()
            history_after.append(extract_immune_metrics(state))
        
        # Sector audit
        sector_results = compute_immune_sector_alignment(history_before, history_after)
        
        all_results[pname] = {
            'description': description,
            'sectors': sector_results,
        }
        
        for sector_name, sr in sector_results.items():
            if 'error' in sr:
                print(f"  {sector_name}: {sr['error']}")
                continue
            print(f"  {sector_name:12s}: raw={sr['raw_similarity']:.4f}  "
                  f"norm={sr['normalized_similarity']:.4f}  "
                  f"Δ={sr['normalization_survival']:+.4f}  "
                  f"→ {sr['verdict']}")
    
    # ─── Structural/Functional Dissociation ───
    print(f"\n{'─' * 50}")
    print("STRUCTURAL/FUNCTIONAL DISSOCIATION")
    print(f"{'─' * 50}")
    
    structural_scores = []
    functional_scores = []
    
    for pname, data in all_results.items():
        sector_data = data.get('sectors', {})
        
        # Structural: topology normalized similarity
        topo = sector_data.get('topology', {})
        structural = max(0, topo.get('normalized_similarity', 0))
        
        # Functional: amplitude normalized similarity
        amp = sector_data.get('amplitude', {})
        functional = max(0, amp.get('normalized_similarity', 0))
        
        structural_scores.append(structural)
        functional_scores.append(functional)
        
        print(f"  {pname}: S={structural:.3f}  F={functional:.3f}")
    
    S_mean = np.mean(structural_scores)
    F_mean = np.mean(functional_scores)
    
    print(f"\n  MEAN: S={S_mean:.3f}  F={F_mean:.3f}")
    
    # Classify regime
    regime = classify_persistence_regime(S_mean, F_mean)
    print(f"  Regime: {regime}")
    
    # ─── Hypothesis Test ───
    print(f"\n{'=' * 70}")
    print("HYPOTHESIS H1 TEST")
    print(f"{'=' * 70}")
    
    # Load previous systems
    with open('/home/student/sgp_core_v2/post_omega_study_001/persistence_geometry_results.json', 'r') as f:
        geometry = json.load(f)
    
    print(f"\n  H1 prediction: moderate-to-high F, moderate S, weaker anti-coupling")
    print(f"  ")
    print(f"  Immune system: S={S_mean:.3f}, F={F_mean:.3f}")
    
    # Check prediction
    moderate_high_F = F_mean > 0.3
    moderate_S = S_mean > 0.2
    coupling = S_mean - F_mean
    
    print(f"  ")
    print(f"  Moderate-to-high F (>0.3): {'YES' if moderate_high_F else 'NO'} (F={F_mean:.3f})")
    print(f"  Moderate S (>0.2): {'YES' if moderate_S else 'NO'} (S={S_mean:.3f})")
    print(f"  Coupling direction: {coupling:+.3f}")
    
    # Compare with ant colony coupling
    ac_data = geometry.get('Ant Colony', {})
    ac_coupling = ac_data.get('coupling', 0)
    print(f"  Ant colony coupling: {ac_coupling:+.3f}")
    print(f"  Immune coupling: {coupling:+.3f}")
    
    if abs(coupling) < abs(ac_coupling):
        print(f"  Weaker anti-coupling than ant colony: YES")
    else:
        print(f"  Weaker anti-coupling than ant colony: NO")
    
    # ─── Persistence Landscape ───
    print(f"\n{'=' * 70}")
    print("PERSISTENCE ALLOCATION LANDSCAPE (all 3 systems)")
    print(f"{'=' * 70}")
    
    # Add immune system to landscape
    geometry['Immune System'] = {
        'S': float(S_mean),
        'F': float(F_mean),
        'F_normalized': float(min(F_mean, 1.0)),
        'regime': regime,
        'coupling': float(coupling),
    }
    
    for name, data in geometry.items():
        print(f"  {name:20s}: S={data['S']:.3f}  F={data['F']:.3f}  regime={data['regime']}")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/immune_study_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    with open('/home/student/sgp_core_v2/post_omega_study_001/persistence_geometry_results.json', 'w') as f:
        json.dump(geometry, f, indent=2)
    
    print(f"\nResults saved")
    print(f"{'=' * 70}")
    
    return all_results, geometry


if __name__ == '__main__':
    # Part 1: Persistence geometry
    run_persistence_geometry()
    
    # Part 2: Immune system study
    run_immune_study()
