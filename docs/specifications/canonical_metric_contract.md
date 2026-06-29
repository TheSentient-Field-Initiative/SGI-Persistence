# Canonical Metric Contract

**Status:** LOCKED — Effective upon verification  
**Authority:** Research Director Directive (Phase 003 corrective)  
**Immutable until:** External replication or synthetic ensemble resolution

---

## Purpose

This document defines the唯一 authoritative operationalizations of G and H. Any future computation that deviates from this contract MUST use a new metric name. No silent substitutions allowed.

---

## G (Replay Stability)

### Definition

G measures the fraction of organizational sectors that maintain structural alignment between a pre-perturbation baseline and a post-perturbation recovery trajectory.

### Procedure

1. **System instantiation:** Create system with canonical parameters (see per-system specifications below)
2. **Baseline collection:** Run system for `n_baseline` steps, recording sector metrics at each step
3. **Perturbation:** Apply canonical perturbation (system-specific, see below)
4. **Recovery collection:** Run system for `n_recovery` steps, recording sector metrics at each step
5. **Sector alignment:** For each sector, compute alignment between baseline and recovery trajectories
6. **G computation:** G = (number of surviving sectors) / (total sectors)

### Sector Alignment Criterion

For each sector with metrics `m_1, ..., m_k`:

1. Construct matrices `B` (baseline) and `A` (recovery), each column = one metric's time series
2. Truncate to `min(len(B), len(A))` rows
3. Compute raw cosine similarity: `raw = cos(B, A)`
4. Compute normalized cosine similarity:
   - `B_norm = (B - mean(B)) / (std(B) + 1e-8)`
   - `A_norm = (A - mean(A)) / (std(A) + 1e-8)`
   - `norm = cos(B_norm, A_norm)`
5. Sector survives if `norm - raw > -0.1`

### Threshold

The survival threshold is `norm - raw > -0.1`. This is NOT configurable.

### Averaging

G = (number of sectors where verdict = 'SURVIVES') / (total number of sectors)

No weighting. No smoothing. Simple fraction.

### Valid Domains

G is valid ONLY for systems with explicitly defined sector structures. The sector definitions are system-specific, NOT universal.

### Invalid Uses

- Comparing G across different system types (different sector definitions)
- Using G as a continuous metric (it is discrete: 0, 0.25, 0.5, 0.75, 1.0 for 4-sector systems)
- Inferring "degree of persistence" from G values (G measures sector count, not alignment strength)

### Canonical Sector Definitions

#### Immune System (study_001i_entanglement.py — IMMUNE-SPECIFIC)

```python
SECTORS = {
    'amplitude': ['mean_act', 'total_cyto', 'n_active'],
    'topology': ['connectivity', 'n_comp', 'largest', 'type_entropy'],
    'transport': ['cov_trace', 'cov_condition'],
    'residual': ['non_principal', 'signaling_noise'],
}
```

Perturbation: `net.inject_pathogen(0.5)`  
Baseline: 20 steps  
Recovery: 50 steps  
System: `ImmuneNet(100, seed, memory_depth, feedback_gain)`

#### Ant Colony (study_001b_colony.py)

```python
SECTORS = {
    'amplitude': ['total_food_remaining', 'total_pheromone', 'recruitment_rate'],
    'topology': ['trail_connectivity', 'n_components', 'path_redundancy', 'largest_component'],
    'transport': ['cov_trace', 'cov_condition', 'anisotropy'],
    'residual': ['residual_deviation', 'residual_energy', 'non_principal'],
}
```

#### Institution (study_001d_institution.py)

```python
SECTORS = {
    'amplitude': ['cooperation_rate', 'mean_payoff', 'mean_trust'],
    'topology': ['network_connectivity', 'n_components', 'largest_component', 'strategy_entropy'],
    'transport': ['cov_trace', 'cov_condition'],
    'residual': ['norm_deviation', 'non_principal'],
}
```

#### Distributed System (study_001.py)

```python
SECTORS = {
    'amplitude': ['n_active', 'connectivity'],
    'topology': ['routing_entropy', 'n_components'],
    'transport': ['cov_trace', 'cov_condition'],
    'residual': ['allocation_entropy'],
}
```

**CRITICAL:** The synthetic ensemble and reproduction package used GENERIC sector definitions that do NOT match any real system. This is the source of the metric identity collapse.

---

## H (Historical Entanglement / Historical Residue Coupling)

### Definition

H measures the autocorrelation of state vectors across time, capturing how strongly the system's current state depends on its recent history.

### Procedure

