# A Condensed Mathematical History of the SFH-SGP Research Program

> **ARCHIVAL NOTICE:** This document preserves the historical mathematical development of the program, including early conceptual frameworks. Some terminology and framing in this document reflect earlier stages of the research and may not match current canonical usage. For current terminology, see `docs/terminology/CANONICAL_TERMS.md`.

## From Sentient Fields to Gauge Theory of Covariance Observability

*Prepared for NotebookLM scientific critique — June 2026*

---

## Prologue: The Original Question

The program began with a single question:

> **Can brain activity patterns be reverse-engineered into geometric representations, and can these representations predict system organization?**

This question drove every mathematical choice that followed. Each section below describes a mathematical framework, why it was adopted, what it revealed, and why it was eventually superseded or transformed.

---

## STAGE 1: The Sentient Field Hypothesis (SFH-SGP)
**Period:** Earliest work (pre-April 2026)
**Repositories:** `sgp-tribe3/sfh_sgp_analysis/`

### Mathematical Framework

The original framework defined five primitives over a 9-node network:

| Symbol | Name | Formula | Purpose |
|--------|------|---------|---------|
| Q | Total Sentient Quota | $\sum_i \|a_i - 0.5\|$ | Total differential flux |
| Q_k | Sub-quota per node | $a_k / Q$ | Partition structure |
| F | Fertility | $a_{DMN}$ (default mode activation) | Generative capacity |
| C | Coherence | $\log_{10}(\pi) + \log_{10}(\lambda_1)$ where $\lambda_1$ = leading eigenvalue of co-activation matrix | Global integration |
| $\chi$ | Sentient Potential | $\alpha C + \beta F$ | Combined field potential |
| $\tau$ | Torsion | $(1 - CV)(1 - \bar{F})$ per node | Locked vs. flexible circuits |

**Dynamics:** Langevin equation $\dot{q} = -\nabla\chi + \sqrt{2D}\xi(t)$ with cooling annealing (rate 0.95). K-depth = iterations to convergence (threshold 0.001).

**Analysis:** Hessian $\nabla^2\chi = 2\alpha M + \beta\Lambda$ where $M$ is the co-activation matrix. Resonance anchors = stable minima of $\chi$.

### Why This Way

The SFH posited that neural systems are projections of an underlying "sentient field." The math was designed to:
1. Quantify total system activity (Q)
2. Separate generative (F) from integrative (C) capacity
3. Classify nodes as locked/flexible ($\tau$)
4. Find stable configurations via energy minimization (Langevin + Hessian)

### What It Revealed

- Coherence C could be computed from co-activation structure
- Torsion $\tau$ classified nodes into LOCKED/MODERATE/FLEXIBLE categories
- K-depth (convergence time) varied systematically with system complexity

### Why It Was Abandoned

1. **The 9-node network was arbitrary** — no principled way to choose nodes
2. **C depended on leading eigenvalue** — sensitive to network topology choices
3. **No ground truth** — couldn't validate against known systems
4. **Metaphysical commitments** embedded in mathematical definitions

**Lesson learned:** Mathematical frameworks should not encode metaphysical assumptions.

---

## STAGE 2: Multiscale Dimensionality D(k)
**Period:** Transitional (April 2026)
**Repositories:** `sfh_sgp_core/modules/`, `sgp-tribe3/empirical_analysis/physics/`

### Mathematical Framework

The core object became the **D(k) estimator**:

1. For each point $x_i$, find $k$ nearest neighbors $N_k(x_i)$
2. Compute local covariance $C_i$ of points in $N_k(x_i)$
3. Eigen-decompose: eigenvalues $\lambda_1, \ldots, \lambda_d$
4. **Participation ratio:** $D_{\text{eff}}(k) = \frac{(\sum \lambda_j)^2}{\sum \lambda_j^2}$

The resulting profile $D(k)$ follows a **universal sigmoid**:

$$D(k) = \frac{A}{1 + e^{-\beta(k - k_0)}}$$

- **A** (Amplitude): Saturation dimensionality — "Dimensional Capacity"
- **k_0** (Midpoint): Scale of organizational transition
- **$\beta$** (Steepness): Rate of transition

### Why This Way

The shift from SFH to D(k) was driven by:
1. **Need for ground truth** — D(k) can be computed on any system
2. **Scale dependence** — different $k$ values probe different organizational scales
3. **Model-free** — participation ratio requires no assumptions about system structure
4. **Cross-domain applicability** — works on neural networks, physics simulations, coupled oscillators

