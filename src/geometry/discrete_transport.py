"""
Phase 002C — Discrete Transport Algebra & Stress Test

Core insight: organizational geometry is discrete/noncommutative,
not smooth-Riemannian. Transport operators compose like morphisms.

Central hypothesis: H ≡ transport noncommutativity
  G ∝ 1/T where T = transport instability

Transport observable:
  T = E[||τ_γ1(f) - τ_γ2(f)||]
  = how much does replay outcome depend on replay path?
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Callable
from scipy.linalg import expm
import json
import sys

sys.path.insert(0, '/home/student/SGI-Persistence/src')
from geometry.connection_formalism import (
    OrganizationalState, HistoricalFiber, ConnectionOperator,
    build_bundle, state_to_vector
)


# ═══════════════════════════════════════════════════════════════════
# Discrete Transport Operators
# ═══════════════════════════════════════════════════════════════════

@dataclass
class TransportOperator:
    """
    Discrete transport operator τ_γ: F_x → F_y
    
    A morphism in the organizational category.
    """
    matrix: np.ndarray
    source_idx: int
    target_idx: int
    path_label: str = ""
    
    def compose(self, other: 'TransportOperator') -> 'TransportOperator':
        """Compose two transport operators: self ∘ other"""
        return TransportOperator(
            matrix=self.matrix @ other.matrix,
            source_idx=other.source_idx,
            target_idx=self.target_idx,
            path_label=f"{self.path_label}∘{other.path_label}",
        )
    
    def apply(self, fiber: HistoricalFiber) -> HistoricalFiber:
        """Apply transport to a fiber."""
        return HistoricalFiber(
            residue=self.matrix @ fiber.residue,
            basis=self.matrix @ fiber.basis,
            connection_matrix=self.matrix @ fiber.connection_matrix @ np.linalg.inv(self.matrix + 1e-10 * np.eye(self.matrix.shape[0])),
        )
    
    def commutator(self, other: 'TransportOperator') -> float:
        """Compute commutator norm ||τ_a τ_b - τ_b τ_a||"""
        ab = self.matrix @ other.matrix
        ba = other.matrix @ self.matrix
        return float(np.linalg.norm(ab - ba))
    
    def inversion_error(self) -> float:
        """Compute ||τ τ^{-1} - I|| — transport reversibility error."""
        inv = np.linalg.inv(self.matrix + 1e-10 * np.eye(self.matrix.shape[0]))
        return float(np.linalg.norm(self.matrix @ inv - np.eye(self.matrix.shape[0])))


class DiscreteTransportAlgebra:
    """
    Algebra of discrete transport operators on organizational fibers.
    
    States → objects
    Transports → morphisms
    Path composition → morphism composition
    Noncommutativity → curvature substitute
    """
    
    def __init__(self, dimension: int = 8):
        self.dimension = dimension
        self.transport_operators: Dict[Tuple[int, int], TransportOperator] = {}
    
    def build_transports(self, states: List[OrganizationalState],
                        fibers: List[HistoricalFiber],
                        connection: ConnectionOperator) -> Dict[Tuple[int, int], TransportOperator]:
        """
        Build transport operators from ACTUAL fiber changes.
        
        τ_i→i+1 is defined by how the fiber actually changes between states,
        not by the connection coefficients. This captures the true transport
        structure of the organizational trajectory.
        """
        self.transport_operators = {}
        
        for i in range(len(states) - 1):
            fiber_from = fibers[i]
            fiber_to = fibers[i + 1]
            
            # Transport = how fiber actually changes
            # τ: F_i → F_{i+1}
            residue_from = fiber_from.residue
            residue_to = fiber_to.residue
            
            from_norm = np.linalg.norm(residue_from)
            to_norm = np.linalg.norm(residue_to)
            
            if from_norm < 1e-10:
                # Zero fiber → identity transport
                self.transport_operators[(i, i+1)] = TransportOperator(
                    matrix=np.eye(self.dimension),
                    source_idx=i,
                    target_idx=i+1,
                    path_label=f"e_{i}",
                )
                continue
            
            # Build transport as linear map that takes residue_from → residue_to
            # Using least-squares: residue_to ≈ M @ residue_from
            # M = residue_to @ residue_from^T / (residue_from @ residue_from^T)
            outer_from = np.outer(residue_from, residue_from)
            outer_to = np.outer(residue_to, residue_from)
            
            if np.linalg.norm(outer_from) > 1e-10:
                # Transport in residue subspace
                transport_matrix = np.eye(self.dimension)
                # Project transport onto residue direction
                transport_matrix += np.outer(residue_to, residue_from) / (np.dot(residue_from, residue_from) + 1e-10)
                transport_matrix -= np.eye(self.dimension) * np.dot(residue_to, residue_from) / (np.dot(residue_from, residue_from) + 1e-10)
            else:
                transport_matrix = np.eye(self.dimension)
            
            self.transport_operators[(i, i+1)] = TransportOperator(
                matrix=transport_matrix,
                source_idx=i,
                target_idx=i+1,
                path_label=f"τ_{i}→{i+1}",
            )
        
        return self.transport_operators
    
    def get_path_transport(self, indices: List[int]) -> TransportOperator:
        """
        Compose transport operators along a path.
        
        τ_path = τ_{n-1→n} ∘ ... ∘ τ_{0→1}
        """
        if len(indices) < 2:
            return TransportOperator(
                matrix=np.eye(self.dimension),
                source_idx=0,
                target_idx=0,
                path_label="identity",
            )
        
        result = None
        for i in range(len(indices) - 1):
            key = (indices[i], indices[i+1])
            if key not in self.transport_operators:
                return None
            op = self.transport_operators[key]
            if result is None:
                result = op
            else:
                result = op.compose(result)
        
        return result
    
    def compute_noncommutativity(self, path_a: List[int], path_b: List[int]) -> Dict:
        """
        Test whether τ_a ∘ τ_b ≠ τ_b ∘ τ_a
        
        Returns commutator norm and individual transport norms.
        """
        op_a = self.get_path_transport(path_a)
        op_b = self.get_path_transport(path_b)
        
        if op_a is None or op_b is None:
            return {'commutator_norm': 0.0, 'path_a_norm': 0.0, 'path_b_norm': 0.0, 'relative_noncommutativity': 0.0}
        
        # Commutator: [τ_a, τ_b] = τ_a τ_b - τ_b τ_a
        ab = op_a.compose(op_b)
        ba = op_b.compose(op_a)
        
        commutator_norm = float(np.linalg.norm(ab.matrix - ba.matrix))
        path_a_norm = float(np.linalg.norm(op_a.matrix))
        path_b_norm = float(np.linalg.norm(op_b.matrix))
        
        # Relative noncommutativity: ||[τ_a, τ_b]|| / (||τ_a|| ||τ_b||)
        relative_nc = commutator_norm / (path_a_norm * path_b_norm + 1e-10)
        
        return {
            'commutator_norm': commutator_norm,
            'path_a_norm': path_a_norm,
            'path_b_norm': path_b_norm,
            'relative_noncommutativity': relative_nc,
            'ab_determinant': float(np.linalg.det(ab.matrix)),
            'ba_determinant': float(np.linalg.det(ba.matrix)),
        }
    
    def compute_transport_path_divergence(self, states: List[OrganizationalState],
                                         fibers: List[HistoricalFiber],
                                         n_pairs: int = 20,
                                         path_length: int = 4) -> Dict:
        """
        Compute T = E[||τ_γ1(f) - τ_γ2(f)||]
        
        Canonical transport instability: how much does replay outcome
        depend on replay path?
        
        Uses two different subsequences of the same trajectory (replay-equivalent).
        """
        n_states = len(states)
        if n_states < path_length + 1:
            return {'T': 0.0, 'divergences': []}
        
        divergences = []
        
        for _ in range(n_pairs):
            # Select two different subsequences of same length
            # Both are valid (consecutive index) paths
            start1 = np.random.randint(0, n_states - path_length)
            start2 = np.random.randint(0, n_states - path_length)
            
            path1 = list(range(start1, start1 + path_length + 1))
            path2 = list(range(start2, start2 + path_length + 1))
            
            # Ensure both paths start at the same point for comparison
            # Use the midpoint of path2 as the "start" for comparison
            mid = path1[0]
            
            # Get fiber at common start point
            fiber_start = fibers[mid]
            
            # Transport along path1
            f1 = fiber_start
            for i in range(len(path1) - 1):
                key = (path1[i], path1[i+1])
                if key in self.transport_operators:
                    f1 = self.transport_operators[key].apply(f1)
                else:
                    f1 = None
                    break
            
            # Transport along path2
            f2 = fiber_start
            for i in range(len(path2) - 1):
                key = (path2[i], path2[i+1])
                if key in self.transport_operators:
                    f2 = self.transport_operators[key].apply(f2)
                else:
                    f2 = None
                    break
            
            if f1 is None or f2 is None:
                continue
            
            # Divergence: how different are the transport outcomes?
            div = np.linalg.norm(f1.residue - f2.residue)
            divergences.append(div)
        
        if not divergences:
            return {'T': 0.0, 'divergences': []}
        
        return {
            'T': float(np.mean(divergences)),
            'T_std': float(np.std(divergences)),
            'T_max': float(np.max(divergences)),
            'divergences': divergences,
        }


# ═══════════════════════════════════════════════════════════════════
# Transport Stress Perturbations
# ═══════════════════════════════════════════════════════════════════

class TransportPerturbationSuite:
    """
    Aggressive perturbation families for transport stress testing.
    """
    
    @staticmethod
    def temporal_replay_delay(trajectory: list, delay: int) -> list:
        """A.1: Delay replay by inserting stale states."""
        if delay <= 0:
            return trajectory
        result = []
        for i, state in enumerate(trajectory):
            result.append(state)
            if i > 0 and i % delay == 0:
                # Insert a stale copy of an earlier state
                stale_idx = max(0, i - delay)
                result.append(trajectory[stale_idx].copy() if isinstance(trajectory[stale_idx], dict) else trajectory[stale_idx])
        return result
    
    @staticmethod
    def temporal_async_replay(trajectory: list, swap_fraction: float) -> list:
        """A.2: Swap random pairs of timesteps (async replay)."""
        result = list(trajectory)
        n_swaps = int(len(result) * swap_fraction)
        for _ in range(n_swaps):
            i, j = np.random.choice(len(result), 2, replace=False)
            result[i], result[j] = result[j], result[i]
        return result
    
    @staticmethod
    def temporal_memory_truncation(trajectory: list, keep_fraction: float) -> list:
        """A.3: Truncate memory — keep only recent fraction."""
        n_keep = max(2, int(len(trajectory) * keep_fraction))
        return trajectory[-n_keep:]
    
    @staticmethod
    def temporal_replay_scramble(trajectory: list, scramble_fraction: float) -> list:
        """A.4: Scramble a random subsequence of states."""
        result = list(trajectory)
        n_scramble = int(len(result) * scramble_fraction)
        start = np.random.randint(0, max(1, len(result) - n_scramble))
        subseq = result[start:start + n_scramble]
        np.random.shuffle(subseq)
        result[start:start + n_scramble] = subseq
        return result
    
    @staticmethod
    def structural_node_deletion(trajectory: list, delete_fraction: float) -> list:
        """B.1: Zero out random dimensions in state vectors."""
        result = []
        for state in trajectory:
            new_state = dict(state)
            for key in new_state:
                if isinstance(new_state[key], (int, float)) and np.random.random() < delete_fraction:
                    new_state[key] = 0.0
            result.append(new_state)
        return result
    
    @staticmethod
    def structural_sector_duplication(trajectory: list, dup_fraction: float) -> list:
        """B.2: Duplicate random state values (sector duplication)."""
        result = []
        for state in trajectory:
            new_state = dict(state)
            keys = [k for k in new_state if isinstance(new_state[k], (int, float))]
            if keys:
                n_dup = max(1, int(len(keys) * dup_fraction))
                dup_keys = np.random.choice(keys, n_dup, replace=False)
                source_key = np.random.choice(keys)
                for k in dup_keys:
                    new_state[k] = new_state[source_key]
            result.append(new_state)
        return result
    
    @staticmethod
    def structural_routing_mutation(trajectory: list, mutate_fraction: float) -> list:
        """B.3: Mutate routing-related values."""
        result = []
        for state in trajectory:
            new_state = dict(state)
            for key in ['routing_entropy', 'assignment_rate', 'allocation_entropy', 'n_components']:
                if key in new_state and isinstance(new_state[key], (int, float)):
                    if np.random.random() < mutate_fraction:
                        new_state[key] = new_state[key] * (1 + np.random.randn() * 0.3)
            result.append(new_state)
        return result
    
    @staticmethod
    def structural_topology_rewire(trajectory: list, rewire_fraction: float) -> list:
        """B.4: Randomly rewire connectivity."""
        result = []
        for state in trajectory:
            new_state = dict(state)
            for key in ['connectivity', 'n_active', 'signaling_connectivity']:
                if key in new_state and isinstance(new_state[key], (int, float)):
                    if np.random.random() < rewire_fraction:
                        new_state[key] = np.random.random()
            result.append(new_state)
        return result
    
    @staticmethod
    def gauge_basis_rotation(trajectory: list, angle: float) -> list:
        """C.1: Rotate state vectors by random orthogonal matrix."""
        dim = 8
        # Random rotation matrix via QR
        Q, _ = np.linalg.qr(np.random.randn(dim, dim))
        
        result = []
        for state in trajectory:
            new_state = dict(state)
            vec = state_to_vector(new_state)
            rotated = Q @ vec
            # Map back to state keys
            keys = ['connectivity', 'n_active', 'routing_entropy', 'assignment_rate',
                    'allocation_entropy', 'mean_activation', 'type_entropy', 'efficiency']
            for i, key in enumerate(keys):
                if key in new_state and i < len(rotated):
                    new_state[key] = float(rotated[i])
            result.append(new_state)
        return result
    
    @staticmethod
    def gauge_nonlinear_normalize(trajectory: list) -> list:
        """C.2: Apply nonlinear normalization (tanh)."""
        result = []
        for state in trajectory:
            new_state = dict(state)
            for key in new_state:
                if isinstance(new_state[key], (int, float)):
                    new_state[key] = float(np.tanh(new_state[key]))
            result.append(new_state)
        return result
    
    @staticmethod
    def gauge_random_projection(trajectory: list, compression: float) -> list:
        """C.3: Random projection to lower dimension and back."""
        dim = 8
        proj_dim = max(2, int(dim * (1 - compression)))
        P = np.random.randn(proj_dim, dim)
        P = P / (np.linalg.norm(P, axis=1, keepdims=True) + 1e-10)
        # Pseudo-inverse for reconstruction
        P_pinv = np.linalg.pinv(P)
        
        result = []
        for state in trajectory:
            new_state = dict(state)
            vec = state_to_vector(new_state)
            # Project down and back
            compressed = P @ vec
            reconstructed = P_pinv @ compressed
            keys = ['connectivity', 'n_active', 'routing_entropy', 'assignment_rate',
                    'allocation_entropy', 'mean_activation', 'type_entropy', 'efficiency']
            for i, key in enumerate(keys):
                if key in new_state and i < len(reconstructed):
                    new_state[key] = float(reconstructed[i])
            result.append(new_state)
        return result
    
    @staticmethod
    def gauge_coordinate_compression(trajectory: list, n_bits: int) -> list:
        """C.4: Quantize coordinates (coordinate compression)."""
        levels = 2 ** n_bits
        result = []
        for state in trajectory:
            new_state = dict(state)
            for key in new_state:
                if isinstance(new_state[key], (int, float)):
                    val = new_state[key]
                    quantized = np.round(val * levels) / levels
                    new_state[key] = float(quantized)
            result.append(new_state)
        return result
    
    @staticmethod
    def historical_memory_overwrite(trajectory: list, overwrite_fraction: float) -> list:
        """D.1: Overwrite early states with random noise."""
        result = list(trajectory)
        n_overwrite = int(len(result) * overwrite_fraction)
        for i in range(n_overwrite):
            new_state = dict(result[i])
            for key in new_state:
                if isinstance(new_state[key], (int, float)):
                    new_state[key] = float(np.random.random())
            result[i] = new_state
        return result
    
    @staticmethod
    def historical_residue_injection(trajectory: list, injection_strength: float) -> list:
        """D.2: Inject random residue into state vectors."""
        result = []
        for state in trajectory:
            new_state = dict(state)
            for key in new_state:
                if isinstance(new_state[key], (int, float)):
                    new_state[key] = new_state[key] + injection_strength * np.random.randn()
            result.append(new_state)
        return result
    
    @staticmethod
    def historical_replay_branch(trajectory: list, branch_fraction: float) -> list:
        """D.3: Insert alternate history branch."""
        result = list(trajectory)
        branch_point = int(len(result) * 0.5)
        branch_length = int(len(result) * branch_fraction)
        
        # Create alternate branch
        branch = []
        for i in range(branch_length):
            idx = min(branch_point + i, len(result) - 1)
            new_state = dict(result[idx])
            for key in new_state:
                if isinstance(new_state[key], (int, float)):
                    new_state[key] = new_state[key] * 0.5 + 0.5 * np.random.random()
            branch.append(new_state)
        
        # Insert branch after branch_point
        result = result[:branch_point + 1] + branch + result[branch_point + 1:]
        return result
    
    @staticmethod
    def historical_counterfactual_replay(trajectory: list, counterfactual_fraction: float) -> list:
        """D.4: Replace states with counterfactual versions."""
        result = list(trajectory)
        n_replace = int(len(result) * counterfactual_fraction)
        for _ in range(n_replace):
            idx = np.random.randint(0, len(result))
            new_state = dict(result[idx])
            # Invert all values
            for key in new_state:
                if isinstance(new_state[key], (int, float)):
                    new_state[key] = 1.0 - new_state[key]
            result[idx] = new_state
        return result


# ═══════════════════════════════════════════════════════════════════
# Transport Stability Phase Diagram
# ═══════════════════════════════════════════════════════════════════

class TransportPhaseDiagram:
    """
    Sweep parameter space and compute transport observables.
    
    Parameters: memory_depth, replay_noise, gauge_distortion, perturbation_intensity
    Observables: T, G, H, transport_error, noncommutativity
    """
    
    def __init__(self, base_trajectory: list, system_name: str = "unknown"):
        self.base_trajectory = base_trajectory
        self.system_name = system_name
        self.suite = TransportPerturbationSuite()
    
    def sweep_parameter_space(self,
                             memory_depths: List[int] = None,
                             noise_levels: List[float] = None,
                             gauge_levels: List[float] = None,
                             intensity_levels: List[float] = None,
                             n_trials: int = 3) -> List[Dict]:
        """
        Sweep parameter space and compute transport observables at each point.
        """
        if memory_depths is None:
            memory_depths = [2, 5, 10, 15, 20]
        if noise_levels is None:
            noise_levels = [0.0, 0.05, 0.1, 0.2, 0.3]
        if gauge_levels is None:
            gauge_levels = [0.0, 0.1, 0.2, 0.3, 0.5]
        if intensity_levels is None:
            intensity_levels = [0.0, 0.1, 0.2, 0.3, 0.5]
        
        results = []
        
        for mem_depth in memory_depths:
            for noise in noise_levels:
                for gauge in gauge_levels:
                    for intensity in intensity_levels:
                        trial_observables = []
                        
                        for trial in range(n_trials):
                            # Apply noise to trajectory
                            traj = list(self.base_trajectory)
                            if noise > 0:
                                traj = self.suite.historical_residue_injection(traj, noise)
                            
                            # Apply gauge distortion
                            if gauge > 0:
                                traj = self.suite.gauge_basis_rotation(traj, gauge)
                            
                            # Apply perturbation based on intensity
                            if intensity > 0:
                                if np.random.random() < 0.25:
                                    traj = self.suite.structural_node_deletion(traj, intensity)
                                elif np.random.random() < 0.5:
                                    traj = self.suite.structural_routing_mutation(traj, intensity)
                                elif np.random.random() < 0.75:
                                    traj = self.suite.temporal_replay_scramble(traj, intensity)
                                else:
                                    traj = self.suite.historical_counterfactual_replay(traj, intensity)
                            
                            # Build bundle and compute observables
                            try:
                                states, fibers, connection = build_bundle(traj, memory_depth=mem_depth)
                                
                                # Build transport algebra
                                algebra = DiscreteTransportAlgebra(dimension=8)
                                algebra.build_transports(states, fibers, connection)
                                
                                # Compute T (transport instability)
                                T_result = algebra.compute_transport_path_divergence(
                                    states, fibers, n_pairs=15, path_length=4
                                )
                                
                                # Compute transport error
                                transport_errors = []
                                for i in range(len(states) - 1):
                                    te = connection.compute_transport_error(fibers[i], fibers[i+1])
                                    transport_errors.append(te)
                                avg_transport_error = np.mean(transport_errors) if transport_errors else 0.0
                                
                                # Compute fiber entanglement
                                fiber_entanglements = [f.entanglement() for f in fibers]
                                avg_fiber_entanglement = np.mean(fiber_entanglements)
                                
                                # Compute noncommutativity (sample random loop pairs)
                                nc_norms = []
                                for _ in range(5):
                                    n = len(states)
                                    if n >= 8:
                                        idx1 = np.random.choice(n, 4, replace=False)
                                        idx2 = np.random.choice(n, 4, replace=False)
                                        nc = algebra.compute_noncommutativity(
                                            sorted(idx1.tolist()), sorted(idx2.tolist())
                                        )
                                        nc_norms.append(nc['relative_noncommutativity'])
                                avg_nc = np.mean(nc_norms) if nc_norms else 0.0
                                
                                trial_observables.append({
                                    'T': T_result['T'],
                                    'transport_error': float(avg_transport_error),
                                    'fiber_entanglement': float(avg_fiber_entanglement),
                                    'noncommutativity': float(avg_nc),
                                })
                            except Exception as e:
                                trial_observables.append({
                                    'T': 0.0,
                                    'transport_error': 0.0,
                                    'fiber_entanglement': 0.0,
                                    'noncommutativity': 0.0,
                                })
                        
                        # Average over trials
                        avg_obs = {}
                        for key in ['T', 'transport_error', 'fiber_entanglement', 'noncommutativity']:
                            vals = [t[key] for t in trial_observables]
                            avg_obs[key] = float(np.mean(vals))
                            avg_obs[f'{key}_std'] = float(np.std(vals))
                        
                        results.append({
                            'memory_depth': mem_depth,
                            'noise': noise,
                            'gauge': gauge,
                            'intensity': intensity,
                            **avg_obs,
                        })
        
        return results


# ═══════════════════════════════════════════════════════════════════
# Discrete Holonomy
# ═══════════════════════════════════════════════════════════════════

class DiscreteHolonomy:
    """
    Discrete holonomy: H_γ = τ_n ∘ ... ∘ τ_1
    
    Holonomy emerges from transport composition,
    not from differential curvature.
    """
    
    def __init__(self, algebra: DiscreteTransportAlgebra):
        self.algebra = algebra
    
    def compute_loop_holonomy(self, loop_indices: List[int]) -> Dict:
        """
        Compute holonomy around a closed loop.
        
        H_γ = τ_{n→0} ∘ τ_{n-1→n} ∘ ... ∘ τ_{0→1}
        
        Closure error = ||H_γ - I||
        """
        if len(loop_indices) < 3:
            return {'holonomy': 0.0, 'closure_error': 0.0, 'det': 1.0, 'spectral_radius': 1.0, 'eigenvalues': [1.0], 'transport_matrix': np.eye(self.algebra.dimension)}
        
        # Compose transport around loop
        path_op = self.algebra.get_path_transport(loop_indices)
        
        if path_op is None:
            return {'holonomy': 0.0, 'closure_error': 0.0, 'det': 1.0, 'spectral_radius': 1.0, 'eigenvalues': [1.0], 'transport_matrix': np.eye(self.algebra.dimension)}
        
        # Closure error: ||H_γ - I||
        closure_error = float(np.linalg.norm(path_op.matrix - np.eye(path_op.matrix.shape[0])))
        
        # Determinant (should be 1 for volume-preserving transport)
        det = float(np.linalg.det(path_op.matrix))
        
        # Spectral analysis
        eigenvalues = np.linalg.eigvals(path_op.matrix)
        spectral_radius = float(np.max(np.abs(eigenvalues)))
        
        return {
            'holonomy': closure_error,
            'closure_error': closure_error,
            'det': det,
            'spectral_radius': spectral_radius,
            'eigenvalues': eigenvalues.tolist(),
            'transport_matrix': path_op.matrix,
        }
    
    def compute_holonomy_spectrum(self, n_states: int, n_loops: int = 30,
                                 loop_length: int = 5) -> Dict:
        """
        Compute holonomy distribution over random loops.
        """
        if n_states < loop_length + 1:
            return {'mean_holonomy': 0.0, 'holonomies': []}
        
        holonomies = []
        dets = []
        spectral_radii = []
        
        for _ in range(n_loops):
            indices = np.random.choice(n_states, loop_length, replace=False)
            indices = np.sort(indices).tolist()
            indices.append(indices[0])  # Close loop
            
            result = self.compute_loop_holonomy(indices)
            holonomies.append(result['holonomy'])
            dets.append(result['det'])
            spectral_radii.append(result['spectral_radius'])
        
        return {
            'mean_holonomy': float(np.mean(holonomies)),
            'std_holonomy': float(np.std(holonomies)),
            'max_holonomy': float(np.max(holonomies)),
            'median_holonomy': float(np.median(holonomies)),
            'mean_det': float(np.mean(dets)),
            'mean_spectral_radius': float(np.mean(spectral_radii)),
            'holonomies': holonomies,
        }
    
    def compute_order_sensitivity(self, path_a: List[int], path_b: List[int]) -> Dict:
        """
        Measure sensitivity of transport to path order.
        
        This is the discrete analog of noncommutativity.
        """
        return self.algebra.compute_noncommutativity(path_a, path_b)


# ═══════════════════════════════════════════════════════════════════
# Transport Canonicalization
# ═══════════════════════════════════════════════════════════════════

class TransportCanonicalization:
    """
    Define and test the canonical transport observable:
    
    T = E[||τ_γ1(f) - τ_γ2(f)||]
    
    where γ1, γ2 are replay-equivalent trajectories.
    
    Test whether G ∝ 1/T outperforms G ∝ 1/H.
    """
    
    def __init__(self, algebra: DiscreteTransportAlgebra):
        self.algebra = algebra
    
    def compute_canonical_T(self, states: List[OrganizationalState],
                           fibers: List[HistoricalFiber],
                           n_pairs: int = 30,
                           path_length: int = 5) -> Dict:
        """
        Compute canonical transport instability T.
        """
        result = self.algebra.compute_transport_path_divergence(
            states, fibers, n_pairs=n_pairs, path_length=path_length
        )
        return result
    
    def compute_replay_divergence(self, states: List[OrganizationalState],
                                 fibers: List[HistoricalFiber],
                                 n_trajectories: int = 10) -> Dict:
        """
        Compute replay divergence: how different are transport outcomes
        from different replay sequences?
        """
        n_states = len(states)
        if n_states < 5:
            return {'replay_divergence': 0.0}
        
        divergences = []
        
        for _ in range(n_trajectories):
            # Random replay order
            indices = np.random.permutation(n_states)
            
            # Transport fiber through shuffled order
            current_fiber = HistoricalFiber(
                residue=fibers[0].residue.copy(),
                basis=fibers[0].basis.copy(),
                connection_matrix=fibers[0].connection_matrix.copy(),
            )
            
            for idx in indices:
                op = self.algebra.get_path_transport([0, idx])
                if op is not None:
                    current_fiber = op.apply(current_fiber)
            
            # Compare with canonical order
            canonical_fiber = HistoricalFiber(
                residue=fibers[0].residue.copy(),
                basis=fibers[0].basis.copy(),
                connection_matrix=fibers[0].connection_matrix.copy(),
            )
            
            for i in range(n_states):
                op = self.algebra.get_path_transport([0, i])
                if op is not None:
                    canonical_fiber = op.apply(canonical_fiber)
            
            div = np.linalg.norm(current_fiber.residue - canonical_fiber.residue)
            divergences.append(div)
        
        return {
            'replay_divergence': float(np.mean(divergences)),
            'replay_divergence_std': float(np.std(divergences)),
        }
    
    def compare_G_T_vs_G_H(self, systems_data: Dict[str, Dict]) -> Dict:
        """
        Compare G ∝ 1/T vs G ∝ 1/H across systems.
        
        systems_data: {system_name: {'G': float, 'H': float, 'T': float}}
        """
        systems = list(systems_data.keys())
        G_vals = np.array([systems_data[s]['G'] for s in systems])
        H_vals = np.array([systems_data[s]['H'] for s in systems])
        T_vals = np.array([systems_data[s]['T'] for s in systems])
        
        # Correlations
        corr_G_H = np.corrcoef(G_vals, H_vals)[0, 1] if np.std(H_vals) > 1e-10 else 0.0
        corr_G_T = np.corrcoef(G_vals, T_vals)[0, 1] if np.std(T_vals) > 1e-10 else 0.0
        
        # 1/H and 1/T correlations
        inv_H = 1.0 / (H_vals + 1e-10)
        inv_T = 1.0 / (T_vals + 1e-10)
        corr_G_invH = np.corrcoef(G_vals, inv_H)[0, 1] if np.std(inv_H) > 1e-10 else 0.0
        corr_G_invT = np.corrcoef(G_vals, inv_T)[0, 1] if np.std(inv_T) > 1e-10 else 0.0
        
        return {
            'corr_G_H': float(corr_G_H),
            'corr_G_T': float(corr_G_T),
            'corr_G_invH': float(corr_G_invH),
            'corr_G_invT': float(corr_G_invT),
            'T_values': {s: float(T_vals[i]) for i, s in enumerate(systems)},
            'better_predictor': 'T' if abs(corr_G_invT) > abs(corr_G_invH) else 'H',
        }


# ═══════════════════════════════════════════════════════════════════
# Category Structure (skeletal)
# ═══════════════════════════════════════════════════════════════════

@dataclass
class OrganizationalObject:
    """An object in the organizational category: a state with its fiber."""
    state: OrganizationalState
    fiber: HistoricalFiber
    label: str = ""


@dataclass
class OrganizationalMorphism:
    """A morphism: transport operator between two objects."""
    source: OrganizationalObject
    target: OrganizationalObject
    transport: TransportOperator
    label: str = ""


class OrganizationalCategory:
    """
    Skeletal category structure for organizational geometry.
    
    Objects: organizational states with fibers
    Morphisms: transport operators
    Composition: path composition
    Identity: identity transport
    """
    
    def __init__(self):
        self.objects: Dict[str, OrganizationalObject] = {}
        self.morphisms: Dict[Tuple[str, str], OrganizationalMorphism] = {}
    
    def add_object(self, obj: OrganizationalObject):
        self.objects[obj.label] = obj
    
    def add_morphism(self, morph: OrganizationalMorphism):
        self.morphisms[(morph.source.label, morph.target.label)] = morph
    
    def compose(self, g: OrganizationalMorphism, f: OrganizationalMorphism) -> Optional[OrganizationalMorphism]:
        """Compose morphisms: g ∘ f"""
        if f.target.label != g.source.label:
            return None
        
        composed_transport = g.transport.compose(f.transport)
        return OrganizationalMorphism(
            source=f.source,
            target=g.target,
            transport=composed_transport,
            label=f"{g.label}∘{f.label}",
        )
    
    def is_commutative(self, f: OrganizationalMorphism, g: OrganizationalMorphism) -> bool:
        """Test whether a diagram commutes: τ_a τ_b ≈ τ_b τ_a"""
        if f.source.label == g.source.label and f.target.label == g.target.label:
            comm_norm = f.transport.commutator(g.transport)
            return comm_norm < 1e-6
        return False
    
    def build_from_bundle(self, states: List[OrganizationalState],
                         fibers: List[HistoricalFiber],
                         algebra: DiscreteTransportAlgebra):
        """Build category from bundle data."""
        for i, (s, f) in enumerate(zip(states, fibers)):
            obj = OrganizationalObject(
                state=s,
                fiber=f,
                label=f"state_{i}",
            )
            self.add_object(obj)
        
        for (i, j), op in algebra.transport_operators.items():
            if f"state_{i}" in self.objects and f"state_{j}" in self.objects:
                morph = OrganizationalMorphism(
                    source=self.objects[f"state_{i}"],
                    target=self.objects[f"state_{j}"],
                    transport=op,
                    label=f"τ_{i}→{j}",
                )
                self.add_morphism(morph)
    
    def summary(self) -> Dict:
        """Return categorical summary."""
        n_objects = len(self.objects)
        n_morphisms = len(self.morphisms)
        
        # Check commutativity of all morphism pairs
        morph_list = list(self.morphisms.values())
        n_commutative = 0
        n_pairs = 0
        commutator_norms = []
        
        for i in range(len(morph_list)):
            for j in range(i + 1, len(morph_list)):
                if morph_list[i].source.label == morph_list[j].source.label:
                    n_pairs += 1
                    cn = morph_list[i].transport.commutator(morph_list[j].transport)
                    commutator_norms.append(cn)
                    if cn < 1e-6:
                        n_commutative += 1
        
        return {
            'n_objects': n_objects,
            'n_morphisms': n_morphisms,
            'n_morphism_pairs': n_pairs,
            'n_commutative': n_commutative,
            'commutativity_fraction': n_commutative / max(n_pairs, 1),
            'mean_commutator_norm': float(np.mean(commutator_norms)) if commutator_norms else 0.0,
            'max_commutator_norm': float(np.max(commutator_norms)) if commutator_norms else 0.0,
        }


# ═══════════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════════

__all__ = [
    'TransportOperator',
    'DiscreteTransportAlgebra',
    'TransportPerturbationSuite',
    'TransportPhaseDiagram',
    'DiscreteHolonomy',
    'TransportCanonicalization',
    'OrganizationalObject',
    'OrganizationalMorphism',
    'OrganizationalCategory',
]
