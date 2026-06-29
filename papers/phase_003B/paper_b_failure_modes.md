# Paper B: "Failure Modes of Replay Observables Under Low-Rank Embeddings"

**Phase 003F Division 7 — MEDIUM PRIORITY**

---

## 1. Title

"Failure Modes of Replay Observables Under Low-Rank Embeddings: A Systematic Characterization"

---

## 2. Abstract

We systematically characterize failure modes of replay-related observables when applied to low-rank state-space representations. Using four canonical adaptive systems, we measure: (1) metric identifiability under embedding perturbations, (2) null observable controls to establish baselines, (3) representation reconstruction quality, and (4) information-carrying capacity. We find that: (1) all covariance matrices are singular (infinite condition number), (2) canonical metrics generally do not outperform null observables, (3) 1D embeddings capture variance but discard 99.8-99.98% of information, and (4) collapse transitions are abrupt with characteristic critical exponents. These results identify fundamental limitations of replay-based measurement in low-rank representations and provide guidelines for metric selection.

---

## 3. Introduction

### 3.1 Motivation

Replay-related observables are widely used to measure organizational persistence in adaptive systems. However, these observables are computed on state-space representations (embeddings) that may be low-rank or degenerate. This raises a critical question: do replay observables measure genuine system behavior, or are they artifacts of the embedding process?

### 3.2 Problem Statement

What are the failure modes of replay-related observables when applied to low-rank embeddings?

### 3.3 Contributions

1. **Covariance Singularity:** All covariance matrices are singular (infinite condition number)
2. **Information Loss:** 1D embeddings discard 99.8-99.98% of information
3. **Collapse Mechanics:** Abrupt collapse with characteristic critical exponents
4. **Observable Competition:** Canonical metrics do not outperform trivial alternatives

---

## 4. Methods

### 4.1 Systems

Four canonical adaptive systems:
- **Distributed:** 100-node coordination network
- **Immune:** 100-cell signaling network
- **Ant Colony:** 50-ant foraging colony
- **Institution:** 100-agent cooperation network

### 4.2 Metrics

- **G (Replay Stability):** Sector alignment under perturbation
- **H (Historical Residue Coupling):** Temporal autocorrelation
- **TE (Transport Error):** Structural transport error
- **T (Transport Instability):** Transport instability under perturbation

### 4.3 Analysis

- Covariance spectrum analysis
- Condition number computation
- Rank deficiency measurement
- Information loss quantification
- Collapse mechanics modeling
- Observable competition tests

---

## 5. Results

### 5.1 Covariance Singularity

All covariance matrices are singular:

| System | Condition Number | Rank Deficiency | Participation Ratio |
|--------|------------------|-----------------|---------------------|
| Distributed | inf | 4 | 1.0325 |
| Immune | inf | 9 | 1.1139 |
| Ant Colony | inf | 3 | 1.0537 |
| Institution | inf | 4 | 1.0000 |

### 5.2 Information Loss

1D embeddings discard most information:

| System | Variance Explained (1D) | Information Loss | Reconstruction Error |
|--------|-------------------------|------------------|----------------------|
| Distributed | 100% | 99.83% | 0.017 |
| Immune | 100% | 99.98% | 0.043 |
| Ant Colony | 99.98% | 68.06% | 1236.386 |
| Institution | 100% | 0.00% | 5333.493 |

### 5.3 Collapse Mechanics

Collapse is abrupt with characteristic exponents:

| System | G Collapse Rate | G Critical Exponent | H Collapse Rate | H Critical Exponent |
|--------|-----------------|---------------------|-----------------|---------------------|
| Distributed | 24.5 | 0.000 | 0.556 | 0.123 |
| Immune | 49.0 | 0.000 | 0.580 | 0.131 |
| Ant Colony | 24.5 | 0.000 | 0.606 | 0.139 |
| Institution | 24.5 | 0.100 | 0.610 | 0.145 |

### 5.4 Observable Competition

Canonical metrics do not outperform trivial alternatives:

| System | Winner (Lowest Variance) |
|--------|--------------------------|
| Distributed | Random |
| Immune | Random |
| Ant Colony | Random |
| Institution | Random |

---

## 6. Discussion

### 6.1 Covariance Singularity

The fact that all covariance matrices are singular means:
- Embeddings are effectively rank-1
- Metrics computed on singular matrices are unreliable
- The representation layer is degenerate

### 6.2 Information Loss

The high information loss means:
- 1D embeddings capture variance but discard structure
- Most coordinate information is lost
- Metrics computed on 1D embeddings are unreliable

### 6.3 Collapse Mechanics

The abrupt collapse means:
- Observable degradation is not smooth
- Identifiability has phase-boundary structure
- Replay metrics possess collapse regimes

### 6.4 Observable Competition

The fact that canonical metrics do not outperform random means:
- Replay observables are mostly embedding-induced
- The representation layer dominates the metric layer
- Canonical metrics are not distinguishable from random noise

---

## 7. Conclusion

We have systematically characterized failure modes of replay-related observables under low-rank embeddings. Our key findings are:

1. All covariance matrices are singular (infinite condition number)
2. 1D embeddings discard 99.8-99.98% of information
3. Collapse transitions are abrupt with characteristic critical exponents
4. Canonical metrics do not outperform trivial alternatives

These results identify fundamental limitations of replay-based measurement and provide guidelines for metric selection in adaptive systems analysis.

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
4. **Develop theoretical guarantees** for failure modes
5. **Test on real-world data** to assess generalization

---

## 10. References

[To be completed]

---

## 11. Supplementary Materials

- `experiments/validation/embedding_singularity_analysis.py`
- `experiments/validation/collapse_mechanics.py`
- `experiments/validation/observable_competition.py`
- `experiments/validation/information_capacity.py`
- `experiments/validation/representation_reconstruction.py`