### What It Revealed

- D(k) profiles are **generic** — all systems follow the sigmoid form (Paper 3)
- Growth is generic (minimal assumptions), saturation is system-specific
- **k_0 is the "pure geometric signal"** — driven 53% by intrinsic system curvature vs. 45% by noise (ANOVA $\eta^2$)
- Cross-system correlation: mean $r = 0.898$ across 5 system types
- Residual structure after sigmoid removal carries system-specific information

### Why It Evolved

1. **D(k) profiles were too similar** — $r = 0.89$ correlation meant low discrimination
2. **Sigmoid parameters conflated** — A, k_0, $\beta$ were correlated
3. **No dynamical content** — D(k) is a static snapshot, not a trajectory
4. **K_0 was sensitive to embedding** — representation-dependent

**Lesson learned:** Universal structure is not always informative. System-specific content lives in deviations from universality.

---

## STAGE 3: Kuramoto Synchronization & Critical Scaling
**Period:** Mid-2026 (Phases 250-264)
**Repositories:** `sgp-tribe3/empirical_analysis/neural_networks/`

### Mathematical Framework

The Kuramoto model of coupled phase oscillators:

$$\dot{\theta}_i = \omega_i - \frac{K}{N}\sum_j \sin(\theta_i - \theta_j)$$

**Metrics defined:**

| Metric | Formula | Purpose |
|--------|---------|---------|
| Order Parameter R | $\|\langle e^{i\theta} \rangle\|$ | Global synchronization |
| Metastability | $\text{std}(R)$ over time | Stability of sync |
| PLV | $\|\langle e^{i\Delta\phi} \rangle\|$ | Pairwise phase locking |
| Sync Entropy | $-\sum p \log p$ | Diversity of sync states |
| DNI | Composite | Dynamical network integration |

**8 Kuramoto variants tested:** Standard, Weak, Strong, Delayed, Chimera, Adaptive, Repulsive, Randomized.

**Finite-size scaling:** $R \sim (K - K_c)^\gamma$ across $N = [4, 8, 16, 32, 64, 128]$.

### Why This Way

1. **Kuramoto is the canonical model** for synchronization — well-understood theory
2. **Critical scaling** provides universal exponents — testable predictions
3. **Phase oscillators** are mathematically tractable — exact solutions exist
4. **Connection to neuroscience** — brain synchronization is a central phenomenon

### What It Revealed

- Kuramoto transition confirmed: $\gamma = 1.14$, $R^2 = 0.985$
- Critical point $K_c \approx 1.3 - 1.8$ (topology-dependent)
- Best variant: KuramotoAdaptive (DNI = 1.2410)
- **CDI** (Composite Dispersion Index): $\text{CDI} = \|x\| \cdot \text{Var}(x) \cdot \text{Std}(x)$
- **Dynamical Torsion** $\chi$: From antisymmetric Jacobian $A = (J - J^T)/2$, $\chi = \|A\|_F$
- $\chi$ maintains partial correlation $r = -0.297$ ($p < 10^{-8}$) after controlling for norm

### Why It Evolved

1. **Kuramoto is too simple** — real systems have amplitude dynamics, not just phase
2. **CDI collapsed** under cross-domain testing (P20-HR2: fails for extreme chaos)
3. **Torsion is representation-dependent** — Jacobian estimation requires embedding choices
4. **Critical scaling is system-specific** — $\gamma$ varies across topologies

**Lesson learned:** Simple models reveal universal structure but cannot capture system-specific organization.

---

## STAGE 4: Φ-Space — The 4D Emergence Manifold
**Period:** Late 2026 (V2_060-V2_081)
**Repositories:** `sgp_core_v2/`

### Mathematical Framework

17 complexity measures compressed to 4 axes via PCA:

| Axis | Name | Loading Variables | Variance Explained |
|------|------|-------------------|-------------------|
| C | Coherence | Total correlation, mutual information | 40.7% |
| F | Fluctuation | Variance, entropy, Lyapunov | 16.9% |
| A | Ablation | Ablation sensitivity | 13.3% |
| R | Replay | Temporal correlation | ~10% |

**Participation ratio:** 3.38 (≈ 2 effective DOF)
**MLE dimension:** ≈ 1.5

