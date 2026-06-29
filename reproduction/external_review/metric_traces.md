# Metric Traces

This document traces the computation of each metric through the codebase.

---

## G (Replay Stability)

### Canonical Implementation

**File:** `src/metrics/contracts.py` → `compute_G()`

**Procedure:**
1. Split trajectory at midpoint (or explicit perturbation index)
2. For each sector in sector_definition:
   a. Extract metric vectors from before/after
   b. Compute raw cosine similarity
   c. Compute normalized cosine similarity
   d. Sector survives if `norm - raw > -0.1`
3. G = surviving sectors / total sectors

**Sector Definitions (system-specific):**
- Distributed: `{'amplitude': ['n_active', 'connectivity'], 'topology': ['routing_entropy', 'n_components']}`
- Immune: `{'amplitude': ['mean_activation', 'n_active'], 'topology': ['signaling_connectivity', 'type_entropy']}`
- Ant Colony: `{'amplitude': ['total_pheromone', 'recruitment_rate'], 'topology': ['trail_connectivity', 'path_redundancy']}`
- Institution: `{'amplitude': ['cooperation_rate', 'mean_trust'], 'topology': ['network_connectivity', 'strategy_entropy']}`

**Known Drift Locations:**
- `experiments/validation/synthetic_ensemble.py` — uses wrong sectors
- `reproduction/minimal_demo/reproduce.py` — uses wrong sectors

---

## H (Historical Residue Coupling)

### Canonical Implementation

**File:** `src/metrics/contracts.py` → `compute_H()`

**Procedure:**
1. Convert trajectory to vectors using `state_to_vector`
2. Check for degenerate vectors (all-zero, coordinate domination)
3. Compute autocorrelation at lags 1-5
4. H = mean of absolute correlations

**Known Drift Locations:**
- `experiments/validation/synthetic_ensemble.py` — uses autocorrelation (correct method, but broken state_to_vector)

---

## TE (Transport Error)

### Canonical Implementation

**File:** `src/metrics/contracts.py` → `compute_TE()`

**Procedure:**
1. Build organizational bundle using `build_bundle()`
2. Compute transport error between adjacent fibers
3. TE = mean transport error

**Dependencies:** Requires working `state_to_vector` (currently broken for cross-system use)

---

## state_to_vector (Generic — BROKEN)

### Current Implementation

**File:** `src/geometry/connection_formalism.py` → `state_to_vector()`

**Status:** BROKEN — coordinate domination (89.9-99.4% of magnitude in one coordinate)

**Replacement:** System-specific embeddings in `src/embeddings/`

---

## System-Specific Embeddings (NEW)

### Distributed

**File:** `src/embeddings/distributed_embedding.py`

**Dimensions:** connectivity, n_active, routing_entropy, assignment_rate, allocation_entropy, n_components, timestep, reserved

**Normalization:** Z-score per dimension

### Immune

**File:** `src/embeddings/immune_embedding.py`

**Dimensions:** signaling_connectivity, n_active, type_entropy, mean_activation, total_cytokines, n_components, cov_trace, non_principal

**Normalization:** Z-score per dimension

### Ant Colony

**File:** `src/embeddings/ant_embedding.py`

**Dimensions:** trail_connectivity, total_pheromone, recruitment_rate, path_redundancy, n_components, cov_trace, anisotropy, non_principal

**Normalization:** Z-score per dimension

### Institution

**File:** `src/embeddings/institution_embedding.py`

**Dimensions:** network_connectivity, mean_trust, cooperation_rate, strategy_entropy, mean_payoff, n_components, cov_trace, non_principal

**Normalization:** Z-score per dimension
