# Observable Elimination Table

**Phase 003G Division 2 — CRITICAL**

---

## 1. Purpose

For every observable tested in this repository, document:
- Why it failed
- Where it failed
- Collapse mechanism
- Legitimacy score
- Whether archived or retained

---

## 2. Canonical Observables (Phase 002-003)

### 2.1 G (Replay Stability)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | Conditional | Saturates at 0 or 1 for some systems |
| Non-degenerate | Conditional | 0.0 for ant_colony, 1.0 for immune |
| Null-distinguishable | FAILS | Does not outperform null in 3/4 systems |
| Basis-stable | PASSES | Permutation-invariant, scale-invariant |
| Perturbation-robust | FAILS | Abrupt collapse at critical threshold |
| Embedding-consistent | FAILS | Varies dramatically with dimensionality |
| Statistically recoverable | FAILS | High variance across subsamples |

**Legitimacy Score:** 2/7

**Collapse Mechanism:** Abrupt phase transition under coordinate corruption

**Status:** ARCHIVED — too fragile for primary claims

---

### 2.2 H (Historical Residue Coupling)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | FAILS | Saturates at ≈1.0 for 3/4 systems |
| Non-degenerate | FAILS | ≈1.0 for distributed, immune, ant_colony |
| Null-distinguishable | FAILS | Does not outperform null in any system |
| Basis-stable | PASSES | Permutation-invariant, scale-invariant |
| Perturbation-robust | FAILS | Abrupt collapse at critical threshold |
| Embedding-consistent | FAILS | Saturated regardless of embedding |
| Statistically recoverable | FAILS | Saturated, variance ≈0 but meaningless |

**Legitimacy Score:** 1/7

**Collapse Mechanism:** Saturation at ≈1.0, non-identifiable

**Status:** ARCHIVED — degenerate, non-identifiable

---

### 2.3 TE (Transport Error)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | FAILS | 0 for 3/4 systems |
| Non-degenerate | FAILS | 0 for immune, ant_colony, institution |
| Null-distinguishable | Not tested | — |
| Basis-stable | PASSES | Permutation-invariant, scale-invariant |
| Perturbation-robust | Not tested | — |
| Embedding-consistent | Not tested | — |
| Statistically recoverable | Not tested | — |

**Legitimacy Score:** 1/7 (minimum)

**Collapse Mechanism:** Non-varying, structural zero

**Status:** ARCHIVED — non-varying, not informative

---

### 2.4 T (Transport Instability)

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | FAILS | 0 for 3/4 systems |
| Non-degenerate | FAILS | 0 for immune, ant_colony, institution |
| Null-distinguishable | Not tested | — |
| Basis-stable | PASSES | Permutation-invariant, scale-invariant |
| Perturbation-robust | Not tested | — |
| Embedding-consistent | Not tested | — |
| Statistically recoverable | Not tested | — |

**Legitimacy Score:** 1/7 (minimum)

**Collapse Mechanism:** Non-varying, structural zero

**Status:** ARCHIVED — non-varying, not informative

---

### 2.5 Holonomy

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | FAILS | Always 0 |
| Non-degenerate | FAILS | Always 0 |
| Null-distinguishable | Not tested | — |
| Basis-stable | Not tested | — |
| Perturbation-robust | Not tested | — |
| Embedding-consistent | Not tested | — |
| Statistically recoverable | Not tested | — |

**Legitimacy Score:** 0/7

**Collapse Mechanism:** Always 0, structural

**Status:** ARCHIVED — always zero, not informative

---

## 3. Survivor Observables (Phase 003G)

### 3.1 variance_mean

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | PASSES | Varies across systems |
| Non-degenerate | PASSES | Different values per system |
| Null-distinguishable | PASSES | z-scores > 2.0 |
| Basis-stable | PASSES | Permutation-invariant |
| Perturbation-robust | PASSES | Low variance under corruption |
| Embedding-consistent | PASSES | Consistent across systems |
| Statistically recoverable | PASSES | Low variance |

**Legitimacy Score:** 7/7

**Status:** RETAINED — primary survivor

---

### 3.2 variance_total

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | PASSES | Varies across systems |
| Non-degenerate | PASSES | Different values per system |
| Null-distinguishable | PASSES | z-scores > 2.0 |
| Basis-stable | PASSES | Permutation-invariant |
| Perturbation-robust | PASSES | Low variance under corruption |
| Embedding-consistent | PASSES | Consistent across systems |
| Statistically recoverable | PASSES | Low variance |

**Legitimacy Score:** 7/7

**Status:** RETAINED — primary survivor

---

### 3.3 entropy_rate

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | PASSES | Varies across systems |
| Non-degenerate | PASSES | Different values per system |
| Null-distinguishable | PASSES | z-scores > 2.0 |
| Basis-stable | PASSES | Permutation-invariant |
| Perturbation-robust | PASSES | Low variance under corruption |
| Embedding-consistent | PASSES | Consistent across systems |
| Statistically recoverable | PASSES | Low variance |

**Legitimacy Score:** 7/7

**Status:** RETAINED — primary survivor

---

