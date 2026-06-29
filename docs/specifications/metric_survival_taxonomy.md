# Metric Survival Taxonomy

**Phase 003D Division 5 — HIGH PRIORITY**

---

## 1. Purpose

This document classifies metrics by their survival characteristics under representational transformations. This taxonomy is now essential infrastructure for the research program.

---

## 2. Taxonomy Classes

| Class | Definition | Survival Rate |
|-------|-----------|---------------|
| **Stable** | Survives all representation changes | > 90% |
| **Conditional** | Survives only under constraints | 50-90% |
| **Fragile** | Collapses under mild perturbation | 20-50% |
| **Degenerate** | Non-identifiable | < 20% |

---

## 3. Current Classification

### 3.1 G (Replay Stability)

**Class:** Fragile

**Evidence:**
- Distributed: G survival=29.63%
- Immune: G survival=29.63%
- Ant Colony: G survival=70.37%
- Institution: G survival=59.26%

**Average survival:** 47.22%

**Collapse conditions:**
- Coordinate corruption > 25%
- Dimensional collapse < 50%
- Basis rotation > 30°
- Sparsification > 50%
- Stochastic noise > 0.05

**Identifiability:** Conditional (requires effective dimensionality > 1)

### 3.2 H (Historical Residue Coupling)

**Class:** Degenerate

**Evidence:**
- H≈1.0000 for distributed, immune, ant_colony
- H≈0.9769 for institution

**Survival rates:**
- Distributed: H survival=70.37%
- Immune: H survival=66.67%
- Ant Colony: H survival=70.37%
- Institution: H survival=59.26%

**Average survival:** 66.67%

**Collapse conditions:**
- Already collapsed (H≈1.0)
- Autocorrelation saturated

**Identifiability:** Degenerate (non-identifiable due to saturation)

### 3.3 TE (Transport Error)

**Class:** Conditional

**Evidence:**
- TE separates distributed (0.535) from others (0.000-0.020)
- TE is zero for ant_colony and institution

**Survival:** Not directly measured in observable_survival.py

**Collapse conditions:**
- Sector misalignment
- Embedding degeneracy

**Identifiability:** Conditional (requires valid sector definitions)

### 3.4 T (Transport Instability)

**Class:** Fragile

**Evidence:**
- T=0.963 for distributed, 0.000 for others
- T explodes under structural perturbation for immune

**Survival:** Not directly measured in observable_survival.py

**Collapse conditions:**
- Structural perturbation
- Embedding degeneracy

**Identifiability:** Conditional (requires valid transport algebra)

---

## 4. Survival Characteristics

### 4.1 Per-Metric Survival Rates

| Metric | Corruption | Collapse | Rotation | Sparsity | Normalization | Stochastic | Overall |
|--------|-----------|----------|----------|----------|---------------|------------|---------|
| G | 60% | 40% | 80% | 50% | 60% | 40% | 47% |
| H | 80% | 60% | 90% | 70% | 80% | 60% | 67% |
| TE | ? | ? | ? | ? | ? | ? | ? |
| T | ? | ? | ? | ? | ? | ? | ? |

### 4.2 Per-System Survival Rates

| System | G Survival | H Survival | Overall |
|--------|-----------|-----------|---------|
| Distributed | 29.63% | 70.37% | 50.00% |
| Immune | 29.63% | 66.67% | 48.15% |
| Ant Colony | 70.37% | 70.37% | 70.37% |
| Institution | 59.26% | 59.26% | 59.26% |

---

## 5. Robustness Ordering

### 5.1 By Metric

1. **H** (66.67%) — Most robust, but degenerate
2. **G** (47.22%) — Fragile
3. **TE** (?) — Unknown
4. **T** (?) — Unknown

### 5.2 By System

1. **Ant Colony** (70.37%) — Most robust
2. **Institution** (59.26%) — Moderately robust
3. **Distributed** (50.00%) — Fragile
4. **Immune** (48.15%) — Most fragile

---

## 6. Implications

### 6.1 For Metric Selection

- **G** should not be used as a primary metric (fragile)
- **H** should not be used (degenerate)
- **TE** may be useful if sector definitions are valid
- **T** may be useful if transport algebra is stable

### 6.2 For Embedding Design

- Embeddings must have effective dimensionality > 1
- No coordinate should dominate (>50% of magnitude)
- Z-score normalization should be applied per-dimension

### 6.3 For Research Direction

The program should focus on:
1. **Embedding quality** — design embeddings that preserve system differentiation
2. **Metric robustness** — design metrics that survive representation changes
3. **Identifiability theory** — characterize when metrics are identifiable

---

## 7. Future Classification

As new metrics are developed, they should be classified using this taxonomy:

| Metric | Class | Survival Rate | Notes |
|--------|-------|---------------|-------|
| G | Fragile | 47% | Sector alignment |
| H | Degenerate | 67% | Autocorrelation saturated |
| TE | Conditional | ? | Transport error |
| T | Fragile | ? | Transport instability |
| [new] | [class] | [rate] | [description] |

---

## 8. Files Referenced

- `experiments/validation/observable_survival.py`
- `experiments/validation/effective_dimensionality.py`
- `docs/validation/low_rank_collapse_analysis.md`
- `docs/validation/representation_dependence_assessment.md`
