# External Statistical Audit

**Phase 003F Division 5 — HIGH PRIORITY**

*Written as if by skeptical reviewers*

---

## 1. Executive Summary

This audit reviews the SGI Persistence repository's statistical methodology, identifiability, null controls, and inferential limitations. We identify several critical concerns that must be addressed before publication.

---

## 2. Sample Size Concerns

### 2.1 System Count

**Issue:** The repository studies only 4 systems (distributed, immune, ant_colony, institution).

**Assessment:** This is insufficient for generalizable claims. The systems may share common biases (e.g., all use similar simulation frameworks).

**Recommendation:** Either increase the number of systems or explicitly limit claims to these 4 systems.

### 2.2 Replication

**Issue:** Most experiments use a single seed (seed=42).

**Assessment:** Results may be seed-dependent. Without replication across multiple seeds, we cannot assess variance.

**Recommendation:** Run all experiments with at least 10 random seeds and report mean ± std.

### 2.3 Sample Size per System

**Issue:** Each system runs for 50 timesteps.

**Assessment:** This is very short for dynamical systems analysis. Long-term behavior may differ.

**Recommendation:** Run for at least 500 timesteps to assess steady-state behavior.

---

## 3. Metric Validity Concerns

### 3.1 G (Replay Stability)

**Issue:** G is computed using sector alignment, but sectors are arbitrary.

**Assessment:** The choice of 2 sectors is not justified. Different sector counts may yield different results.

**Recommendation:** Test G with multiple sector counts (2, 3, 4, 5) and report sensitivity.

### 3.2 H (Historical Residue Coupling)

**Issue:** H saturates at ≈1.0 for 3/4 systems.

**Assessment:** H is non-identifiable and should not be used as a primary metric.

**Recommendation:** Remove H from all primary claims. Report it only as a cautionary example.

### 3.3 TE and T

**Issue:** TE and T are 0 for 3/4 systems.

**Assessment:** These metrics are non-varying and should not be used as primary metrics.

**Recommendation:** Remove TE and T from all primary claims.

---

## 4. Null Control Concerns

### 4.1 Null Observable Failure

**Issue:** Canonical metrics generally do not outperform null observables.

**Assessment:** This is a critical finding. It means canonical metrics are not distinguishable from random noise.

**Recommendation:** This must be the central finding of any publication. Do not suppress this result.

### 4.2 Null Observable Design

**Issue:** Null observables (random, shuffled, constant, trend) may not be the best baselines.

**Assessment:** More sophisticated null models (e.g., surrogate data, permutation tests) may be needed.

**Recommendation:** Implement surrogate data testing and permutation tests.

---

## 5. Identifiability Concerns

### 5.1 Embedding Degeneracy

**Issue:** All embeddings are effectively 1D despite nominal dimensionality of 6-13.

**Assessment:** This is a critical finding. It means embeddings carry almost no independent information.

**Recommendation:** This must be the central finding of any publication. Do not suppress this result.

### 5.2 Covariance Singularity

**Issue:** All covariance matrices are singular (infinite condition number).

**Assessment:** This confirms the embedding degeneracy. Metrics computed on singular matrices are unreliable.

**Recommendation:** Report condition numbers and rank deficiency for all systems.

---

## 6. Inferential Limitations

### 6.1 No Theoretical Guarantees

**Issue:** The repository provides empirical characterizations, not theoretical proofs.

**Assessment:** This is acceptable for exploratory work, but limits the strength of claims.

**Recommendation:** Frame all claims as empirical observations, not theoretical laws.

### 6.2 No Generalization

**Issue:** Results are limited to 4 systems with specific simulation frameworks.

**Assessment:** We cannot generalize to other systems or frameworks.

**Recommendation:** Explicitly limit claims to the 4 studied systems.

### 6.3 No Causal Claims

**Issue:** The repository cannot make causal claims about representation-metric relationships.

**Assessment:** Correlation does not imply causation.

**Recommendation:** Frame all claims as correlations, not causal relationships.

---

## 7. Publication Risk Assessment

### 7.1 Paper A: "Representation Stability of Replay Metrics"

**Risk Level:** MEDIUM

**Key Risks:**
- Reviewers may ask for more systems
- Reviewers may ask for theoretical guarantees
- Reviewers may find the null control failure unsurprising

**Mitigations:**
- Frame as empirical characterization
- Acknowledge limitations explicitly
- Emphasize the novelty of the collapse transition analysis

### 7.2 Paper B: "Failure Modes of Replay Observables"

**Risk Level:** LOW-MEDIUM

**Key Risks:**
- Reviewers may find failure modes unsurprising
- Reviewers may ask for more sophisticated null models

**Mitigations:**
- Frame as systematic quantification
- Implement surrogate data testing
- Emphasize the practical implications

---

## 8. Recommendations for Revision

### 8.1 Must Fix Before Publication

1. **Replicate all experiments** with at least 10 random seeds
2. **Remove H, TE, T from primary claims** (they are non-identifiable)
3. **Acknowledge null control failure** as central finding
4. **Report embedding degeneracy** (effective dimensionality ≈ 1)
5. **Report covariance singularity** (infinite condition number)

### 8.2 Should Fix Before Publication

1. **Increase system count** (at least 6-8 systems)
2. **Increase timestep count** (at least 500 timesteps)
3. **Test G with multiple sector counts**
4. **Implement surrogate data testing**
5. **Run with multiple random seeds**

### 8.3 Nice to Have

1. **Theoretical guarantees** for metric behavior
2. **More sophisticated null models**
3. **Causal analysis** (if possible)

---

## 9. Conclusion

The repository has strong empirical findings but significant statistical limitations. The central findings (null control failure, embedding degeneracy, covariance singularity) are robust and publishable. However, the repository must acknowledge its limitations and frame claims appropriately.

**Overall Assessment:** CONDITIONAL PASS — requires revisions before publication.

---

## 10. Reviewer Signatures

- Statistical Reviewer: [Pending]
- Methodological Reviewer: [Pending]
- Domain Reviewer: [Pending]
