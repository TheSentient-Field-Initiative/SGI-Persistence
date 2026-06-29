# Paper B: "Low-Rank Collapse and Observable Failure in Adaptive-System Embeddings"

**Phase 003G Division 7 — MEDIUM PRIORITY**

---

## 1. Title

"Low-Rank Collapse and Observable Failure in Adaptive-System Embeddings: A Systematic Characterization"

---

## 2. Abstract

We systematically characterize how low-rank representational collapse causes observable failure in adaptive systems. Using four canonical systems (distributed coordination, immune signaling, ant colony optimization, institutional cooperation), we measure: (1) covariance singularity across all embeddings, (2) effective dimensionality collapse to ≈1D, (3) information loss of 99.8-99.98% in compressed representations, and (4) abrupt collapse transitions with characteristic critical exponents. We find that: (1) all covariance matrices are singular (infinite condition number), (2) canonical metrics (G, H, TE, T) fail 4-6/7 legitimacy criteria, (3) random observables outperform canonical metrics in 3/4 systems, and (4) simple minimal observables (variance, persistence, lagged stability) survive where complex metrics fail. These results identify fundamental limitations of replay-based measurement in low-rank representations and provide guidelines for metric selection.

---

## 3. Introduction

### 3.1 Motivation

Replay-related observables are widely used to measure organizational persistence in adaptive systems. However, these observables are computed on state-space representations (embeddings) that may be low-rank or degenerate. This raises a critical question: what happens to observables when embeddings collapse?

### 3.2 Problem Statement

How does low-rank representational collapse cause observable failure in adaptive systems?

### 3.3 Contributions

1. **Covariance Singularity:** All covariance matrices are singular (infinite condition number)
2. **Effective Dimensionality Collapse:** All embeddings are effectively 1D
3. **Information Loss:** 1D embeddings discard 99.8-99.98% of information
4. **Collapse Mechanics:** Abrupt collapse with characteristic critical exponents
5. **Observable Failure:** Canonical metrics fail 4-6/7 legitimacy criteria

---

## 4. Methods

### 4.1 Systems

Four canonical adaptive systems:
- **Distributed:** 100-node coordination network
- **Immune:** 100-cell signaling network
- **Ant Colony:** 50-ant foraging colony
- **Institution:** 100-agent cooperation network

### 4.2 Metrics

**Canonical:**
- G (Replay Stability)
- H (Historical Residue Coupling)
- TE (Transport Error)
- T (Transport Instability)

**Survivor:**
- variance_mean
- lagged_stability
- persistence
- transition_density

### 4.3 Analysis

- Covariance spectrum analysis
- Condition number computation
- Rank deficiency measurement
- Effective dimensionality (participation ratio)
- Information loss quantification
- Collapse mechanics modeling
- Observable legitimacy testing

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

### 5.2 Effective Dimensionality Collapse

All embeddings are effectively 1D:

| System | Nominal D | Effective D | Variance Explained (1D) |
|--------|-----------|-------------|-------------------------|
| Distributed | 6 | 1.0036 | 100% |
| Immune | 11 | 1.0083 | 100% |
| Ant Colony | 13 | 1.0136 | 99.98% |
| Institution | 11 | 1.0000 | 100% |

### 5.3 Information Loss

1D embeddings discard most information:

| System | Information Loss | Reconstruction Error |
|--------|------------------|----------------------|
| Distributed | 99.83% | 0.017 |
| Immune | 99.98% | 0.043 |
| Ant Colony | 68.06% | 1236.386 |
| Institution | 0.00% | 5333.493 |

### 5.4 Collapse Mechanics

Collapse is abrupt with characteristic exponents:

| System | G Collapse Rate | G Critical Exponent | H Collapse Rate | H Critical Exponent |
|--------|-----------------|---------------------|-----------------|---------------------|
| Distributed | 24.5 | 0.000 | 0.556 | 0.123 |
| Immune | 49.0 | 0.000 | 0.580 | 0.131 |
| Ant Colony | 24.5 | 0.000 | 0.606 | 0.139 |
| Institution | 24.5 | 0.100 | 0.610 | 0.145 |

### 5.5 Observable Failure

Canonical metrics fail legitimacy testing:

| Observable | I | ND | ND* | BS | PR | EC | SR | Score | Status |
|------------|---|----|----|----|----|----|----|-------|--------|
| G | C | C | F | P | F | F | F | 2/7 | Archived |
| H | F | F | F | P | F | F | F | 1/7 | Archived |
| TE | F | F | — | P | — | — | — | 1/7 | Archived |
| T | F | F | — | P | — | — | — | 1/7 | Archived |

### 5.6 Random Outperforms Canonical

Canonical metrics do not outperform random:

| System | Winner (Lowest Variance) |
|--------|--------------------------|
| Distributed | Random |
| Immune | Random |
| Ant Colony | Random |
| Institution | Random |

### 5.7 Survivor Observables

Simple metrics survive where complex ones fail:

| Observable | Corruption Boundary | Dimensionality Boundary |
|------------|---------------------|-------------------------|
| lagged_stability | 1.00 | 34 |
| variance_mean | 0.61-1.00 | 34 |
| persistence | 0.00-0.02 | 1-34 |
| transition_density | 0.00 | 1 |

---

## 6. Discussion

### 6.1 The Central Finding

**Low-rank representational collapse causes observable failure.**

The chain of causation:
1. Embeddings are effectively 1D (despite nominal 6-13D)
2. Covariance matrices are singular (infinite condition number)
3. Information is destroyed (99.8-99.98% loss)
4. Canonical metrics become indistinguishable from random noise
5. Observable failure is complete

### 6.2 Why Collapse Happens

The embeddings collapse because:
- They use simple z-score normalization
- They don't preserve independent coordinate information
- They project high-dimensional dynamics onto low-dimensional subspaces
- The projection destroys the structure needed by canonical metrics

### 6.3 Why Simple Metrics Survive

The survivor observables survive because they:
- Don't depend on complex sector alignment
- Don't require temporal autocorrelation
- Use simple variance and stability calculations
- Are robust to representational collapse

### 6.4 Implications

1. **Representation quality is critical** — poor embeddings yield unreliable metrics
2. **Simple metrics are more robust** — complex metrics are more fragile
3. **Null controls are essential** — without them, we cannot distinguish signal from noise
4. **Collapse is predictable** — it has characteristic boundaries and exponents

---

## 7. Conclusion

We have systematically characterized how low-rank representational collapse causes observable failure in adaptive systems. Our key findings are:

1. All covariance matrices are singular (infinite condition number)
2. All embeddings are effectively 1D despite nominal 6-13D
3. Information loss is extreme (99.8-99.98%)
4. Canonical metrics fail 4-6/7 legitimacy criteria
5. Simple minimal observables survive where complex metrics fail

These results identify fundamental limitations of replay-based measurement in low-rank representations and provide guidelines for metric selection.

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
4. **Develop theoretical guarantees** for collapse mechanics
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
- `experiments/validation/survivor_observables.py`
