# Metric validators — input validation and degeneracy checks.

import numpy as np
from typing import List, Dict, Optional


class MetricValidationError(Exception):
    """Raised when metric input validation fails."""
    pass


class MetricDegeneracyError(Exception):
    """Raised when metric computation detects degenerate input."""
    pass


def validate_trajectory(
    trajectory: List[Dict],
    min_length: int = 10,
    name: str = "trajectory",
) -> None:
    """Validate trajectory input for metric computation.

    Args:
        trajectory: List of state dictionaries.
        min_length: Minimum required length.
        name: Name for error messages.

    Raises:
        MetricValidationError: If trajectory is invalid.
    """
    if not isinstance(trajectory, list):
        raise MetricValidationError(f"{name} must be a list, got {type(trajectory).__name__}")

    if len(trajectory) < min_length:
        raise MetricValidationError(
            f"{name} too short: {len(trajectory)} < {min_length}"
        )

    if not all(isinstance(s, dict) for s in trajectory):
        raise MetricValidationError(f"{name} must contain only dictionaries")


def validate_sector_definition(
    sector_definition: Dict[str, List[str]],
    trajectory: Optional[List[Dict]] = None,
) -> None:
    """Validate sector definition for G computation.

    Args:
        sector_definition: Mapping of sector name -> list of metric keys.
        trajectory: Optional trajectory to check key existence against.

    Raises:
        MetricValidationError: If sector definition is invalid.
    """
    if not isinstance(sector_definition, dict):
        raise MetricValidationError(
            f"sector_definition must be a dict, got {type(sector_definition).__name__}"
        )

    if len(sector_definition) == 0:
        raise MetricValidationError("sector_definition is empty")

    for sector, metrics in sector_definition.items():
        if not isinstance(metrics, list):
            raise MetricValidationError(
                f"sector '{sector}' metrics must be a list, got {type(metrics).__name__}"
            )
        if len(metrics) == 0:
            raise MetricValidationError(f"sector '{sector}' has no metrics")

    if trajectory is not None:
        all_keys = set()
        for state in trajectory[:5]:
            all_keys.update(state.keys())

        for sector, metrics in sector_definition.items():
            missing = [m for m in metrics if m not in all_keys]
            if missing:
                raise MetricValidationError(
                    f"sector '{sector}' references missing keys: {missing}"
                )


def check_coordinate_domination(
    vectors: np.ndarray,
    threshold: float = 0.8,
) -> Optional[Dict]:
    """Check if vectors suffer from coordinate domination.

    Args:
        vectors: Array of shape (n, dim).
        threshold: Dominance ratio threshold.

    Returns:
        Dict with domination info if detected, None otherwise.
    """
    mean_abs = np.abs(vectors.mean(axis=0))
    total = mean_abs.sum()
    if total < 1e-10:
        return {"type": "all_zero", "severity": "critical"}

    dominance_ratio = mean_abs.max() / total
    if dominance_ratio > threshold:
        dominant_dim = int(np.argmax(mean_abs))
        return {
            "type": "coordinate_domination",
            "dominant_dim": dominant_dim,
            "dominance_ratio": float(dominance_ratio),
            "severity": "critical" if dominance_ratio > 0.95 else "high",
        }
    return None


def check_zero_vectors(
    vectors: np.ndarray,
    threshold: float = 1e-10,
) -> bool:
    """Check if all vectors are near-zero.

    Args:
        vectors: Array of shape (n, dim).
        threshold: Norm threshold.

    Returns:
        True if all vectors are near-zero.
    """
    norms = np.linalg.norm(vectors, axis=1)
    return bool(np.all(norms < threshold))


def check_nan_inf(values: np.ndarray) -> bool:
    """Check for NaN or Inf values.

    Args:
        values: Array of values.

    Returns:
        True if any NaN or Inf found.
    """
    return bool(np.any(np.isnan(values)) or np.any(np.isinf(values)))


def validate_embedding(
    vectors: np.ndarray,
    system_name: str = "unknown",
) -> List[Dict]:
    """Run all embedding validations.

    Args:
        vectors: Array of shape (n, dim).
        system_name: Name for error messages.

    Returns:
        List of detected issues (empty if all pass).
    """
    issues = []

    if check_zero_vectors(vectors):
        issues.append({
            "check": "zero_vectors",
            "severity": "critical",
            "system": system_name,
            "message": "all vectors are near-zero",
        })

    dom = check_coordinate_domination(vectors)
    if dom is not None:
        dom["system"] = system_name
        issues.append(dom)

    if check_nan_inf(vectors):
        issues.append({
            "check": "nan_inf",
            "severity": "critical",
            "system": system_name,
            "message": "NaN or Inf values detected",
        })

    return issues
