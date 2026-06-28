# Canonical Terminology

This document freezes the canonical terminology for the SGI Persistence Program.

**No synonym drift is permitted.** Use only these names.

## Core Concepts

| Canonical Name | Definition | Deprecated Synonyms |
|---------------|------------|-------------------|
| **Organizational replay stability** | The degree to which an organizational state can be reproduced through replay of its generative process | Gauge stability, gauge invariance |
| **Historical residue coupling** | The measurable correlation between an organization's current state and its historical trajectory | Historical entanglement, H |
| **Replay transport coupling** | The correlation between fiber states in the organizational bundle | Fiber entanglement |
| **Transport instability** | The expected divergence of replay outcomes under different transport paths: T = E[∥τ_γ₁(f) − τ_γ₂(f)∥] | T |
| **Replay loop nonclosure** | The failure of a transport loop to return the fiber to its initial state | Holonomy |
| **Transport error** | The measured inconsistency between fiber states at adjacent points along a trajectory | — |

## Mathematical Objects

| Canonical Name | Definition |
|---------------|------------|
| **Organizational manifold** (M) | The state space of an organization, parameterized by observable metrics |
| **Historical fiber** (F) | The residue of an organization's history attached to each point on M |
| **Organizational bundle** (B = M × F) | The fiber bundle combining state space with historical residue |
| **Transport operator** (τ) | A morphism mapping fibers between organizational states |
| **Connection coefficients** (Γ) | Local coefficients governing parallel transport along M |

## System Classes

| Canonical Name | Description |
|---------------|-------------|
| **Distributed system** | Graph-based coordination with heterogeneous nodes and routing |
| **Immune system** | Cytokine-mediated signaling network with receptor-based coordination |
| **Ant colony** | Pheromone-based stigmergic coordination |
| **Institution** | Trust-based organizational network |

## Perturbation Classes

| Canonical Name | Family |
|---------------|--------|
| Replay delay | Temporal |
| Asynchronous replay | Temporal |
| Memory truncation | Temporal |
| Replay scrambling | Temporal |
| Node deletion | Structural |
| Sector duplication | Structural |
| Routing mutation | Structural |
| Topology rewiring | Structural |
| Basis rotation | Gauge |
| Nonlinear normalization | Gauge |
| Random projection | Gauge |
| Coordinate compression | Gauge |
| Memory overwrite | Historical |
| Residue injection | Historical |
| Replay branch insertion | Historical |
| Counterfactual replay | Historical |

## Forbidden Synonyms

The following terms must NEVER be used:

- "latent manifold" → use "organizational state space"
- "gauge invariance" → use "organizational replay stability"
- "curvature" → use "replay loop nonclosure" or "transport inconsistency"
- "differential geometry" → use "discrete transport algebra"
- "consciousness" → outside scope
- "sentience" → outside scope
- "emergence" → use "organizational persistence"
