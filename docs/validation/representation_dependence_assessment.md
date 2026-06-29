# Representation-Dependence Assessment

**Phase 003C Division 5 — HIGH PRIORITY**

---

## 1. Question

> Are the observed correlations intrinsic, or representation artifacts?

---

## 2. Evidence Summary

### 2.1 Identifiability Analysis (Division 1)

| System | G | H | G Identifiable | H Identifiable | Sector Collapsed | Embedding Degenerate |
|--------|------|------|----------------|----------------|------------------|---------------------|
| Distributed | 0.5000 | 1.0000 | True | False | True | False |
| Immune | 0.5000 | 1.0000 | True | False | True | True |
| Ant Colony | 0.0000 | 1.0000 | False | False | False | True |
| Institution | 0.0000 | 0.9769 | False | True | True | True |

**Critical Finding:** H=1.0000 for three systems, meaning autocorrelation is saturated. This makes H useless for correlation with G.

### 2.2 Dimensionality Stress Test (Division 3)

| System | 2D G | 8D G | 64D G | Sparse G | Orthogonal G |
|--------|------|------|-------|----------|--------------|
| Distributed | 0.0000 | 0.5000 | N/A | 0.5000 | 0.0000 |
| Immune | 1.0000 | 1.0000 | N/A | 1.0000 | 0.0000 |
| Ant Colony | 0.0000 | 0.0000 | N/A | 0.0000 | 0.0000 |
| Institution | 0.0000 | 0.0000 | N/A | 0.5000 | 0.0000 |

**Critical Finding:** G values vary dramatically with embedding dimensionality. G=0.5 for distributed only appears at specific dimensionalities.

### 2.3 Stability Envelope (Phase 003B Division 5)

| System | Perturbation Threshold | Corruption Threshold | Dropout Threshold |
|--------|----------------------|---------------------|-------------------|
| Distributed | 0.01 | 0.5 | 0.5 |
| Immune | 0.01 | 1.0 | None |
| Ant Colony | None | 1.0 | None |
| Institution | None | 1.0 | 0.25 |

**Critical Finding:** G collapses at noise=0.01 for distributed and immune systems. This is extremely fragile.

### 2.4 Synthetic Ensemble (Phase 003 Division A)

| Metric | Result |
|--------|--------|
| Corr(G, 1/H) | -0.0121 |
| Permutation p | 0.000000 |
| Bootstrap CI | [-0.9983, -0.0800] |

**Critical Finding:** The G∝1/H correlation does not generalize to 100 randomized systems.

---

## 3. Analysis

### 3.1 Is G∝1/H Intrinsic?

**Evidence Against:**
1. H is saturated (≈1.0) for 3/4 systems, making it useless for correlation
2. G values vary dramatically with embedding dimensionality
3. G collapses at noise=0.01 for 2/4 systems
4. The correlation does not generalize to randomized systems

**Evidence For:**
1. Original Phase 001 results are reproducible with canonical implementations
2. The correlation holds across 4 curated systems

**Assessment:** The correlation is likely an artifact of the specific embedding and metric implementations, not an intrinsic structural feature.

### 3.2 Is G∝1/H a Representation Artifact?

**Evidence For:**
1. H saturation (H=1.0000) is an artifact of the autocorrelation computation
2. G values depend critically on sector definitions
3. G values depend critically on embedding dimensionality
4. G collapses under minimal perturbation (noise=0.01)

**Assessment:** Yes, the correlation is largely a representation artifact.

### 3.3 What Would Constitute Evidence of Intrinsic Structure?

To claim intrinsic structure, we would need:
1. H that is not saturated (H < 1.0 for all systems)
2. G that is robust to embedding perturbation (noise > 0.1)
3. G that is robust to sector corruption (corruption < 0.5)
4. Correlation that generalizes to randomized systems (Corr(G, 1/H) < -0.5)
5. Correlation that holds across multiple embedding dimensionalities

None of these conditions are met.

---

## 4. Failure Cases

### 4.1 H Saturation

H=1.0000 for distributed, immune, and ant_colony systems. This means the autocorrelation is at its maximum value, making H useless for distinguishing systems or correlating with G.

**Cause:** The autocorrelation computation is sensitive to the specific embedding and normalization used.

### 4.2 G Fragility

G collapses at noise=0.01 for distributed and immune systems. This means the metric is extremely sensitive to small perturbations in the embedding.

**Cause:** The sector alignment criterion (normalized_cosine - raw_cosine > -0.1) is too strict.

### 4.3 G Dimensionality Dependence

G values vary dramatically with embedding dimensionality. For example, distributed G=0.0000 at 2D but G=0.5000 at 8D.

**Cause:** The sector definitions are defined for specific dimensionalities and do not generalize.

---

## 5. Bounded Interpretations

### 5.1 What We Can Claim

1. **Observable:** In 4 curated systems with specific embeddings and sector definitions, G and H take specific values.
2. **Correlation:** Among these 4 systems, G and 1/H are correlated (r = -0.951).
3. **Limitation:** The correlation is fragile, representation-dependent, and does not generalize.

### 5.2 What We Cannot Claim

1. **Universality:** The correlation does not generalize to randomized systems.
2. **Intrinsic Structure:** The correlation is likely an artifact of the specific implementations.
3. **Robustness:** The metrics are extremely sensitive to perturbation.

### 5.3 What We Should Investigate

1. **Alternative Metrics:** Are there metrics that are more robust to perturbation?
2. **Alternative Embeddings:** Are there embeddings that produce more stable metrics?
3. **Alternative Correlations:** Are there correlations that generalize better?

---

## 6. Conclusions

### 6.1 Primary Finding

The observed G∝1/H correlation is **largely a representation artifact**, not an intrinsic structural feature.

### 6.2 Evidence

1. H is saturated (≈1.0) for 3/4 systems
2. G is fragile (collapses at noise=0.01)
3. G is dimensionality-dependent
4. The correlation does not generalize

### 6.3 Implications

1. **The original hypothesis (G∝1/H) is weakened.** It may still hold for specific systems, but it is not a universal law.
2. **The research program should pivot** from "Is G∝1/H a law?" to "Under what representational conditions do replay stability metrics remain identifiable?"
3. **The stability envelope is the primary result.** It characterizes the conditions under which metrics are identifiable.

### 6.4 Recommendations

1. **Document the limitation.** The correlation is representation-dependent and fragile.
2. **Investigate alternative metrics.** The current metrics are not robust.
3. **Focus on identifiability.** The question "When are metrics identifiable?" is more tractable than "Is G∝1/H a law?"

---

## 7. Files Referenced

- `experiments/validation/metric_identifiability.py`
- `experiments/validation/dimensionality_stress_test.py`
- `experiments/validation/stability_envelope.py`
- `experiments/validation/synthetic_ensemble.py`
- `docs/audits/embedding_geometry_audit.md`
