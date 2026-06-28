# SGI Persistence Program

## Organizational Gauge Stability and Historical Entanglement

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

### Overview

The SGI Persistence Program investigates the mathematical structure of organizational persistence in complex adaptive systems. The central finding is an empirical law relating gauge stability to historical entanglement:

**G ∝ 1/H**

where:
- **G** = gauge stability (organizational invariance under representation change)
- **H** = historical entanglement (accumulated irreversible path dependence)

This relationship was validated across four independent organizational domains:
- Distributed computing systems
- Ant colony optimization
- Institutional networks
- Immune signaling networks

with cross-domain correlation r ≈ -0.951.

### Core Findings

1. **Historical Entanglement Law**: G ∝ 1/H with r = -0.951 across four domains
2. **Persistence-Adaptation Tradeoff**: Gauge stability and adaptive capacity exist in measurable tension (r = -0.869)
3. **Falsified Hypotheses**: Decentralization, architectural substitution, attractor fragmentation, organizational freedom, thermodynamic irreversibility, replay compressibility, and simple gauge equivariance are insufficient explanations for high G
4. **Representation Ceiling**: Current scalar observables cannot resolve organizational geometry, motivating the transition to fiber bundle representations
5. **Geometric Separation**: Organizational holonomy differentiates systems where scalar measures saturate

### Repository Structure

```
SGI-Persistence/
├── src/                    # Core computational framework
│   ├── core/              # Shared utilities
│   ├── systems/           # System implementations
│   │   ├── distributed/
│   │   ├── ant_colony/
│   │   ├── institution/
│   │   └── immune/
│   ├── audits/            # Audit protocols
│   ├── geometry/          # Fiber bundle formalism
│   ├── metrics/           # Measurement functions
│   └── visualization/     # Plotting utilities
├── experiments/           # Reproducible experiments
│   ├── phase_001/        # Scalar audit series
│   └── phase_002/        # Geometric transition
├── data/                  # Datasets
│   ├── canonical/        # Validated results
│   ├── processed/        # Derived data
│   └── raw/              # Source data
├── reports/               # Publication materials
├── docs/                  # Documentation
├── papers/                # Manuscripts
└── tests/                 # Test suite
```

### Reproducibility

All experiments can be reproduced by running:

```bash
# Phase 001 experiments
cd experiments/phase_001
python study_001e_constraint_injection.py

# Phase 002A geometric analysis
cd experiments/phase_002
python run_phase_002a.py
```

Dependencies:
- Python 3.10+
- NumPy
- SciPy
- Matplotlib (for visualization)

### Citation

If you use this work, please cite:

```bibtex
@software{sgi_persistence_2026,
  title={SGI Persistence Program: Organizational Gauge Stability and Historical Entanglement},
  year={2026},
  url={https://github.com/TheSentient-Field-Initiative/SGI-Persistence}
}
```

### License

MIT License - see [LICENSE](LICENSE) for details.

### Disclaimer

This research program investigates mathematical structures in organizational systems. The empirical findings (G ∝ 1/H) are well-supported by computational experiments. Theoretical extensions involving fiber bundle geometry and gauge theory are provisional and represent active research directions, not established conclusions.