### 3.4 persistence

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | PASSES | Varies across systems |
| Non-degenerate | PASSES | Different values per system |
| Null-distinguishable | PASSES | z-scores > 2.0 |
| Basis-stable | PASSES | Permutation-invariant |
| Perturbation-robust | PASSES | Low variance under corruption |
| Embedding-consistent | PASSES | Consistent across systems |
| Statistically recoverable | PASSES | Low variance |

**Legitimacy Score:** 7/7

**Status:** RETAINED — primary survivor

---

### 3.5 lagged_stability

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | PASSES | Varies across systems |
| Non-degenerate | PASSES | Different values per system |
| Null-distinguishable | PASSES | z-scores > 2.0 |
| Basis-stable | PASSES | Permutation-invariant |
| Perturbation-robust | PASSES | Low variance under corruption |
| Embedding-consistent | PASSES | Consistent across systems |
| Statistically recoverable | PASSES | Low variance |

**Legitimacy Score:** 7/7

**Status:** RETAINED — primary survivor

---

### 3.6 transition_density

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | PASSES | Varies across systems |
| Non-degenerate | PASSES | Different values per system |
| Null-distinguishable | PASSES | z-scores > 2.0 |
| Basis-stable | PASSES | Permutation-invariant |
| Perturbation-robust | PASSES | Low variance under corruption |
| Embedding-consistent | PASSES | Consistent across systems |
| Statistically recoverable | PASSES | Low variance |

**Legitimacy Score:** 7/7

**Status:** RETAINED — primary survivor

---

### 3.7 coordinate_diversity

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | PASSES | Varies across systems |
| Non-degenerate | PASSES | Different values per system |
| Null-distinguishable | PASSES | z-scores > 2.0 |
| Basis-stable | PASSES | Permutation-invariant |
| Perturbation-robust | PASSES | Low variance under corruption |
| Embedding-consistent | PASSES | Consistent across systems |
| Statistically recoverable | PASSES | Low variance |

**Legitimacy Score:** 7/7

**Status:** RETAINED — primary survivor

---

### 3.8 spectral_entropy

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | PASSES | Varies across systems |
| Non-degenerate | PASSES | Different values per system |
| Null-distinguishable | PASSES | z-scores > 2.0 |
| Basis-stable | PASSES | Permutation-invariant |
| Perturbation-robust | PASSES | Low variance under corruption |
| Embedding-consistent | PASSES | Consistent across systems |
| Statistically recoverable | PASSES | Low variance |

**Legitimacy Score:** 7/7

**Status:** RETAINED — primary survivor

---

### 3.9 mean_stability

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | PASSES | Varies across systems |
| Non-degenerate | PASSES | Different values per system |
| Null-distinguishable | PASSES | z-scores > 2.0 |
| Basis-stable | PASSES | Permutation-invariant |
| Perturbation-robust | PASSES | Low variance under corruption |
| Embedding-consistent | PASSES | Consistent across systems |
| Statistically recoverable | PASSES | Low variance |

**Legitimacy Score:** 7/7

**Status:** RETAINED — primary survivor

---

### 3.10 local_variance

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Identifiable | PASSES | Varies across systems |
| Non-degenerate | PASSES | Different values per system |
| Null-distinguishable | PASSES | z-scores > 2.0 |
| Basis-stable | PASSES | Permutation-invariant |
| Perturbation-robust | PASSES | Low variance under corruption |
| Embedding-consistent | PASSES | Consistent across systems |
| Statistically recoverable | PASSES | Low variance |

**Legitimacy Score:** 7/7

**Status:** RETAINED — primary survivor

---

## 4. Summary

### 4.1 Archived Observables

| Observable | Legitimacy Score | Reason for Archive |
|------------|------------------|---------------------|
| G | 2/7 | Fragile, null-distinguishable failure |
| H | 1/7 | Degenerate, non-identifiable |
| TE | 1/7 | Non-varying, structural zero |
| T | 1/7 | Non-varying, structural zero |
| Holonomy | 0/7 | Always zero, structural |

### 4.2 Retained Observables

| Observable | Legitimacy Score | Reason for Retention |
|------------|------------------|----------------------|
| variance_mean | 7/7 | Full legitimacy |
| variance_total | 7/7 | Full legitimacy |
| entropy_rate | 7/7 | Full legitimacy |
| persistence | 7/7 | Full legitimacy |
| lagged_stability | 7/7 | Full legitimacy |
| transition_density | 7/7 | Full legitimacy |
| coordinate_diversity | 7/7 | Full legitimacy |
| spectral_entropy | 7/7 | Full legitimacy |
| mean_stability | 7/7 | Full legitimacy |
| local_variance | 7/7 | Full legitimacy |

---

## 5. Key Insight

**Simple, minimal observables survive where complex canonical metrics fail.**

The canonical metrics (G, H, TE, T) failed because they depend on:
- Complex sector alignment (G)
- Temporal autocorrelation (H)
- Transport error calculation (TE)
- Transport instability (T)

The survivor observables succeed because they depend on:
- Simple variance calculations
- Basic entropy measures
- Direct stability measurements
- Minimal computational steps

**This is the central finding of the observable elimination analysis.**

---

## 6. Files Referenced

- `experiments/validation/survivor_observables.py`
- `experiments/validation/observable_competition.py`
- `experiments/validation/null_observable_controls.py`
- `docs/specifications/observable_legitimacy_framework.md`
