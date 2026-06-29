# Publication Triage — Paper A and Paper B

**Phase 003E Division 7 — MEDIUM PRIORITY**

---

## 1. Paper A: "Representation Stability of Replay Metrics in Adaptive Systems"

### 1.1 Title
"Representation Stability of Replay Metrics in Adaptive Systems: An Empirical Characterization"

### 1.2 Abstract
We study how the reliability of replay-related observables depends on the quality of state-space representations in adaptive systems. Using four canonical systems (distributed coordination, immune signaling, ant colony optimization, institutional cooperation), we measure the effective dimensionality of learned embeddings and characterize how metric behavior changes under representation perturbations. We find that: (1) all embeddings are effectively one-dimensional despite nominal dimensionality of 6-13, (2) collapse transitions are abrupt (phase-transition-like) rather than gradual, and (3) metric survival rates vary from 47% (fragile) to 67% (degenerate). These results provide a systematic characterization of representation-dependent metric failure modes, with implications for the design of robust organizational measurement tools.

### 1.3 Key Results
1. Effective dimensionality ≈ 1 for all embeddings (participation ratio ≈ 1.0)
2. Collapse transitions are abrupt (critical thresholds vary by system)
3. G survival = 47%, H survival = 67% (H is degenerate)
4. Hysteresis effects present in all systems

### 1.4 Target Venues
- Physical Review E
- Chaos
- Journal of Nonlinear Science

### 1.5 Rigor Assessment
- Empirical: 5/5
- Reproducible: 4/5 (deterministic pipeline, hash verification)
- Falsifiable: 4/5 (clear predictions, null controls)
- Novel: 4/5 (systematic representation stability analysis)

---

## 2. Paper B: "Failure Modes of Replay Observables Under Low-Rank Embeddings"

### 2.1 Title
"Failure Modes of Replay Observables Under Low-Rank Embeddings: A Systematic Characterization"

### 2.2 Abstract
We systematically characterize failure modes of replay-related observables when applied to low-rank state-space representations. Using four canonical systems, we measure: (1) metric identifiability under embedding perturbations, (2) null observable controls to establish baselines, (3) representation reconstruction quality, and (4) information-carrying capacity. We find that: (1) canonical metrics generally do not outperform null observables, (2) 1D embeddings capture variance but discard 99.8-99.98% of information, (3) reconstruction error is high for systems with complex dynamics, and (4) predictive information from 1D representations is unreliable. These results identify fundamental limitations of replay-based measurement in low-rank representations and provide guidelines for metric selection.

### 2.3 Key Results
1. Null observable controls: G outperforms null only in immune system (degenerate case)
2. Information loss: 99.83% (distributed), 99.98% (immune), 68.06% (ant colony), 0% (institution)
3. Reconstruction error: 0.017 (distributed), 0.043 (immune), 1236 (ant colony), 5333 (institution)
4. Predictive information from 1D: unreliable (high error in institution)

### 2.4 Target Venues
- PLOS ONE
- Royal Society Open Science
- Scientific Reports

### 2.5 Rigor Assessment
- Empirical: 5/5
- Reproducible: 4/5 (deterministic pipeline, hash verification)
- Falsifiable: 4/5 (clear predictions, null controls)
- Novel: 3/5 (failure modes well-documented, but not surprising)

---

## 3. Key Differences

| Aspect | Paper A | Paper B |
|--------|---------|---------|
| Focus | Representation stability | Failure modes |
| Novelty | Abrupt collapse transitions | Null controls, reconstruction |
| Audience | Physicists, nonlinear scientists | Broad science |
| Venue tier | Top field journal | Broad science journal |

---

## 4. Writing Strategy

### 4.1 Paper A Outline
1. Introduction: Why representation stability matters
2. Methods: Systems, metrics, perturbations
3. Results: Effective dimensionality, collapse transitions, survival rates
4. Discussion: Implications for organizational measurement
5. Conclusion: Guidelines for robust metric design

### 4.2 Paper B Outline
1. Introduction: Why failure modes matter
2. Methods: Null controls, reconstruction, information capacity
3. Results: Null baseline comparison, information loss, reconstruction error
4. Discussion: Limitations of low-rank representations
5. Conclusion: When not to use replay metrics

---

## 5. Timeline

1. **Week 1-2:** Draft Paper A methods and results
2. **Week 3-4:** Draft Paper B methods and results
3. **Week 5-6:** Write introductions and discussions
4. **Week 7-8:** Internal review and revision
5. **Week 9-10:** Submit Paper A
6. **Week 11-12:** Submit Paper B

---

## 6. Risks

1. **Paper A:** Reviewers may ask for theoretical guarantees (we have none)
2. **Paper B:** Reviewers may find failure modes unsurprising
3. **Both:** Limited to 4 systems, may not generalize

---

## 7. Mitigations

1. **Theoretical guarantees:** Frame as empirical characterization, not theory
2. **Failure modes:** Emphasize systematic quantification, not surprise
3. **Generalization:** Acknowledge limitation, suggest future work

---

## 8. Conclusion

Both papers are viable for publication:
- Paper A targets top field journals with novel collapse transition results
- Paper B targets broad science journals with systematic failure mode characterization

The key is to frame results as empirical characterization, not theoretical claims.
