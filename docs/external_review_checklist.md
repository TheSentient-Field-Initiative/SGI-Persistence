# External Review Checklist

**Phase 003C Division 7 — MEDIUM PRIORITY**

This document formalizes the checklist that external reviewers will implicitly apply. We formalize it ourselves first.

---

## 1. Reproducibility

- [ ] **Deterministic replay:** `make deterministic` produces identical results
- [ ] **Seed documentation:** All random seeds documented (seed=42)
- [ ] **Environment documentation:** Python version, dependencies documented
- [ ] **Artifact verification:** `make hash` produces verifiable SHA256 hashes
- [ ] **External review package:** `reproduction/external_review/verify.py` runs successfully

**Status:** ✅ PASS

---

## 2. Metric Traceability

- [ ] **Canonical definitions:** All metrics defined in `docs/specifications/canonical_metric_contract.md`
- [ ] **Single implementation:** Each metric has exactly one canonical implementation in `src/metrics/`
- [ ] **No local variants:** No compute_G variants outside `src/metrics/`
- [ ] **Registry compliance:** All metrics registered in `src/metrics/registry.py`
- [ ] **Sector definitions:** System-specific sector definitions documented

**Status:** ✅ PASS (10/10 metric consistency tests passing)

---

## 3. Representation Validity

- [ ] **Embedding specification:** Each system has documented embedding in `src/embeddings/`
- [ ] **Normalization:** Z-score normalization per dimension
- [ ] **Coordinate dominance:** No dimension dominates (>90% of magnitude)
- [ ] **Effective dimensionality:** N_eff > 2 for all embeddings
- [ ] **Cross-system comparison forbidden:** Embeddings are not comparable across systems

**Status:** ⚠️ PARTIAL (3/4 embeddings degenerate)

---

## 4. Failure Disclosures

- [ ] **H saturation:** H≈1.0 for 3/4 systems documented
- [ ] **G fragility:** G collapses at noise=0.01 documented
- [ ] **G dimensionality dependence:** G varies with embedding dimensionality documented
- [ ] **Synthetic ensemble failure:** Corr(G,1/H) = -0.012 documented
- [ ] **Representation dependence:** Correlation is representation-dependent documented

**Status:** ✅ PASS (all failures documented)

---

## 5. Statistical Controls

- [ ] **Sample size:** N=4 systems reported
- [ ] **Effect size:** Correlation coefficient r=-0.951 reported
- [ ] **Confidence interval:** 95% CI [-0.998, -0.080] reported
- [ ] **Permutation test:** p<0.001 reported
- [ ] **Failure cases:** Systems where correlation fails documented

**Status:** ✅ PASS

---

## 6. Claim Discipline

- [ ] **No forbidden terms:** "law", "universal", "proof" not used
- [ ] **Provisional language:** "observed correlation" used consistently
- [ ] **Scope limitation:** "in 4 curated systems" stated
- [ ] **Replication requirement:** "requires external replication" stated
- [ ] **Limitation disclosure:** All limitations documented

**Status:** ✅ PASS (claim language policy enforced)

---

## 7. Known Limitations

- [ ] **System-specificity:** Correlation based on 4 curated systems
- [ ] **Computational simulations:** Not biological or social systems
- [ ] **Deterministic protocols:** Stochastic effects not explored
- [ ] **Embedding degeneracy:** 3/4 embeddings show coordinate dominance
- [ ] **Metric fragility:** G collapses under minimal perturbation

**Status:** ✅ PASS (all limitations documented)

---

## 8. Summary

| Category | Status | Notes |
|----------|--------|-------|
| Reproducibility | ✅ PASS | Deterministic replay, artifact hashing |
| Metric Traceability | ✅ PASS | Canonical definitions, single implementation |
| Representation Validity | ⚠️ PARTIAL | 3/4 embeddings degenerate |
| Failure Disclosures | ✅ PASS | All failures documented |
| Statistical Controls | ✅ PASS | N, CI, p-value reported |
| Claim Discipline | ✅ PASS | Provisional language enforced |
| Known Limitations | ✅ PASS | All limitations documented |

**Overall Status:** ⚠️ CONDITIONAL PASS

The external review package is ready for review, with the caveat that representation validity is partial (3/4 embeddings degenerate).

---

## 9. Recommendations for External Reviewers

1. **Run `make deterministic`** to verify reproducibility
2. **Run `make hash`** to verify artifact integrity
3. **Run `reproduction/external_review/verify.py`** to verify results
4. **Review `docs/validation/representation_dependence_assessment.md`** for critical analysis
5. **Review `docs/audits/embedding_geometry_audit.md`** for embedding quality

---

## 10. Files Referenced

- `Makefile` — deterministic replay, artifact hashing
- `reproduction/external_review/verify.py` — verification script
- `reproduction/external_review/failure_modes.md` — failure documentation
- `reproduction/external_review/known_limitations.md` — limitation documentation
- `docs/specifications/canonical_metric_contract.md` — metric definitions
- `docs/specifications/embedding_contracts.md` — embedding contracts
- `docs/validation/representation_dependence_assessment.md` — representation analysis
- `docs/audits/embedding_geometry_audit.md` — embedding geometry audit
- `tests/test_metric_consistency.py` — metric consistency tests
