"""
SGI Post-Ω Study 001: Distributed Coordination Persistence Under Perturbation

System: Graph-based distributed system (50-200 nodes, heterogeneous workloads)
Persistence Object: Coordination architecture (routing, task allocation, recovery trajectories)
Perturbations: Node removal, communication delay, resource starvation, scheduler distortion
"""

import numpy as np
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
import time

# ─── System Definition ───

class WorkloadType(Enum):
    STATELESS = 0
    STATEFUL = 1
    QUEUE = 2
    STORAGE = 3

@dataclass
class Node:
    id: int
    workload: WorkloadType
    cpu_capacity: float
    memory_capacity: float
    cpu_used: float = 0.0
    memory_used: float = 0.0
    active: bool = True
    latency: float = 0.0  # added communication latency
    
    @property
    def cpu_available(self) -> float:
        return max(0, self.cpu_capacity - self.cpu_used)
    
    @property
    def memory_available(self) -> float:
        return max(0, self.memory_capacity - self.memory_used)

@dataclass
class Task:
    id: int
    workload_type: WorkloadType
    cpu_required: float
    memory_required: float
    assigned_node: Optional[int] = None
    completed: bool = False

@dataclass
class Edge:
    source: int
    target: int
    bandwidth: float
    latency: float
    active: bool = True


