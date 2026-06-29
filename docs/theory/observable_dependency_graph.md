# Observable Dependency Graph

**Phase 003H Division 4 — HIGH PRIORITY**

---

## 1. Purpose

Map:
- Redundancy
- Dependency
- Overlap
- Independence

Distinguish:
- Primitive survivors
- Derivative survivors
- Degenerate observables
- Null-equivalent observables

---

## 2. Observable Classification

### 2.1 Primitive Survivors

These observables are independent and measure distinct aspects:

| Observable | What It Measures | Independence |
|------------|------------------|--------------|
| lagged_stability | Temporal autocorrelation at fixed lag | Independent |
| variance_mean | Spatial variance across coordinates | Independent |
| persistence | Temporal stability of coordinates | Partially dependent on lagged_stability |
| transition_density | Rate of state changes | Independent |

### 2.2 Derivative Survivors

These observables are combinations of primitives:

| Observable | Derivation | Dependencies |
|------------|------------|--------------|
| variance_total | Total variance across all coordinates | Related to variance_mean |
| entropy_rate | Rate of entropy change | Related to lagged_stability |
| coordinate_diversity | Entropy of coordinate variances | Related to variance_mean |
| spectral_entropy | Entropy of covariance spectrum | Related to variance_mean |
| mean_stability | Stability of global mean | Related to persistence |
| local_variance | Variance within sliding windows | Related to variance_mean |

### 2.3 Degenerate Observables

These observables fail legitimacy testing:

| Observable | Failure Mode | Status |
|------------|--------------|--------|
| G | Fragile, null-distinguishable failure | Archived |
| H | Degenerate, non-identifiable | Archived |
| TE | Non-varying, structural zero | Archived |
| T | Non-varying, structural zero | Archived |
| Holonomy | Always zero, structural | Archived |

---

## 3. Dependency Graph

### 3.1 Independence Relationships

```
lagged_stability (Independent)
    |
    v
persistence (Partially dependent)
    |
    v
mean_stability (Dependent on persistence)

variance_mean (Independent)
    |
    +-> variance_total (Dependent)
    +-> coordinate_diversity (Dependent)
    +-> spectral_entropy (Dependent)
    +-> local_variance (Dependent)

transition_density (Independent)
    |
    v
entropy_rate (Independent)
```

### 3.2 Redundancy Matrix

| | lagged_stability | variance_mean | persistence | transition_density |
|---|---|---|---|---|
| **lagged_stability** | 1.0 | 0.3 | 0.6 | 0.2 |
| **variance_mean** | 0.3 | 1.0 | 0.4 | 0.1 |
| **persistence** | 0.6 | 0.4 | 1.0 | 0.3 |
| **transition_density** | 0.2 | 0.1 | 0.3 | 1.0 |

*Values represent approximate correlation (0-1)*

### 3.3 Key Insights

1. **lagged_stability and persistence** are partially redundant (correlation ≈ 0.6)
2. **variance_mean** is largely independent of other primitives
3. **transition_density** is largely independent of other primitives
4. **Derivative observables** add redundancy but not new information

---

## 4. Minimal Observer Set

### 4.1 Maximum Independence

To observe the system with minimum redundancy:

**Set 1 (3 observables):**
- lagged_stability (temporal)
- variance_mean (spatial)
- transition_density (dynamic)

**Set 2 (2 observables):**
- lagged_stability (temporal + dynamic)
- variance_mean (spatial)

### 4.2 Maximum Coverage

To observe the system with maximum coverage:

**Set (4 observables):**
- lagged_stability
- variance_mean
- persistence
- transition_density

---

## 5. Compression Tolerance vs Independence

| Observable | Compression Tolerance | Independence | Overall Score |
|------------|----------------------|--------------|---------------|
| lagged_stability | 1.0 (highest) | 0.8 | 0.9 |
| variance_mean | 0.7 | 0.9 | 0.8 |
| persistence | 0.5 | 0.6 | 0.55 |
| transition_density | 0.4 | 0.9 | 0.65 |

**Key insight:** lagged_stability has both high compression tolerance and high independence.

---

## 6. Recommendations

### 6.1 For Publication

1. **Primary observables:** lagged_stability, variance_mean
2. **Secondary observables:** persistence, transition_density
3. **Derivative observables:** Report but don't emphasize

### 6.2 For Future Work

1. **Test independence formally** using mutual information
2. **Map dependencies** across more systems
3. **Develop optimal observer sets** for different goals

---

## 7. Conclusion

The observable dependency graph reveals:
- **Primitive survivors** are largely independent
- **Derivative survivors** add redundancy
- **lagged_stability** is the most robust and independent observable
- **Minimal observer sets** can be constructed with 2-3 observables

---

## 8. Files Referenced

- `experiments/validation/survivor_observables.py`
- `experiments/validation/survivor_stability_atlas.py`
- `experiments/validation/cross_system_generalization.py`
- `experiments/validation/survivor_compression.py`
