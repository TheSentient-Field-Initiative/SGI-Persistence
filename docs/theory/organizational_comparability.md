# Organizational Comparability

**Status:** Mandatory infrastructure
**Version:** 0.3.0
**Last updated:** 2026-06-28

This document formally defines admissible organizational comparison. Without it, reviewers will reject the framework as category collapse.

---

## 1. Organizational State

An **organizational state** is a point in a measurable space $(S, \Sigma, \mu)$ where:

- $S$ is the set of all possible configurations
- $\Sigma$ is a $\sigma$-algebra on $S$
- $\mu$ is a probability measure on $\Sigma$

**Operational definition:** An organizational state is any vector $\mathbf{s} \in \mathbb{R}^n$ where each component represents a measurable system property (connectivity, activation, allocation, etc.).

**Admissibility criterion:** States must be comparable across systems. This requires:
1. Fixed dimensionality (currently $n = 8$)
2. Normalization (currently max-absolute-value normalization)
3. Consistent component semantics

---

## 2. Replay Structure

A **replay structure** is a map $\rho: S \times T \to S$ where $T$ is a set of replay indices.

**Operational definition:** Given a trajectory $\{s_0, s_1, \ldots, s_N\}$, a replay operation takes a state $s_i$ and produces a new state $s_j$ through the system's own generative process.

**Admissibility criterion:** Replay must be:
1. Deterministic given the same history (reproducible)
2. Bounded (output stays in $S$)
3. Observable (result is measurable)

---

## 3. Memory Topology

A **memory topology** $\mathcal{M}$ on trajectory $\{s_0, \ldots, s_N\}$ is a family of subsets $\{M_t\}_{t=0}^N$ where $M_t \subseteq \{s_0, \ldots, s_t\}$.

**Operational definition:** $M_t$ is the set of historical states that influence $s_t$. Currently defined as $M_t = \{s_{t-k}, \ldots, s_{t-1}\}$ for memory depth $k$.

**Admissibility criterion:** Memory must be:
1. Finite (bounded memory depth)
2. Causal (only past states in $M_t$)
3. Measurable (computable from trajectory)

---

## 4. Adaptation Loop

An **adaptation loop** is a feedback cycle:

$$s_t \xrightarrow{\text{observe}} o_t \xrightarrow{\text{compare}} \Delta_t \xrightarrow{\text{update}} s_{t+1}$$

where $o_t$ is an observation, $\Delta_t$ is a discrepancy signal, and the update is bounded.

**Operational definition:** The adaptation loop in our systems is:
1. Observe current state metrics
2. Compare with target or history
3. Adjust node behaviors accordingly

**Admissibility criterion:** Adaptation must be:
1. Bounded (no divergent updates)
2. Observable (changes are measurable)
3. Rate-limited (adaptation rate $\alpha \in [0, 1]$)

---

## 5. Persistence Architecture

A **persistence architecture** is a tuple $(S, \rho, \mathcal{M}, \alpha, P)$ where:

- $S$ is the state space
- $\rho$ is the replay structure
- $\mathcal{M}$ is the memory topology
- $\alpha$ is the adaptation rate
- $P$ is a persistence measure (currently $G$)

**Admissibility criterion:** Persistence architectures are comparable if:
1. State spaces are isomorphic (same dimension, comparable semantics)
2. Replay structures are of the same type (deterministic, stochastic)
3. Memory topologies have comparable structure (finite, causal)
4. Persistence measures are computed identically

---

## 6. Equivalence Conditions

Two organizational systems are **admissibly comparable** if:

1. **State equivalence:** Both produce vectors in $\mathbb{R}^n$ with consistent semantics
2. **Replay equivalence:** Both use deterministic replay from history
3. **Memory equivalence:** Both have finite, causal memory
4. **Metric equivalence:** Both compute $G$, $H$, $TE$ using identical formulas
5. **Perturbation equivalence:** Both can be subjected to comparable perturbations

**Non-equivalence:** Systems that differ in any of the above are not admissibly comparable without additional justification.

---

## 7. What This Document Does NOT Claim

- It does NOT claim all organizations are equivalent
- It does NOT claim our metrics capture all relevant structure
- It does NOT claim cross-domain transfer is automatic
- It does NOT claim the framework is complete

It ONLY claims that the specific systems we compare satisfy the admissibility conditions above.
