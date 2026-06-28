# Canonical Metrics Definition

**Single citation source for all manuscripts.**

Version: 0.2.0 | Last updated: 2026-06-28

---

## G — Organizational Replay Stability

**Symbolic definition:**

$$G = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}[\text{replay}(s_i) \approx s_i]$$

**Implementation:** `src/systems/*/study_*.py` — fraction of organizational states reproducible through replay.

**Units/domain:** [0, 1]. Dimensionless.

**Interpretation:** Measures how faithfully an organization can reproduce its states through its own generative process. High G indicates robust persistence.

**Failure modes:** Saturates at ceiling when scalar observables collapse (Phase 001N).

---

## H — Historical Residue Coupling

**Symbolic definition:**

$$H = \text{corr}\left(\{s_t\}, \{\bar{s}_{t-k:t}\}\right)$$

**Implementation:** `src/geometry/connection_formalism.py:build_bundle()` — correlation between current state and trajectory of historical states.

**Units/domain:** [-1, 1]. Dimensionless.

**Interpretation:** Measures how strongly an organization's current state depends on its history. High H indicates strong historical coupling.

**Failure modes:** May be confounded with autocorrelation in slowly varying systems.

---

## T — Transport Instability

**Symbolic definition:**

$$T = \mathbb{E}_{\gamma_1, \gamma_2} \left[ \|\tau_{\gamma_1}(f) - \tau_{\gamma_2}(f)\| \right]$$

**Implementation:** `src/geometry/discrete_transport.py:DiscreteTransportAlgebra.compute_transport_path_divergence()`

**Units/domain:** [0, ∞). Norm of fiber difference.

**Interpretation:** Expected divergence of replay outcomes under different transport paths. High T indicates path-dependent replay.

**Failure modes:** Currently = 0 for ant_colony and institution (no transport structure). Explodes to 10^10 for immune under perturbation (fragility artifact).

---

## TE — Transport Error

**Symbolic definition:**

$$TE = \frac{1}{n-1} \sum_{i=1}^{n-1} \|f_{i+1} - \tau_i(f_i)\|_F$$

**Implementation:** `src/geometry/connection_formalism.py:ConnectionOperator.compute_transport_error()`

**Units/domain:** [0, ∞). Frobenius norm.

**Interpretation:** Inconsistency between predicted and actual fiber states along a trajectory. High TE indicates poor fiber predictability.

**Failure modes:** Depends on transport operator definition. Currently = 0 for ant_colony and institution.

---

## RTC — Replay Transport Coupling

**Symbolic definition:**

$$RTC = \frac{1}{n} \sum_{i=1}^{n} \|f_i\|$$

**Implementation:** `src/geometry/connection_formalism.py:HistoricalFiber.entanglement()`

**Units/domain:** [0, ∞). Norm of fiber residue.

**Interpretation:** Magnitude of historical residue. High RTC indicates strong historical memory.

**Failure modes:** May be confounded with state magnitude. Normalization-dependent.

---

## Holonomy — Replay Loop Nonclosure

**Symbolic definition:**

$$h = \left\|\tau_{\gamma}^{-1} \circ \tau_{\gamma}(f) - f\right\|$$

**Implementation:** `src/geometry/discrete_transport.py:DiscreteHolonomy.compute_loop_holonomy()`

**Units/domain:** [0, ∞). Norm of closure error.

**Interpretation:** Failure of transport loops to return fibers to initial state. Non-zero holonomy indicates path-dependent geometry.

**Failure modes:** Currently = 0 for all systems with current transport model. Numerically unstable.

---

## Curvature — Curvature Magnitude

**Symbolic definition:**

$$\|R\| = \left\| \partial_k \Gamma^i_{jl} - \partial_l \Gamma^i_{jk} + \Gamma^i_{mk} \Gamma^m_{jl} - \Gamma^i_{ml} \Gamma^m_{jk} \right\|_F$$

**Implementation:** `src/geometry/connection_formalism.py:CurvatureTensor.curvature_magnitude()`

**Units/domain:** [0, ∞). Frobenius norm.

**Interpretation:** Noncommutativity of parallel transport. Non-zero curvature indicates non-trivial geometry.

**Failure modes:** Currently ≈ O(1e-3) due to coordinate artifact. Not physically meaningful with current model.

---

## Ricci Scalar

**Symbolic definition:**

$$R = g^{jl} R_{jl} = g^{jl} R^i_{jil}$$

**Implementation:** `src/geometry/connection_formalism.py:CurvatureTensor.ricci_scalar()`

**Units/domain:** ℝ. Real number.

**Interpretation:** Scalar curvature of organizational manifold. Positive = sphere-like, negative = hyperbolic.

**Failure modes:** Currently ≈ 0 due to flat manifold embedding.

---

## Noncommutativity — Relative Noncommutativity

**Symbolic definition:**

$$\text{NC} = \frac{\|[\tau_a, \tau_b]\|}{\|\tau_a\| \cdot \|\tau_b\|}$$

**Implementation:** `src/geometry/discrete_transport.py:DiscreteTransportAlgebra.compute_noncommutativity()`

**Units/domain:** [0, ∞). Dimensionless ratio.

**Interpretation:** Degree to which transport operators fail to commute. Non-zero NC indicates path ordering matters.

**Failure modes:** Currently = 0 for all systems. Transport model does not produce noncommutativity.

---

## Replay Divergence

**Symbolic definition:**

$$RD = \mathbb{E}_{\pi} \left[ \|f_{\pi} - f_{\text{canonical}}\| \right]$$

**Implementation:** `src/geometry/discrete_transport.py:TransportCanonicalization.compute_replay_divergence()`

**Units/domain:** [0, ∞). Norm of fiber difference.

**Interpretation:** How different are transport outcomes from different replay orderings.

**Failure modes:** Depends on canonical ordering definition.

---

## Torsion — Fiber Torsion

**Symbolic definition:**

$$\tau = \|f - \text{proj}_{\text{basis}}(f)\|$$

**Implementation:** `src/geometry/connection_formalism.py:FiberTwist.compute_fiber_torsion()`

**Units/domain:** [0, ∞). Norm of out-of-plane component.

**Interpretation:** How much the fiber twists relative to its basis.

**Failure modes:** Basis-dependent. May be artifact of QR orthogonalization.
