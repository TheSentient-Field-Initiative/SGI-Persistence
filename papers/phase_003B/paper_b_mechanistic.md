# Paper B: Mechanistic Hardening

**Phase 003H Division 7 — MEDIUM PRIORITY**

---

## 1. Paper Title

"Low-Rank Collapse and Observable Failure in Adaptive-System Embeddings: A Systematic Characterization"

---

## 2. Core Mechanistic Focus

This paper must focus mechanistically on:
- Rank collapse
- Covariance singularity
- Information destruction
- Abrupt observable failure
- Phase-transition-like collapse
- Null equivalence

**Avoid:** Speculative interpretation
**Focus:** Pure empirical mechanics

---

## 3. Required Figures

### Figure 1: Covariance Spectrum Collapse
**Source:** `experiments/validation/embedding_singularity_analysis.py`

**Content:** Singular value spectra for all systems

**Key Message:** All covariance matrices are singular (infinite condition number)

---

### Figure 2: Effective Dimensionality Collapse
**Source:** `experiments/validation/effective_dimensionality.py`

**Content:** Participation ratios and spectral entropy

**Key Message:** All embeddings effectively 1D

---

### Figure 3: Information Loss
**Source:** `experiments/validation/information_capacity.py`

**Content:** Information loss across systems

**Key Message:** 99.8-99.98% information discarded

---

### Figure 4: Collapse Transitions
**Source:** `experiments/validation/collapse_transitions.py`

**Content:** Metric degradation under corruption

**Key Message:** Abrupt phase-transition-like collapse

---

### Figure 5: Null Equivalence
**Source:** `experiments/validation/null_observable_controls.py`

**Content:** Canonical vs null observable comparison

**Key Message:** Canonical metrics indistinguishable from random

---

### Figure 6: Observable Failure
**Source:** `docs/specifications/observable_elimination_table.md`

**Content:** Legitimacy scores for all observables

**Key Message:** Canonical metrics fail 4-6/7 criteria

---

## 4. Paper Structure

### 4.1 Abstract (150 words)

We systematically characterize how low-rank representational collapse causes observable failure in adaptive systems. Using four canonical systems, we measure: (1) covariance singularity across all embeddings, (2) effective dimensionality collapse to ≈1D, (3) information loss of 99.8-99.98%, and (4) abrupt collapse transitions with characteristic critical exponents. We find that: (1) all covariance matrices are singular, (2) canonical metrics fail 4-6/7 legitimacy criteria, (3) random observables outperform canonical metrics, and (4) simple minimal observables survive where complex metrics fail. These results identify fundamental limitations of replay-based measurement in low-rank representations.

---

### 4.2 Introduction (1 page)

**Motivation:**
- Replay observables measure organizational persistence
- Computations depend on embedding quality
- What happens when embeddings collapse?

**Problem:**
- How does low-rank collapse cause observable failure?

**Contributions:**
1. Covariance singularity characterization
2. Effective dimensionality collapse
3. Information destruction quantification
4. Collapse mechanics modeling

---

### 4.3 Methods (2 pages)

**Systems:**
- Distributed (100 nodes)
- Immune (100 cells)
- Ant Colony (50 ants)
- Institution (100 agents)

**Metrics:**
- Canonical: G, H, TE, T
- Survivor: variance_mean, lagged_stability, persistence, transition_density

**Analysis:**
- Covariance spectrum analysis
- Condition number computation
- Rank deficiency measurement
- Effective dimensionality (participation ratio)
- Information loss quantification
- Collapse mechanics modeling

---

### 4.4 Results (3 pages)

**Section 1: Covariance Singularity**
- Table 1: Condition numbers and rank deficiency
- All matrices singular (infinite condition number)
- Rank deficiency 3-9 dimensions

**Section 2: Effective Dimensionality**
- Figure 2: Participation ratios
- All embeddings effectively 1D
- Nominal 6-13D vs effective 1D

