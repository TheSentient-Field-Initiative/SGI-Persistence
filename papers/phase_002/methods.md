# Methods

## Fiber Bundle Formalism

### Organizational Manifold (M)
The state space of an organization, parameterized by 8 observable metrics:
- Connectivity, active element count, routing entropy, assignment rate, allocation entropy, mean activation, type entropy, efficiency

### Historical Fiber (F)
The residue of an organization's history, computed as normalized deviation from recent history mean.

### Transport Operator (τ)
A morphism mapping fibers between adjacent states along a trajectory, defined by actual fiber residue changes (not connection coefficient exponential maps).

## Geometric Observables

### Transport Error (TE)
$$TE = \frac{1}{n-1} \sum_{i=1}^{n-1} \|f_{i+1} - \tau_i(f_i)\|_F$$

Measures inconsistency between predicted and actual fiber states.

### Replay Transport Coupling (RTC)
$$RTC = \frac{1}{n} \sum_{i=1}^{n} \|f_i\|$$

Measures magnitude of historical residue.

### Transport Instability (T)
$$T = \mathbb{E}[\|\tau_{\gamma_1}(f) - \tau_{\gamma_2}(f)\|]$$

Expected divergence of replay outcomes under different transport paths.

### Discrete Holonomy
$$h = \left\|\tau_{\gamma}^{-1} \circ \tau_{\gamma}(f) - f\right\|$$

Failure of transport loops to return fibers to initial state.

## Experimental Protocol

### Systems
- Distributed: 100 nodes, heterogeneous workloads, shortest-path routing
- Immune: 100 cells, cytokine signaling, receptor-based coordination
- Ant Colony: 50 ants, 100 food sources, pheromone stigmergy
- Institution: 100 agents, trust-based coordination

### Perturbation Protocols
- Temporal: replay delay, asynchronous replay, memory truncation, replay scrambling
- Structural: node deletion, sector duplication, routing mutation, topology rewiring
- Gauge: basis rotation, nonlinear normalization, random projection, coordinate compression
- Historical: memory overwrite, residue injection, replay branch insertion, counterfactual replay

### Reproducibility
- Deterministic seeds (seed=42)
- 50 timesteps per simulation
- 50 timesteps of recovery measurement
- JSON result exports
