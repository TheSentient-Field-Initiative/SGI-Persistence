# Distributed system embedding — explicit semantic mapping.

import numpy as np
from typing import Dict


# Canonical dimension names for distributed system
DIMENSION_NAMES = [
    "connectivity",        # dim 0: graph connectivity (largest component / n_active)
    "n_active",            # dim 1: active nodes
    "routing_entropy",     # dim 2: routing diversity
    "assignment_rate",     # dim 3: task assignment rate
    "allocation_entropy",  # dim 4: task allocation diversity
    "n_components",        # dim 5: connected components
    "timestep",            # dim 6: simulation time
    "reserved",            # dim 7: reserved for future use
]

# Dimension ranges (approximate, from simulation observations)
DIMENSION_RANGES = {
    "connectivity": (0.0, 1.0),
    "n_active": (0, 100),
    "routing_entropy": (0.0, 7.0),
    "assignment_rate": (0.0, 1.0),
    "allocation_entropy": (0.0, 5.0),
    "n_components": (1, 50),
    "timestep": (0, 100),
    "reserved": (0.0, 0.0),
}

# Keys to extract from simulation state
STATE_KEYS = [
    "connectivity",
    "n_active",
    "routing_entropy",
    "assignment_rate",
    "allocation_entropy",
    "n_components",
    "timestep",
]

# Normalization: z-score per dimension (computed from reference trajectory)
# These are approximate reference values from a 50-step trajectory
REFERENCE_MEAN = np.array([0.85, 95.0, 1.2, 0.3, 1.5, 3.0, 25.0, 0.0])
REFERENCE_STD = np.array([0.1, 5.0, 0.5, 0.1, 0.5, 2.0, 15.0, 1.0])


def embed(state: Dict) -> np.ndarray:
    """Convert distributed system state to 8D vector.

    Uses z-score normalization per dimension. No unit normalization
    (preserves relative scale information).

    Args:
        state: Simulation state dictionary.

    Returns:
        8D numpy array.
    """
    vec = np.zeros(8)
    for i, key in enumerate(STATE_KEYS):
        if key in state and isinstance(state[key], (int, float)):
            vec[i] = float(state[key])

    # Z-score normalization (preserves relative scale)
    vec = (vec - REFERENCE_MEAN) / (REFERENCE_STD + 1e-8)

    return np.clip(vec, -3, 3)  # Clip to 3 standard deviations


def validate(state: Dict) -> dict:
    """Validate a distributed system state for embedding.

    Returns:
        Dict with 'valid' bool and 'issues' list.
    """
    issues = []
    for key in STATE_KEYS:
        if key not in state:
            issues.append(f"missing key: {key}")
        elif not isinstance(state[key], (int, float)):
            issues.append(f"non-numeric value for {key}: {type(state[key]).__name__}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
    }
