# SGI Operational Research Template

## System Definition

Every experiment must specify:

1. **System class**: distributed | immune | ant_colony | institution
2. **State space**: Observable metrics and their ranges
3. **Persistence object**: What organizational structure is being tracked
4. **Perturbation protocol**: What threatens the persistence object
5. **Measurement protocol**: How persistence is quantified

## Measurement Framework

### Tier 1: Interaction Persistence
- Active element counts
- Connectivity measures
- Assignment/allocation rates

### Tier 2: Organizational Stability
- Transport error (fiber consistency)
- Replay transport coupling (fiber entanglement)
- Transport instability (path dependence)

### Tier 3: Geometric Structure
- Discrete holonomy (loop nonclosure)
- Transport noncommutativity
- Category commutativity fraction

## Representation Audit

Every reported metric must pass:

1. **Normalization survival**: Does the metric survive z-score normalization?
2. **Gauge covariance**: Does the metric behave predictably under basis rotation?
3. **Embedding independence**: Does the metric depend on the specific state-space embedding?
4. **Segmentation independence**: Does the metric depend on how the system is partitioned?

## Falsification Protocol

Every hypothesis must declare pre-registered failure conditions:

- F1: Metric disappears after normalization (scale artifact)
- F2: Metric varies wildly across embeddings (representation-dependent)
- F3: Metric only appears under one segmentation (observer-conditioned)
- F4: Recovery trajectories fail replication (non-transportable)

## Reporting Mandate

- Separate Transportable Sector from Residual Sector
- Never report "method A performs better" without specifying what was preserved
- Document all information destroyed by each measurement
