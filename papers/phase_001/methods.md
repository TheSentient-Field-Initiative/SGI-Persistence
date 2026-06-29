# Methods

## System Classes

### Distributed Coordination Network
- 100 nodes with heterogeneous workloads (stateless, stateful, queue, storage)
- Shortest-path routing with workload-aware task assignment
- Perturbations: node removal, communication delay, resource starvation, scheduler distortion

### Immune Signaling Network
- 100 cells (macrophages, T cells, B cells, dendritic cells)
- Cytokine-mediated coordination with receptor-based signal processing
- Perturbations: pathogen attack, immunosuppression, cell depletion, receptor blockade

### Ant Colony Stigmergy
- 50 ants, 100 food sources
- Pheromone-based stigmergic coordination
- Perturbations: pheromone evaporation, trail disruption, food depletion

### Institutional Trust Network
- 100 agents with trust-based coordination
- Reputation-mediated cooperation
- Perturbations: trust erosion, reputation noise, agent turnover

## Metrics

### Organizational Replay Stability (G)
Fraction of organizational states that can be reproduced through replay of the generative process.

**Canonical Implementation:** `src/metrics/contracts.py` → `compute_G()`
**Sector Definitions:** System-specific (see `docs/specifications/canonical_metric_contract.md`)

### Historical Residue Coupling (H)
Correlation between current organizational state and the trajectory of historical states.

**Canonical Implementation:** `src/metrics/contracts.py` → `compute_H()`
**Embedding:** System-specific z-score normalized embeddings (see `src/embeddings/`)

### Transport Error
Frobenius norm of the difference between fiber states at adjacent points along a trajectory.

**Canonical Implementation:** `src/metrics/contracts.py` → `compute_TE()`

### Fiber Entanglement (Replay Transport Coupling)
Magnitude of the historical fiber residue vector.

## Experimental Protocol

All experiments use:
- 50 timesteps per simulation
- Deterministic seeds (seed=42)
- 4 perturbation protocols per system class
- 50 timesteps of recovery measurement
- Canonical metric contracts (see `docs/specifications/canonical_metric_contract.md`)
- System-specific embeddings (see `src/embeddings/`)

## Reproducibility

All experiments are reproducible via:
- `make deterministic` (deterministic replay with fixed seeds)
- `make hash` (artifact verification)
- External review package (see `reproduction/external_review/`)
