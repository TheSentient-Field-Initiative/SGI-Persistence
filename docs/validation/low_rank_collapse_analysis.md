# Low-Rank Collapse Analysis

**Phase 003D Division 4 — HIGH PRIORITY**

---

## 1. Executive Summary

All four system embeddings are effectively **one-dimensional**. This is the most important structural finding of Phase 003D.

| System | Participation Ratio | Effective Info Dim | Covariance Rank | Stable Rank |
|--------|-------------------|-------------------|-----------------|-------------|
| Distributed | 1.0071 | 1.0036 | 2 | 1.0000 |
| Immune | 1.0166 | 1.0083 | 4 | 1.0000 |
| Ant Colony | 1.0272 | 1.0136 | 11 | 1.0002 |
| Institution | 1.0000 | 1.0000 | 7 | 1.0000 |

**Interpretation:** Despite nominal dimensionalities of 6-13, all embeddings collapse to effectively 1D. The embeddings are degenerate.

---

## 2. Coordinate Dominance Evidence

### 2.1 From Metric Identifiability (Phase 003C)

| System | Dominant Dim | Dominant % | Near-Zero Coords |
|--------|-------------|-----------|-----------------|
| Distributed | dim 1 (n_active) | 89.9% | 5/8 |
| Immune | dim 1 (n_active) | 96.2% | 6/8 |
| Ant Colony | dim 5 (mean_activation) | 99.4% | 7/8 |
| Institution | dim 7 (efficiency) | 98.5% | 7/8 |

**Implication:** One coordinate dominates the vector norm, compressing all other coordinates to near-zero.

---

## 3. Singular Spectrum Analysis

### 3.1 Distributed

**Singular values (normalized):** [1.0000, 0.0071, 0.0000, 0.0000, 0.0000, 0.0000]

**Interpretation:** First singular value dominates completely. Effective rank = 1.

### 3.2 Immune

**Singular values (normalized):** [1.0000, 0.0166, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]

**Interpretation:** First singular value dominates completely. Effective rank = 1.

### 3.3 Ant Colony

**Singular values (normalized):** [1.0000, 0.0272, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]

**Interpretation:** First singular value dominates completely. Effective rank = 1.

### 3.4 Institution

**Singular values (normalized):** [1.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]

**Interpretation:** First singular value dominates completely. Effective rank = 1.

---

## 4. Embedding Compression Behavior

### 4.1 Dimensionality Reduction

When reducing from nominal dimensionality to 1D:
- **All metrics become identical** (G and H converge to constants)
- **System differentiation is lost** (all systems look the same)
- **Correlations become meaningless** (no variance to correlate)

### 4.2 Implication

The embeddings are already compressed to 1D before any explicit dimensionality reduction. The nominal dimensionality is an illusion.

---

## 5. Rank-Collapse Pathways

### 5.1 Pathway 1: Coordinate Domination

One coordinate dominates the vector norm, compressing all others to near-zero.

**Evidence:** 89.9-99.4% of magnitude in one coordinate.

### 5.2 Pathway 2: Normalization Compression

Unit normalization destroys relative scale information.

**Evidence:** After normalization, all vectors become nearly identical.

### 5.3 Pathway 3: Z-Score Saturation

Z-score normalization produces near-constant values when variance is low.

**Evidence:** H≈1.0000 for 3/4 systems.

---

## 6. Observable Degradation

### 6.1 G Degradation

| System | Baseline G | G after 50% corruption | G after 50% collapse |
|--------|-----------|----------------------|---------------------|
| Distributed | 0.5000 | varies | varies |
| Immune | 1.0000 | varies | varies |
| Ant Colony | 0.0000 | varies | varies |
| Institution | 0.5000 | varies | varies |

**From observable_survival.py:**
- Distributed: G survival=29.63%
- Immune: G survival=29.63%
- Ant Colony: G survival=70.37%
- Institution: G survival=59.26%

### 6.2 H Degradation

**From observable_survival.py:**
- Distributed: H survival=70.37%
- Immune: H survival=66.67%
- Ant Colony: H survival=70.37%
- Institution: H survival=59.26%

**Interpretation:** H is more robust than G, but H is saturated (≈1.0) for most systems, making it useless.

---

## 7. Implications

### 7.1 For G∝1/H

The G∝1/H correlation is an artifact of:
1. H saturation (H≈1.0)
2. Embedding degeneracy (1D effective)
3. Coordinate domination (one dim dominates)

The correlation is not a structural feature of the systems.

### 7.2 For Metric Identifiability

Metrics are only identifiable when:
1. Embedding has effective dimensionality > 1
2. No coordinate dominates
3. H is not saturated

None of these conditions are met in the current implementation.

### 7.3 For the Research Program

The program should focus on:
1. **Embedding quality:** Design embeddings with effective dimensionality > 1
2. **Metric robustness:** Design metrics that survive representation changes
3. **Identifiability conditions:** Characterize when metrics are identifiable

---

## 8. Recommendations

### 8.1 Immediate Actions

1. **Redesign embeddings** to have effective dimensionality > 1
2. **Remove coordinate domination** by normalizing per-dimension variance
3. **Avoid H saturation** by using alternative correlation measures

### 8.2 Research Directions

1. **Embedding design:** How to design embeddings that preserve system differentiation?
2. **Metric survival:** Which metrics survive representation changes?
3. **Identifiability theory:** What are the necessary and sufficient conditions for metric identifiability?

---

## 9. Files Referenced

- `experiments/validation/effective_dimensionality.py`
- `experiments/validation/observable_survival.py`
- `experiments/validation/metric_identifiability.py`
- `docs/audits/embedding_geometry_audit.md`
- `docs/validation/representation_dependence_assessment.md`
