# State Representation Failure Report

**Date:** 2026-06-28  
**Authority:** Research Director Directive (Phase 003 corrective)  
**Purpose:** Formally document the state representation failure modes

---

## Executive Summary

The 8-dimensional `state_to_vector` embedding suffers from **catastrophic coordinate domination** across all 4 canonical systems. Each system is dominated by a single coordinate, with 5-7 other coordinates compressed to near-zero. This makes the embedding organizationally uninformative — vectors from different systems are nearly identical after normalization.

---

## Evidence

### Numerical Results (20-step trajectories)

| System | Dominant Dim | Dominant % | Near-Zero Coords | Std Range |
|--------|-------------|-----------|-----------------|-----------|
| distributed | dim 1 (n_active) | 89.9% | 5/8 | [0, 0.0016] |
| immune | dim 1 (n_active) | 96.2% | 6/8 | [0, 0] |
| ant_colony | dim 5 (mean_activation) | 99.4% | 7/8 | [0, 0.0003] |
| institution | dim 7 (efficiency) | 98.5% | 7/8 | [0, 0.0012] |

### Vector Visualization

**distributed:**
```
[0.01, 1.00, 0.04, 0.00, 0.05, 0.00, 0.01, 0.00]
         ^
         |
    89.9% of total magnitude
```

**immune:**
```
[0.01, 1.00, 0.02, 0.00, 0.00, 0.00, 0.01, 0.00]
         ^
         |
    96.2% of total magnitude
```

**ant_colony:**
```
[0.00, 0.00, 0.00, 0.00, 0.00, 1.00, 0.00, 0.00]
                     ^
                     |
              99.4% of total magnitude
```

**institution:**
```
[0.00, 0.00, 0.01, 0.00, 0.00, 0.00, 0.00, 1.00]
                                             ^
                                             |
                                      98.5% of total magnitude
```

---

## Root Cause Analysis

### 1. Coordinate Domination

**Severity:** CRITICAL

Each system has one coordinate that is orders of magnitude larger than all others:

- distributed: `n_active` = 100 (all nodes active)
- immune: `n_active` = 100 (all cells active)
- ant_colony: `total_pheromone` >> all other metrics
- institution: `efficiency` >> all other metrics

After unit normalization, this dominant coordinate becomes 1.0 and all other coordinates are compressed to near-zero.

**Evidence:** Std of vectors is [0, 0.0016] — almost zero variation across time.

### 2. Over-Normalization

**Severity:** HIGH

The `state_to_vector` function normalizes by max absolute value:
```python
max_abs = np.max(np.abs(vec))
if max_abs > 1e-10:
    vec = vec / max_abs
```

This destroys relative scale information. A coordinate with value 0.01 and a coordinate with value 0.001 become 0.01 and 0.001 after normalization — but if the dominant coordinate is 100, both become 0.0001 and 0.00001.

**Evidence:** After normalization, all vectors have norm ≈ 1.0, regardless of system.

### 3. Cross-Domain Semantic Mismatch

**Severity:** HIGH

Different systems emit incomparable observables mapped to the same dimension:

- dim 0: `connectivity` (distributed) vs `signaling_connectivity` (immune) vs `trail_connectivity` (ant_colony) vs `network_connectivity` (institution)
- dim 5: `mean_activation` (distributed/immune) vs `total_pheromone` (ant_colony) vs `mean_trust` (institution)

These are semantically different quantities that happen to occupy the same vector dimension.

**Evidence:** Ant colony and institution vectors are dominated by completely different coordinates (dim 5 vs dim 7).

### 4. Low Manifold Dimensionality

**Severity:** MEDIUM

The 8-dimensional embedding may be insufficient to capture the organizational structure of these systems. Each system has 10-15 observable metrics, but only 8 can fit in the vector.

**Evidence:** 5-7 out of 8 coordinates are near-zero, suggesting the embedding is wasting dimensions.

---

## Failure Modes

| Failure Mode | Severity | Evidence | Fix Candidate |
|-------------|----------|----------|---------------|
| Coordinate domination | CRITICAL | 89.9-99.4% of magnitude in one dim | Per-coordinate normalization before unit normalization |
| Over-normalization | HIGH | All vectors have norm ≈ 1.0 | Remove unit normalization; use raw values |
| Cross-domain semantic mismatch | HIGH | Different systems dominate different dims | System-specific vector mappings |
| Low manifold dimensionality | MEDIUM | 5-7 dims near-zero | Increase embedding dimension or use variable-length |
| Temporal collapse | HIGH | Std ≈ 0 across time | Use differences instead of raw values |

---

## Impact on Phase 003

### Why the Synthetic Ensemble Failed

The synthetic ensemble used `state_to_vector` to convert trajectories to vectors, then computed G and H from these vectors. But:

1. **G computation:** Used wrong sector definitions (generic instead of system-specific)
2. **H computation:** Used autocorrelation of vectors that are all nearly identical
3. **Result:** G = 0.5-0.75 for all systems, H ≈ 1.0 for all systems

The correlation of -0.0121 is NOT a scientific finding. It is the expected result of feeding organizationally uninformative vectors into metrics that require organizational structure.

### Why the Original Phase 001 Results Are Valid

The original Phase 001 results (G = 0.250, 0.875, 0.125, 0.250) used:

1. **System-specific sector definitions** — each system has its own sectors with its own metrics
2. **Raw metrics** — not `state_to_vector` vectors
3. **Explicit perturbation** — not arbitrary trajectory splitting

The original results are valid because they bypassed the broken `state_to_vector` embedding entirely.

---

## Recommendations

1. **DO NOT use `state_to_vector` for G computation** — use system-specific sector definitions
2. **DO NOT use `state_to_vector` for H computation** — use raw metric autocorrelation
3. **Consider replacing unit normalization** with per-coordinate z-scoring
4. **Consider system-specific vector mappings** instead of universal key mapping
5. **Document which metrics are comparable across systems** and which are not

---

## Conclusion

The `state_to_vector` embedding is organizationally uninformative due to coordinate domination and over-normalization. This is a known limitation that must be accounted for in all metric computations.

The original Phase 001 results are valid because they used system-specific sector definitions that bypassed this broken embedding. The synthetic ensemble results are invalid because they used the broken embedding directly.