**Section 3: Information Loss**
- Figure 3: Information loss percentages
- 99.8-99.98% loss in 1D embeddings
- Reconstruction error high

**Section 4: Collapse Mechanics**
- Figure 4: Collapse transitions
- Abrupt phase-transition-like
- Critical exponents 0.0-0.14

**Section 5: Null Equivalence**
- Figure 5: Null comparison
- Canonical metrics do not outperform random
- Central negative result

**Section 6: Observable Failure**
- Figure 6: Legitimacy scores
- Canonical metrics fail 4-6/7 criteria
- Simple metrics pass 7/7

---

### 4.5 Discussion (1 page)

**Central Finding:**
- Low-rank collapse causes observable failure
- Chain of causation established

**Why Collapse Happens:**
- Simple z-score normalization
- No independent coordinate preservation
- High-dimensional to low-dimensional projection
- Structure destruction

**Why Canonical Metrics Fail:**
- Complex sector alignment (G)
- Temporal autocorrelation (H)
- Transport error calculation (TE)
- Transport instability (T)

**Why Simple Metrics Survive:**
- Don't depend on complex calculations
- Robust to representational collapse
- Minimal computational steps

**Implications:**
1. Representation quality is critical
2. Simple metrics are more robust
3. Null controls are essential
4. Collapse is predictable

---

### 4.6 Conclusion (0.5 pages)

**Key Findings:**
1. All covariance matrices singular
2. All embeddings effectively 1D
3. Information loss extreme (99.8-99.98%)
4. Canonical metrics fail 4-6/7 criteria
5. Simple metrics survive where complex ones fail

**Future Work:**
1. Increase system count
2. Increase simulation length
3. Replicate with multiple seeds
4. Develop theoretical guarantees

---

## 5. Mechanistic Details

### 5.1 Covariance Singularity

**Mechanism:**
- Embeddings use z-score normalization
- Normalization destroys coordinate independence
- Covariance matrix becomes singular
- Condition number → ∞

**Evidence:**
- All 4 systems: condition number = inf
- Rank deficiency: 3-9 dimensions

---

### 5.2 Effective Dimensionality Collapse

**Mechanism:**
- High-dimensional dynamics projected onto low-dimensional subspace
- Subspace captures variance but not structure
- Participation ratio ≈ 1.0

**Evidence:**
- All systems: participation ratio 1.0-1.1
- Nominal 6-13D vs effective 1D

---

### 5.3 Information Destruction

**Mechanism:**
- 1D embedding captures variance
- Discards coordinate relationships
- 99.8-99.98% information lost

**Evidence:**
- High reconstruction error
- Low predictive information

---

### 5.4 Abrupt Collapse

**Mechanism:**
- Metric degradation is not smooth
- Phase-transition-like behavior
- Critical thresholds exist

**Evidence:**
- Collapse rates: 24.5-49.0
- Critical exponents: 0.0-0.14
- Hysteresis effects

---

### 5.5 Null Equivalence

**Mechanism:**
- Canonical metrics depend on structure destroyed by collapse
- Random metrics don't depend on structure
- Both produce similar values

**Evidence:**
- Canonical does not outperform random
- z-scores < 2.0 for most comparisons

---

## 6. Quality Checklist

- [ ] All figures generated
- [ ] All tables compiled
- [ ] All mechanistic explanations complete
- [ ] All speculative interpretation removed
- [ ] All empirical evidence presented
- [ ] All co-authors reviewed
- [ ] All formatting requirements met
- [ ] All submission guidelines followed

---

## 7. Files Referenced

- `experiments/validation/embedding_singularity_analysis.py`
- `experiments/validation/effective_dimensionality.py`
- `experiments/validation/information_capacity.py`
- `experiments/validation/collapse_transitions.py`
- `experiments/validation/null_observable_controls.py`
- `docs/specifications/observable_elimination_table.md`
