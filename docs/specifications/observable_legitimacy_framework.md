# Observable Legitimacy Framework

**Phase 003F Division 1 — CRITICAL**

---

## 1. Purpose

Formalize criteria for an observable to be considered legitimate in this repository.

---

## 2. Legitimacy Criteria

### 2.1 Identifiability (I)

**Definition:** The observable produces distinct values for distinct system states.

**Test:** Compute the observable across a range of perturbation levels. If the observable saturates or becomes constant, it fails identifiability.

**Threshold:** Observable must vary by >10% across the perturbation range.

**Status:**
- G: Conditional (saturates at 0 or 1 for some systems)
- H: FAILS (saturates at ≈1.0 for 3/4 systems)
- TE: FAILS (0 for 3/4 systems)
- T: FAILS (0 for 3/4 systems)
- Holonomy: FAILS (always 0)

---

### 2.2 Non-Degeneracy (ND)

**Definition:** The observable does not collapse to a trivial value (0, 1, or constant).

**Test:** Compute the observable for multiple systems. If the value is identical across systems, it fails non-degeneracy.

**Threshold:** Observable must differ by >5% across systems.

**Status:**
- G: Conditional (0.0 for ant_colony, 1.0 for immune)
- H: FAILS (≈1.0 for 3/4 systems)
- TE: FAILS (0 for 3/4 systems)
- T: FAILS (0 for 3/4 systems)
- Holonomy: FAILS (always 0)

---

### 2.3 Null-Distinguishable (ND)

**Definition:** The observable outperforms random/null observables.

**Test:** Compare canonical observable against null observables (random, shuffled, constant, trend). If canonical does not outperform null, it fails null-distinguishable.

**Threshold:** Canonical must exceed 95th percentile of null distribution.

**Status:**
- G: FAILS (outperforms null only in immune, degenerate case)
- H: FAILS (does not outperform null in any system)
- TE: Not tested
- T: Not tested
- Holonomy: Not tested

---

### 2.4 Basis-Stable (BS)

**Definition:** The observable is invariant under permutation and scaling of coordinates.

**Test:** Apply random permutations and scalings to the embedding matrix. Compute observable before and after. If relative change >10%, it fails basis-stable.

**Threshold:** Relative change <10% under permutation and scaling.

**Status:**
- G: PASSES (permutation-invariant, scale-invariant)
- H: PASSES (permutation-invariant, scale-invariant)
- TE: PASSES (permutation-invariant, scale-invariant)
- T: PASSES (permutation-invariant, scale-invariant)
- Holonomy: Not tested

---

### 2.5 Perturbation-Robust (PR)

**Definition:** The observable degrades gracefully under noise, not abruptly.

**Test:** Compute observable under increasing noise levels. If collapse is abrupt (phase-transition-like), it fails perturbation-robust.

**Threshold:** Observable must degrade smoothly (no discontinuities).

**Status:**
- G: FAILS (abrupt collapse at critical threshold)
- H: FAILS (abrupt collapse at critical threshold)
- TE: Not tested
- T: Not tested
- Holonomy: Not tested

---

### 2.6 Embedding-Consistent (EC)

**Definition:** The observable behaves consistently across different embedding methods.

**Test:** Compute observable using different embedding methods (z-score, PCA, autoencoder). If values differ by >20%, it fails embedding-consistent.

**Threshold:** Observable must agree within 20% across embedding methods.

**Status:**
- G: FAILS (varies dramatically with dimensionality)
- H: FAILS (saturated regardless of embedding)
- TE: Not tested
- T: Not tested
- Holonomy: Not tested

---

### 2.7 Statistically Recoverable (SR)

**Definition:** The observable can be recovered from finite samples with reasonable accuracy.

**Test:** Subsample the trajectory (50%, 25%, 10%). Compute observable for each subsample. If variance >20% of mean, it fails statistically-recoverable.

**Threshold:** Coefficient of variation <20%.

**Status:**
- G: FAILS (high variance across subsamples)
- H: FAILS (saturated, variance ≈0 but meaningless)
- TE: Not tested
- T: Not tested
- Holonomy: Not tested

---

## 3. Legitimacy Classification

### 3.1 Survives (passes all criteria)

None.

### 3.2 Conditional (passes some criteria)

| Observable | I | ND | ND* | BS | PR | EC | SR | Verdict |
|------------|---|----|----|----|----|----|----| ---- |
| G | C | C | F | P | F | F | F | Conditional |
| H | F | F | F | P | F | F | F | Fails |
| TE | F | F | — | P | — | — | — | Fails |
| T | F | F | — | P | — | — | — | Fails |
| Holonomy | F | F | — | — | — | — | — | Fails |

*C = Conditional, P = Passes, F = Fails, — = Not Tested

### 3.3 Fails (fails most criteria)

- H: Degenerate, non-identifiable, not null-distinguishable
- TE: Non-varying, not null-distinguishable
- T: Non-varying, not null-distinguishable
- Holonomy: Always 0, non-varying

---

## 4. Implications

### 4.1 For Publication

1. **No observable is fully legitimate.** This is the central finding.
2. **G is the most legitimate** but still fails 4/7 criteria.
3. **H should be removed from all primary claims.**
4. **TE, T, Holonomy should be removed from all primary claims.**

### 4.2 For Future Work

1. **Design new observables** that satisfy all 7 criteria
2. **Test observables on more systems** to assess generalization
3. **Develop theoretical guarantees** for observable legitimacy

### 4.3 For the Repository

1. **The legitimacy framework is the central scientific contribution**
2. **Negative results are the strongest results**
3. **The repository is now a measurement science effort**

---

## 5. Conclusion

The Observable Legitimacy Framework reveals that:
- No canonical observable is fully legitimate
- G is the most legitimate but still fails 4/7 criteria
- H is degenerate and should be removed from primary claims
- The framework itself is the primary scientific contribution

This is a strong, honest, publishable result.

---

## 6. Files Referenced

- `experiments/validation/metric_identifiability.py`
- `experiments/validation/observable_survival.py`
- `experiments/validation/null_observable_controls.py`
- `experiments/validation/effective_dimensionality.py`
- `tests/test_basis_invariance.py`
