# Embedding Geometry Audit

**Phase 003C Division 2 — CRITICAL**

---

## 1. Purpose

This document audits the geometry of system-specific embeddings to prove they are not accidental low-rank artifacts. It includes covariance spectra, singular value structure, coordinate dominance maps, effective dimensionality, and redundancy analysis.

---

## 2. Embedding Specifications

### 2.1 Distributed Embedding

**File:** `src/embeddings/distributed_embedding.py`

**Dimensions (8D):**
| Dim | Key | Range | Role |
|-----|-----|-------|------|
| 0 | connectivity | [0, 1] | Topology |
| 1 | n_active | [0, 100] | Amplitude |
| 2 | routing_entropy | [0, 1] | Topology |
| 3 | assignment_rate | [0, 1] | Topology |
| 4 | allocation_entropy | [0, 1] | Residual |
| 5 | n_components | [0, 100] | Topology |
| 6 | timestep | [0, 50] | Time |
| 7 | reserved | [0, 0] | Placeholder |

**Normalization:** Z-score per dimension

### 2.2 Immune Embedding

**File:** `src/embeddings/immune_embedding.py`

**Dimensions (8D):**
| Dim | Key | Range | Role |
|-----|-----|-------|------|
| 0 | signaling_connectivity | [0, 1] | Topology |
| 1 | n_active | [0, 100] | Amplitude |
| 2 | type_entropy | [0, 1] | Topology |
| 3 | mean_activation | [0, 1] | Amplitude |
| 4 | total_cytokines | [0, 1000] | Amplitude |
| 5 | n_components | [0, 100] | Topology |
| 6 | cov_trace | [0, 100] | Transport |
| 7 | non_principal | [0, 1] | Residual |

**Normalization:** Z-score per dimension

### 2.3 Ant Colony Embedding

**File:** `src/embeddings/ant_embedding.py`

**Dimensions (8D):**
| Dim | Key | Range | Role |
|-----|-----|-------|------|
| 0 | trail_connectivity | [0, 1] | Topology |
| 1 | total_pheromone | [0, 1000] | Amplitude |
| 2 | recruitment_rate | [0, 1] | Amplitude |
| 3 | path_redundancy | [0, 1] | Topology |
| 4 | n_components | [0, 100] | Topology |
| 5 | cov_trace | [0, 100] | Transport |
| 6 | anisotropy | [0, 1] | Transport |
| 7 | non_principal | [0, 1] | Residual |

**Normalization:** Z-score per dimension

### 2.4 Institution Embedding

**File:** `src/embeddings/institution_embedding.py`

**Dimensions (8D):**
| Dim | Key | Range | Role |
|-----|-----|-------|------|
| 0 | network_connectivity | [0, 1] | Topology |
| 1 | mean_trust | [0, 1] | Amplitude |
| 2 | cooperation_rate | [0, 1] | Amplitude |
| 3 | strategy_entropy | [0, 1] | Topology |
| 4 | mean_payoff | [0, 1] | Amplitude |
| 5 | n_components | [0, 100] | Topology |
| 6 | cov_trace | [0, 100] | Transport |
| 7 | non_principal | [0, 1] | Residual |

**Normalization:** Z-score per dimension

---

## 3. Covariance Spectra

### 3.1 Distributed

**Computed from 50-step trajectory:**
- Covariance matrix: 8×8
- Eigenvalues: [λ₁, λ₂, ..., λ₈]
- Effective dimensionality: N_eff = exp(-Σ pᵢ log pᵢ) where pᵢ = λᵢ / Σ λⱼ

**Expected:** If embedding is well-structured, eigenvalues should span multiple orders of magnitude.

### 3.2 Immune

**Expected:** Similar to distributed, but with different spectral shape due to different semantic content.

### 3.3 Ant Colony

**Expected:** May show degeneracy due to pheromone-dominated dynamics.

### 3.4 Institution

**Expected:** May show degeneracy due to trust-dominated dynamics.

---

## 4. Singular Value Structure

### 4.1 Method

For each trajectory of length T:
1. Construct matrix X ∈ ℝ^{T×8} where each row is an embedding vector
2. Compute SVD: X = UΣVᵀ
3. Report singular values σ₁ ≥ σ₂ ≥ ... ≥ σ₈

### 4.2 Expected Results

| System | σ₁/σ₈ | Interpretation |
|--------|--------|----------------|
| Distributed | Moderate | Well-structured embedding |
| Immune | High | Possible degeneracy |
| Ant Colony | Very High | Likely degenerate |
| Institution | High | Possible degeneracy |

---

## 5. Coordinate Dominance Maps

### 5.1 Method

For each embedding dimension d:
1. Compute mean absolute value across trajectory: μ_d = E[|x_d|]
2. Compute dominance ratio: d_d = μ_d / Σ μ_j

### 5.2 Results

**From metric_identifiability.py:**
- Distributed: dominance dict available in results
- Immune: embedding degenerate = True
- Ant Colony: embedding degenerate = True
- Institution: embedding degenerate = True

**Implication:** Three of four embeddings show coordinate dominance, meaning one dimension contributes disproportionately to the vector norm.

---

## 6. Effective Dimensionality

### 6.1 Method

N_eff = exp(-Σ pᵢ log pᵢ) where pᵢ = λᵢ / Σ λⱼ

### 6.2 Interpretation

| N_eff | Interpretation |
|-------|----------------|
| 8 | All dimensions equally important |
| 4-7 | Moderate dimensionality |
| 2-3 | Low dimensionality |
| 1 | Single dimension dominates |

---

## 7. Redundancy Analysis

### 7.1 Method

For each pair of dimensions (i, j):
1. Compute correlation: ρ_ij = corr(x_i, x_j)
2. Flag pairs with |ρ_ij| > 0.8 as redundant

### 7.2 Expected Results

**Distributed:** Low redundancy (dimensions are semantically distinct)
**Immune:** Moderate redundancy (amplitude dimensions may correlate)
**Ant Colony:** High redundancy (pheromone-dominated)
**Institution:** High redundancy (trust-dominated)

---

## 8. Conclusions

### 8.1 Embedding Quality Assessment

| System | Quality | Issue |
|--------|---------|-------|
| Distributed | Moderate | Sector collapsed, but embedding functional |
| Immune | Poor | Embedding degenerate, H saturated |
| Ant Colony | Poor | G=0, embedding degenerate, H saturated |
| Institution | Poor | G=0, embedding degenerate |

### 8.2 Recommendations

1. **Distributed:** Acceptable for continued use. Sector definitions need review.
2. **Immune:** Embedding needs restructuring. Consider fewer dimensions or different normalization.
3. **Ant Colony:** Embedding likely unusable for G/H computation. Consider alternative metrics.
4. **Institution:** Embedding needs restructuring. Consider alternative metrics.

### 8.3 Implications for G∝1/H

The identifiability analysis reveals that H=1.0000 for three systems, meaning the autocorrelation is saturated. This suggests the G∝1/H correlation may be an artifact of the specific embedding and metric implementations, not a universal structural feature.

---

## 9. Files Referenced

- `experiments/validation/metric_identifiability.py`
- `src/embeddings/distributed_embedding.py`
- `src/embeddings/immune_embedding.py`
- `src/embeddings/ant_embedding.py`
- `src/embeddings/institution_embedding.py`
- `docs/specifications/embedding_contracts.md`
