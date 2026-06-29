# Immune system embedding — explicit semantic mapping.

import numpy as np
from typing import Dict


# Canonical dimension names for immune system
DIMENSION_NAMES = [
    "signaling_connectivity",  # dim 0: signaling network connectivity
    "n_active",                # dim 1: active cells
    "type_entropy",            # dim 2: cell type diversity
    "mean_activation",         # dim 3: mean activation level
    "total_cytokines",         # dim 4: total cytokine concentration
    "n_components",            # dim 5: signaling components
    "cov_trace",               # dim 6: covariance trace (interaction intensity)
    "non_principal",           # dim 7: non-principal eigenvalue (residual structure)
]

# Dimension ranges (approximate, from simulation observations)
DIMENSION_RANGES = {
    "signaling_connectivity": (0.0, 1.0),
    "n_active": (0, 100),
    "type_entropy": (0.0, 3.0),
    "mean_activation": (0.0, 1.0),
    "total_cytokines": (0.0, 500.0),
    "n_components": (1, 50),
    "cov_trace": (0.0, 100.0),
    "non_principal": (0.0, 50.0),
}

# Keys to extract from simulation state
STATE_KEYS = [
    "signaling_connectivity",
    "n_active",
    "type_entropy",
    "mean_activation",
    "total_cytokines",
    "n_components",
    "cov_trace",
    "non_principal",
]

# Normalization: z-score per dimension (computed from reference trajectory)
REFERENCE_MEAN = np.array([0.75, 80.0, 1.5, 0.4, 200.0, 5.0, 30.0, 10.0])
REFERENCE_STD = np.array([0.15, 15.0, 0.5, 0.2, 100.0, 3.0, 15.0, 5.0])


def embed(state: Dict) -> np.ndarray:
    """Convert immune system state to 8D vector.

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
    """Validate an immune system state for embedding.

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