**Derived objects:**
- **Flow field:** Neighborhood asymmetry on Φ-space — $F(x) = \bar{x}_{\text{forward}} - \bar{x}_{\text{backward}}$
- **Stability tensor:** $4 \times 17$ Jacobian $\partial\Phi/\partial\epsilon$ — perturbation response
- **Geodesic embedding:** Combined Φ-stability metric

### Why This Way

1. **17 metrics were redundant** — PCA revealed latent structure
2. **4 axes are interpretable** — each maps to a distinct organizational property
3. **Flow field provides dynamics** — not just snapshots but trajectories
4. **Stability tensor connects to perturbation theory** — causal structure

### What It Revealed

- Φ-space exists: 4 emergence axes from 17 measures
- Flow field is causal: $r = -0.778$ ($p = 0.001$) — neighborhood asymmetry predicts collapse
- Bridge is a dynamical transition zone (not a category)
- C/F axes respond linearly to perturbation; A/R respond nonlinearly

### Why It Was Abandoned

1. **PCA is linear** — may miss nonlinear structure
2. **17 metrics were from the same pipeline** — observer coupling
3. **Cross-domain generalization FAILED** — all 6 new systems out-of-distribution
4. **Flow field prediction was domain-specific** — $r = -0.778$ did not transfer

**Lesson learned:** Linear dimensionality reduction on pipeline-dependent metrics produces pipeline-dependent geometry.

---

## STAGE 5: The Audit Era — Metric Validation & Invariant Extraction
**Period:** June 2026 (P1-P22, RD-019 through RD-10B)
**Repositories:** `sgp_core_v2/audits/`

### Mathematical Framework

This was not a new mathematical theory but a **systematic interrogation** of all previous mathematics. Key tools:

**Variance Decomposition:**
$$\text{ratio} = \frac{\text{between\_variance}}{\text{within\_variance}}$$

**Metric Coefficient of Variation:**
$$\text{CV} = \frac{\sigma(\text{metric values})}{\mu(\text{metric values})}$$

**Convergence Half-Life:** $N$ at which CV halves (from $1/\sqrt{N}$ scaling)

**Participation Ratio (again):** $PR = 1/\sum(p_i^2)$ for eigenvalue distributions

**Observer Bias Subtraction:**
$$\text{Structure}_{\text{genuine}} = \text{Structure}_{\text{observed}} - \text{Structure}_{\text{observer}}$$

**Invariant Stripping Protocol (P17):**
6 layers of progressive deprivation:
- Layer 0: Full conditions
- Layer 1: Descriptor removal
- Layer 2: Transform minimality
- Layer 3: Observer minimality
- Layer 4: Warning suppression
- Layer 5: Information collapse

### Why This Way

The program had accumulated 136 failures. The audit era was designed to:
1. **Catalog what actually survives** — not what we hope survives
2. **Separate genuine structure from observer artifacts**
3. **Establish minimal invariants** — the smallest set that predicts
4. **Test reconstruction vs. prediction** — can invariants predict new data?

### What It Revealed

**The three strongest surviving findings:**

1. **CV positivity** — CV > 0 always (survives all 6 stripping layers)
2. **Convergence floor** — CV asymptotes above zero (survives all layers)
3. **cv_decreasing** — CV decreases with $N$ for GS/RB/CML (survives all layers)

**Critical corrections:**
- MHD 10× claim was protocol artifact (P6) → corrected to 1.09×
- Most temporal signatures fragile under perturbation (P10)
- Zero organizational invariants across 5 observer pipelines (P15)
- P18 "prediction" was actually reconstruction — failed at zero perturbation (P19)
- CV positivity fails for extreme chaos and agent-based systems (P20-HR2)

**The deepest finding:**
> "Research repeatedly discovers hidden fixed variables" — the most empirically supported law in the archive.

### Why It Mattered

The audit era established **methodological infrastructure** before any theoretical claims. It separated:
- **What we can measure** from **what we claim to measure**
- **What survives perturbation** from **what survives only our pipeline**
- **Reconstruction** from **prediction**

**Lesson learned:** Measurement validation is not optional. Every metric must survive adversarial testing before theoretical use.

---

## STAGE 6: The Well — Cross-Domain Testing
**Period:** June 2026
**Repositories:** `sgp_core_v2/the_well/`

### Mathematical Framework

