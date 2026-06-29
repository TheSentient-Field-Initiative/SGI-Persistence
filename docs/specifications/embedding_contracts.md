# Embedding Contracts

**Status:** LOCKED — Effective upon verification  
**Authority:** Research Director Directive (Phase 003B)  
**Purpose:** Define system-specific embedding functions that replace the generic `state_to_vector`

---

## Design Principles

1. **No shared generic embedding.** Each system has its own embedding function.
2. **Explicit semantic mapping.** Each dimension has a documented meaning.
3. **Z-score normalization.** Preserves relative scale (no unit normalization).
4. **Documented ranges.** Expected value ranges for each dimension.
5. **Failure conditions.** Clear criteria for when embedding is invalid.

---

## Distributed System Embedding

**File:** `src/embeddings/distributed_embedding.py`

### Dimensions

| Dim | Name | Semantic Meaning | Range |
|-----|------|-----------------|-------|
| 0 | connectivity | Graph connectivity (largest component / n_active) | [0, 1] |
| 1 | n_active | Number of active nodes | [0, 100] |
| 2 | routing_entropy | Routing diversity (Shannon entropy) | [0, 7] |
| 3 | assignment_rate | Task assignment rate | [0, 1] |
| 4 | allocation_entropy | Task allocation diversity | [0, 5] |
| 5 | n_components | Connected components | [1, 50] |
| 6 | timestep | Simulation time | [0, 100] |
| 7 | reserved | Reserved for future use | [0, 0] |

### Normalization

Z-score per dimension using reference values:
- Mean: [0.85, 95.0, 1.2, 0.3, 1.5, 3.0, 25.0, 0.0]
- Std: [0.1, 5.0, 0.5, 0.1, 0.5, 2.0, 15.0, 1.0]

Clipped to [-3, 3] standard deviations.

### Failure Conditions

- Missing keys in state dictionary
- Non-numeric values
- All dimensions near zero

---

## Immune System Embedding

**File:** `src/embeddings/immune_embedding.py`

### Dimensions

| Dim | Name | Semantic Meaning | Range |
|-----|------|-----------------|-------|
| 0 | signaling_connectivity | Signaling network connectivity | [0, 1] |
| 1 | n_active | Number of active cells | [0, 100] |
| 2 | type_entropy | Cell type diversity (Shannon entropy) | [0, 3] |
| 3 | mean_activation | Mean activation level | [0, 1] |
| 4 | total_cytokines | Total cytokine concentration | [0, 500] |
| 5 | n_components | Signaling components | [1, 50] |
| 6 | cov_trace | Covariance trace (interaction intensity) | [0, 100] |
| 7 | non_principal | Non-principal eigenvalue (residual structure) | [0, 50] |

### Normalization

Z-score per dimension using reference values:
- Mean: [0.75, 80.0, 1.5, 0.4, 200.0, 5.0, 30.0, 10.0]
- Std: [0.15, 15.0, 0.5, 0.2, 100.0, 3.0, 15.0, 5.0]

Clipped to [-3, 3] standard deviations.

### Failure Conditions

- Missing keys in state dictionary
- Non-numeric values
- All dimensions near zero

---

## Ant Colony Embedding

**File:** `src/embeddings/ant_embedding.py`

### Dimensions

| Dim | Name | Semantic Meaning | Range |
|-----|------|-----------------|-------|
| 0 | trail_connectivity | Pheromone trail connectivity | [0, 1] |
| 1 | total_pheromone | Total pheromone concentration | [0, 100] |
| 2 | recruitment_rate | Ant recruitment rate | [0, 1] |
| 3 | path_redundancy | Path redundancy (alternative routes) | [0, 1] |
| 4 | n_components | Trail components | [1, 20] |
| 5 | cov_trace | Covariance trace (interaction intensity) | [0, 50] |
| 6 | anisotropy | Trail anisotropy (directional bias) | [0, 1] |
| 7 | non_principal | Non-principal eigenvalue (residual structure) | [0, 20] |

### Normalization

Z-score per dimension using reference values:
- Mean: [0.6, 50.0, 0.4, 0.5, 5.0, 20.0, 0.3, 8.0]
- Std: [0.2, 20.0, 0.2, 0.2, 3.0, 10.0, 0.15, 4.0]

Clipped to [-3, 3] standard deviations.

### Failure Conditions

- Missing keys in state dictionary
- Non-numeric values
- All dimensions near zero

---

## Institution Embedding

**File:** `src/embeddings/institution_embedding.py`

### Dimensions

| Dim | Name | Semantic Meaning | Range |
|-----|------|-----------------|-------|
| 0 | network_connectivity | Trust network connectivity | [0, 1] |
| 1 | mean_trust | Mean trust level | [0, 1] |
| 2 | cooperation_rate | Cooperation rate | [0, 1] |
| 3 | strategy_entropy | Strategy diversity (Shannon entropy) | [0, 3] |
| 4 | mean_payoff | Mean payoff | [0, 10] |
| 5 | n_components | Network components | [1, 50] |
| 6 | cov_trace | Covariance trace (interaction intensity) | [0, 50] |
| 7 | non_principal | Non-principal eigenvalue (residual structure) | [0, 20] |

### Normalization

Z-score per dimension using reference values:
- Mean: [0.7, 0.5, 0.4, 1.2, 3.0, 5.0, 15.0, 6.0]
- Std: [0.15, 0.2, 0.2, 0.5, 1.5, 3.0, 8.0, 3.0]

Clipped to [-3, 3] standard deviations.

### Failure Conditions

- Missing keys in state dictionary
- Non-numeric values
- All dimensions near zero

---

## Cross-System Comparability

**CRITICAL:** Embeddings from different systems are NOT directly comparable. Each system has:
- Different semantic meanings for each dimension
- Different reference ranges
- Different normalization parameters

Comparisons must be made using:
1. Sector alignment (G computation) — uses raw metrics, not embeddings
2. Transport error (TE) — uses system-specific embeddings within a single system
3. Autocorrelation (H) — uses system-specific embeddings within a single system

**NEVER compare embedding vectors across systems.**

---

## Amendment Process

Any change to embedding contracts requires:

1. Explicit documentation of the change
2. Version bump (major version for breaking changes)
3. Re-running all validation experiments with new embeddings
4. Research Director approval
