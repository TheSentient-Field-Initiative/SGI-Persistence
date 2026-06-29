# Observable Redundancy Analysis

**Phase 003E Division 3 — HIGH PRIORITY**

---

## 1. Question

Are G, H, TE, and T partially redundant, or do they carry independent information?

---

## 2. Current Evidence

### 2.1 Metric Values

| System | G | H | TE | T |
|--------|------|------|------|------|
| Distributed | 0.5000 | 1.0000 | 0.535 | 0.963 |
| Immune | 1.0000 | 1.0000 | 0.020 | 0.000 |
| Ant Colony | 0.0000 | 1.0000 | 0.000 | 0.000 |
| Institution | 0.5000 | 0.9769 | 0.000 | 0.000 |

### 2.2 Survival Rates

| Metric | Survival Rate | Class |
|--------|---------------|-------|
| G | 47% | Fragile |
| H | 67% | Degenerate |
| TE | ? | Conditional |
| T | ? | Fragile |

---

## 3. Redundancy Analysis

### 3.1 G vs H

**Correlation:** Not computable (H saturated at ≈1.0)

**Redundancy:** Unknown, but both are computed from the same embedding matrix.

**Independence:** G measures sector alignment; H measures autocorrelation. They are conceptually different, but both depend on the embedding quality.

### 3.2 G vs TE

**Correlation:** Not directly measured.

**Redundancy:** G measures replay stability; TE measures transport error. They are conceptually different.

**Independence:** TE may carry information about structural perturbations that G misses.

### 3.3 G vs T

**Correlation:** Corr(G, 1/T) = 0.243 (from Phase 002C)

**Redundancy:** Low correlation suggests partial independence.

**Independence:** T measures transport instability; G measures replay stability. They capture different aspects.

### 3.4 H vs TE

**Correlation:** Not directly measured.

**Redundancy:** H is saturated; TE is not. They are not redundant.

**Independence:** H measures temporal correlation; TE measures spatial correlation. They are conceptually different.

### 3.5 H vs T

**Correlation:** Not directly measured.

**Redundancy:** H is saturated; T is not. They are not redundant.

**Independence:** H measures temporal correlation; T measures transport instability. They are conceptually different.

### 3.6 TE vs T

**Correlation:** Not directly measured.

**Redundancy:** Both measure transport-related quantities.

**Independence:** TE measures transport error; T measures transport instability. They may be partially redundant.

---

## 4. Information Content Assessment

### 4.1 G (Replay Stability)

**Information content:** Low (fragile, survival rate 47%)

**Unique information:** Sector alignment under perturbation

**Redundancy with others:** Unknown

### 4.2 H (Historical Residue Coupling)

**Information content:** Very low (degenerate, saturated at ≈1.0)

**Unique information:** None (non-identifiable)

**Redundancy with others:** N/A (degenerate)

### 4.3 TE (Transport Error)

**Information content:** Moderate (conditional, separates systems)

**Unique information:** Structural transport error

**Redundancy with others:** Unknown, but potentially independent of G

### 4.4 T (Transport Instability)

**Information content:** Moderate (fragile, but captures transport dynamics)

**Unique information:** Transport instability under perturbation

**Redundancy with others:** Potentially redundant with TE

---

## 5. Recommendations

### 5.1 For Publication

1. **Remove H from primary claims** — it is degenerate and non-identifiable
2. **Focus on G and TE** — they carry the most independent information
3. **Investigate T** — it may carry information beyond TE
4. **Compute pairwise correlations** — quantify redundancy directly

### 5.2 For Future Work

1. **Design new metrics** that are more robust to representation changes
2. **Compute mutual information** between metrics to quantify redundancy
3. **Test whether metrics capture complementary aspects** of system behavior

---

## 6. Conclusion

The metrics are partially redundant:
- H is degenerate (non-identifiable)
- G is fragile but carries some unique information
- TE and T may be partially redundant

The strongest publication strategy focuses on G and TE, with T as a secondary metric. H should be removed from primary claims.

---

## 7. Files Referenced

- `experiments/validation/observable_survival.py`
- `experiments/validation/effective_dimensionality.py`
- `experiments/validation/information_capacity.py`
- `docs/specifications/metric_survival_taxonomy.md`
