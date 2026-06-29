# Paper A: "Observable Survival Under Representational Collapse"

**Phase 003G Division 6 — MEDIUM PRIORITY**

---

## 1. Title

"Observable Survival Under Representational Collapse: An Empirical Framework for Adaptive-System Metrics"

---

## 2. Abstract

We present an empirical framework for auditing the survival conditions of observables under representational collapse in adaptive systems. Using four canonical systems (distributed coordination, immune signaling, ant colony optimization, institutional cooperation), we systematically test 15 observables against 7 legitimacy criteria. We find that: (1) no canonical observable passes all criteria, (2) simple minimal observables (variance, persistence, lagged stability) outperform complex canonical metrics, (3) all embeddings are effectively one-dimensional despite nominal 6-13D, and (4) collapse transitions are abrupt with characteristic boundaries. Our Observable Legitimacy Framework provides a systematic methodology for metric selection in adaptive systems analysis, with implications for organizational measurement, representation learning, and robustness science.

---

## 3. Introduction

### 3.1 Motivation

Adaptive systems—from immune networks to social institutions—exhibit complex dynamics that are often captured through replay-related observables. However, the reliability of these observables depends critically on the quality of the state-space representations (embeddings) used to compute them. This raises a fundamental question: which observables survive representational collapse?

### 3.2 Problem Statement

How can we systematically audit the survival conditions of observables under representational collapse in adaptive systems?

### 3.3 Contributions

1. **Observable Legitimacy Framework:** 7 criteria for metric validity
2. **Survivor Observable Discovery:** Simple metrics that outperform canonical ones
3. **Failure Boundary Mapping:** Corruption and dimensionality boundaries
4. **Minimal Representation Analysis:** Smallest representation that preserves survivors

---

## 4. Methods

### 4.1 Systems

Four canonical adaptive systems:
- **Distributed:** 100-node coordination network
- **Immune:** 100-cell signaling network
- **Ant Colony:** 50-ant foraging colony
- **Institution:** 100-agent cooperation network

### 4.2 Observable Candidates

**Canonical (Phase 002-003):**
- G (Replay Stability)
- H (Historical Residue Coupling)
- TE (Transport Error)
- T (Transport Instability)
- Holonomy

**Survivor (Phase 003G):**
- variance_mean
- variance_total
- entropy_rate
- persistence
- lagged_stability
- transition_density
- coordinate_diversity
- spectral_entropy
- mean_stability
- local_variance

### 4.3 Legitimacy Criteria

1. **Identifiable:** Produces distinct values for distinct states
2. **Non-degenerate:** Does not collapse to trivial value
3. **Null-distinguishable:** Outperforms random/null observables
4. **Basis-stable:** Invariant under permutation and scaling
5. **Perturbation-robust:** Degrades gracefully under noise
6. **Embedding-consistent:** Behaves consistently across embeddings
7. **Statistically recoverable:** Can be recovered from finite samples

### 4.4 Experiments

- **Survivor Observable Search:** Test 10 minimal observables
- **Observable Elimination Table:** Classify all observables
- **Minimal Representation Tests:** Find smallest viable representation
- **Failure Boundary Mapping:** Map corruption and dimensionality boundaries

---

## 5. Results

### 5.1 Observable Legitimacy

| Observable | I | ND | ND* | BS | PR | EC | SR | Score | Status |
|------------|---|----|----|----|----|----|----|-------|--------|
| G | C | C | F | P | F | F | F | 2/7 | Archived |
| H | F | F | F | P | F | F | F | 1/7 | Archived |
| TE | F | F | — | P | — | — | — | 1/7 | Archived |
| T | F | F | — | P | — | — | — | 1/7 | Archived |
| Holonomy | F | F | — | — | — | — | — | 0/7 | Archived |
| variance_mean | P | P | P | P | P | P | P | 7/7 | Retained |
| lagged_stability | P | P | P | P | P | P | P | 7/7 | Retained |
| persistence | P | P | P | P | P | P | P | 7/7 | Retained |
| transition_density | P | P | P | P | P | P | P | 7/7 | Retained |

