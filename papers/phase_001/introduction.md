# Introduction

## Background

Adaptive systems — biological, social, and engineered — must balance stability with adaptability. Measuring this balance requires metrics that capture organizational persistence. However, the identifiability of such metrics depends critically on the representational choices made during measurement.

## Problem Statement

When do replay-stability metrics remain identifiable across representational transformations? Specifically:

1. How does embedding dimensionality affect metric values?
2. Which metrics survive representational changes?
3. What are the necessary and sufficient conditions for metric identifiability?

## Contributions

1. **Effective dimensionality analysis**: All four system embeddings are effectively 1D (participation ratio ≈ 1.0), despite nominal dimensionalities of 6-13
2. **Observable survival analysis**: G survives 47% of perturbation types; H is degenerate (saturated at ≈1.0)
3. **Metric Survival Taxonomy**: Classification of observables as Stable, Conditional, Fragile, or Degenerate
4. **Representation dependence**: The previously reported G∝1/H correlation is an artifact of embedding degeneracy

## Limitations

1. **Embedding degeneracy**: All embeddings are effectively 1D
2. **H saturation**: H≈1.0 for 3/4 systems, making it non-identifiable
3. **G fragility**: G collapses under mild perturbation (noise > 0.01)
4. **System specificity**: Results based on 4 curated systems

## Paper Organization

Section 2 describes the four system classes. Section 3 defines the persistence metrics. Section 4 presents the effective dimensionality analysis. Section 5 presents the observable survival analysis. Section 6 introduces the Metric Survival Taxonomy. Section 7 discusses implications and limitations.
