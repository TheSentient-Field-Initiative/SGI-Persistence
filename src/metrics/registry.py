# Metric registry — single authoritative registry for all canonical metrics.

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from .contracts import compute_G, compute_H, compute_TE, MetricResult


@dataclass
class MetricEntry:
    """Registry entry for a canonical metric."""
    name: str
    canonical_definition: str
    implementation: Callable
    required_inputs: List[str]
    forbidden_substitutions: List[str]
    version_introduced: str
    validation_status: str  # "canonical", "provisional", "experimental", "unresolved"
    valid_domains: List[str]
    invalid_uses: List[str]


# ═══════════════════════════════════════════════════════════════════
# Canonical Metric Registry
# ═══════════════════════════════════════════════════════════════════

METRIC_REGISTRY: Dict[str, MetricEntry] = {
    "G": MetricEntry(
        name="G",
        canonical_definition=(
            "Fraction of organizational sectors that maintain structural alignment "
            "between pre-perturbation baseline and post-perturbation recovery. "
            "Alignment criterion: normalized_cosine - raw_cosine > -0.1."
        ),
        implementation=compute_G,
        required_inputs=["trajectory", "sector_definition"],
        forbidden_substitutions=[
            "trajectory_prediction (replay stability ≠ prediction accuracy)",
            "autocorrelation (G measures sector alignment, not temporal correlation)",
            "generic_sector_definitions (must be system-specific)",
        ],
        version_introduced="0.1.0",
        validation_status="canonical",
        valid_domains=["systems with explicit sector definitions"],
        invalid_uses=[
            "comparing G across systems with different sector definitions",
            "using G as a continuous metric (discrete: 0, 0.25, 0.5, 0.75, 1.0)",
            "inferring degree of persistence from G values",
        ],
    ),
    "H": MetricEntry(
        name="H",
        canonical_definition=(
            "Mean absolute autocorrelation of state vectors across lags 1-5. "
            "Measures temporal persistence of organizational state."
        ),
        implementation=compute_H,
        required_inputs=["trajectory"],
        forbidden_substitutions=[
            "composite_measures (path_dependence, MI, divergence, hysteresis are different metrics)",
            "state_history_mi (MI ≠ autocorrelation)",
        ],
        version_introduced="0.1.0",
        validation_status="canonical",
        valid_domains=["any trajectory convertible to 8D vectors"],
        invalid_uses=[
            "comparing H across systems with different state_to_vector mappings",
            "using H as a measure of entanglement (H measures temporal correlation)",
            "using H to predict G (correlation is provisional and system-dependent)",
        ],
    ),
    "TE": MetricEntry(
        name="TE",
        canonical_definition=(
            "Mean transport error between adjacent fibers in the organizational bundle. "
            "Measures inconsistency of the connection operator."
        ),
        implementation=compute_TE,
        required_inputs=["trajectory"],
        forbidden_substitutions=[],
        version_introduced="0.2.0",
        validation_status="provisional-valid",
        valid_domains=["systems where build_bundle produces meaningful fibers"],
        invalid_uses=[
            "comparing TE across systems with different state_to_vector mappings",
            "interpreting TE as a measure of curvature (TE measures transport inconsistency)",
        ],
    ),
    "T": MetricEntry(
        name="T",
        canonical_definition=(
            "Transport instability: ratio of TE under perturbation to TE under baseline. "
            "Measures sensitivity of transport structure to structural perturbation."
        ),
        implementation=None,  # Not yet implemented as standalone
        required_inputs=["trajectory_baseline", "trajectory_perturbed"],
        forbidden_substitutions=[],
        version_introduced="0.2.0",
        validation_status="experimental",
        valid_domains=["systems with non-zero TE"],
        invalid_uses=[
            "comparing T across systems (T is system-specific)",
            "interpreting T as a measure of fragility (T measures transport sensitivity)",
        ],
    ),
}


def get_metric(name: str) -> MetricEntry:
    """Get a metric entry from the registry.

    Args:
        name: Metric name ("G", "H", "TE", "T").

    Returns:
        MetricEntry.

    Raises:
        KeyError: If metric not found.
    """
    if name not in METRIC_REGISTRY:
        raise KeyError(f"Unknown metric '{name}'. Available: {list(METRIC_REGISTRY.keys())}")
    return METRIC_REGISTRY[name]


def list_metrics() -> Dict[str, str]:
    """List all registered metrics with their validation status.

    Returns:
        Dict mapping metric name to validation status.
    """
    return {name: entry.validation_status for name, entry in METRIC_REGISTRY.items()}


def compute_metric(name: str, **kwargs) -> MetricResult:
    """Compute a metric by name.

    Args:
        name: Metric name.
        **kwargs: Arguments to pass to the metric implementation.

    Returns:
        MetricResult.

    Raises:
        KeyError: If metric not found.
        RuntimeError: If metric has no implementation.
    """
    entry = get_metric(name)
    if entry.implementation is None:
        raise RuntimeError(f"Metric '{name}' has no implementation (status: {entry.validation_status})")
    return entry.implementation(**kwargs)
