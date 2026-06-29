# Known Limitations

This document acknowledges known limitations of the SGI Persistence Program.

---

## 1. System-Specificity

**Limitation:** The observed G∝1/H correlation (r = -0.951) is based on 4 curated systems. The synthetic ensemble test (100 randomized systems) did not reproduce the relation.

**Implication:** The correlation may reflect shared architectural features of the 4 curated systems rather than a universal law.

**Current Status:** Under investigation.

---

## 2. Metric Identity Collapse

**Limitation:** The generic `state_to_vector` embedding produces organizationally uninformative vectors (89.9-99.4% coordinate domination).

**Implication:** Metrics computed using the generic embedding are not meaningful.

**Current Status:** Fixed with system-specific embeddings.

---

## 3. Sector Definition Dependence

**Limitation:** G values depend on the specific sector definitions used. Different sector definitions produce different G values.

**Implication:** G values are not comparable across systems with different sector definitions.

**Current Status:** Documented in canonical metric contract.

---

## 4. Deterministic Protocols Only

**Limitation:** All current experiments use deterministic protocols. Stochastic effects are not explored.

**Implication:** Results may not generalize to stochastic systems.

**Current Status:** Acknowledged, not yet addressed.

---

## 5. Computational Simulations Only

**Limitation:** All experiments use computational simulations, not biological or social systems.

**Implication:** Results may not generalize to real-world systems.

**Current Status:** Acknowledged, not yet addressed.

---

## 6. No Runtime Cost Analysis

**Limitation:** No analysis of computational costs for real-time organizational monitoring.

**Implication:** Feasibility of real-world deployment is unknown.

**Current Status:** Acknowledged, not yet addressed.

---

## 7. Transport Model Instability

**Limitation:** Holonomy and curvature observables are numerically unstable (currently zero for all systems).

**Implication:** These observables cannot be used for system differentiation.

**Current Status:** Under investigation.

---

## 8. Representation Ceiling

**Limitation:** Scalar observables saturate at a fundamental limit (Study 001N).

**Implication:** Scalar metrics alone cannot fully characterize organizational persistence.

**Current Status:** Motivated geometric formalism in Phase 002.

---

## 9. No External Replication

**Limitation:** No independent replication by external researchers.

**Implication:** Results are not yet independently verified.

**Current Status:** External review package created to facilitate replication.

---

## 10. Claim Discipline

**Limitation:** Previous versions of the codebase used language implying universal laws.

**Implication:** Claims were stronger than the evidence supports.

**Current Status:** All claims downgraded to "observed correlation" (provisional, system-specific).

---

## Summary

| Limitation | Severity | Status |
|-----------|----------|--------|
| System-specificity | HIGH | Under investigation |
| Metric identity collapse | CRITICAL | Fixed |
| Sector definition dependence | HIGH | Documented |
| Deterministic protocols only | MEDIUM | Acknowledged |
| Computational simulations only | MEDIUM | Acknowledged |
| No runtime cost analysis | LOW | Acknowledged |
| Transport model instability | HIGH | Under investigation |
| Representation ceiling | MEDIUM | Motivated Phase 002 |
| No external replication | HIGH | Facilitated |
| Claim discipline | HIGH | Stabilized |
