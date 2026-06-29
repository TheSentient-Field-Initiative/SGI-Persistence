# Failure Modes

This document demonstrates known failure modes of the metric pipeline.

---

## Failure Mode 1: Coordinate Domination

**Description:** The generic `state_to_vector` embedding produces vectors where one coordinate dominates (>89% of magnitude), compressing all other coordinates to near-zero.

**Evidence:**
| System | Dominant Dim | Dominant % | Near-Zero Coords |
|--------|-------------|-----------|-----------------|
| distributed | dim 1 (n_active) | 89.9% | 5/8 |
| immune | dim 1 (n_active) | 96.2% | 6/8 |
| ant_colony | dim 5 (mean_activation) | 99.4% | 7/8 |
| institution | dim 7 (efficiency) | 98.5% | 7/8 |

**Impact:** Makes H computation meaningless (all vectors nearly identical).

**Fix:** Use system-specific embeddings with z-score normalization.

---

## Failure Mode 2: Metric Identity Collapse

**Description:** The synthetic ensemble used metric implementations that are NOT semantically compatible with the original Phase 001 implementations.

**Evidence:**
- `compute_G` in synthetic ensemble uses wrong sector definitions
- `compute_H` in synthetic ensemble uses autocorrelation instead of composite
- `state_to_vector` produces organizationally uninformative vectors

**Impact:** Apparent "G∝1/H falsification" (-0.0121) is an artifact, not a finding.

**Fix:** Use canonical metric contracts from `src/metrics/contracts.py`.

---

## Failure Mode 3: Sector Definition Mismatch

**Description:** Different implementations use different sector definitions for the same system.

**Evidence:**
- Original Phase 001: `{'amplitude': ['mean_act', 'total_cyto', 'n_active'], ...}`
- Synthetic ensemble: `{'amplitude': ['mean_activation', 'n_active'], ...}`
- Reproduction package: `{'amplitude': ['mean_activation', 'n_active'], ...}`

**Impact:** G values are not comparable across implementations.

**Fix:** Use canonical sector definitions from `docs/specifications/canonical_metric_contract.md`.

---

## Failure Mode 4: Cross-System Embedding Comparison

**Description:** Comparing embedding vectors across systems that have different semantic meanings for each dimension.

**Evidence:**
- Distributed dim 0: `connectivity` (graph connectivity)
- Immune dim 0: `signaling_connectivity` (signaling network connectivity)
- Ant Colony dim 0: `trail_connectivity` (pheromone trail connectivity)
- Institution dim 0: `network_connectivity` (trust network connectivity)

**Impact:** Meaningless comparisons between systems.

**Fix:** Never compare embedding vectors across systems. Use sector alignment (G) instead.

---

## Failure Mode 5: Normalization Compression

**Description:** Unit normalization (dividing by max absolute value) destroys relative scale information.

**Evidence:**
- Before normalization: coordinates range from 0.001 to 100
- After normalization: all coordinates near 0.0001

**Impact:** All vectors become nearly identical after normalization.

**Fix:** Use z-score normalization instead of unit normalization.

---

## Summary

| Failure Mode | Severity | Status | Fix |
|-------------|----------|--------|-----|
| Coordinate domination | CRITICAL | Fixed | System-specific embeddings |
| Metric identity collapse | CRITICAL | Fixed | Canonical metric contracts |
| Sector definition mismatch | HIGH | Fixed | Canonical sector definitions |
| Cross-system embedding comparison | HIGH | Documented | Never compare across systems |
| Normalization compression | HIGH | Fixed | Z-score normalization |