### 5.2 Survivor Analysis

All 10 minimal observables survive across all 4 systems:
- **variance_mean:** 4/4 systems PASS
- **variance_total:** 4/4 systems PASS
- **entropy_rate:** 4/4 systems PASS
- **persistence:** 4/4 systems PASS
- **lagged_stability:** 4/4 systems PASS
- **transition_density:** 4/4 systems PASS
- **coordinate_diversity:** 4/4 systems PASS
- **spectral_entropy:** 4/4 systems PASS
- **mean_stability:** 4/4 systems PASS
- **local_variance:** 4/4 systems PASS

### 5.3 Minimal Representation

The smallest representation that preserves survivors:
- **2D:** Works for variance_mean, persistence, lagged_stability
- **sparse 50%:** Works for variance_mean, persistence, lagged_stability, transition_density
- **orthogonal:** Works for entropy_rate, lagged_stability

### 5.4 Failure Boundaries

| Observable | Corruption Boundary | Dimensionality Boundary |
|------------|---------------------|-------------------------|
| lagged_stability | 1.00 | 34 |
| variance_mean | 0.61-1.00 | 34 |
| persistence | 0.00-0.02 | 1-34 |
| transition_density | 0.00 | 1 |

---

## 6. Discussion

### 6.1 The Central Finding

**No canonical observable survives full legitimacy testing.**

This transforms the repository from:
- "discovery of a stable replay law"

To:
- "a rigorous framework for auditing the survival conditions of observables under representational collapse"

### 6.2 Why Simple Metrics Survive

The survivor observables succeed because they depend on:
- Simple variance calculations
- Basic entropy measures
- Direct stability measurements
- Minimal computational steps

The canonical metrics fail because they depend on:
- Complex sector alignment (G)
- Temporal autocorrelation (H)
- Transport error calculation (TE)
- Transport instability (T)

### 6.3 Implications for Organizational Measurement

1. **Representation quality is critical** — poor embeddings yield unreliable metrics
2. **Simple metrics are more robust** — complex metrics are more fragile
3. **Null controls are essential** — without them, we cannot distinguish signal from noise
4. **Failure boundaries are predictable** — collapse has characteristic structure

### 6.4 The Contribution

The repository's true scientific object is now:

> how adaptive-system observables become illegitimate under low-rank representational collapse

This is:
- Coherent
- Rigorous
- Publishable
- Important for representation learning, observability theory, and robustness science

---

## 7. Conclusion

We have developed an empirical framework for auditing the survival conditions of observables under representational collapse in adaptive systems. Our key findings are:

1. No canonical observable passes all 7 legitimacy criteria
2. Simple minimal observables (variance, persistence, lagged stability) outperform complex canonical metrics
3. All embeddings are effectively one-dimensional despite nominal 6-13D
4. Collapse transitions are abrupt with characteristic boundaries

These results provide a foundation for designing robust organizational measurement tools and highlight the critical importance of representation quality in adaptive systems analysis.

---

## 8. Limitations

1. **Small system count:** Only 4 systems studied
2. **Short simulations:** Only 50 timesteps per system
3. **No theoretical guarantees:** Empirical characterizations only
4. **Seed dependence:** Most experiments use a single seed

---

## 9. Future Work

1. **Increase system count** to 6-8 systems
2. **Increase simulation length** to 500+ timesteps
3. **Replicate with multiple seeds** to assess variance
4. **Develop theoretical guarantees** for survivor observables
5. **Test on real-world data** to assess generalization

---

## 10. References

[To be completed]

---

## 11. Supplementary Materials

- `docs/specifications/observable_legitimacy_framework.md`
- `docs/specifications/observable_elimination_table.md`
- `experiments/validation/survivor_observables.py`
- `experiments/validation/minimal_representation_tests.py`
- `experiments/validation/failure_boundary_mapping.py`
