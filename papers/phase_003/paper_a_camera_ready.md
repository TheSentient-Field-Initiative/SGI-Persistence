# Paper A: Camera-Ready Preparation

**Phase 003H Division 6 — MEDIUM PRIORITY**

---

## 1. Paper Title

"Observable Survival Under Representational Collapse: An Empirical Framework for Adaptive-System Metrics"

---

## 2. Required Figures

### Figure 1: Observable Elimination Table
**Source:** `docs/specifications/observable_elimination_table.md`

**Content:** Heatmap showing legitimacy scores (0-7) for all observables

**Key Message:** No canonical observable passes all criteria; simple metrics survive

---

### Figure 2: Effective Dimensionality Collapse
**Source:** `experiments/validation/effective_dimensionality.py`

**Content:** Bar chart showing participation ratios for all systems

**Key Message:** All embeddings are effectively 1D despite nominal 6-13D

---

### Figure 3: Survivor Stability Atlas
**Source:** `experiments/validation/survivor_stability_atlas.py`

**Content:** Multi-panel heatmap showing survival across 7 perturbation types

**Key Message:** lagged_stability and variance_mean are most robust

---

### Figure 4: Failure Boundary Maps
**Source:** `experiments/validation/failure_boundary_mapping.py`

**Content:** Phase diagrams showing corruption vs dimensionality boundaries

**Key Message:** Collapse boundaries are predictable and characteristic

---

### Figure 5: Null-Control Comparison
**Source:** `experiments/validation/null_observable_controls.py`

**Content:** Bar chart comparing canonical vs null observables

**Key Message:** Canonical metrics do not outperform random noise

---

### Figure 6: Representation Minimalism
**Source:** `experiments/validation/minimal_representation_tests.py`

**Content:** Heatmap showing observable survival across 8 representations

**Key Message:** 2D is the minimal viable representation

---

## 3. Paper Structure

### 3.1 Abstract (150 words)

We present an empirical framework for auditing the survival conditions of observables under representational collapse in adaptive systems. Using four canonical systems, we systematically test 15 observables against 7 legitimacy criteria. We find that: (1) no canonical observable passes all criteria, (2) simple minimal observables outperform complex canonical metrics, (3) all embeddings are effectively one-dimensional, and (4) collapse transitions are abrupt with characteristic boundaries. Our Observable Legitimacy Framework provides a systematic methodology for metric selection in adaptive systems analysis.

---

### 3.2 Introduction (1 page)

**Motivation:**
- Adaptive systems exhibit complex dynamics
- Replay-related observables measure organizational persistence
- Reliability depends on representation quality

**Problem:**
- Which observables survive representational collapse?

**Contributions:**
1. Observable Legitimacy Framework (7 criteria)
2. Survivor Observable Discovery (simple metrics outperform complex ones)
3. Failure Boundary Mapping (predictable collapse structure)
4. Minimal Representation Analysis (2D is sufficient)

---

### 3.3 Methods (2 pages)

**Systems:**
- Distributed (100 nodes)
- Immune (100 cells)
- Ant Colony (50 ants)
- Institution (100 agents)

**Observable Candidates:**
- Canonical: G, H, TE, T, Holonomy
- Survivor: variance_mean, lagged_stability, persistence, transition_density

**Legitimacy Criteria:**
1. Identifiable
2. Non-degenerate
3. Null-distinguishable
4. Basis-stable
5. Perturbation-robust
6. Embedding-consistent
7. Statistically recoverable

**Experiments:**
- Survivor Observable Search
- Observable Elimination Table
- Minimal Representation Tests
- Failure Boundary Mapping

---

### 3.4 Results (3 pages)

**Section 1: Observable Legitimacy**
- Table 1: Legitimacy scores for all observables
- No canonical observable passes all criteria
- Simple metrics achieve 7/7

**Section 2: Effective Dimensionality**
- Figure 2: Participation ratios
- All embeddings effectively 1D
- Explains canonical metric failure

**Section 3: Survivor Analysis**
- Figure 3: Stability atlas
- lagged_stability most robust (0.968)
- variance_mean second (0.925)

**Section 4: Failure Boundaries**
- Figure 4: Phase diagrams
- Corruption boundaries: 0.00-1.00
- Dimensionality boundaries: 1-34

**Section 5: Null Controls**
- Figure 5: Null comparison
- Canonical metrics do not outperform random
- Central negative result

**Section 6: Representation Minimalism**
- Figure 6: Representation survival
- 2D preserves most survivors
- Sparse 50% also works

---

### 3.5 Discussion (1 page)

**Central Finding:**
- No canonical observable survives full legitimacy testing
- This transforms the repository's contribution

**Why Simple Metrics Survive:**
- Low complexity
- Representation-light
- Basis-tolerant
- Non-sectorized

**Implications:**
1. Representation quality is critical
2. Simple metrics are more robust
3. Null controls are essential
4. Collapse is predictable

**The Contribution:**
- Framework for auditing observable survival
- Not a universal replay law

---

### 3.6 Conclusion (0.5 pages)

**Key Findings:**
1. No canonical observable passes all 7 criteria
2. Simple metrics outperform complex ones
3. All embeddings effectively 1D
4. Collapse is abrupt with characteristic boundaries

**Future Work:**
1. Increase system count
2. Increase simulation length
3. Replicate with multiple seeds
4. Test on real-world data

---

## 4. Submission Strategy

### 4.1 Target Journals

**Primary:**
- Physical Review E
- Chaos

**Secondary:**
- Journal of Nonlinear Science
- PLOS ONE

### 4.2 Submission Timeline

**Week 1-2:** Finalize figures and tables
**Week 3-4:** Write manuscript
**Week 5-6:** Internal review
**Week 7-8:** Submit

---

## 5. Quality Checklist

- [ ] All figures generated
- [ ] All tables compiled
- [ ] All references complete
- [ ] All appendices written
- [ ] All supplementary materials ready
- [ ] All co-authors reviewed
- [ ] All formatting requirements met
- [ ] All submission guidelines followed

---

## 6. Files Referenced

- `docs/specifications/observable_elimination_table.md`
- `experiments/validation/survivor_stability_atlas.py`
- `experiments/validation/effective_dimensionality.py`
- `experiments/validation/failure_boundary_mapping.py`
- `experiments/validation/null_observable_controls.py`
- `experiments/validation/minimal_representation_tests.py`
