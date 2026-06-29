# Related Work Positioning

**Phase 003E Division 6 — MEDIUM PRIORITY**

---

## 1. Question

Where does this work fit in the broader literature?

---

## 2. Related Fields

### 2.1 Representation Learning

**Key Works:**
- Bengio et al. (2013) "Representation Learning: A Review and New Perspectives"
- Hamilton et al. (2017) "Inductive Representation Learning on Large Graphs" (GraphSAGE)
- Kipf & Welling (2017) "Semi-Supervised Classification with Graph Convolutional Networks"

**Positioning:** Our work studies how representation quality affects metric reliability, not how to learn better representations.

### 2.2 Dynamical Systems Identification

**Key Works:**
- Brunton et al. (2016) "Discovering governing equations from data by sparse identification of nonlinear dynamical systems"
- Lusch et al. (2018) "Deep learning for universal linear embeddings of nonlinear dynamics"
- Champion et al. (2019) "Data-enabled discovery of partial differential equations"

**Positioning:** Our work focuses on organizational persistence metrics, not equation discovery.

### 2.3 Embedding Robustness

**Key Works:**
- Gilmer et al. (2018) "Neural Message Passing for Quantum Chemistry"
- Xu et al. (2018) "How Powerful are Graph Neural Networks?"
- Brody et al. (2021) "How Attentive are Graph Attention Networks?"

**Positioning:** Our work studies metric robustness under embedding perturbations, not graph neural network architectures.

### 2.4 Complexity Science

**Key Works:**
- Mitchell (2009) "Complexity: A Guided Tour"
- Ladyman et al. (2013) "Towards a Theoretical Framework for Complexity"
- Hidalgo & Hausmann (2009) "The Building Blocks of Economic Complexity"

**Positioning:** Our work provides empirical measurement tools, not theoretical complexity frameworks.

### 2.5 Organizational Theory

**Key Works:**
- March (1991) "Exploration and Exploitation in Organizational Learning"
- Levinthal & March (1993) "The Myopia of Learning"
- Weick & Sutcliffe (2007) "Managing the Unexpected"

**Positioning:** Our work provides computational metrics, not organizational theory.

---

## 3. Unique Contributions

### 3.1 What We Add

1. **Metric Identifiability Analysis:** Systematic study of how embedding quality affects metric reliability
2. **Collapse Transition Characterization:** Abrupt vs gradual collapse under representation perturbations
3. **Null Observable Controls:** Baseline comparison for canonical metrics
4. **Representation Reconstruction Tests:** Quantifying information loss in compressed embeddings

### 3.2 What We Do NOT Add

1. **New representation learning methods**
2. **New dynamical systems identification algorithms**
3. **New complexity theory frameworks**
4. **New organizational theory**

---

## 4. Publication Venues

### 4.1 Paper A: "Representation Stability of Replay Metrics in Adaptive Systems"

**Target Venues:**
- Physical Review E (statistical physics, nonlinear dynamics)
- Chaos (nonlinear science)
- Journal of Nonlinear Science

**Rigor:** 4/5 (empirical, reproducible, falsifiable)

### 4.2 Paper B: "Failure Modes of Replay Observables Under Low-Rank Embeddings"

**Target Venues:**
- PLOS ONE (broad audience, negative results welcome)
- Royal Society Open Science (broad science)
- Scientific Reports (broad science)

**Rigor:** 4/5 (empirical, reproducible, falsifiable)

---

## 5. Key Differentiators

| Aspect | Our Work | Related Work |
|--------|----------|--------------|
| Focus | Metric robustness | Representation learning |
| Methods | Empirical measurement | Algorithm design |
| Systems | Adaptive organizations | Physical/biological systems |
| Output | Failure modes, collapse boundaries | New algorithms, theories |

---

## 6. Limitations of Positioning

1. **Narrow scope:** We study 4 systems, not general classes
2. **Specific metrics:** We study G, H, TE, T, not general complexity measures
3. **Limited embedding types:** We test z-score normalization, not learned embeddings
4. **No theoretical guarantees:** We provide empirical characterizations, not proofs

---

## 7. Conclusion

This work fills a gap between:
- Representation learning (how to learn embeddings)
- Dynamical systems identification (how to discover equations)
- Complexity science (how to measure complexity)

Our unique contribution is: **systematic empirical characterization of how representation quality affects metric reliability in adaptive systems.**

---

## 8. References

### Representation Learning
- Bengio, Y., Courville, A., & Vincent, P. (2013). Representation learning: A review and new perspectives. IEEE TPAMI.
- Hamilton, W. L., Ying, R., & Leskovec, J. (2017). Inductive representation learning on large graphs. NeurIPS.
- Kipf, T. N., & Welling, M. (2017). Semi-supervised classification with graph convolutional networks. ICLR.

### Dynamical Systems
- Brunton, S. L., Proctor, J. L., & Kutz, J. N. (2016). Discovering governing equations from data. PNAS.
- Lusch, E., Kutz, J. N., & Brunton, S. L. (2018). Deep learning for universal linear embeddings of nonlinear dynamics. Nature Communications.
- Champion, K., Lusch, E., Kutz, J. N., & Brunton, S. L. (2019). Data-enabled discovery of partial differential equations. Science Advances.

### Graph Neural Networks
- Gilmer, J., Schoenholz, S. S., Riley, P. F., Vinyals, O., & Dahl, G. E. (2017). Neural message passing for quantum chemistry. ICML.
- Xu, K., Hu, W., Leskovec, J., & Jegelka, S. (2018). How powerful are graph neural networks? ICLR.
- Brody, S., Alon, U., & Yahav, E. (2021). How attentive are graph attention networks? ICLR.

### Complexity Science
- Mitchell, M. (2009). Complexity: A guided tour. Oxford University Press.
- Ladyman, J., Ross, D., Spurrett, D., & Collier, J. (2013). Around the bend of the double helix. Oxford University Press.
- Hidalgo, C. A., & Hausmann, R. (2009). The building blocks of economic complexity. Science.

### Organizational Theory
- March, J. G. (1991). Exploration and exploitation in organizational learning. Organization Science.
- Levinthal, D. A., & March, J. G. (1993). The myopia of learning. Strategic Management Journal.
- Weick, K. E., & Sutcliffe, K. M. (2007). Managing the unexpected: Resilient performance in an age of uncertainty. Jossey-Bass.