class DistributedSystem:
    """Graph-based distributed system with heterogeneous nodes and routing."""
    
    def __init__(self, n_nodes: int = 100, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.n_nodes = n_nodes
        self.nodes: Dict[int, Node] = {}
        self.edges: List[Edge] = []
        self.adjacency: Dict[int, List[int]] = {}
        self.routing_table: Dict[int, Dict[int, int]] = {}  # node -> dest -> next_hop
        self.task_queue: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.timestep = 0
        self.history: List[Dict] = []
        
        self._build_topology()
        self._build_routing()
    
    def _build_topology(self):
        """Build heterogeneous node set and connectivity."""
        # Workload distribution: 40% stateless, 25% stateful, 20% queue, 15% storage
        workload_probs = [0.40, 0.25, 0.20, 0.15]
        
        for i in range(self.n_nodes):
            wl = self.rng.choice(len(workload_probs), p=workload_probs)
            cpu_cap = self.rng.uniform(2.0, 8.0)
            mem_cap = self.rng.uniform(4.0, 16.0)
            self.nodes[i] = Node(
                id=i,
                workload=WorkloadType(wl),
                cpu_capacity=cpu_cap,
                memory_capacity=mem_cap
            )
            self.adjacency[i] = []
        
        # Build edges: preferential attachment with locality
        for i in range(1, self.n_nodes):
            # Connect to 2-4 existing nodes
            n_edges = self.rng.randint(2, 5)
            # Prefer nodes with similar workload (locality)
            targets = []
            for _ in range(n_edges):
                candidates = list(range(i))
                # 70% prefer same workload
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
                self.edges.append(Edge(source=i, target=t, bandwidth=bw, latency=lat))
                self.edges.append(Edge(source=t, target=i, bandwidth=bw, latency=lat))
                self.adjacency[i].append(t)
                self.adjacency[t].append(i)
        
        # Remove duplicates
        for i in self.adjacency:
            self.adjacency[i] = list(set(self.adjacency[i]))
    
    def _build_routing(self):
        """Build shortest-path routing tables."""
        for src in range(self.n_nodes):
            self.routing_table[src] = {}
            # BFS from src
            visited = {src}
            queue = [(src, src)]  # (node, first_hop)
            while queue:
                node, first_hop = queue.pop(0)
                for neighbor in self.adjacency[node]:
                    if neighbor not in visited and self.nodes[neighbor].active:
                        visited.add(neighbor)
                        self.routing_table[src][neighbor] = first_hop
                        queue.append((neighbor, first_hop))
    
    def _rebuild_routing(self):
        """Rebuild routing after perturbation."""
        self._build_routing()
    
    def generate_tasks(self, n_tasks: int = 50):
        """Generate workload-appropriate tasks."""
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
            else:  # STORAGE
                cpu = self.rng.uniform(0.1, 0.5)
                mem = self.rng.uniform(4.0, 12.0)
            
            self.task_queue.append(Task(
                id=i,
                workload_type=wl,
                cpu_required=cpu,
                memory_required=mem
            ))
    
    def _release_completed_tasks(self):
        """Release resources from completed tasks and remove them."""
        for task in self.task_queue:
            if task.assigned_node is not None and not task.completed:
                # Tasks complete after 1-3 timesteps (simplified)
                if self.rng.random() < 0.3:
                    task.completed = True
                    node = self.nodes[task.assigned_node]
                    node.cpu_used = max(0, node.cpu_used - task.cpu_required)
                    node.memory_used = max(0, node.memory_used - task.memory_required)
        # Remove completed tasks
        self.task_queue = [t for t in self.task_queue if not t.completed]
    
    def _arrive_new_tasks(self, n_new: int = 10):
        """Generate new arriving tasks each timestep."""
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
            self.task_queue.append(Task(
                id=self.timestep * 1000 + i,
                workload_type=wl,
                cpu_required=cpu,
                memory_required=mem
            ))
    
    def assign_tasks(self) -> float:
        """Assign tasks using routing structure. Returns fraction assigned."""
        assigned = 0
        for task in self.task_queue:
            if task.assigned_node is not None:
                continue
            # Find best node: prefer matching workload, fallback to any with capacity
            best_node = None
            best_score = -1
            for nid, node in self.nodes.items():
                if not node.active:
                    continue
                if node.cpu_available < task.cpu_required or node.memory_available < task.memory_required:
                    continue
                # Score: matching workload gets 2x bonus
                workload_bonus = 2.0 if node.workload == task.workload_type else 1.0
                score = workload_bonus * (node.cpu_available + node.memory_available)
                if score > best_score:
                    best_score = score
                    best_node = nid
            
            if best_node is not None:
                task.assigned_node = best_node
                self.nodes[best_node].cpu_used += task.cpu_required
                self.nodes[best_node].memory_used += task.memory_required
                assigned += 1
        
        return assigned / max(len(self.task_queue), 1)
    
    def step(self) -> Dict:
        """Execute one timestep: release, arrive, assign, measure."""
        # Release completed tasks
        self._release_completed_tasks()
        
        # New tasks arrive
        self._arrive_new_tasks(n_new=10)
        
        # Assign unassigned tasks
        assignment_rate = self.assign_tasks()
        
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
        
        # Routing entropy
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
        """Find connected component sizes in active subgraph."""
        visited = set()
        components = []
        for node_id in range(self.n_nodes):
            if node_id in visited or not self.nodes[node_id].active:
                continue
            # BFS
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
        """Compute entropy of routing table distribution."""
        if not self.routing_table:
            return 0.0
        route_lengths = []
        for src, table in self.routing_table.items():
            route_lengths.extend(list(table.values()))
        if not route_lengths:
            return 0.0
        # Histogram of next-hop destinations
        hist, _ = np.histogram(route_lengths, bins=min(20, self.n_nodes))
        hist = hist / max(hist.sum(), 1)
        return -np.sum(hist[hist > 0] * np.log2(hist[hist > 0]))
    
    def _compute_covariance_eigenvalues(self) -> np.ndarray:
        """Compute eigenvalues of node interaction covariance matrix."""
        # Build interaction matrix from task assignments
        interaction_matrix = np.zeros((self.n_nodes, self.n_nodes))
        for task in self.task_queue:
            if task.assigned_node is not None:
                src = task.assigned_node
                for neighbor in self.adjacency[src]:
                    if self.nodes[neighbor].active:
                        interaction_matrix[src, neighbor] += 1
        
        # Normalize
        row_sums = interaction_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        interaction_matrix = interaction_matrix / row_sums
        
        # Covariance
        cov = np.cov(interaction_matrix)
        eigenvalues = np.linalg.eigvalsh(cov)
        return np.sort(np.abs(eigenvalues))[::-1]


# ─── Perturbation Protocols ───

class PerturbationProtocol:
    """Base class for perturbation protocols."""
    
    @staticmethod
    def apply(system: DistributedSystem, severity: float) -> str:
        raise NotImplementedError

class NodeRemoval(PerturbationProtocol):
    """P1: Remove fraction of nodes."""
    
    @staticmethod
    def apply(system: DistributedSystem, severity: float) -> str:
        n_remove = int(system.n_nodes * severity)
        active_ids = [nid for nid, node in system.nodes.items() if node.active]
        remove_ids = system.rng.choice(active_ids, size=min(n_remove, len(active_ids)), replace=False)
        for nid in remove_ids:
            system.nodes[nid].active = False
        system._rebuild_routing()
        return f"Removed {len(remove_ids)} nodes ({severity*100:.0f}%)"

class CommunicationDelay(PerturbationProtocol):
    """P2: Inject latency gradients."""
    
    @staticmethod
    def apply(system: DistributedSystem, severity: float) -> str:
        for edge in system.edges:
            if system.nodes[edge.source].active and system.nodes[edge.target].active:
                edge.latency *= (1 + severity * system.rng.uniform(0.5, 2.0))
        for node in system.nodes.values():
            node.latency += severity * system.rng.uniform(1.0, 10.0)
        system._rebuild_routing()
        return f"Injected delay gradient (severity={severity:.2f})"

class ResourceStarvation(PerturbationProtocol):
    """P3: Throttle CPU/memory."""
    
    @staticmethod
    def apply(system: DistributedSystem, severity: float) -> str:
        throttled = 0
        for node in system.nodes.values():
            if node.active and system.rng.random() < severity:
                node.cpu_capacity *= (1 - severity * 0.5)
                node.memory_capacity *= (1 - severity * 0.3)
                throttled += 1
        return f"Throttled {throttled} nodes (severity={severity:.2f})"

class SchedulerDistortion(PerturbationProtocol):
    """P4: Distort placement heuristics."""
    
    @staticmethod
    def apply(system: DistributedSystem, severity: float) -> str:
        # Randomly reassign tasks to non-optimal nodes
        reassigned = 0
        for task in system.task_queue:
            if task.assigned_node is not None and system.rng.random() < severity:
                active_ids = [nid for nid, node in system.nodes.items() if node.active]
                if active_ids:
                    # Move to random node (anti-optimal)
                    old_node = system.nodes[task.assigned_node]
                    old_node.cpu_used -= task.cpu_required
                    old_node.memory_used -= task.memory_required
                    
                    new_id = system.rng.choice(active_ids)
                    task.assigned_node = new_id
                    system.nodes[new_id].cpu_used += task.cpu_required
                    system.nodes[new_id].memory_used += task.memory_required
                    reassigned += 1
        return f"Reassigned {reassigned} tasks (severity={severity:.2f})"


# ─── Recovery Dynamics ───

def measure_recovery(system: DistributedSystem, n_steps: int = 50) -> Dict:
    """Measure recovery trajectory after perturbation."""
    baseline = system.history[0] if system.history else {}
    recovery_trajectory = []
    
    for _ in range(n_steps):
        state = system.step()
        recovery_trajectory.append(state)
    
    # Compute recovery metrics
    if not recovery_trajectory:
        return {}
    
    connectivity_values = [s['connectivity'] for s in recovery_trajectory]
    assignment_values = [s['assignment_rate'] for s in recovery_trajectory]
    
    # Recovery time: time to reach 90% of baseline connectivity
    baseline_conn = baseline.get('connectivity', 1.0)
    threshold = 0.9 * baseline_conn
    recovery_time = None
    for i, conn in enumerate(connectivity_values):
        if conn >= threshold:
            recovery_time = i
            break
    
    # Persistence half-life: time to lose half the perturbation impact
    initial_drop = baseline_conn - connectivity_values[0] if connectivity_values else 0
    half_drop = initial_drop / 2
    persistence_half_life = None
    for i, conn in enumerate(connectivity_values):
        if conn >= baseline_conn - half_drop:
            persistence_half_life = i
            break
    
    # Oscillation amplitude
    if len(connectivity_values) > 2:
        diffs = np.diff(connectivity_values)
        oscillation_amplitude = float(np.std(diffs))
    else:
        oscillation_amplitude = 0.0
    
    # Throughput stabilization
    throughput_stabilization = float(np.std(assignment_values[-10:])) if len(assignment_values) >= 10 else float(np.std(assignment_values))
    
    return {
        'recovery_time': recovery_time,
        'persistence_half_life': persistence_half_life,
        'oscillation_amplitude': oscillation_amplitude,
        'throughput_stabilization': throughput_stabilization,
        'final_connectivity': connectivity_values[-1],
        'final_assignment_rate': assignment_values[-1],
        'connectivity_trajectory': connectivity_values,
        'assignment_trajectory': assignment_values,
    }


# ─── Representation Audit ───

def representation_audit(system: DistributedSystem, history_before: List[Dict], history_after: List[Dict]) -> Dict:
    """Audit representation dependence of observables."""
    
    def extract_metric_vectors(hist):
        if not hist:
            return np.array([])
        metrics = ['connectivity', 'routing_entropy', 'assignment_rate', 'allocation_entropy']
        return np.array([[h.get(m, 0) for m in metrics] for h in hist])
    
    before = extract_metric_vectors(history_before)
    after = extract_metric_vectors(history_after)
    
    if before.size == 0 or after.size == 0:
        return {'error': 'insufficient data'}
    
    # Truncate to minimum length for comparison
    min_len = min(len(before), len(after))
    before = before[:min_len]
    after = after[:min_len]
    
    # Embedding sensitivity: compare raw vs normalized
    before_norm = (before - before.mean(axis=0)) / (before.std(axis=0) + 1e-8)
    after_norm = (after - after.mean(axis=0)) / (after.std(axis=0) + 1e-8)
    
    # Cosine similarity of metric trajectories
    def cosine_sim(a, b):
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    raw_similarity = cosine_sim(before.flatten(), after.flatten())
    norm_similarity = cosine_sim(before_norm.flatten(), after_norm.flatten())
    
    # Normalization survival
    normalization_survival = norm_similarity - raw_similarity
    
    # Segmentation dependence: compare workload-type segments
    segment_scores = []
    for wl in WorkloadType:
        wl_nodes_before = [h for h in history_before if h.get('n_active', 0) > 0]
        wl_nodes_after = [h for h in history_after if h.get('n_active', 0) > 0]
        if wl_nodes_before and wl_nodes_after:
            seg_before = np.mean([h.get('assignment_rate', 0) for h in wl_nodes_before])
            seg_after = np.mean([h.get('assignment_rate', 0) for h in wl_nodes_after])
            segment_scores.append(abs(seg_before - seg_after))
    
    segmentation_dependence = float(np.mean(segment_scores)) if segment_scores else 0.0
    
    # Gauge-removable: difference between raw and normalized eigenvalue structure
    eigenvalues_before = np.mean([h.get('cov_eigenvalues', [0])[:3] for h in history_before], axis=0) if history_before else np.zeros(3)
    eigenvalues_after = np.mean([h.get('cov_eigenvalues', [0])[:3] for h in history_after], axis=0) if history_after else np.zeros(3)
    
    gauge_removable = float(np.linalg.norm(eigenvalues_before - eigenvalues_after) / (np.linalg.norm(eigenvalues_before) + 1e-8))
    
    return {
        'raw_similarity': raw_similarity,
        'normalization_similarity': norm_similarity,
        'normalization_survival': normalization_survival,
        'segmentation_dependence': segmentation_dependence,
        'gauge_removable': gauge_removable,
        'raw_embedding_change': float(np.linalg.norm(before - before.mean(axis=0)) / (np.linalg.norm(before) + 1e-8)),
        'normalized_embedding_change': float(np.linalg.norm(before_norm - after_norm) / (np.linalg.norm(before_norm) + 1e-8)),
    }


# ─── Main Experiment ───

def run_study_001():
    """Run the complete Post-Ω Study 001."""
    print("=" * 70)
    print("SGI Post-Ω Study 001: Distributed Coordination Persistence")
    print("=" * 70)
    
    results = {}
    
    # ─── Phase 1: Baseline ───
    print("\n[Phase 1] Building baseline system...")
    system = DistributedSystem(n_nodes=100, seed=42)
    system.generate_tasks(n_tasks=100)
    
    # Run 20 timesteps to establish baseline
    for _ in range(20):
        system.step()
    
    baseline_state = system.history[-1]
    print(f"  Active nodes: {baseline_state['n_active']}")
    print(f"  Connectivity: {baseline_state['connectivity']:.4f}")
    print(f"  Assignment rate: {baseline_state['assignment_rate']:.4f}")
    print(f"  Routing entropy: {baseline_state['routing_entropy']:.4f}")
    
    results['baseline'] = {
        'connectivity': baseline_state['connectivity'],
        'assignment_rate': baseline_state['assignment_rate'],
        'routing_entropy': baseline_state['routing_entropy'],
        'allocation_entropy': baseline_state['allocation_entropy'],
        'n_components': baseline_state['n_components'],
    }
    
    # ─── Phase 2: Perturbation Protocols ───
    perturbations = {
        'P1_node_removal': (NodeRemoval, 0.3),
        'P2_communication_delay': (CommunicationDelay, 0.5),
        'P3_resource_starvation': (ResourceStarvation, 0.4),
        'P4_scheduler_distortion': (SchedulerDistortion, 0.3),
    }
    
    for name, (protocol, severity) in perturbations.items():
        print(f"\n[Phase 2] Applying {name} (severity={severity})...")
        
        # Reset system
        system = DistributedSystem(n_nodes=100, seed=42)
        system.generate_tasks(n_tasks=100)
        
        # Establish baseline
        history_before = []
        for _ in range(20):
            state = system.step()
            history_before.append(state)
        
        # Apply perturbation
        description = protocol.apply(system, severity)
        print(f"  {description}")
        
        # Measure recovery
        recovery = measure_recovery(system, n_steps=50)
        
        # Representation audit
        audit = representation_audit(system, history_before, system.history[-50:])
        
        results[name] = {
            'description': description,
            'recovery_time': recovery.get('recovery_time'),
            'persistence_half_life': recovery.get('persistence_half_life'),
            'oscillation_amplitude': recovery.get('oscillation_amplitude'),
            'throughput_stabilization': recovery.get('throughput_stabilization'),
            'final_connectivity': recovery.get('final_connectivity'),
            'final_assignment_rate': recovery.get('final_assignment_rate'),
            'representation_audit': audit,
        }
        
        print(f"  Recovery time: {recovery.get('recovery_time')}")
        print(f"  Persistence half-life: {recovery.get('persistence_half_life')}")
        print(f"  Oscillation amplitude: {recovery.get('oscillation_amplitude'):.4f}")
        print(f"  Normalization survival: {audit.get('normalization_survival', 'N/A')}")
        print(f"  Segmentation dependence: {audit.get('segmentation_dependence', 'N/A')}")
        print(f"  Gauge-removable: {audit.get('gauge_removable', 'N/A')}")
    
    # ─── Phase 3: Failure Condition Evaluation ───
    print("\n[Phase 3] Evaluating failure conditions...")
    
    f1_violations = 0
    f2_violations = 0
    f3_violations = 0
    f4_violations = 0
    
    for name, data in results.items():
        if name == 'baseline':
            continue
        
        audit = data.get('representation_audit', {})
        
        # F1: persistence disappears after normalization
        if audit.get('normalization_survival', 0) < -0.1:
            f1_violations += 1
            print(f"  F1 VIOLATION: {name} — structure was scale artifact")
        
        # F2: observables vary wildly across embeddings
        if audit.get('raw_embedding_change', 0) > 0.5:
            f2_violations += 1
            print(f"  F2 VIOLATION: {name} — representation-dependent only")
        
        # F3: topology persistence under one segmentation only
        if audit.get('segmentation_dependence', 0) > 0.3:
            f3_violations += 1
            print(f"  F3 VIOLATION: {name} — observer-conditioned artifact")
        
        # F4: recovery trajectories fail replication
        if data.get('recovery_time') is None and data.get('final_connectivity', 0) < 0.5:
            f4_violations += 1
            print(f"  F4 VIOLATION: {name} — no transportable persistence")
    
    total_violations = f1_violations + f2_violations + f3_violations + f4_violations
    print(f"\n  Total violations: {total_violations}/12")
    
    # ─── Phase 4: Transport Verdict ───
    print("\n[Phase 4] Transport verdict...")
    
    if total_violations == 0:
        verdict = "TRANSPORTABLE: All persistence observables survive representation audit."
    elif total_violations <= 3:
        verdict = "PARTIALLY TRANSPORTABLE: Some structure survives, some is gauge-induced."
    else:
        verdict = "NOT TRANSPORTABLE: Most persistence structure is representation-dependent."
    
    print(f"  VERDICT: {verdict}")
    results['verdict'] = verdict
    results['failure_conditions'] = {
        'F1': f1_violations,
        'F2': f2_violations,
        'F3': f3_violations,
        'F4': f4_violations,
    }
    
    # Save results
    with open('/home/student/sgp_core_v2/post_omega_study_001/results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to post_omega_study_001/results.json")
    print("=" * 70)
    
    return results


if __name__ == '__main__':
    run_study_001()
