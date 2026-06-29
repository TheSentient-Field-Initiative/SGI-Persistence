# Claim Language Policy

**Phase 003B — Claim Discipline Enforcement**

---

## 1. Purpose

This document defines the permitted and forbidden language for claims in the SGI Persistence Program. All publications, documentation, and code comments must adhere to this policy.

---

## 2. Terminology Rules

### 2.1 Forbidden Terms

| Term | Reason | Replacement |
|------|--------|-------------|
| "law" | Implies universality not supported by evidence | "observed correlation" |
| "universal" | Implies applicability beyond tested systems | "observed in [system list]" |
| "proof" | Implies mathematical certainty for empirical claims | "evidence consistent with" |
| "fundamental" | Implies ontological status | "candidate structural feature" |
| "principle" | Implies foundational status | "pattern" or "regularity" |
| "true" | Implies correspondence to reality | "measured" or "observed" |
| "intrinsic" | Implies observer-independent property | "observed in [measurement method]" |
| "necessary" | Implies logical inevitability | "observed" or "consistent with" |
| "sufficient" | Implies causal completeness | "associated with" |

### 2.2 Permitted Terms

| Term | Usage | Example |
|------|-------|---------|
| "observed correlation" | For statistical relationships | "An observed correlation between G and 1/H (r = -0.951) was found in 4 systems." |
| "evidence consistent with" | For supported hypotheses | "Evidence is consistent with the hypothesis that G ∝ 1/H." |
| "candidate" | For unvalidated features | "A candidate structural feature was identified." |
| "provisional" | For preliminary results | "The result is provisional and requires external replication." |
| "system-specific" | For non-generalizable findings | "The correlation is system-specific and may not generalize." |
| "observed in" | For scope limitation | "The correlation was observed in distributed, immune, ant_colony, and institution systems." |

---

## 3. Claim Categories

### 3.1 Level 1: Observational Claims

**Status:** Permitted with appropriate hedging.

**Examples:**
- "In 4 computational systems, G was observed to be proportional to 1/H."
- "The correlation between G and 1/H was r = -0.951."

**Requirements:**
- Report N (number of systems)
- Report effect size (Cohen's d, correlation coefficient)
- Report confidence interval
- Report permutation p-value

### 3.2 Level 2: Hypothetical Claims

**Status:** Permitted with explicit hypothesis framing.

**Examples:**
- "A hypothesis: G ∝ 1/H may reflect a structural feature of organizational persistence."
- "If G ∝ 1/H, then... [testable prediction]"

**Requirements:**
- Explicitly state "hypothesis" or "if"
- Provide testable prediction
- Acknowledge alternative explanations

### 3.3 Level 3: Theoretical Claims

**Status:** Forbidden until Level 2 is validated.

**Examples (FORBIDDEN):**
- "G ∝ 1/H is a law of organizational persistence."
- "The correlation is universal."

**Status:** Only permitted with explicit caveats.

---

## 4. Reporting Standards

### 4.1 Statistical Reporting

Every correlation claim must include:
- **N:** Number of systems or observations
- **Effect size:** Correlation coefficient, Cohen's d, or equivalent
- **Confidence interval:** Bootstrap 95% CI
- **Permutation test:** p-value from permutation test
- **Failure cases:** Systems or conditions where the correlation fails

### 4.2 Scope Limitation

Every claim must explicitly state:
- The systems tested
- The measurement methods used
- The conditions under which the result was obtained
- The conditions under which the result may not hold

### 4.3 Reproducibility

Every claim must be reproducible via:
- `make deterministic` (deterministic replay)
- `make hash` (artifact verification)
- External review package

---

## 5. Manuscript Language

### 5.1 Abstract

**Permitted:**
- "An observed correlation between G and 1/H (r = -0.951) was found in 4 computational systems."

**Forbidden:**
- "A universal law of organizational persistence was discovered."

### 5.2 Introduction

**Permitted:**
- "We test whether G ∝ 1/H generalizes beyond the original 4 systems."

**Forbidden:**
- "We demonstrate that G ∝ 1/H is a fundamental law."

### 5.3 Results

**Permitted:**
- "G was proportional to 1/H in the original 4 systems (r = -0.951, 95% CI [-0.998, -0.080], permutation p < 0.001)."
- "The synthetic ensemble test did not reproduce the correlation (r = -0.012)."

**Forbidden:**
- "The correlation is universal across all organizational systems."

### 5.4 Discussion

**Permitted:**
- "The correlation may reflect shared architectural features of the 4 curated systems."
- "The result is provisional and requires external replication."

**Forbidden:**
- "The correlation is a fundamental law of organizational persistence."

---

## 6. Code Comments

### 6.1 Forbidden Comments

- "# Universal organizational law"
- "# Fundamental correlation"
- "# Proof of G ∝ 1/H"

### 6.2 Permitted Comments

- "# Observed correlation in 4 systems (r = -0.951)"
- "# Provisional result, requires external replication"
- "# System-specific metric, not comparable across systems"

---

## 7. Enforcement

### 7.1 Pre-Submission Checklist

Before submitting any manuscript or documentation:
- [ ] No forbidden terms used
- [ ] All claims include N, effect size, CI, p-value
- [ ] All claims include scope limitation
- [ ] All claims include failure cases
- [ ] Reproducibility instructions provided

### 7.2 Review Process

Manuscripts must be reviewed for claim language compliance before submission.

---

## 8. Exceptions

### 8.1 Mathematical Claims

Mathematical claims (e.g., "G = surviving sectors / total sectors") are permitted without hedging, as they are definitions, not empirical claims.

### 8.2 Methodological Claims

Methodological claims (e.g., "The canonical sector alignment procedure is defined as...") are permitted without hedging, as they are methodological descriptions, not empirical claims.

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-28 | Initial claim language policy |
