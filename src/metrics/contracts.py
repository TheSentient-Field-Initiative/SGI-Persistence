# Metric contracts — canonical callable interfaces.
# These are the ONLY legal public metric interfaces.

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MetricResult:
    """Standard result container for all metric computations."""
    value: float
    name: str
    metadata: dict
    valid: bool
    failure_reason: Optional[str] = None


def compute_G(
    trajectory: List[Dict],
    sector_definition: Dict[str, List[str]],
    perturbation_index: Optional[int] = None,
) -> MetricResult:
    """Compute organizational replay stability (G).

    G measures the fraction of organizational sectors that maintain
    structural alignment between a pre-perturbation baseline and a
    post-perturbation recovery trajectory.

    Args:
        trajectory: List of state dictionaries.
        sector_definition: Mapping of sector name -> list of metric keys.
        perturbation_index: Index in trajectory where perturbation occurs.
            If None, uses midpoint split.

    Returns:
        MetricResult with G value in [0, 1].

    Raises:
        ValueError: If trajectory is too short or sector_definition is empty.
    """
    if len(trajectory) < 10:
        return MetricResult(
            value=0.0, name="G", valid=False,
            failure_reason="trajectory too short (< 10 steps)",
            metadata={"n_steps": len(trajectory)},
        )
    if not sector_definition:
        return MetricResult(
            value=0.0, name="G", valid=False,
            failure_reason="sector_definition is empty",
            metadata={},
        )

    n = len(trajectory)
    if perturbation_index is None:
        perturbation_index = n // 2

    before = trajectory[:perturbation_index]
    after = trajectory[perturbation_index:]

    # Validate sector keys exist in trajectory
    all_keys = set()
    for state in trajectory[:5]:
        all_keys.update(state.keys())

    missing_keys = {}
    for sector, metrics in sector_definition.items():
        missing = [m for m in metrics if m not in all_keys]
        if missing:
            missing_keys[sector] = missing

    if missing_keys:
        return MetricResult(
            value=0.0, name="G", valid=False,
            failure_reason=f"missing sector keys: {missing_keys}",
            metadata={"missing_keys": missing_keys},
        )

    # Compute sector alignment
    surviving = 0
    total = len(sector_definition)
    sector_results = {}

    for sector_name, metrics in sector_definition.items():
        bv = np.array([[bm.get(m, 0) for bm in before] for m in metrics]).T
        av = np.array([[am.get(m, 0) for am in after] for m in metrics]).T

        if bv.size == 0 or av.size == 0:
            sector_results[sector_name] = "NO_DATA"
            continue

        ml = min(len(bv), len(av))
        bv, av = bv[:ml], av[:ml]

        def _cosine(a, b):
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            return float(np.dot(a.flatten(), b.flatten()) / (na * nb)) if na > 0 and nb > 0 else 0.0

        raw = _cosine(bv, av)
        bn = (bv - bv.mean(0)) / (bv.std(0) + 1e-8)
        an = (av - av.mean(0)) / (av.std(0) + 1e-8)
        norm = _cosine(bn, an)

        survives = (norm - raw) > -0.1
        if survives:
            surviving += 1
        sector_results[sector_name] = "SURVIVES" if survives else "COLLAPSES"

    g = surviving / total if total > 0 else 0.0

    return MetricResult(
        value=g, name="G", valid=True,
        metadata={
            "sector_results": sector_results,
            "surviving": surviving,
            "total": total,
            "perturbation_index": perturbation_index,
        },
    )


def compute_H(
    trajectory: List[Dict],
    max_lag: int = 5,
) -> MetricResult:
    """Compute historical residue coupling (H).

    H measures the temporal autocorrelation of state vectors,
    capturing how strongly the system's current state depends
    on its recent history.

    Args:
        trajectory: List of state dictionaries.
        max_lag: Maximum lag for autocorrelation (default 5).

    Returns:
        MetricResult with H value in [0, 1].
    """
    from src.geometry.connection_formalism import state_to_vector

    if len(trajectory) < 10:
        return MetricResult(
            value=0.0, name="H", valid=False,
            failure_reason="trajectory too short (< 10 steps)",
            metadata={"n_steps": len(trajectory)},
        )

    vectors = np.array([state_to_vector(tr) for tr in trajectory])

    # Check for degenerate vectors
    norms = np.linalg.norm(vectors, axis=1)
    if np.all(norms < 1e-10):
        return MetricResult(
            value=0.0, name="H", valid=False,
            failure_reason="all vectors are zero",
            metadata={"norm_range": [float(norms.min()), float(norms.max())]},
        )

    # Check for coordinate domination
    mean_abs = np.abs(vectors.mean(axis=0))
    if mean_abs.max() / (mean_abs.sum() + 1e-10) > 0.8:
        dominant_dim = int(np.argmax(mean_abs))
        return MetricResult(
            value=0.0, name="H", valid=False,
            failure_reason=f"coordinate domination: dim {dominant_dim} = {mean_abs.max() / mean_abs.sum():.1%}",
            metadata={"dominant_dim": dominant_dim, "dominance_ratio": float(mean_abs.max() / mean_abs.sum())},
        )

    # Compute autocorrelation
    correlations = []
    for lag in range(1, min(max_lag + 1, len(vectors))):
        corr = np.corrcoef(vectors[lag:], vectors[:-lag])[0, 1]
        if np.isfinite(corr):
            correlations.append(abs(corr))

    h = float(np.mean(correlations)) if correlations else 0.0

    return MetricResult(
        value=h, name="H", valid=True,
        metadata={
            "n_lags": len(correlations),
            "max_lag": max_lag,
            "vector_norms": [float(n) for n in norms[:5]],
        },
    )


def compute_TE(
    trajectory: List[Dict],
    memory_depth: int = 10,
) -> MetricResult:
    """Compute transport error (TE).

    TE measures the inconsistency of the connection operator
    between adjacent fibers in the organizational bundle.

    Args:
        trajectory: List of state dictionaries.
        memory_depth: Memory depth for fiber construction.

    Returns:
        MetricResult with TE value.
    """
    from src.geometry.connection_formalism import build_bundle

    if len(trajectory) < memory_depth + 2:
        return MetricResult(
            value=0.0, name="TE", valid=False,
            failure_reason=f"trajectory too short (< {memory_depth + 2} steps)",
            metadata={"n_steps": len(trajectory), "required": memory_depth + 2},
        )

    try:
        states, fibers, connection = build_bundle(trajectory, memory_depth=memory_depth)
        errors = [
            connection.compute_transport_error(fibers[i], fibers[i + 1])
            for i in range(len(states) - 1)
        ]
        te = float(np.mean(errors)) if errors else 0.0

        return MetricResult(
            value=te, name="TE", valid=True,
            metadata={
                "n_fibers": len(fibers),
                "memory_depth": memory_depth,
                "error_range": [float(min(errors)), float(max(errors))] if errors else [0, 0],
            },
        )
    except Exception as e:
        return MetricResult(
            value=0.0, name="TE", valid=False,
            failure_reason=f"computation failed: {e}",
            metadata={"exception": str(e)},
        )
