# Results

## Observed G ∝ 1/H Correlation

| System | G | H | G × H |
|--------|------|------|-------|
| Distributed | 0.250 | 0.396 | 0.099 |
| Ant Colony | 0.125 | 0.576 | 0.072 |
| Institution | 0.250 | 0.497 | 0.124 |
| Immune | 0.875 | 0.180 | 0.158 |

Cross-domain correlation: r = −0.951 (95% CI [−0.998, −0.080], permutation p < 0.001, N = 4)

**Note:** This correlation is provisional and based on 4 curated systems. The synthetic ensemble test (100 randomized systems) did not reproduce the relation (r = -0.012), suggesting it may reflect shared architectural features of the curated systems rather than a universal law.

## Stability Envelope

| System | Perturbation Threshold | Corruption Threshold | Dropout Threshold |
|--------|----------------------|---------------------|-------------------|
| Distributed | 0.01 | 0.5 | 0.5 |
| Immune | 0.01 | 1.0 | None |
| Ant Colony | None | 1.0 | None |
| Institution | None | 1.0 | 0.25 |

## Representation Ceiling

Starting at Study 001N, scalar observables saturated — distinct systems collapsed to identical values. This ceiling motivated the transition to geometric analysis in Phase 002.

## Perturbation Response

| System | Recovery Time | Persistence Half-Life | Oscillation |
|--------|--------------|----------------------|-------------|
| Distributed | 5-15 steps | 8-12 steps | Low |
| Immune | 10-25 steps | 12-20 steps | Moderate |
| Ant Colony | 3-8 steps | 5-10 steps | Low |
| Institution | 5-12 steps | 8-15 steps | Low |

## Summary

1. Observed G ∝ 1/H correlation across four curated system classes (r = -0.951, provisional)
2. Stability envelope characterizes embedding perturbation tolerance
3. Representation ceiling discovered at scalar level
4. Transport geometry needed for further differentiation
