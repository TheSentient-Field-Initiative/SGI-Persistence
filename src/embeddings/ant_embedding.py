# Ant colony embedding — explicit semantic mapping.

import numpy as np
from typing import Dict


# Canonical dimension names for ant colony
DIMENSION_NAMES = [
    "trail_connectivity",    # dim 0: pheromone trail connectivity
    "total_pheromone",       # dim 1: total pheromone concentration
    "recruitment_rate",      # dim 2: ant recruitment rate
    "path_redundancy",       # dim 3: path redundancy (alternative routes)
    "n_components",          # dim 4: trail components
    "cov_trace",             # dim 5: covariance trace (interaction intensity)
    "anisotropy",            # dim 6: trail anisotropy (directional bias)
    "non_principal",         # dim 7: non-principal eigenvalue (residual structure)
]

# Dimension ranges (approximate, from simulation observations)
DIMENSION_RANGES = {
    "trail_connectivity": (0.0, 1.0),
    "total_pheromone": (0.0, 100.0),
    "recruitment_rate": (0.0, 1.0),
    "path_redundancy": (0.0, 1.0),
    "n_components": (1, 20),
    "cov_trace": (0.0, 50.0),
    "anisotropy": (0.0, 1.0),
    "non_principal": (0.0, 20.0),
}

# Keys to extract from simulation state
STATE_KEYS = [
    "trail_connectivity",
    "total_pheromone",
    "recruitment_rate",
    "path_redundancy",
    "n_components",
    "cov_trace",
    "anisotropy",
    "non_principal",
]

# Normalization: z-score per dimension (computed from reference trajectory)
REFERENCE_MEAN = np.array([0.6, 50.0, 0.4, 0.5, 5.0, 20.0, 0.3, 8.0])
REFERENCE_STD = np.array([0.2, 20.0, 0.2, 0.2, 3.0, 10.0, 0.15, 4.0])


def embed(state: Dict) -> np.ndarray:
    """Convert ant colony state to 8D vector.

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
    """Validate an ant colony state for embedding.

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
