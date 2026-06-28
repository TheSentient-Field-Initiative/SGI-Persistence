# SGI Persistence Program

**Computational Organizational Geometry: Empirical Laws of Persistent Adaptive Systems**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

## Program Overview

The SGI Persistence Program investigates the mathematical structure of persistent adaptive organization across radically different systems. We study four core concepts:

- **Organizational replay stability (G)**: The degree to which an organizational state can be reproduced through replay of its generative process.
- **Historical residue coupling (H)**: The measurable correlation between an organization's current state and its historical trajectory.
- **Organizational geometry**: The fiber bundle structure over organizational state space, enabling geometric observables beyond scalar metrics.
- **Replay equivalence**: The relationship between different replay paths and their outcomes, formalized through transport operators.

## Main Empirical Law

We discover a robust inverse relationship between organizational replay stability and historical residue coupling:

$$G \propto \frac{1}{H}$$

with cross-domain correlation **r = -0.951** across four system classes (distributed coordination, immune signaling, ant colony stigmergy, institutional trust networks).

## Phase Evolution

| Phase | Purpose | Outcome |
|-------|---------|---------|
| 001 | Scalar persistence audits | G ∝ 1/H confirmed (r = -0.951); representation ceiling discovered |
| 002A | Organizational fiber geometry | Geometric differentiation achieved; transport error separates systems |
| 002B | True connection formalism | 122.5x improvement in replay transport coupling separation |
| 002C | Discrete transport algebra | Transport instability T emerges; immune fragility discovered |

## Reproduction Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run Phase 002A (fiber geometry)
python experiments/phase_002/run_phase_002a.py

# Run Phase 002B (connection formalism)
python experiments/phase_002/run_phase_002b.py

# Run Phase 002C (transport stress test)
python experiments/phase_002/run_phase_002c.py

# Generate all figures
make figures

# Run test suite
make test
```

## Repository Structure

```
SGI-Persistence/
├── src/geometry/          # Core geometric formalism
│   ├── connection_formalism.py   # Phase 002B: fiber bundles
│   ├── discrete_transport.py     # Phase 002C: transport algebra
│   ├── noncommutative/           # Phase 002D scaffold
│   ├── path_groupoids/           # Phase 002D scaffold
│   └── replay_algebra/           # Phase 002D scaffold
├── src/systems/           # Simulation systems
│   ├── distributed/       # Graph-based distributed coordination
│   ├── immune/            # Cytokine-mediated signaling network
│   ├── ant_colony/        # Pheromone-based stigmergy
│   └── institution/       # Trust-based organizational network
├── experiments/           # Reproducible experiment scripts
├── tests/                 # Test suite
├── data/canonical/        # Canonical result exports
├── results/figures/       # Publication-grade figures
├── papers/                # Manuscript drafts
├── docs/                  # Methodology, terminology, status
├── scripts/               # Automation scripts
├── archive/               # Superseded exploratory work
├── Makefile               # Build automation
├── pyproject.toml         # Project configuration
├── requirements.txt       # Dependencies
├── CITATION.cff           # Citation metadata
└── LICENSE                # Apache-2.0
```

## Canonical Terminology

| Term | Canonical Name |
|------|---------------|
| Gauge stability | Organizational replay stability |
| Historical entanglement | Historical residue coupling |
| Fiber entanglement | Replay transport coupling |
| Transport instability | Transport instability (T) |
| Holonomy | Replay loop nonclosure |

See [docs/terminology/](docs/terminology/) for full glossary.

## Citation

```bibtex
@software{sgi_persistence_2026,
  title={SGI Persistence Program: Computational Organizational Geometry},
  year={2026},
  version={0.2.0},
  url={https://github.com/TheSentient-Field-Initiative/SGI-Persistence}
}
```

## License

Apache License 2.0. See [LICENSE](LICENSE).

## Scientific Position

This repository presents **computational organizational experiments**, not settled physics. All claims are framed as:

- Exploratory geometric formalism
- Empirical organizational correlations
- Candidate mathematical structures

All claims are provisional and subject to revision.
