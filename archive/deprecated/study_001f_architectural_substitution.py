"""
SGI Post-Ω Study 001F — Architectural Substitution

Replace organizational primitives in the distributed system:

| Remove                    | Replace With              |
|---------------------------|---------------------------|
| global scheduler          | local signaling           |
| arbitrary routing         | receptor matching         |
| static nodes              | adaptive specialization   |
| centralized coordination  | distributed activation    |
| fixed assignment          | selective amplification   |

Goal: determine whether high G emerges only after architectural transition.
"""

import numpy as np
import json
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum

sys.path.insert(0, '/home/student/sgp_core_v2/post_omega_study_001')
from study_001 import (
    WorkloadType, NodeRemoval, CommunicationDelay,
    ResourceStarvation, SchedulerDistortion
)


# ═══════════════════════════════════════════════════════════════════
# Decentralized-Selective Architecture
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ReceptorProfile:
    """Task receptor profile — determines compatibility with nodes."""
    workload_affinity: Dict[WorkloadType, float] = field(default_factory=dict)
    cpu_range: Tuple[float, float] = (0.0, 10.0)
    memory_range: Tuple[float, float] = (0.0, 20.0)
    
    def match_score(self, node: 'DSNode') -> float:
        """Compute receptor-ligand match score."""
        wl_affinity = self.workload_affinity.get(node.workload, 0.5)
        cpu_fit = 1.0 - abs(node.cpu_normalized - 0.5)  # prefer mid-range
        mem_fit = 1.0 - abs(node.memory_normalized - 0.5)
        return wl_affinity * 0.5 + cpu_fit * 0.3 + mem_fit * 0.2


@dataclass
class DSNode:
    """Decentralized-selective node with adaptive specialization."""
    id: int
    workload: WorkloadType
    cpu_capacity: float
    memory_capacity: float
    cpu_used: float = 0.0
    memory_used: float = 0.0
    active: bool = True
    latency: float = 0.0
    
    # Adaptive specialization
    specialization: Dict[WorkloadType, float] = field(default_factory=dict)
    success_history: List[float] = field(default_factory=list)
    amplification_factor: float = 1.0
    
    # Local signaling
    signal_strength: float = 0.0
    signal_decay: float = 0.9
    
    @property
    def cpu_available(self) -> float:
        return max(0, self.cpu_capacity - self.cpu_used)
    
    @property
    def memory_available(self) -> float:
        return max(0, self.memory_capacity - self.memory_used)
    
    @property
    def cpu_normalized(self) -> float:
        return self.cpu_used / max(self.cpu_capacity, 1e-8)
    
    @property
    def memory_normalized(self) -> float:
        return self.memory_used / max(self.memory_capacity, 1e-8)
    
    def initialize_specialization(self, rng):
        """Initialize specialization with slight bias toward native workload."""
        for wl in WorkloadType:
            base = 0.25
            if wl == self.workload:
                base = 0.4  # Slight native bias
            self.specialization[wl] = base + rng.uniform(-0.05, 0.05)
        # Normalize
        total = sum(self.specialization.values())
        for wl in self.specialization:
            self.specialization[wl] /= total
    
    def update_specialization(self, workload: WorkloadType, success: bool):
        """Update specialization based on task completion success."""
        if success:
            self.specialization[workload] *= (1 + 0.1 * self.amplification_factor)
        else:
            self.specialization[workload] *= 0.9
        
        # Normalize
        total = sum(self.specialization.values())
        if total > 0:
            for wl in self.specialization:
                self.specialization[wl] /= total
        
        # Update amplification based on rolling success rate
        self.success_history.append(1.0 if success else 0.0)
        if len(self.success_history) > 20:
            self.success_history = self.success_history[-20:]
        recent_success = np.mean(self.success_history)
        self.amplification_factor = 0.5 + 2.0 * recent_success  # [0.5, 2.5]
    
    def emit_signal(self) -> float:
        """Emit availability signal to neighbors."""
        load = self.cpu_normalized + self.memory_normalized
        self.signal_strength = max(0, 1.0 - load) * self.amplification_factor
        return self.signal_strength
    
    def receive_signal(self, neighbor_signals: Dict[int, float]):
        """Receive and integrate signals from neighbors."""
        if neighbor_signals:
            avg_signal = np.mean(list(neighbor_signals.values()))
            self.signal_strength = self.signal_strength * self.signal_decay + avg_signal * (1 - self.signal_decay)