Same metrics (C, TE, MSE, etc.) applied to 15TB of real PDE simulation data:
- Gray-Scott (reaction-diffusion)
- Rayleigh-Bénard (convection)
- Active Matter (self-propelled particles)
- MHD (magnetohydrodynamics)
- Coupled Map Lattices
- Acoustic Scattering
- Rayleigh-Taylor (3D instability)

**Variance Decomposition:** between/within ratio across trajectories within each system.

### Why This Way

1. **Real physics** — not synthetic or pipeline-dependent
2. **Multiple system classes** — reaction-diffusion, fluid dynamics, plasma, active matter
3. **Known ground truth** — PDE parameters are known
4. **Scale separation** — different systems have different intrinsic scales

### What It Revealed

**Table E — Complete Variance Decomposition:**

| System | Within | Between | Ratio | Mean C |
|--------|--------|---------|-------|--------|
| Gray-Scott | 0.004087 | 0.003936 | 1.04× | 0.161 |
| Rayleigh-Bénard | 0.000015 | 0.000014 | 1.05× | 0.008 |
| Active Matter | 0.000030 | 0.000024 | 1.24× | 0.018 |
| MHD | ≈0 | ≈0 | 1.09× | 0.001 |
| CML | ≈0 | ≈0 | 1.19-6.23× | 0.817 |

**Key findings:**
- Within ≈ between for all systems — convergence behavior is trajectory-independent
- C is 80% reconstructable from MSE ($r = -0.89$) within granular domain
- 3-factor latent structure: Fluidity (40.7%), Perturbation Response (16.9%), Recovery (13.3%)

### Why It Mattered

The Well provided the **first genuine cross-domain validation** — metrics computed on real physics, not synthetic systems. The results were sobering: ratios close to 1× meant that organizational differences between trajectories were small compared to measurement noise.

**Lesson learned:** Real systems have much less organizational structure than synthetic systems suggest.

---

## STAGE 7: The Parallel Director — Mapping Experiments
**Period:** June 2026
**Repositories:** `sgp_core_v2/director_new/mapping_experiment/`

### Mathematical Framework

Three model systems with known ground truth:
- **System A:** Coupled oscillators (moderate coupling)
- **System B:** Coupled oscillators (strong coupling + noise)
- **System C:** Coupled oscillators (weak coupling)

**Six structural metrics:**
1. D_exp — Dimensionality expansion
2. E_closure — Effective closure error
3. F_memory — Memory recovery fidelity
4. R_compression — Compression ratio
5. L_reconstruction — Reconstruction loss
6. S_stability — Stability under perturbation

**Five embedding families** (measurement operators):
1. delay_coordinate — Time-delay embedding
2. pca_projection — Principal component analysis
3. random_projection — Johnson-Lindenstrauss
4. rank_ordering — Monotone transform
5. spectral_embedding — Laplacian eigenmaps

**Transport operators:** Procrustes alignment between metric vectors of consecutive instances.

### Why This Way

1. **Known ground truth** — Systems A/B/C have known differences
2. **Multiple embeddings** — tests representation dependence
3. **Transport operators** — models how measurements transform under composition
4. **Adversarial design** — designed to fail if metrics are artifacts

### What It Revealed (Phases B1-B3g')

