# Canonical Observability Gate

**Effective immediately.** No new observable enters canonical status unless it satisfies ALL requirements.

---

## Requirements

| Criterion | Requirement | How Verified |
|-----------|-------------|--------------|
| Mathematical definition | Formal symbolic definition with well-definedness proof | `docs/canonical_metrics.md` |
| Implementation reproducibility | Deterministic output given same seed and parameters | `tests/test_reproducibility.py` |
| Cross-system differentiation | Separates at least 2 of 4 system classes | Cross-system comparison |
| Null-model robustness | Survives comparison against randomized controls | `experiments/validation/` |
| Representation covariance | Survives normalization and basis rotation | Representation covariance test |
| Failure-mode documentation | Known failure modes explicitly documented | `docs/canonical_metrics.md` |

---

## Process

1. Propose observable with formal definition
2. Implement with tests
3. Run validation ensemble (100+ systems)
4. Run null model comparison
5. Run representation covariance test
6. Document failure modes
7. Submit for review

If ANY criterion fails, the observable remains exploratory only.

---

## Current Canonical Observables

| Observable | Status | Notes |
|-----------|--------|-------|
| G | Canonical | Core finding |
| H | Canonical | Core finding |
| TE | Canonical | Strong discriminator |
| RTC | Canonical | 122.5x improvement |
| T | Canonical | Immune fragility |
| Holonomy | Exploratory | Currently = 0 |
| Curvature | Exploratory | Numerically unstable |
| Noncommutativity | Exploratory | Currently = 0 |
| Torsion | Exploratory | Basis-dependent |