@dataclass
class DSTask:
    """Task with receptor profile for matching."""
    id: int
    workload_type: WorkloadType
    cpu_required: float
    memory_required: float
    receptor: ReceptorProfile = field(default_factory=lambda: ReceptorProfile())
    assigned_node: Optional[int] = None
    completed: bool = False
    
    def initialize_receptor(self):
        """Initialize receptor profile based on task type."""
        self.receptor = ReceptorProfile(
            workload_affinity={wl: (1.0 if wl == self.workload_type else 0.3) for wl in WorkloadType},
            cpu_range=(self.cpu_required * 0.5, self.cpu_required * 2.0),
            memory_range=(self.memory_required * 0.5, self.memory_required * 2.0),
        )


@dataclass
class DSEdge:
    """Edge for local signaling."""
    source: int
    target: int
    bandwidth: float
    latency: float
    active: bool = True
    success_rate: float = 0.5  # Adaptive routing metric


class DecentralizedSelectiveSystem:
    """
    Decentralized-selective architecture with:
    - Local signaling (no global scheduler)
    - Receptor matching (task-node compatibility)
    - Adaptive specialization (nodes specialize over time)
    - Distributed activation (self-assignment based on signals)
    - Selective amplification (successful pairs reinforced)
    """
    
    def __init__(self, n_nodes: int = 100, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.n_nodes = n_nodes
        self.nodes: Dict[int, DSNode] = {}
        self.edges: List[DSEdge] = []
        self.adjacency: Dict[int, List[int]] = {}
        self.task_queue: List[DSTask] = []
        self.timestep = 0
        self.history: List[Dict] = []
        
        # Global activation threshold (adaptive)
        self.activation_threshold = 0.3
        
        self._build_topology()
    
    def _build_topology(self):
        """Build topology with local connectivity."""
        workload_probs = [0.40, 0.25, 0.20, 0.15]
        
        for i in range(self.n_nodes):
            wl = self.rng.choice(len(workload_probs), p=workload_probs)
            cpu_cap = self.rng.uniform(2.0, 8.0)
            mem_cap = self.rng.uniform(4.0, 16.0)
            node = DSNode(
                id=i,
                workload=WorkloadType(wl),
                cpu_capacity=cpu_cap,
                memory_capacity=mem_cap
            )
            node.initialize_specialization(self.rng)
            self.nodes[i] = node
            self.adjacency[i] = []
        
        # Build edges: local connectivity (no global routing tables)
        for i in range(1, self.n_nodes):
            n_edges = self.rng.randint(2, 5)
            targets = []
            for _ in range(n_edges):
                candidates = list(range(i))
                if self.rng.random() < 0.7:
                    same_wl = [c for c in candidates 
                              if self.nodes[c].workload == self.nodes[i].workload]
                    if same_wl:
                        targets.append(self.rng.choice(same_wl))
                        continue
                targets.append(self.rng.choice(candidates))
            
            for t in targets:
                bw = self.rng.uniform(1.0, 10.0)
                lat = self.rng.uniform(0.1, 5.0)
                self.edges.append(DSEdge(source=i, target=t, bandwidth=bw, latency=lat))
                self.edges.append(DSEdge(source=t, target=i, bandwidth=bw, latency=lat))
                self.adjacency[i].append(t)
                self.adjacency[t].append(i)
        
        for i in self.adjacency:
            self.adjacency[i] = list(set(self.adjacency[i]))
    
    def generate_tasks(self, n_tasks: int = 50):
        """Generate tasks with receptor profiles."""
        self.task_queue = []
        for i in range(n_tasks):
            wl = self.rng.choice(list(WorkloadType))
            if wl == WorkloadType.STATELESS:
                cpu = self.rng.uniform(0.1, 0.5)
                mem = self.rng.uniform(0.5, 2.0)
            elif wl == WorkloadType.STATEFUL:
                cpu = self.rng.uniform(0.5, 2.0)
                mem = self.rng.uniform(2.0, 8.0)
            elif wl == WorkloadType.QUEUE:
                cpu = self.rng.uniform(0.2, 1.0)
                mem = self.rng.uniform(1.0, 4.0)
            else:
                cpu = self.rng.uniform(0.1, 0.5)
                mem = self.rng.uniform(4.0, 12.0)
            
            task = DSTask(
                id=i,
                workload_type=wl,
                cpu_required=cpu,
                memory_required=mem
            )
            task.initialize_receptor()
            self.task_queue.append(task)
    
    def _release_completed_tasks(self):
        """Release resources from completed tasks."""
        for task in self.task_queue:
            if task.assigned_node is not None and not task.completed:
                if self.rng.random() < 0.3:
                    task.completed = True
                    node = self.nodes[task.assigned_node]
                    node.cpu_used = max(0, node.cpu_used - task.cpu_required)
                    node.memory_used = max(0, node.memory_used - task.memory_required)
                    # Update specialization based on success
                    node.update_specialization(task.workload_type, success=True)
        self.task_queue = [t for t in self.task_queue if not t.completed]
    
    def _arrive_new_tasks(self, n_new: int = 10):
        """Generate new tasks with receptor profiles."""
        for i in range(n_new):
            wl = self.rng.choice(list(WorkloadType))
            if wl == WorkloadType.STATELESS:
                cpu = self.rng.uniform(0.1, 0.5)
                mem = self.rng.uniform(0.5, 2.0)
            elif wl == WorkloadType.STATEFUL:
                cpu = self.rng.uniform(0.5, 2.0)
                mem = self.rng.uniform(2.0, 8.0)
            elif wl == WorkloadType.QUEUE:
                cpu = self.rng.uniform(0.2, 1.0)
                mem = self.rng.uniform(1.0, 4.0)
            else:
                cpu = self.rng.uniform(0.1, 0.5)
                mem = self.rng.uniform(4.0, 12.0)
            task = DSTask(
                id=self.timestep * 1000 + i,
                workload_type=wl,
                cpu_required=cpu,
                memory_required=mem
            )
            task.initialize_receptor()
            self.task_queue.append(task)
    
    def _local_signaling(self):
        """Phase 1: Nodes emit and receive local signals."""
        # Each node emits availability signal
        for node in self.nodes.values():
            if node.active:
                node.emit_signal()
        
        # Signals propagate through local connections
        for node in self.nodes.values():
            if not node.active:
                continue
            neighbor_signals = {}
            for neighbor_id in self.adjacency[node.id]:
                neighbor = self.nodes[neighbor_id]
                if neighbor.active:
                    neighbor_signals[neighbor_id] = neighbor.signal_strength
            node.receive_signal(neighbor_signals)
    
    def _receptor_matching(self) -> float:
        """Phase 2: Tasks self-assign based on receptor-ligand matching."""
        assigned = 0
        for task in self.task_queue:
            if task.assigned_node is not None:
                continue
            
            # Find best matching node using receptor profile
            best_node = None
            best_score = -1
            
            for nid, node in self.nodes.items():
                if not node.active:
                    continue
                if node.cpu_available < task.cpu_required or node.memory_available < task.memory_required:
                    continue
                
                # Receptor-ligand match score
                receptor_score = task.receptor.match_score(node)
                
                # Signal-based activation: prefer nodes with strong signals
                signal_score = node.signal_strength
                
                # Specialization score: prefer nodes specialized for this workload
                spec_score = node.specialization.get(task.workload_type, 0.25)
                
                # Combined score
                score = (receptor_score * 0.4 + 
                        signal_score * 0.3 + 
                        spec_score * 0.3)
                
                # Apply activation threshold
                if score < self.activation_threshold:
                    continue
                
                if score > best_score:
                    best_score = score
                    best_node = nid
            
            if best_node is not None:
                task.assigned_node = best_node
                self.nodes[best_node].cpu_used += task.cpu_required
                self.nodes[best_node].memory_used += task.memory_required
                assigned += 1
        
        return assigned / max(len(self.task_queue), 1)
    
    def _selective_amplification(self):
        """Phase 3: Amplify successful task-node pairs."""
        for task in self.task_queue:
            if task.assigned_node is not None and task.completed:
                node = self.nodes[task.assigned_node]
                # Reinforce the receptor profile for this workload
                task.receptor.workload_affinity[task.workload_type] *= 1.1
                # Reinforce the edge success rate
                for edge in self.edges:
                    if edge.source == task.assigned_node or edge.target == task.assigned_node:
                        edge.success_rate = min(1.0, edge.success_rate + 0.05)
    
    def step(self) -> Dict:
        """Execute one timestep with decentralized-selective dynamics."""
        # Release completed tasks
        self._release_completed_tasks()
        
        # New tasks arrive
        self._arrive_new_tasks(n_new=10)
        
        # Phase 1: Local signaling
        self._local_signaling()
        
        # Phase 2: Receptor matching (distributed assignment)
        assignment_rate = self._receptor_matching()
        
        # Phase 3: Selective amplification
        self._selective_amplification()
        
        # Compute observables
        active_nodes = [n for n in self.nodes.values() if n.active]
        n_active = len(active_nodes)
        
        # Graph connectivity
        if n_active > 0:
            component_sizes = self._find_components()
            largest_component = max(component_sizes) if component_sizes else 0
            connectivity = largest_component / max(n_active, 1)
        else:
            connectivity = 0.0
        
        # Routing entropy (from edge success rates, not routing tables)
        routing_entropy = self._compute_routing_entropy()
        
        # Task allocation distribution
        allocation = np.zeros(self.n_nodes)
        for task in self.task_queue:
            if task.assigned_node is not None:
                allocation[task.assigned_node] += 1
        allocation = allocation / max(allocation.sum(), 1)
        
        # Covariance of node interactions
        cov_eigenvalues = self._compute_covariance_eigenvalues()
        
        state = {
            'timestep': self.timestep,
            'n_active': n_active,
            'connectivity': connectivity,
            'routing_entropy': routing_entropy,
            'assignment_rate': assignment_rate,
            'n_components': len(self._find_components()),
            'cov_eigenvalues': cov_eigenvalues.tolist(),
            'allocation_entropy': -np.sum(allocation[allocation > 0] * np.log2(allocation[allocation > 0])) if allocation.sum() > 0 else 0,
        }
        
        self.history.append(state)
        self.timestep += 1
        return state
    
    def _find_components(self) -> List[int]:
        """Find connected component sizes."""
        visited = set()
        components = []
        for node_id in range(self.n_nodes):
            if node_id in visited or not self.nodes[node_id].active:
                continue
            component_size = 0
            queue = [node_id]
            visited.add(node_id)
            while queue:
                current = queue.pop(0)
                component_size += 1
                for neighbor in self.adjacency[current]:
                    if neighbor not in visited and self.nodes[neighbor].active:
                        visited.add(neighbor)
                        queue.append(neighbor)
            components.append(component_size)
        return components
    
    def _compute_routing_entropy(self) -> float:
        """Compute entropy from edge success rates (not routing tables)."""
        success_rates = [edge.success_rate for edge in self.edges if edge.active]
        if not success_rates:
            return 0.0
        hist, _ = np.histogram(success_rates, bins=20, range=(0, 1))
        hist = hist / max(hist.sum(), 1)
        return -np.sum(hist[hist > 0] * np.log2(hist[hist > 0]))
    
    def _compute_covariance_eigenvalues(self) -> np.ndarray:
        """Compute eigenvalues of node interaction covariance."""
        interaction_matrix = np.zeros((self.n_nodes, self.n_nodes))
        for task in self.task_queue:
            if task.assigned_node is not None:
                src = task.assigned_node
                for neighbor in self.adjacency[src]:
                    if self.nodes[neighbor].active:
                        interaction_matrix[src, neighbor] += 1
        
        row_sums = interaction_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        interaction_matrix = interaction_matrix / row_sums
        
        cov = np.cov(interaction_matrix)
        eigenvalues = np.linalg.eigvalsh(cov)
        return np.sort(np.abs(eigenvalues))[::-1]
    
    def perturb(self, protocol, severity: float):
        """Apply perturbation protocol."""
        protocol.apply(self, severity)
    
    def _rebuild_after_perturbation(self):
        """Rebuild local connectivity after perturbation."""
        # No global routing tables to rebuild — just update adjacency
        for i in self.adjacency:
            self.adjacency[i] = [n for n in self.adjacency[i] if self.nodes[n].active]


# ═══════════════════════════════════════════════════════════════════
# Perturbation Adapters (adapt original protocols to DS system)
# ═══════════════════════════════════════════════════════════════════

class DSNodeRemoval:
    @staticmethod
    def apply(system: DecentralizedSelectiveSystem, severity: float) -> str:
        n_remove = int(system.n_nodes * severity)
        active_ids = [nid for nid, node in system.nodes.items() if node.active]
        remove_ids = system.rng.choice(active_ids, size=min(n_remove, len(active_ids)), replace=False)
        for nid in remove_ids:
            system.nodes[nid].active = False
        system._rebuild_after_perturbation()
        return f"Removed {len(remove_ids)} nodes ({severity*100:.0f}%)"

class DSCommunicationDelay:
    @staticmethod
    def apply(system: DecentralizedSelectiveSystem, severity: float) -> str:
        for edge in system.edges:
            if system.nodes[edge.source].active and system.nodes[edge.target].active:
                edge.latency *= (1 + severity * system.rng.uniform(0.5, 2.0))
        for node in system.nodes.values():
            node.latency += severity * system.rng.uniform(1.0, 10.0)
        return f"Injected delay gradient (severity={severity:.2f})"

class DSResourceStarvation:
    @staticmethod
    def apply(system: DecentralizedSelectiveSystem, severity: float) -> str:
        throttled = 0
        for node in system.nodes.values():
            if node.active and system.rng.random() < severity:
                node.cpu_capacity *= (1 - severity * 0.5)
                node.memory_capacity *= (1 - severity * 0.3)
                throttled += 1
        return f"Throttled {throttled} nodes (severity={severity:.2f})"

class DSSchedulerDistortion:
    @staticmethod
    def apply(system: DecentralizedSelectiveSystem, severity: float) -> str:
        # Distort receptor profiles (the decentralized equivalent of scheduler distortion)
        distorted = 0
        for task in system.task_queue:
            if system.rng.random() < severity:
                for wl in task.receptor.workload_affinity:
                    task.receptor.workload_affinity[wl] *= system.rng.uniform(0.5, 1.5)
                distorted += 1
        # Also distort node specialization
        for node in system.nodes.values():
            if node.active and system.rng.random() < severity:
                for wl in node.specialization:
                    node.specialization[wl] *= system.rng.uniform(0.5, 1.5)
                total = sum(node.specialization.values())
                for wl in node.specialization:
                    node.specialization[wl] /= total
        return f"Distorted {distorted} receptor profiles (severity={severity:.2f})"


# ═══════════════════════════════════════════════════════════════════
# Sector Audit (from 001E)
# ═══════════════════════════════════════════════════════════════════

def extract_sector_metrics(state: dict) -> dict:
    result = {}
    result['assignment_rate'] = state.get('assignment_rate', 0)
    result['throughput'] = state.get('assignment_rate', 0) * state.get('n_active', 0)
    result['allocation_entropy'] = state.get('allocation_entropy', 0)
    result['connectivity'] = state.get('connectivity', 0)
    result['n_components'] = state.get('n_components', 0)
    result['routing_entropy'] = state.get('routing_entropy', 0)
    
    eigenvalues = state.get('cov_eigenvalues', [0])
    if isinstance(eigenvalues, list) and len(eigenvalues) > 0:
        ev = np.array(eigenvalues)
        result['cov_trace'] = float(np.sum(np.abs(ev)))
        result['cov_condition'] = float(ev[0] / (ev[-1] + 1e-10)) if len(ev) > 1 else 1.0
    else:
        result['cov_trace'] = 0
        result['cov_condition'] = 1.0
    
    if isinstance(eigenvalues, list) and len(eigenvalues) > 3:
        ev = np.array(eigenvalues)
        total = np.sum(np.abs(ev))
        residual = np.sum(np.abs(ev[3:]))
        result['residual_energy'] = float(residual / (total + 1e-10))
    else:
        result['residual_energy'] = 0
    
    return result


def compute_sector_alignment(before_metrics: list, after_metrics: list) -> dict:
    sectors = {
        'amplitude': ['assignment_rate', 'throughput', 'allocation_entropy'],
        'topology': ['connectivity', 'n_components', 'routing_entropy'],
        'transport': ['cov_trace', 'cov_condition'],
        'residual': ['residual_energy'],
    }
    
    results = {}
    for sector_name, metrics in sectors.items():
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
# Main Experiment
# ═══════════════════════════════════════════════════════════════════

def run_study_001f():
    print("=" * 70)
    print("Study 001F — Architectural Substitution")
    print("=" * 70)
    
    print("\n  REPLACING ORGANIZATIONAL PRIMITIVES:")
    print("  global scheduler       → local signaling")
    print("  arbitrary routing      → receptor matching")
    print("  static nodes           → adaptive specialization")
    print("  centralized coord.     → distributed activation")
    print("  fixed assignment       → selective amplification")
    
    # Create system
    system = DecentralizedSelectiveSystem(n_nodes=100, seed=42)
    system.generate_tasks(n_tasks=100)
    
    # Establish baseline
    print("\n[Baseline] Establishing baseline...")
    history_before = []
    for _ in range(20):
        state = system.step()
        history_before.append(state)
    
    baseline = history_before[-1]
    print(f"  Active nodes: {baseline['n_active']}")
    print(f"  Connectivity: {baseline['connectivity']:.4f}")
    print(f"  Assignment rate: {baseline['assignment_rate']:.4f}")
    print(f"  Routing entropy: {baseline['routing_entropy']:.4f}")
    
    # Perturbations
    perturbations = {
        'P1_node_removal': (DSNodeRemoval, 0.3),
        'P2_communication_delay': (DSCommunicationDelay, 0.5),
        'P3_resource_starvation': (DSResourceStarvation, 0.4),
        'P4_receptor_distortion': (DSSchedulerDistortion, 0.3),
    }
    
    all_sectors = []
    
    for name, (protocol, severity) in perturbations.items():
        print(f"\n[Perturbation] {name} (severity={severity})...")
        
        # Reset system
        system = DecentralizedSelectiveSystem(n_nodes=100, seed=42)
        system.generate_tasks(n_tasks=100)
        
        # Establish baseline
        history_before = []
        for _ in range(20):
            state = system.step()
            history_before.append(state)
        
        # Apply perturbation
        desc = protocol.apply(system, severity)
        print(f"  {desc}")
        
        # Measure recovery
        history_after = []
        for _ in range(50):
            state = system.step()
            history_after.append(state)
        
        # Sector audit
        before_metrics = [extract_sector_metrics(h) for h in history_before]
        after_metrics = [extract_sector_metrics(h) for h in history_after]
        sector_results = compute_sector_alignment(before_metrics, after_metrics)
        G = compute_gauge_fraction(sector_results)
        
        all_sectors.append(sector_results)
        
        print(f"  G={G:.3f}")
        for sector in ['amplitude', 'topology', 'transport', 'residual']:
            data = sector_results.get(sector, {})
            verdict = data.get('verdict', 'N/A')
            norm_surv = data.get('normalization_survival', 0)
            print(f"    {sector:12s}: {verdict:10s} (Δ={norm_surv:+.3f})")
    
    # ─── Aggregate Results ───
    print(f"\n{'=' * 70}")
    print("AGGREGATE RESULTS")
    print(f"{'=' * 70}")
    
    # Average G across perturbations
    avg_G = np.mean([compute_gauge_fraction(s) for s in all_sectors])
    
    # Sector survival counts
    sector_survival = {'amplitude': 0, 'topology': 0, 'transport': 0, 'residual': 0}
    for sector_data in all_sectors:
        for sector in sector_survival:
            if sector_data.get(sector, {}).get('verdict') == 'SURVIVES':
                sector_survival[sector] += 1
    
    print(f"\n  Average G: {avg_G:.3f}")
    print(f"  Sector survival (out of 4 perturbations):")
    for sector, count in sector_survival.items():
        print(f"    {sector:12s}: {count}/4")
    
    # ─── Compare with Existing Systems ───
    print(f"\n{'=' * 70}")
    print("PERSISTENCE ALLOCATION LANDSCAPE (all systems)")
    print(f"{'=' * 70}")
    
    with open('/home/student/sgp_core_v2/post_omega_study_001/gauge_geometry_results.json', 'r') as f:
        geometry = json.load(f)
    
    # Compute S and F for DS-architectural
    # S = topology normalized similarity (average)
    avg_S = np.mean([s.get('topology', {}).get('normalized_similarity', 0) for s in all_sectors])
    avg_F = np.mean([s.get('amplitude', {}).get('normalized_similarity', 0) for s in all_sectors])
    
    geometry['DS-Architectural'] = {
        'S': float(avg_S),
        'F': float(avg_F),
        'G': float(avg_G),
        'regime': 'engineered',
    }
    
    for name, data in geometry.items():
        print(f"  {name:25s}: S={data['S']:.3f}  F={data['F']:.3f}  G={data['G']:.3f}  regime={data['regime']}")
    
    # ─── Scientific Verdict ───
    print(f"\n{'=' * 70}")
    print("SCIENTIFIC VERDICT")
    print(f"{'=' * 70}")
    
    immune_G = geometry.get('Immune System', {}).get('G', 0)
    distributed_G = geometry.get('Distributed System', {}).get('G', 0)
    
    print(f"\n  Distributed (baseline) G: {distributed_G:.3f}")
    print(f"  DS-Architectural G: {avg_G:.3f}")
    print(f"  Immune System G: {immune_G:.3f}")
    print(f"  ")
    
    if avg_G > immune_G * 0.8:
        print(f"  OUTCOME A: Architectural transition successful")
        print(f"  High-G persistence is achievable through architectural substitution.")
        print(f"  Gauge stability is an organizational phase, not a biological property.")
    elif avg_G > distributed_G * 1.5:
        print(f"  OUTCOME B: Partial architectural transition")
        print(f"  G increased but did not reach immune levels.")
        print(f"  Architectural changes matter but are not sufficient.")
    else:
        print(f"  OUTCOME C: Architectural substitution failed")
        print(f"  G did not increase despite replacing organizational primitives.")
        print(f"  Immune persistence may depend on biology-specific mechanisms.")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/architectural_substitution_results.json', 'w') as f:
        json.dump({
            'avg_G': float(avg_G),
            'avg_S': float(avg_S),
            'avg_F': float(avg_F),
            'sector_survival': sector_survival,
            'geometry': geometry,
        }, f, indent=2, default=str)
    
    with open('/home/student/sgp_core_v2/post_omega_study_001/gauge_geometry_results.json', 'w') as f:
        json.dump(geometry, f, indent=2)
    
    print(f"\nResults saved")
    print(f"{'=' * 70}")


if __name__ == '__main__':
    run_study_001f()
