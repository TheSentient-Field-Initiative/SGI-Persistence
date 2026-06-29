# Institution embedding — explicit semantic mapping.

import numpy as np
from typing import Dict


# Canonical dimension names for institution
DIMENSION_NAMES = [
    "network_connectivity",  # dim 0: trust network connectivity
    "mean_trust",            # dim 1: mean trust level
    "cooperation_rate",      # dim 2: cooperation rate
    "strategy_entropy",      # dim 3: strategy diversity
    "mean_payoff",           # dim 4: mean payoff
    "n_components",          # dim 5: network components
    "cov_trace",             # dim 6: covariance trace (interaction intensity)
    "non_principal",         # dim 7: non-principal eigenvalue (residual structure)
]

# Dimension ranges (approximate, from simulation observations)
DIMENSION_RANGES = {
    "network_connectivity": (0.0, 1.0),
    "mean_trust": (0.0, 1.0),
    "cooperation_rate": (0.0, 1.0),
    "strategy_entropy": (0.0, 3.0),
    "mean_payoff": (0.0, 10.0),
    "n_components": (1, 50),
    "cov_trace": (0.0, 50.0),
    "non_principal": (0.0, 20.0),
}

# Keys to extract from simulation state
STATE_KEYS = [
    "network_connectivity",
    "mean_trust",
    "cooperation_rate",
    "strategy_entropy",
    "mean_payoff",
    "n_components",
    "cov_trace",
    "non_principal",
]

# Normalization: z-score per dimension (computed from reference trajectory)
REFERENCE_MEAN = np.array([0.7, 0.5, 0.4, 1.2, 3.0, 5.0, 15.0, 6.0])
REFERENCE_STD = np.array([0.15, 0.2, 0.2, 0.5, 1.5, 3.0, 8.0, 3.0])


def embed(state: Dict) -> np.ndarray:
    """Convert institution state to 8D vector.

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
    """Validate an institution state for embedding.

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