1. **Trajectory collection:** Collect trajectory of `n` steps
2. **Vector conversion:** Convert each state to 8-dimensional vector using `state_to_vector`
3. **Autocorrelation:** For lags 1 to `min(5, n-1)`:
   - Compute Pearson correlation between `vectors[lag:]` and `vectors[:-lag]`
   - Take absolute value
4. **H computation:** H = mean of absolute correlations across lags

### Normalization

- Vectors are normalized by max absolute value (handled by `state_to_vector`)
- Correlations are absolute values (direction-independent)

### Memory Window

Lags 1 through `min(5, n-1)`. No configurability.

### Stationarity Assumption

H assumes the trajectory is approximately stationary. Non-stationary trajectories (e.g., during perturbation recovery) should NOT be used for H computation.

### What H Is

H is a measure of **temporal persistence** — how correlated the system's state is with its own recent history. Higher H means the system's state is more predictable from its past.

### What H Is NOT

- H is NOT "historical entanglement" in the quantum sense
- H is NOT "replay residue" (that is G's domain)
- H is NOT "hysteresis" (that requires explicit perturbation-recovery)
- H is NOT "coupling persistence" (that requires multi-system interaction)

### Valid Domains

H is valid for any trajectory of states that can be converted to 8-dimensional vectors. However, H values are only meaningful when compared across systems using the SAME `state_to_vector` mapping.

### Invalid Uses

- Comparing H across systems with different `state_to_vector` key mappings
- Using H as a measure of "how entangled" the system is (H measures temporal correlation, not entanglement)
- Using H to predict G (the correlation is provisional and system-dependent)

---

## TE (Transport Error)

### Status: PROVISIONAL-VALID

TE measures the inconsistency of the connection operator between adjacent fibers in the organizational bundle.

### Definition

TE = mean of `connection.compute_transport_error(fibers[i], fibers[i+1])` across all adjacent fiber pairs.

### Valid Domains

TE is valid for systems where `build_bundle` produces meaningful fibers. Systems where `state_to_vector` returns near-zero vectors will produce degenerate TE values.

---

## T (Transport Instability)

### Status: EXPERIMENTAL

T measures the sensitivity of transport error to structural perturbations.

### Definition

T = ratio of TE under perturbation to TE under baseline.

### Known Issues

- T explodes for immune system under structural perturbation (T → 10^10)
- T = 0 for systems with no transport structure (ant_colony, institution)
- T is NOT comparable across systems

---

## Holonomy

### Status: UNRESOLVED

Holonomy measures the failure of parallel transport to return to the starting fiber after traversing a loop.

### Known Issues

- Holonomy = 0 for all 4 canonical systems (flat manifold)
- Numerically unstable due to transport definition ambiguity
- Noncommutativity = 0 (no loop-order dependence)

### Conclusion

Holonomy is NOT a valid observable in the current framework. It may become valid if a non-flat connection is discovered.

---

## Curvature

### Status: UNRESOLVED

Curvature measures the local deviation from flatness in the connection.

### Known Issues

- Curvature ≈ 0 for all 4 canonical systems
- Numerically unstable (finite-difference on flat manifold)
- May be a coordinate artifact

### Conclusion

Curvature is NOT a valid observable in the current framework.

---

## State Vector Conversion

### `state_to_vector` Contract

Converts a simulation state dictionary to a fixed 8-dimensional normalized vector.

### Canonical Key Mapping

| Dimension | Canonical Key | Acceptable Aliases |
|-----------|--------------|-------------------|
| 0 | connectivity | signaling_connectivity, trail_connectivity, network_connectivity |
| 1 | n_active | — |
| 2 | routing_entropy | type_entropy, strategy_entropy |
| 3 | assignment_rate | recruitment_rate, cooperation_rate |
| 4 | allocation_entropy | path_redundancy |
| 5 | mean_activation | mean_trust, total_pheromone |
| 6 | n_components | largest_component |
| 7 | efficiency | mean_payoff |

### Normalization

Vector is divided by max absolute value, then clipped to [-1, 1].

### Known Failure Modes

1. **Coordinate domination:** When one coordinate (e.g., n_active) dominates, normalization compresses all other coordinates to near-zero
2. **Cross-domain semantic mismatch:** Different systems emit incomparable observables mapped to the same dimension
3. **Low manifold dimensionality:** 8D embedding may be insufficient for some systems

---

## Amendment Process

Any change to this contract requires:

1. Explicit documentation of the change
2. Version bump (major version for breaking changes)
3. Re-running all validation experiments with new definitions
4. Research Director approval

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-28 | Initial locked contract |
