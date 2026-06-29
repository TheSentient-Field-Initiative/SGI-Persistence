# src.metrics — Canonical metric registry, contracts, and validators.

from .contracts import compute_G, compute_H, compute_TE, MetricResult
from .registry import METRIC_REGISTRY, get_metric, list_metrics, compute_metric
from .validators import (
    validate_trajectory,
    validate_sector_definition,
    validate_embedding,
    check_coordinate_domination,
    check_zero_vectors,
    MetricValidationError,
    MetricDegeneracyError,
)

__all__ = [
    "compute_G",
    "compute_H",
    "compute_TE",
    "MetricResult",
    "METRIC_REGISTRY",
    "get_metric",
    "list_metrics",
    "compute_metric",
    "validate_trajectory",
    "validate_sector_definition",
    "validate_embedding",
    "check_coordinate_domination",
    "check_zero_vectors",
    "MetricValidationError",
    "MetricDegeneracyError",
]
