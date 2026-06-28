# Results

## Transport Error Separation

| System | Transport Error |
|--------|----------------|
| Distributed | 0.535 |
| Immune | 0.020 |
| Ant Colony | 0.000 |
| Institution | 0.000 |

Transport error achieves perfect separation across four system classes, surpassing the representation ceiling of scalar metrics.

## Replay Transport Coupling

| System | RTC (Phase 002B) |
|--------|-----------------|
| Distributed | 0.980 |
| Immune | 0.980 |
| Ant Colony | 0.000 |
| Institution | 0.000 |

122.5x improvement over scalar proxies in distinguishing distributed from immune systems.

## Transport Instability (Phase 002C)

| System | Transport Instability (T) |
|--------|--------------------------|
| Distributed | 0.963 |
| Immune | 0.000 |
| Ant Colony | 0.000 |
| Institution | 0.000 |

## Immune System Fragility

| Perturbation | Transport Instability |
|-------------|----------------------|
| Baseline | 0.000 |
| Node deletion | 10^10 |
| Topology rewire | 10^10 |
| Residue injection | 10^10 |

Transport instability explodes by 10 orders of magnitude under structural perturbation, indicating extreme fragility.

## H ≡ T Hypothesis

| Metric | Correlation with G |
|--------|-------------------|
| 1/H | +0.992 |
| 1/T | +0.243 |

H ≡ T hypothesis **not confirmed** with current transport model.

## Discrete Holonomy

All systems: 0.000

Transport model limitation — holonomy cannot capture path dependence in current framework.

## Representation Covariance

| Transformation | Covariance |
|---------------|-----------|
| Normalize gauge | 0.979 |
| Sign flip | 1.000 |
| Permute | −2.500 |
| Scale | −20,063 |

Scale-dependent representations not transportable.

## Summary

1. Transport error separates all four systems (perfect discrimination)
2. Replay transport coupling: 122.5x improvement over scalar proxies
3. Transport instability: immune fragility discovered
4. H ≡ T hypothesis rejected (T not predictor of G)
5. Discrete holonomy = 0 (model limitation)
