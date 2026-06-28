"""
Phase 002B — Organizational Connection Formalism

True geometric formalism for organizational fiber bundles:
  B = (M, F, π, ∇)

where:
  M = organizational manifold
  F = historical fiber
  π = projection from fiber to observable
  ∇ = replay transport connection
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Callable
from scipy.linalg import expm, logm
from scipy.integrate import quad
import json


# ═══════════════════════════════════════════════════════════════════
# Core Structures
# ═══════════════════════════════════════════════════════════════════

@dataclass
class OrganizationalState:
    """Point on the organizational manifold M."""
    vector: np.ndarray
    timestamp: int = 0
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        self.vector = np.asarray(self.vector, dtype=float)
    
    def distance_to(self, other: 'OrganizationalState') -> float:
        """Euclidean distance between two organizational states."""
        return float(np.linalg.norm(self.vector - other.vector))
    
    def interpolate(self, other: 'OrganizationalState', t: float) -> 'OrganizationalState':
        """Linearly interpolate between two organizational states at parameter t ∈ [0, 1]."""
        interp_vec = self.vector * (1 - t) + other.vector * t
        return OrganizationalState(vector=interp_vec, timestamp=int(self.timestamp * (1 - t) + other.timestamp * t))


@dataclass
class HistoricalFiber:
    """Fiber F attached to a point on M."""
    residue: np.ndarray
    basis: np.ndarray  # Fiber basis vectors (columns = basis)
    connection_matrix: np.ndarray = None  # Local connection coefficients
    
    def __post_init__(self):
        self.residue = np.asarray(self.residue, dtype=float)
        self.basis = np.asarray(self.basis, dtype=float)
        if self.connection_matrix is None:
            dim = len(self.residue)
            self.connection_matrix = np.eye(dim)
    
    def entanglement(self) -> float:
        return float(np.linalg.norm(self.residue))
    
    def twist_angle(self) -> float:
        """Compute twist angle of fiber relative to basis."""
        if self.basis.shape[1] < 2:
            return 0.0
        # Angle between residue and first basis vector
        v1 = self.basis[:, 0]
        cos_angle = np.dot(self.residue, v1) / (np.linalg.norm(self.residue) * np.linalg.norm(v1) + 1e-10)
        return float(np.arccos(np.clip(cos_angle, -1, 1)))


# ═══════════════════════════════════════════════════════════════════
# Connection Operator
# ═══════════════════════════════════════════════════════════════════

class ConnectionOperator:
    """
    Transport connection ∇: F_x → F_y along trajectory segment γ.
    
    Implements parallel transport of historical residue with
    local connection coefficients.
    """
    
    def __init__(self, dimension: int = 4, connection_type: str = 'levi_civita'):
        self.dimension = dimension
        self.connection_type = connection_type
        self.connection_coefficients = np.zeros((dimension, dimension, dimension))
    
    def compute_connection_coefficients(self, manifold_points: List[np.ndarray]) -> np.ndarray:
        """
        Compute local connection coefficients Γ^k_ij from manifold geometry.
        
        Uses finite differences on the manifold to estimate Christoffel symbols.
        """
        n = len(manifold_points)
        if n < 3:
            return self.connection_coefficients
        
        self.connection_coefficients = np.zeros((self.dimension, self.dimension, self.dimension))
        
        # Estimate tangent vectors
        tangents = []
        for i in range(n - 1):
            tangent = manifold_points[i + 1] - manifold_points[i]
            tangents.append(tangent)
        
        # Estimate second derivatives (acceleration) and distribute to Γ^k_ij
        for i in range(len(tangents) - 1):
            acceleration = tangents[i + 1] - tangents[i]
            base = manifold_points[i]
            # For each dimension k of acceleration, distribute to Γ^k_jj
            for k in range(self.dimension):
                norm_sq = np.sum(base ** 2)
                if norm_sq > 1e-10:
                    for j in range(self.dimension):
                        self.connection_coefficients[k, j, j] += acceleration[k] * base[j] / norm_sq
        
        # Normalize by number of samples
        self.connection_coefficients /= max(n - 2, 1)
        
        return self.connection_coefficients
    
    def parallel_transport(self, fiber: HistoricalFiber, 
                          from_point: np.ndarray, 
                          to_point: np.ndarray,
                          dt: float = 1.0) -> HistoricalFiber:
        """
        Parallel transport fiber along geodesic from from_point to to_point.
        
        Transport equation: dF/dt = -Γ(γ̇)F
        """
        # Tangent vector
        tangent = to_point - from_point
        tangent_norm = np.linalg.norm(tangent)
        if tangent_norm < 1e-10:
            return HistoricalFiber(
                residue=fiber.residue.copy(),
                basis=fiber.basis.copy(),
                connection_matrix=fiber.connection_matrix.copy(),
            )
        
        tangent_unit = tangent / tangent_norm
        
        # Compute transport operator using exponential map
        # ∇_γ̇ = Γ^k_ij γ̇^i
        transport_generator = np.zeros((self.dimension, self.dimension))
        for k in range(self.dimension):
            for i in range(self.dimension):
                for j in range(self.dimension):
                    transport_generator[k, j] += self.connection_coefficients[k, i, j] * tangent_unit[i]
        
        # Transport matrix: exp(-∫ Γ γ̇ dt)
        transport_matrix = expm(-transport_generator * tangent_norm * dt)
        
        # Transport fiber
        transported_residue = transport_matrix @ fiber.residue
        transported_basis = transport_matrix @ fiber.basis
        new_connection = transport_matrix @ fiber.connection_matrix @ np.linalg.inv(transport_matrix)
        
        return HistoricalFiber(
            residue=transported_residue,
            basis=transported_basis,
            connection_matrix=new_connection,
        )
    
    def compute_transport_error(self, fiber1: HistoricalFiber, fiber2: HistoricalFiber) -> float:
        """Measure transport inconsistency between two fibers."""
        return float(np.linalg.norm(fiber1.residue - fiber2.residue))


# ═══════════════════════════════════════════════════════════════════
# Curvature Tensor
# ═══════════════════════════════════════════════════════════════════

class CurvatureTensor:
    """
    Local curvature tensor R(X,Y) = ∇_X ∇_Y - ∇_Y ∇_X - ∇_[X,Y]
    
    Measures noncommutativity of replay transport.
    """
    
    def __init__(self, connection: ConnectionOperator):
        self.connection = connection
        self.dimension = connection.dimension
        self.curvature_array = np.zeros((self.dimension, self.dimension, 
                                         self.dimension, self.dimension))
    
    def compute_curvature(self, point: np.ndarray, 
                         basis_vectors: List[np.ndarray]) -> np.ndarray:
        """
        Compute curvature tensor at a point.
        
        R^i_jkl = ∂_k Γ^i_jl - ∂_l Γ^i_jk + Γ^i_mk Γ^m_jl - Γ^i_ml Γ^m_jk
        """
        if len(basis_vectors) < 2:
            return self.curvature_array
        
        epsilon = 1e-6
        Gamma = self.connection.connection_coefficients
        
        for i in range(self.dimension):
            for j in range(self.dimension):
                for k in range(self.dimension):
                    for l in range(self.dimension):
                        # ∂_k Γ^i_jl
                        point_k = point.copy()
                        point_k[k] += epsilon
                        self.connection.compute_connection_coefficients([point, point_k])
                        Gamma_k = self.connection.connection_coefficients.copy()
                        
                        point_mk = point.copy()
                        point_mk[k] -= epsilon
                        self.connection.compute_connection_coefficients([point_mk, point])
                        Gamma_mk = self.connection.connection_coefficients.copy()
                        
                        d_k_Gamma = (Gamma_k - Gamma_mk) / (2 * epsilon)
                        
                        # ∂_l Γ^i_jk
                        point_l = point.copy()
                        point_l[l] += epsilon
                        self.connection.compute_connection_coefficients([point, point_l])
                        Gamma_l = self.connection.connection_coefficients.copy()
                        
                        point_ml = point.copy()
                        point_ml[l] -= epsilon
                        self.connection.compute_connection_coefficients([point_ml, point])
                        Gamma_ml = self.connection.connection_coefficients.copy()
                        
                        d_l_Gamma = (Gamma_l - Gamma_ml) / (2 * epsilon)
                        
                        # Quadratic terms: Γ^i_mk Γ^m_jl - Γ^i_ml Γ^m_jk
                        quad1 = sum(Gamma[i, m, k] * Gamma[m, j, l] for m in range(self.dimension))
                        quad2 = sum(Gamma[i, m, l] * Gamma[m, j, k] for m in range(self.dimension))
                        
                        self.curvature_array[i, j, k, l] = (
                            d_k_Gamma[i, j, l] - d_l_Gamma[i, j, k] + quad1 - quad2
                        )
        
        # Restore original connection coefficients
        self.connection.compute_connection_coefficients([point])
        
        return self.curvature_array
    
    def curvature_magnitude(self) -> float:
        """Frobenius norm of curvature tensor."""
        return float(np.linalg.norm(self.curvature_array))
    
    def ricci_scalar(self) -> float:
        """Ricci scalar curvature: contract R^i_jkl -> R_jl = R^i_jil, then trace."""
        n = self.dimension
        ricci = np.zeros((n, n))
        for j in range(n):
            for l in range(n):
                for i in range(n):
                    ricci[j, l] += self.curvature_array[i, j, i, l]
        return float(np.trace(ricci))


# ═══════════════════════════════════════════════════════════════════
# Holonomy Spectrum
# ═══════════════════════════════════════════════════════════════════

class HolonomySpectrum:
    """
    Compute holonomy distribution over replay loops.
    """
    
    def __init__(self, connection: ConnectionOperator):
        self.connection = connection
    
    def compute_loop_holonomy(self, bundle_states: List[OrganizationalState],
                             bundle_fibers: List[HistoricalFiber],
                             loop_indices: List[int]) -> Dict:
        """
        Compute holonomy around a closed loop.
        
        Returns closure error and transport matrix product.
        """
        if len(loop_indices) < 3:
            return {'holonomy': 0.0, 'transport_matrix': np.eye(self.connection.dimension)}
        
        # Start fiber
        initial_fiber = bundle_fibers[loop_indices[0]]
        current_fiber = HistoricalFiber(
            residue=initial_fiber.residue.copy(),
            basis=initial_fiber.basis.copy(),
            connection_matrix=initial_fiber.connection_matrix.copy(),
        )
        
        # Transport around loop
        transport_product = np.eye(self.connection.dimension)
        
        for i in range(len(loop_indices) - 1):
            from_idx = loop_indices[i]
            to_idx = loop_indices[i + 1]
            
            from_point = bundle_states[from_idx].vector
            to_point = bundle_states[to_idx].vector
            
            current_fiber = self.connection.parallel_transport(
                current_fiber, from_point, to_point
            )
            
            # Accumulate transport matrix
            tangent = to_point - from_point
            tangent_norm = np.linalg.norm(tangent)
            if tangent_norm > 1e-10:
                tangent_unit = tangent / tangent_norm
                transport_gen = np.zeros((self.connection.dimension, self.connection.dimension))
                for k in range(self.connection.dimension):
                    for j in range(self.connection.dimension):
                        transport_gen[k, j] += self.connection.connection_coefficients[k, j, j] * tangent_unit[j]
                transport_product = expm(-transport_gen * tangent_norm) @ transport_product
        
        # Close the loop
        current_fiber = self.connection.parallel_transport(
            current_fiber,
            bundle_states[loop_indices[-1]].vector,
            bundle_states[loop_indices[0]].vector
        )
        
        # Holonomy = closure error
        holonomy_error = float(np.linalg.norm(current_fiber.residue - initial_fiber.residue))
        
        return {
            'holonomy': holonomy_error,
            'transport_matrix': transport_product,
            'final_residue': current_fiber.residue,
            'initial_residue': initial_fiber.residue,
        }
    
    def compute_spectrum(self, bundle_states: List[OrganizationalState],
                        bundle_fibers: List[HistoricalFiber],
                        n_loops: int = 50,
                        loop_length: int = 4) -> Dict:
        """
        Compute holonomy spectrum over many random loops.
        """
        n_states = len(bundle_states)
        if n_states < loop_length + 1:
            return {'mean_holonomy': 0.0, 'std_holonomy': 0.0, 'holonomies': []}
        
        holonomies = []
        transport_matrices = []
        
        for _ in range(n_loops):
            # Random loop
            indices = np.random.choice(n_states, loop_length, replace=False)
            indices = np.sort(indices).tolist()
            indices.append(indices[0])  # Close loop
            
            result = self.compute_loop_holonomy(bundle_states, bundle_fibers, indices)
            holonomies.append(result['holonomy'])
            transport_matrices.append(result['transport_matrix'])
        
        holonomies = np.array(holonomies)
        
        # Spectral analysis of transport matrices
        spectral_data = []
        for tm in transport_matrices:
            eigenvalues = np.linalg.eigvals(tm)
            spectral_data.append({
                'eigenvalues': eigenvalues,
                'spectral_radius': float(np.max(np.abs(eigenvalues))),
                'determinant': float(np.abs(np.linalg.det(tm))),
            })
        
        return {
            'mean_holonomy': float(np.mean(holonomies)),
            'std_holonomy': float(np.std(holonomies)),
            'max_holonomy': float(np.max(holonomies)),
            'min_holonomy': float(np.min(holonomies)),
            'median_holonomy': float(np.median(holonomies)),
            'holonomies': holonomies.tolist(),
            'spectral_data': spectral_data,
            'loop_instability': float(np.std(holonomies) / (np.mean(holonomies) + 1e-10)),
        }


# ═══════════════════════════════════════════════════════════════════
# Fiber Twist / Historical Curvature
# ═══════════════════════════════════════════════════════════════════

class FiberTwist:
    """
    Measure historical entanglement as geometric twisting of replay fibers.
    """
    
    def __init__(self, connection: ConnectionOperator):
        self.connection = connection
    
    def compute_fiber_torsion(self, fiber: HistoricalFiber) -> float:
        """
        Compute torsion of fiber: how much the fiber twists relative to its basis.
        
        Torsion = |∇_X Y - ∇_Y X - [X,Y]|
        """
        if fiber.basis.shape[1] < 2:
            return 0.0
        
        # Compute covariant derivatives along basis vectors
        X = fiber.basis[:, 0]
        Y = fiber.basis[:, 1] if fiber.basis.shape[1] > 1 else np.zeros_like(X)
        
        # Approximate Lie bracket [X,Y] ≈ X·∇Y - Y·∇X
        # For discrete fibers, use residue winding
        
        # Torsion as angle between residue and basis plane
        residue_proj = np.dot(fiber.residue, fiber.basis[:, 0]) * fiber.basis[:, 0]
        if fiber.basis.shape[1] > 1:
            residue_proj += np.dot(fiber.residue, fiber.basis[:, 1]) * fiber.basis[:, 1]
        
        torsion = np.linalg.norm(fiber.residue - residue_proj)
        return float(torsion)
    
    def compute_replay_phase_drift(self, trajectory_fibers: List[HistoricalFiber]) -> float:
        """
        Measure phase drift along trajectory.
        
        Phase drift = accumulated angle change of fiber orientation.
        """
        if len(trajectory_fibers) < 2:
            return 0.0
        
        phases = []
        for fiber in trajectory_fibers:
            phase = fiber.twist_angle()
            phases.append(phase)
        
        # Phase drift = total variation
        drift = sum(abs(phases[i+1] - phases[i]) for i in range(len(phases) - 1))
        return float(drift)
    
    def compute_winding_number(self, trajectory_fibers: List[HistoricalFiber]) -> float:
        """
        Compute winding number of fiber residue trajectory.
        
        Winding = total angle / 2π
        """
        if len(trajectory_fibers) < 3:
            return 0.0
        
        angles = []
        for fiber in trajectory_fibers:
            angle = np.arctan2(fiber.residue[1] if len(fiber.residue) > 1 else 0, 
                              fiber.residue[0])
            angles.append(angle)
        
        # Unwrap angles
        unwrapped = np.unwrap(angles)
        
        # Winding number
        total_angle = unwrapped[-1] - unwrapped[0]
        winding = total_angle / (2 * np.pi)
        
        return float(winding)
    
    def compute_transport_asymmetry(self, fiber_forward: HistoricalFiber,
                                   fiber_backward: HistoricalFiber) -> float:
        """
        Measure path-dependent transport asymmetry.
        
        Asymmetry = ||F_forward - F_backward|| / (||F_forward|| + ||F_backward||)
        """
        forward_norm = np.linalg.norm(fiber_forward.residue)
        backward_norm = np.linalg.norm(fiber_backward.residue)
        
        if forward_norm + backward_norm < 1e-10:
            return 0.0
        
        asymmetry = np.linalg.norm(fiber_forward.residue - fiber_backward.residue) / (forward_norm + backward_norm)
        return float(asymmetry)
    
    def compute_monodromy(self, bundle_states: List[OrganizationalState],
                         bundle_fibers: List[HistoricalFiber],
                         loop_indices: List[int]) -> float:
        """
        Compute monodromy: failure of fiber to return to original state
        after parallel transport around a closed loop.
        """
        holonomy_spectrum = HolonomySpectrum(self.connection)
        result = holonomy_spectrum.compute_loop_holonomy(
            bundle_states, bundle_fibers, loop_indices
        )
        
        # Monodromy = log of holonomy matrix determinant
        det = np.linalg.det(result['transport_matrix'])
        monodromy = float(np.abs(np.log(det + 1e-10)))
        
        return monodromy


# ═══════════════════════════════════════════════════════════════════
# Organizational Geodesics
# ═══════════════════════════════════════════════════════════════════

class OrganizationalGeodesics:
    """
    Compute shortest replay-equivalent paths between organizational states.
    """
    
    def __init__(self, connection: ConnectionOperator):
        self.connection = connection
    
    def replay_distance(self, state1: OrganizationalState, fiber1: HistoricalFiber,
                       state2: OrganizationalState, fiber2: HistoricalFiber,
                       n_interpolations: int = 10) -> Dict:
        """
        Compute organizational distance d_G(x,y) as replay cost.
        """
        # Direct geodesic cost
        direct_cost = state1.distance_to(state2)
        
        # Transport cost: transport fiber1 to state2, compare with fiber2
        transported = self.connection.parallel_transport(
            fiber1, state1.vector, state2.vector
        )
        transport_cost = np.linalg.norm(transported.residue - fiber2.residue)
        
        # Interpolated path cost
        path_costs = []
        for t in np.linspace(0, 1, n_interpolations):
            interp_state = state1.interpolate(state2, t)
            interp_fiber = self.connection.parallel_transport(
                fiber1, state1.vector, interp_state.vector
            )
            path_cost = np.linalg.norm(interp_fiber.residue)
            path_costs.append(path_cost)
        
        # Total geodesic cost: combines state distance + fiber transport + path integrity
        geodesic_cost = direct_cost + transport_cost + np.std(path_costs)
        
        return {
            'geodesic_cost': float(geodesic_cost),
            'direct_cost': float(direct_cost),
            'transport_cost': float(transport_cost),
            'path_variability': float(np.std(path_costs)),
            'transported_residue': transported.residue,
        }
    
    def find_optimal_path(self, state1: OrganizationalState, fiber1: HistoricalFiber,
                         state2: OrganizationalState, fiber2: HistoricalFiber,
                         n_waypoints: int = 5, n_iterations: int = 50) -> Dict:
        """
        Find optimal replay path by variational optimization.
        """
        dim = len(state1.vector)
        
        # Initialize waypoints
        waypoints = []
        for i in range(n_waypoints):
            t = (i + 1) / (n_waypoints + 1)
            wp = state1.interpolate(state2, t)
            waypoints.append(wp)
        
        best_cost = float('inf')
        best_waypoints = waypoints.copy()
        
        for iteration in range(n_iterations):
            # Compute current cost
            total_cost = 0.0
            current_state = state1
            current_fiber = fiber1
            
            for wp in waypoints:
                cost = self.replay_distance(current_state, current_fiber, wp, fiber2)
                total_cost += cost['geodesic_cost']
                current_state = wp
                current_fiber = cost['transported_residue']
            
            # Final segment
            cost = self.replay_distance(current_state, current_fiber, state2, fiber2)
            total_cost += cost['geodesic_cost']
            
            if total_cost < best_cost:
                best_cost = total_cost
                best_waypoints = [wp for wp in waypoints]
            
            # Gradient descent update
            learning_rate = 0.1 / (iteration + 1)
            for i, wp in enumerate(waypoints):
                # Perturb waypoint
                perturbation = np.random.randn(dim) * 0.01
                new_wp = OrganizationalState(
                    vector=wp.vector + perturbation,
                    timestamp=wp.timestamp,
                )
                waypoints[i] = new_wp
        
        return {
            'optimal_cost': float(best_cost),
            'waypoints': best_waypoints,
            'n_iterations': n_iterations,
        }


# ═══════════════════════════════════════════════════════════════════
# Bundle Construction
# ═══════════════════════════════════════════════════════════════════

def state_to_vector(state: dict) -> np.ndarray:
    """Convert simulation state dict to fixed 8-dimensional normalized vector."""
    if not state:
        return np.zeros(8)
    
    # Fixed-order keys: always map to the same 8 dimensions
    fixed_keys = [
        'connectivity',        # dim 0: graph connectivity
        'n_active',            # dim 1: active elements
        'routing_entropy',     # dim 2: routing diversity
        'assignment_rate',     # dim 3: task allocation
        'allocation_entropy',  # dim 4: allocation diversity
        'mean_activation',     # dim 5: mean activation level
        'type_entropy',        # dim 6: type diversity
        'efficiency',          # dim 7: system efficiency
    ]
    
    vec = np.zeros(8)
    for i, key in enumerate(fixed_keys):
        v = state.get(key, None)
        if v is not None and isinstance(v, (int, float)):
            vec[i] = float(v)
    
    # Normalize by max absolute value
    max_abs = np.max(np.abs(vec))
    if max_abs > 1e-10:
        vec = vec / max_abs
    return np.clip(vec, -1, 1)


def build_bundle(trajectory: list, memory_depth: int = 10) -> Tuple[
    List[OrganizationalState], List[HistoricalFiber], ConnectionOperator
]:
    """
    Build organizational bundle from simulation trajectory.
    
    Fiber residue = normalized deviation of current state from recent history mean.
    This makes the residue bounded and meaningful relative to the manifold scale.
    """
    dim = 8  # State dimension
    
    # Initialize connection
    connection = ConnectionOperator(dimension=dim)
    
    states = []
    fibers = []
    
    for t, state in enumerate(trajectory):
        vec = state_to_vector(state)
        
        # Create state
        org_state = OrganizationalState(vector=vec, timestamp=t)
        states.append(org_state)
        
        # Create fiber: residue = deviation from recent history mean
        lineage = []
        for i in range(max(0, t - memory_depth), t):
            lineage.append(state_to_vector(trajectory[i]))
        
        if lineage:
            history_mean = np.mean(lineage, axis=0)
            residue = vec - history_mean  # Deviation from recent mean
            # Normalize residue to bounded scale
            res_norm = np.linalg.norm(residue)
            if res_norm > 1e-10:
                residue = residue / res_norm
        else:
            residue = np.zeros(dim)
        
        # Create orthonormal basis for fiber from recent state differences
        actual_dim = len(residue)
        if len(lineage) > 2:
            diffs = []
            for i in range(1, len(lineage)):
                d = lineage[i] - lineage[i-1]
                if len(d) == actual_dim:
                    diffs.append(d)
            if len(diffs) >= 1:
                n_cols = min(len(diffs), actual_dim)
                basis = np.column_stack(diffs[:n_cols])
                if basis.shape[1] < actual_dim:
                    pad = np.eye(actual_dim)[:, :actual_dim - basis.shape[1]]
                    basis = np.column_stack([basis, pad])
                basis, _ = np.linalg.qr(basis)
            else:
                basis = np.eye(actual_dim)
        else:
            basis = np.eye(actual_dim)
        
        fiber = HistoricalFiber(
            residue=residue,
            basis=basis,
            connection_matrix=np.eye(dim),
        )
        fibers.append(fiber)
    
    # Compute connection coefficients from manifold geometry
    manifold_points = [s.vector for s in states]
    connection.compute_connection_coefficients(manifold_points)
    
    return states, fibers, connection


# ═══════════════════════════════════════════════════════════════════
# Representation Covariance Test
# ═══════════════════════════════════════════════════════════════════

class RepresentationCovarianceTest:
    """
    Test whether geometric observables survive representation change.
    """
    
    def __init__(self):
        self.gauge_transforms = {
            'identity': lambda v: v.copy(),
            'normalize': lambda v: v / (np.linalg.norm(v) + 1e-10),
            'permute': lambda v: v[np.argsort(-v)],
            'scale': lambda v: v * (0.5 + np.random.random()),
            'sign_flip': lambda v: v * np.sign(v + 1e-10),
        }
    
    def apply_gauge(self, states: List[OrganizationalState],
                   fibers: List[HistoricalFiber],
                   gauge_name: str) -> Tuple[List[OrganizationalState], List[HistoricalFiber]]:
        """Apply gauge transformation to bundle."""
        gauge_fn = self.gauge_transforms[gauge_name]
        
        new_states = []
        new_fibers = []
        
        for state, fiber in zip(states, fibers):
            new_vec = gauge_fn(state.vector)
            new_residue = gauge_fn(fiber.residue)
            new_basis = np.column_stack([gauge_fn(fiber.basis[:, i]) for i in range(fiber.basis.shape[1])])
            
            new_states.append(OrganizationalState(vector=new_vec, timestamp=state.timestamp))
            new_fibers.append(HistoricalFiber(
                residue=new_residue,
                basis=new_basis,
                connection_matrix=fiber.connection_matrix.copy(),
            ))
        
        return new_states, new_fibers
    
    def test_covariance(self, states: List[OrganizationalState],
                       fibers: List[HistoricalFiber],
                       connection: ConnectionOperator) -> Dict:
        """
        Test whether geometric observables are gauge-covariant.
        """
        # Compute observables in original gauge
        original_observables = self._compute_observables(states, fibers, connection)
        
        results = {'original': original_observables}
        
        # Test each gauge
        for gauge_name in self.gauge_transforms:
            if gauge_name == 'identity':
                continue
            
            new_states, new_fibers = self.apply_gauge(states, fibers, gauge_name)
            new_connection = ConnectionOperator(dimension=connection.dimension)
            new_connection.compute_connection_coefficients([s.vector for s in new_states])
            
            gauge_observables = self._compute_observables(new_states, new_fibers, new_connection)
            
            # Compute invariance
            invariance = {}
            for key in original_observables:
                if key in gauge_observables and isinstance(original_observables[key], (int, float)):
                    orig = original_observables[key]
                    gauge = gauge_observables[key]
                    if abs(orig) > 1e-10:
                        invariance[key] = 1.0 - abs(orig - gauge) / abs(orig)
                    else:
                        invariance[key] = 1.0 if abs(gauge) < 1e-10 else 0.0
            
            results[gauge_name] = {
                'observables': gauge_observables,
                'invariance': invariance,
            }
        
        return results
    
    def _compute_observables(self, states: List[OrganizationalState],
                            fibers: List[HistoricalFiber],
                            connection: ConnectionOperator) -> Dict:
        """Compute geometric observables."""
        # Curvature
        curvature = CurvatureTensor(connection)
        if len(states) > 0:
            curvature.compute_curvature(states[0].vector, [np.eye(connection.dimension)])
        
        # Holonomy spectrum
        holonomy = HolonomySpectrum(connection)
        spectrum = holonomy.compute_spectrum(states, fibers, n_loops=20, loop_length=4)
        
        # Fiber twist
        twist = FiberTwist(connection)
        torsions = [twist.compute_fiber_torsion(f) for f in fibers]
        
        return {
            'curvature_magnitude': curvature.curvature_magnitude(),
            'ricci_scalar': curvature.ricci_scalar(),
            'mean_holonomy': spectrum['mean_holonomy'],
            'std_holonomy': spectrum['std_holonomy'],
            'loop_instability': spectrum['loop_instability'],
            'mean_torsion': float(np.mean(torsions)),
            'max_torsion': float(np.max(torsions)),
        }


# ═══════════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════════

__all__ = [
    'OrganizationalState',
    'HistoricalFiber',
    'ConnectionOperator',
    'CurvatureTensor',
    'HolonomySpectrum',
    'FiberTwist',
    'OrganizationalGeodesics',
    'RepresentationCovarianceTest',
    'build_bundle',
    'state_to_vector',
]
