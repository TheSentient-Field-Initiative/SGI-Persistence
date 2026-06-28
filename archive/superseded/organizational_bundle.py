"""
Phase 002A — Organizational Fiber Geometry

Minimal formal representation:
  F → O → G

where:
  O = organizational manifold
  G = representation gauge group
  F = historical fiber bundle
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Callable
import json


# ═══════════════════════════════════════════════════════════════════
# Core Structures
# ═══════════════════════════════════════════════════════════════════

@dataclass
class OrganizationalState:
    """A point on the organizational manifold O."""
    vector: np.ndarray          # Position in organizational space
    timestamp: int = 0          # Temporal coordinate
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        self.vector = np.asarray(self.vector, dtype=float)
    
    def distance_to(self, other: 'OrganizationalState') -> float:
        """Geodesic distance on the manifold (Euclidean for now)."""
        return float(np.linalg.norm(self.vector - other.vector))
    
    def interpolate(self, other: 'OrganizationalState', t: float) -> 'OrganizationalState':
        """Linear interpolation along geodesic."""
        return OrganizationalState(
            vector=(1 - t) * self.vector + t * other.vector,
            timestamp=int((1 - t) * self.timestamp + t * other.timestamp),
        )


@dataclass
class HistoricalFiber:
    """Fiber attached to an organizational state — represents history."""
    lineage: List[np.ndarray]    # Ancestral state vectors
    residue: np.ndarray          # Accumulated historical residue
    memory_depth: int = 0        # How many steps of history are retained
    overwrite_mask: np.ndarray = None  # Which dimensions are overwritable
    
    def __post_init__(self):
        self.lineage = list(self.lineage) if self.lineage else []
        self.residue = np.asarray(self.residue, dtype=float)
        if self.overwrite_mask is None:
            self.overwrite_mask = np.ones_like(self.residue)
    
    def accumulate(self, state_vector: np.ndarray) -> 'HistoricalFiber':
        """Add new historical residue from a state transition."""
        new_lineage = self.lineage[-(self.memory_depth - 1):] + [state_vector.copy()] if self.memory_depth > 0 else [state_vector.copy()]
        new_residue = self.residue + state_vector * self.overwrite_mask
        return HistoricalFiber(
            lineage=new_lineage,
            residue=new_residue,
            memory_depth=self.memory_depth,
            overwrite_mask=self.overwrite_mask.copy(),
        )
    
    def overwrite(self, fraction: float) -> 'HistoricalFiber':
        """Erase a fraction of historical residue."""
        n_overwrite = int(len(self.residue) * fraction)
        indices = np.random.choice(len(self.residue), n_overwrite, replace=False)
        new_residue = self.residue.copy()
        new_residue[indices] = 0.0
        new_mask = self.overwrite_mask.copy()
        new_mask[indices] = 0.0
        return HistoricalFiber(
            lineage=self.lineage.copy(),
            residue=new_residue,
            memory_depth=self.memory_depth,
            overwrite_mask=new_mask,
        )
    
    def entanglement(self) -> float:
        """Measure historical entanglement (magnitude of residue)."""
        return float(np.linalg.norm(self.residue))
    
    def diff(self, other: 'HistoricalFiber') -> float:
        """Difference between two fibers."""
        return float(np.linalg.norm(self.residue - other.residue))


@dataclass
class OrganizationalBundle:
    """
    The fiber bundle F → O → G.
    
    Base manifold O: set of organizational states
    Fiber F: historical lineage at each point
    Gauge group G: representation transformations
    """
    states: List[OrganizationalState] = field(default_factory=list)
    fibers: List[HistoricalFiber] = field(default_factory=list)
    gauge_group: List[Callable] = field(default_factory=list)
    name: str = "unnamed"
    
    def add_state(self, state: OrganizationalState, fiber: HistoricalFiber):
        """Add a state with its attached fiber."""
        self.states.append(state)
        self.fibers.append(fiber)
    
    def transport(self, from_idx: int, to_idx: int) -> Tuple[OrganizationalState, HistoricalFiber]:
        """
        Parallel transport along the manifold.
        Moves state from from_idx to to_idx while updating the fiber.
        """
        if from_idx >= len(self.states) or to_idx >= len(self.states):
            raise IndexError("State index out of bounds")
        
        from_state = self.states[from_idx]
        to_state = self.states[to_idx]
        
        # Transport the state
        transported_state = OrganizationalState(
            vector=to_state.vector.copy(),
            timestamp=to_state.timestamp,
            metadata={'transported_from': from_idx},
        )
        
        # Transport the fiber: accumulate residue from the transition
        from_fiber = self.fibers[from_idx]
        transition_vector = to_state.vector - from_state.vector
        transported_fiber = from_fiber.accumulate(transition_vector)
        
        return transported_state, transported_fiber
    
    def gauge_transform(self, state_idx: int, gauge_idx: int) -> Tuple[OrganizationalState, HistoricalFiber]:
        """
        Apply a gauge transformation to a state-fiber pair.
        """
        if gauge_idx >= len(self.gauge_group):
            raise IndexError("Gauge index out of bounds")
        
        state = self.states[state_idx]
        fiber = self.fibers[state_idx]
        
        # Transform the state
        gauge_fn = self.gauge_group[gauge_idx]
        transformed_vector = gauge_fn(state.vector)
        
        transformed_state = OrganizationalState(
            vector=transformed_vector,
            timestamp=state.timestamp,
            metadata={'gauge_transformed': gauge_idx},
        )
        
        # Transform the fiber residue
        transformed_residue = gauge_fn(fiber.residue)
        transformed_fiber = HistoricalFiber(
            lineage=[gauge_fn(v) for v in fiber.lineage],
            residue=transformed_residue,
            memory_depth=fiber.memory_depth,
            overwrite_mask=fiber.overwrite_mask.copy(),
        )
        
        return transformed_state, transformed_fiber
    
    def compute_holonomy(self, loop_indices: List[int], gauge_idx: int = 0) -> float:
        """
        Compute holonomy around a closed loop.
        
        Transport around the loop, apply gauge transformation at each step,
        and measure closure error.
        """
        if len(loop_indices) < 2:
            return 0.0
        
        # Start at first state
        current_state = self.states[loop_indices[0]]
        current_fiber = self.fibers[loop_indices[0]]
        initial_fiber_residue = current_fiber.residue.copy()
        
        # Transport around the loop
        for i in range(len(loop_indices) - 1):
            from_idx = loop_indices[i]
            to_idx = loop_indices[i + 1]
            
            # Transport
            current_state, current_fiber = self.transport(from_idx, to_idx)
            
            # Apply gauge transformation
            current_state, current_fiber = self.gauge_transform_state_fiber(
                current_state, current_fiber, gauge_idx
            )
        
        # Close the loop (transport back to start)
        current_state, current_fiber = self.transport(loop_indices[-1], loop_indices[0])
        current_state, current_fiber = self.gauge_transform_state_fiber(
            current_state, current_fiber, gauge_idx
        )
        
        # Measure closure error (holonomy)
        closure_error = current_fiber.diff(
            HistoricalFiber(lineage=[], residue=initial_fiber_residue)
        )
        
        return closure_error
    
    def gauge_transform_state_fiber(self, state: OrganizationalState, 
                                     fiber: HistoricalFiber, 
                                     gauge_idx: int) -> Tuple[OrganizationalState, HistoricalFiber]:
        """Apply gauge transformation to an arbitrary state-fiber pair."""
        gauge_fn = self.gauge_group[gauge_idx]
        
        transformed_state = OrganizationalState(
            vector=gauge_fn(state.vector),
            timestamp=state.timestamp,
            metadata=state.metadata.copy(),
        )
        
        transformed_fiber = HistoricalFiber(
            lineage=[gauge_fn(v) for v in fiber.lineage],
            residue=gauge_fn(fiber.residue),
            memory_depth=fiber.memory_depth,
            overwrite_mask=fiber.overwrite_mask.copy(),
        )
        
        return transformed_state, transformed_fiber


# ═══════════════════════════════════════════════════════════════════
# Gauge Group Definitions
# ═══════════════════════════════════════════════════════════════════

def gauge_normalize(v: np.ndarray) -> np.ndarray:
    """L2 normalization gauge."""
    norm = np.linalg.norm(v)
    if norm > 0:
        return v / norm
    return v.copy()

def gauge_permute(v: np.ndarray) -> np.ndarray:
    """Dimension permutation gauge."""
    return v[np.argsort(-v)]

def gauge_sign_flip(v: np.ndarray) -> np.ndarray:
    """Sign flip gauge."""
    return v * np.sign(v + 1e-10)

def gauge_scale(v: np.ndarray) -> np.ndarray:
    """Random scaling gauge."""
    scale = 0.5 + np.random.random() * 1.0
    return v * scale

def gauge_identity(v: np.ndarray) -> np.ndarray:
    """Identity gauge (no transformation)."""
    return v.copy()

DEFAULT_GAUGE_GROUP = [
    gauge_identity,
    gauge_normalize,
    gauge_permute,
    gauge_sign_flip,
]


# ═══════════════════════════════════════════════════════════════════
# Bundle Construction from Simulation Trajectories
# ═══════════════════════════════════════════════════════════════════

def state_to_vector(state: dict) -> np.ndarray:
    """Convert simulation state dict to normalized vector."""
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
    
    vec = np.array(vals[:8], dtype=float)
    max_vals = np.maximum(np.abs(vec), 1.0)
    vec = vec / max_vals
    return np.clip(vec, -1, 1)


def build_bundle_from_trajectory(trajectory: list, 
                                  name: str = "system",
                                  memory_depth: int = 5,
                                  gauge_group: List = None) -> OrganizationalBundle:
    """
    Construct an organizational bundle from a simulation trajectory.
    
    Each timestep becomes a point on the base manifold.
    Historical fibers accumulate from trajectory lineage.
    """
    if gauge_group is None:
        gauge_group = DEFAULT_GAUGE_GROUP
    
    bundle = OrganizationalBundle(name=name, gauge_group=gauge_group)
    
    # Build states and fibers
    for t, state in enumerate(trajectory):
        vec = state_to_vector(state)
        
        # Create state
        org_state = OrganizationalState(
            vector=vec,
            timestamp=t,
            metadata={'original_index': t},
        )
        
        # Create fiber from lineage
        lineage = []
        for i in range(max(0, t - memory_depth), t):
            lineage.append(state_to_vector(trajectory[i]))
        
        residue = np.sum(lineage, axis=0) if lineage else np.zeros_like(vec)
        
        fiber = HistoricalFiber(
            lineage=lineage,
            residue=residue,
            memory_depth=memory_depth,
            overwrite_mask=np.ones_like(vec),
        )
        
        bundle.add_state(org_state, fiber)
    
    return bundle


# ═══════════════════════════════════════════════════════════════════
# Curvature Computation
# ═══════════════════════════════════════════════════════════════════

def compute_curvature_proxy(bundle: OrganizationalBundle, 
                             loop_length: int = 4) -> float:
    """
    Compute organizational curvature as average holonomy over all loops.
    
    Curvature ~ ∫ Ω where Ω is the curvature 2-form.
    """
    n_states = len(bundle.states)
    if n_states < loop_length + 1:
        return 0.0
    
    holonomies = []
    
    # Sample random loops
    n_samples = min(20, n_states)
    for _ in range(n_samples):
        # Random loop
        indices = np.random.choice(n_states, loop_length, replace=False)
        indices = np.sort(indices).tolist()
        indices.append(indices[0])  # Close the loop
        
        h = bundle.compute_holonomy(indices, gauge_idx=0)
        holonomies.append(h)
    
    return float(np.mean(holonomies)) if holonomies else 0.0


def compute_replay_divergence(bundle: OrganizationalBundle,
                               n_trajectories: int = 5) -> float:
    """
    Compute divergence between replayed trajectories.
    
    High divergence = non-trivial curvature.
    """
    n_states = len(bundle.states)
    if n_states < 10:
        return 0.0
    
    # Transport from start to end multiple times with different gauges
    divergences = []
    
    for i in range(n_trajectories):
        # Transport with different gauge at each step
        current_fiber = bundle.fibers[0]
        current_state = bundle.states[0]
        
        for t in range(1, n_states):
            # Transport
            current_state, current_fiber = bundle.transport(t - 1, t)
            # Apply random gauge
            gauge_idx = np.random.randint(0, len(bundle.gauge_group))
            current_state, current_fiber = bundle.gauge_transform_state_fiber(
                current_state, current_fiber, gauge_idx
            )
        
        divergences.append(current_fiber.entanglement())
    
    return float(np.std(divergences)) if divergences else 0.0


# ═══════════════════════════════════════════════════════════════════
# Holonomy Experiment
# ═══════════════════════════════════════════════════════════════════

def run_holonomy_experiment(bundle: OrganizationalBundle,
                            perturbation_sequence: List[int] = None) -> Dict:
    """
    Run the replay-loop experiment.
    
    1. Start at initial state
    2. Apply perturbation sequence (forward transport)
    3. Apply gauge transformation
    4. Replay inverse perturbations (backward transport)
    5. Measure closure error
    """
    n_states = len(bundle.states)
    if n_states < 5:
        return {'holonomy': 0.0, 'closure_error': 0.0}
    
    if perturbation_sequence is None:
        # Default: forward then backward
        perturbation_sequence = list(range(n_states // 2)) + list(range(n_states // 2, 0, -1))
    
    # Start at state 0
    current_state = bundle.states[0]
    current_fiber = bundle.fibers[0]
    initial_residue = current_fiber.residue.copy()
    
    # Forward transport
    for idx in perturbation_sequence:
        if idx < n_states:
            current_state, current_fiber = bundle.transport(
                current_state.metadata.get('original_index', 0), idx
            )
            # Apply gauge
            gauge_idx = np.random.randint(0, len(bundle.gauge_group))
            current_state, current_fiber = bundle.gauge_transform_state_fiber(
                current_state, current_fiber, gauge_idx
            )
    
    # Measure closure error
    closure_error = float(np.linalg.norm(current_fiber.residue - initial_residue))
    
    # Compute fiber entanglement
    fiber_entanglement = current_fiber.entanglement()
    
    return {
        'holonomy': closure_error,
        'closure_error': closure_error,
        'fiber_entanglement': fiber_entanglement,
        'initial_entanglement': float(np.linalg.norm(initial_residue)),
    }


# ═══════════════════════════════════════════════════════════════════
# Export
# ═══════════════════════════════════════════════════════════════════

__all__ = [
    'OrganizationalState',
    'HistoricalFiber',
    'OrganizationalBundle',
    'build_bundle_from_trajectory',
    'compute_curvature_proxy',
    'compute_replay_divergence',
    'run_holonomy_experiment',
    'DEFAULT_GAUGE_GROUP',
    'state_to_vector',
]
