# Results

## Effective Dimensionality Analysis

| System | Nominal Dims | Participation Ratio | Effective Info Dim | Covariance Rank | Stable Rank |
|--------|-------------|-------------------|-------------------|-----------------|-------------|
| Distributed | 6 | 1.0071 | 1.0036 | 2 | 1.0000 |
| Immune | 11 | 1.0166 | 1.0083 | 4 | 1.0000 |
| Ant Colony | 13 | 1.0272 | 1.0136 | 11 | 1.0002 |
| Institution | 11 | 1.0000 | 1.0000 | 7 | 1.0000 |

**Finding:** All embeddings are effectively 1D, despite nominal dimensionalities of 6-13.

## Observable Survival Analysis

| System | G Survival | H Survival | Overall |
|--------|-----------|-----------|---------|
| Distributed | 29.63% | 70.37% | 50.00% |
| Immune | 29.63% | 66.67% | 48.15% |
| Ant Colony | 70.37% | 70.37% | 70.37% |
| Institution | 59.26% | 59.26% | 59.26% |

**Finding:** G is fragile (47% average survival); H is degenerate (saturated at ≈1.0).

## Metric Survival Taxonomy

| Metric | Class | Survival Rate | Notes |
|--------|-------|---------------|-------|
| G | Fragile | 47% | Sector alignment |
| H | Degenerate | 67% | Autocorrelation saturated |
| TE | Conditional | ? | Transport error |
| T | Fragile | ? | Transport instability |

## Stability Envelope

| System | Perturbation Threshold | Corruption Threshold | Dropout Threshold |
|--------|----------------------|---------------------|-------------------|
| Distributed | 0.01 | 0.5 | 0.5 |
| Immune | 0.01 | 1.0 | None |
| Ant Colony | None | 1.0 | None |
| Institution | None | 1.0 | 0.25 |

## Summary

1. All embeddings are effectively 1D (participation ratio ≈ 1.0)
2. G is fragile: survival rate 47% across perturbation types
3. H is degenerate: saturated at ≈1.0 for 3/4 systems
4. The G∝1/H correlation is an artifact of embedding degeneracy