- **No embedding-invariant metric exists** (B1): All metrics change under re-embedding
- **Ranking structure is unstable** (B2): $\rho \approx 0.2$ — systems reorder under different embeddings
- **Metric contribution is uniform** (B3m): No single metric dominates — identity gauge artifact
- **Sensitivity suppression exists** (B3r): Some embeddings suppress perturbation sensitivity
- **Metric-collective instability** (B3s): Metrics change collectively, not individually
- **Identity is not neutral** (B3g'): Different reference systems produce different stability rankings
- **Independent residual topology is not significant** (B3ε): $p = 1.0$ — no structure beyond what metrics already capture

### Why It Mattered

The mapping experiments established **admissibility conditions** — what must be true before any measurement can be trusted. The key finding: **no metric is representation-independent**. Every measurement depends on the embedding chosen.

**Lesson learned:** Measurement is not observation. The embedding is part of the measurement.

---

## STAGE 8: The B3Ω Series — Gauge Theory of Covariance Transport
**Period:** June 2026 (Ω.1 through Ω.16)
**Repositories:** `sgp_core_v2/director_new/mapping_experiment/`

### Mathematical Framework

**Transport operators:** $\Gamma_{ij} = \text{Procrustes}(m_i, m_j)$ where $m_i$ are metric vectors.

**Polar decomposition:** $\Gamma = s \cdot R$ where:
- $s = \|\Gamma\|_F / \sqrt{d}$ (scale factor)
- $R = U V^T$ (rotation from SVD of $\Gamma$)

**Gauge normalization:** $\hat{\Gamma} = \Gamma / \|\Gamma\|_F$

**Key quantities:**

| Quantity | Formula | Purpose |
|----------|---------|---------|
| Spectral radius | $\rho(\Gamma) = \max\|\lambda_i\|$ | Expansion/contraction |
| Frobenius norm | $\|\Gamma\|_F$ | Total deformation |
| Condition number | $\kappa = \sigma_{\max}/\sigma_{\min}$ | Anisotropy |
| Closure error | $\|\Gamma_1\Gamma_2\cdots\Gamma_n - I\|$ | Non-commutativity |
| Lyapunov exponents | $\lambda_i = \lim_{n\to\infty} \frac{1}{n}\log\|\Lambda_i^{(n)}\|$ | Long-term growth rates |
| Oseledets exponents | Same as Lyapunov but for multiplicative cocycles | Growth along specific directions |
| Commutator | $[\Gamma_1, \Gamma_2] = \Gamma_1\Gamma_2 - \Gamma_2\Gamma_1$ | Non-commutativity |
| Residual | $r = m_{i+1} - \hat{\Gamma}_i m_i$ | Prediction error under normalized transport |

### The Complete Causal Chain

The Ω-series uncovered a step-by-step mechanism:

1. **Raw-channel magnitude** (structural property): B raw 2.2× A/C
2. **Frobenius norm > √d** (unit-normalization violation): B: 3.18 vs √d = 2.24
3. **Singular values σ > 1** (isotropic scaling): B: 1.42
4. **Spectral radius ρ > 1** (expansive generators): B: 78.9% of observations
5. **Positive Oseledets exponents** (multiplicative-ergodic): B: 5 positive, max 0.24
6. **Observable high-energy residuals** (gauge-induced amplification)
7. **Gauge-invariant alignment structure** (geometric, survives normalization)

### The Final Decomposition

$$\boxed{\Gamma = s \cdot R}$$

| Component | Role | Properties |
|-----------|------|------------|
| $s$ (scale) | Amplification | Universal, removable, governs expansion via $\alpha/\alpha_c$ |
| $R$ (rotation) | Geometry | System-specific, preserves covariance eigenspaces, has curvature |

### Key Results

**Ω.1–Ω.3:** Residual sector has 5 orders of magnitude energy structure. Channel localization is projection artifact (corrected by methodological review).

**Ω.4:** First structurally reliable phase. $\rho$ rank = 3.74. Negative result is valid.

**Ω.5:** Channel concentration — B 73% raw. Operators rank-5, residuals rank-1.

**Ω.6:** Covariance→residual alignment 0.97–0.99. Transport→residual ~0.3.

**Ω.7:** Mode preservation = 1.000. Paradox index B = 4.40. Compression B = 8.19.

**Ω.8:** First true generator: raw-channel +5.49, chain 11.9→1074.6, no conservation.

**Ω.9:** Genuine multiplicative growth confirmed. Eigenvector alignment DECREASES (not locking). Noise/scrambling INCREASES amplification (×3.23). Raw channel essential (suppress → 0.0001×).

**Ω.10:** Non-commutative Lyapunov structure. B commutator = 5.60 (2.9× A). B Lyapunov λ = +0.31 (amplifying). A/C λ < 0 (compressing). Non-normality identical across systems (artifact).

**Ω.11:** Multiplicative-ergodic structure. B: 5 positive Oseledets exponents (max λ = 0.243). A/C: 0 positive. B ρ > 1 for 78.9% of observations. **Expansion NOT channel-specific** — all channels expand equally.

**Ω.12:** Generator-driven expansion. B individual operators have ρ > 1. Single B operator suffices for λ > 0. Covariance feedback ratio = 1.000 (no effect). Commutator-λ correlation = 0 (not predictive). **Source is individual generators, not composition or feedback.**

**Ω.13:** Unit-normalization violation. B $\|\Gamma\|_F/\sqrt{d} = 1.42$ (78.9% > √d). B raw-channel 2.2× larger than A/C. Singular values isotropic (condition = 1). ρ stabilizes at ~1.4 for $n_{\text{inst}} \geq 10$.

**Ω.14:** Scale-gauge bifurcation. Normalized λ → 0 for ALL systems. ALL systems become expansive above critical $\alpha_c$ (A: 1.5, B: 1.0, C: 2.0). **B is not dynamically unique — only pre-threshold elevated.**

**Ω.15:** Gauge-invariant structure exists. Residual alignment IMPROVES after normalization (A: 0.68→0.91, B: 0.73→0.91, C: 0.98→0.99). Mode alignment SURVIVES (0.99→0.99). Pure rotations R: $|\lambda| = 1$, $\lambda_{\text{Lyap}} = 0$ (neutral). **Scale inflation was partially masking underlying geometry.**

**Ω.16:** Covariance eigenspaces are invariant under normalized rotational transport. Systems remain distinguishable after full gauge removal. Rotation space has genuine curvature and holonomy. Scale and geometry carry independent information.

### The Deepest Result

$$\boxed{\text{The instability was never in the transport.}}$$

$$\boxed{\text{Transport remained stable throughout; only observable amplitude became gauge-inflated.}}$$

$$\boxed{\text{Observable residuals are gauge-amplified projections of covariance geometry transported by stable rotational dynamics.}}$$

### Why It Mattered

The Ω-series resolved a paradox that had persisted through 16 phases of the program. The original observation — "stable transport produces unstable observables" — was real but misattributed. The instability was not in the transport dynamics but in the **gauge freedom of measurement amplitude**. After removing this gauge, invariant geometry persists.

This is the program's deepest structural result and its conceptual endpoint.

---

## Summary: The Mathematical Trajectory

| Stage | Framework | Core Object | Key Choice | Outcome |
|-------|-----------|-------------|------------|---------|
| 1 | SFH-SGP Field Theory | Coherence C | Leading eigenvalue of co-activation | Abandoned: arbitrary network |
| 2 | D(k) Multiscale | Participation ratio | Scale-dependent dimensionality | Universal but low discrimination |
| 3 | Kuramoto Synchronization | Order parameter R | Phase oscillator model | Too simple for real systems |
| 4 | Φ-Space Manifold | 4D emergence axes | PCA on 17 metrics | Pipeline-dependent geometry |
| 5 | Audit Era | Invariants | Adversarial validation | 136 failures cataloged |
| 6 | The Well | Variance ratio | Cross-domain PDE testing | Sobering: ratios ≈ 1× |
| 7 | Mapping Experiments | Transport operators | Embedding families | No embedding-invariant metric |
| 8 | Gauge Theory | Γ = sR | Polar decomposition | Paradox resolved |

### The Recurring Pattern

At every stage, the program discovered the same pattern:

1. **Define a mathematical object** (C, D(k), R, Φ, Γ)
2. **Find it works** on the training domain
3. **Test it adversarially** — it partially fails
4. **Discover the failure is informative** — it reveals hidden structure
5. **Refine the mathematics** — decompose the object further
6. **Repeat**

This is not a failure pattern. It is the **scientific method working**. Each failure eliminated a false belief and revealed a deeper truth.

### What NotebookLM Should Critique

1. **The coherence metric C** — is total correlation the right measure, or would mutual information, integrated information (Φ), or causal density be more appropriate?

2. **The D(k) sigmoid** — is the participation ratio the right dimensionality estimator, or would correlation dimension, Lyapunov dimension, or information dimension be more informative?

3. **The Kuramoto model** — is the phase oscillator approximation too restrictive, or would Stuart-Landau, Winfree, or Kuramoto-Sakaguchi models capture more structure?

4. **The Φ-space PCA** — is linear dimensionality reduction appropriate, or would kernel PCA, UMAP, or autoencoders reveal different structure?

5. **The variance decomposition ratio** — is between/within the right comparison, or would effect sizes (Cohen's d), mutual information, or optimal transport be more sensitive?

6. **The Procrustes transport operators** — is rigid alignment the right comparison, or would diffeomorphic registration, Wasserstein distance, or optimal transport be more appropriate?

7. **The gauge decomposition Γ = sR** — is polar decomposition the right factorization, or would QR, LU, or SVD-based factorizations reveal different structure?

8. **The critical scaling exponents** — are finite-size scaling laws the right framework, or would renormalization group flow, conformal field theory, or topological methods be more appropriate?

---

*This document describes the mathematical choices made by the research program. The mathematics should be evaluated on its own merits — internal consistency, empirical adequacy, and predictive power — independent of the philosophical framework in which it was developed.*
