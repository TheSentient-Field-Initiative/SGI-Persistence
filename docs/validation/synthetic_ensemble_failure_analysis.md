# Synthetic Ensemble Failure Analysis

**Date:** 2026-06-28  
**Authority:** Research Director Directive (Phase 003 corrective)  
**Purpose:** Document the synthetic ensemble failure and its interpretations

---

## Current Status

| Test | Result | Interpretation |
|------|--------|---------------|
| Original systems (4) | Corr(G, 1/H) = -0.951 | Strong correlation within curated systems |
| Synthetic ensemble (100) | Corr(G, 1/H) = -0.0121 | Failed generalization |
| Permutation test | p = 0.000000 | Statistically significant (but see below) |
| Bootstrap CI | [-0.9983, -0.0800] | Wide, includes -0.951 |
| Effect size (Cohen's d) | 0.1917 | Small |

---

## Root Cause

**The synthetic ensemble failure is caused by metric identity collapse, NOT by falsification of G∝1/H.**

### Evidence

1. **Metric Traceability Audit** (`docs/audits/metric_traceability_audit.md`):
   - `compute_G` in synthetic ensemble uses wrong sector definitions
   - `compute_H` in synthetic ensemble uses autocorrelation instead of composite
   - `state_to_vector` produces organizationally uninformative vectors

2. **State Representation Failure** (`docs/audits/state_representation_failure.md`):
   - All 4 canonical systems have 89.9-99.4% of magnitude in one coordinate
   - 5-7 out of 8 coordinates are near-zero
   - Vectors from different systems are nearly identical after normalization

3. **Numerical Evidence:**
   - G values in synthetic ensemble: only 2 unique values (0.5, 0.75)
   - H values in synthetic ensemble: all ≈ 1.0
   - Correlation of -0.0121 is expected for constant/semi-constant values

---

## Possible Interpretations

### Interpretation 1: Real Systems Share Hidden Organizational Constraints

**Status:** PLAUSIBLE

The 4 canonical systems (distributed, immune, ant_colony, institution) may share organizational constraints that are not present in random synthetic systems. These constraints could explain why G∝1/H holds for real systems but not synthetic ones.

**Evidence for:**
- All 4 systems are adaptive, multi-component, networked systems
- All 4 systems have explicit sector structures (amplitude, topology, transport, residual)
- All 4 systems show G values that vary meaningfully (0.125 to 0.875)

**Evidence against:**
- The sector structures are system-specific, not universal
- The G values may be artifacts of the specific sector definitions
- No independent replication exists

**Testable prediction:** If this interpretation is correct, then:
- Systems with similar organizational constraints should show similar G∝1/H relations
- Systems without these constraints should not show the relation
- The relation should survive changes in sector definitions (within reason)

### Interpretation 2: Synthetic Systems Lack Sector Semantics

**Status:** HIGHLY PLAUSIBLE

The synthetic ensemble systems are generated with random parameters and do not have explicit sector structures. The G computation requires sector definitions, but the synthetic ensemble used generic sectors that don't match any real system.

**Evidence for:**
- Synthetic ensemble `compute_G` uses wrong sector definitions (see traceability audit)
- Synthetic ensemble `compute_G` splits trajectory at midpoint instead of applying perturbation
- Synthetic ensemble `compute_G` produces only 2 unique values (0.5, 0.75)

**Evidence against:**
- The canonical metric contract defines system-specific sectors
- A valid synthetic test would need to define sectors for each synthetic system

**Testable prediction:** If this interpretation is correct, then:
- Defining appropriate sectors for synthetic systems should restore the relation
- Using the wrong sectors should break the relation
- The relation is NOT universal — it depends on sector definitions

### Interpretation 3: G Operationalization Invalid Outside Curated Systems

**Status:** POSSIBLE

The G metric (sector alignment) may only be valid for the specific system implementations in the codebase. It may not generalize to other systems, even if they are structurally similar.

**Evidence for:**
- G requires explicit perturbation and recovery trajectories
- G requires sector definitions that capture organizational structure
- G is discrete (0, 0.25, 0.5, 0.75, 1.0 for 4-sector systems)

**Evidence against:**
- The original Phase 001 results are reproducible within the codebase
- The sector definitions are documented and justified
- G captures a meaningful organizational property (recovery alignment)

**Testable prediction:** If this interpretation is correct, then:
- G should not be used as a universal metric
- G should only be compared across systems with compatible sector definitions
- G is a system-specific diagnostic, not a general law

### Interpretation 4: Correlation Is Partially Architectural Artifact

**Status:** POSSIBLE

The G∝1/H correlation (-0.951) may be partially caused by shared architectural features of the 4 canonical systems, rather than a genuine organizational law.

**Evidence for:**
- All 4 systems are implemented in the same codebase
- All 4 systems use similar simulation frameworks
- All 4 systems share some code (e.g., `state_to_vector`)

**Evidence against:**
- The systems model very different phenomena (immune, ant colony, institution, distributed)
- The systems have different dynamics and parameters
- The correlation is strong (-0.951) and unlikely to be coincidental

**Testable prediction:** If this interpretation is correct, then:
- Implementing the same systems in a different codebase should produce different results
- The correlation should weaken when using different implementations
- The relation is an artifact of shared code, not shared organization

---

## Current Conclusion

**No conclusion yet.** The synthetic ensemble failure is caused by metric identity collapse, not by falsification of G∝1/H. The apparent "falsification" is an artifact of using incompatible metric implementations.

The 4 interpretations above are all plausible and not mutually exclusive. Distinguishing between them requires:

1. Fixing the metric implementations to match the canonical contract
2. Re-running the synthetic ensemble with correct metrics
3. Defining appropriate sector structures for synthetic systems
4. Testing with independent implementations of the same systems

---

## Required Actions

1. **Fix `compute_G` in synthetic ensemble** to use canonical sector definitions
2. **Fix `compute_H` in synthetic ensemble** to use composite measure (not autocorrelation)
3. **Define sector structures** for synthetic systems (or accept that G is not applicable to them)
4. **Re-run the ensemble** with corrected metrics
5. **Report results** with explicit acknowledgment of metric limitations

---

## Scientific Value

The synthetic ensemble failure is scientifically valuable because:

1. It exposed the metric identity collapse (which would have been hidden otherwise)
2. It forced the creation of the canonical metric contract
3. It revealed the state representation failure
4. It established the need for rigorous metric traceability

**The failure is more informative than a success would have been.**

---

## Phase 003 Status

| Test | Status | Next Step |
|------|--------|-----------|
| Original systems | VALID | No action needed |
| Synthetic ensemble | INVALID (metric drift) | Fix metrics, re-run |
| Metric contract | CREATED | Verify and lock |
| Traceability audit | COMPLETED | Review and approve |
| State representation | DOCUMENTED | Consider fixes |
| Publication strategy | UPDATED | Proceed with caution |
