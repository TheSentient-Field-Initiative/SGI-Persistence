# Migration Manifest

**Date:** 2026-06-28
**From:** Pre-migration SGI-Persistence
**To:** Publication-grade SGI-Persistence v0.2.0

## File Status Legend

| Status | Meaning |
|--------|---------|
| **retained** | Canonical file, kept in place |
| **archived** | Deprecated, moved to `archive/` |
| **superseded** | Replaced by newer version, moved to `archive/superseded/` |
| **new** | Created during migration |
| **modified** | Updated during migration |

## Geometry Modules

| File | Status | Reason |
|------|--------|--------|
| `src/geometry/connection_formalism.py` | retained | Core Phase 002B module, cleaned with docstrings |
| `src/geometry/discrete_transport.py` | retained | Core Phase 002C module, cleaned imports |
| `src/geometry/organizational_bundle.py` | superseded | Replaced by connection_formalism.py; moved to `archive/superseded/` |
| `src/geometry/noncommutative/` | new | Phase 002D scaffold |
| `src/geometry/path_groupoids/` | new | Phase 002D scaffold |
| `src/geometry/replay_algebra/` | new | Phase 002D scaffold |

## System Modules

| File | Status | Reason |
|------|--------|--------|
| `src/systems/distributed/study_001.py` | retained | Canonical distributed system |
| `src/systems/immune/study_001c_immune.py` | retained | Canonical immune system |
| `src/systems/ant_colony/study_001b_colony.py` | retained | Canonical ant colony |
| `src/systems/institution/study_001d_institution.py` | retained | Canonical institution |

## Experiment Scripts

| File | Status | Reason |
|------|--------|--------|
| `experiments/phase_001/study_001i_entanglement.py` | retained | Core Phase 001 study |
| `experiments/phase_001/study_001j_cross_domain_entanglement.py` | retained | Core cross-domain study |
| `experiments/phase_002/run_phase_002a.py` | retained | Phase 002A validation |
| `experiments/phase_002/run_phase_002b.py` | retained | Phase 002B validation |
| `experiments/phase_002/run_phase_002c.py` | retained | Phase 002C validation |
| `experiments/phase_001/study_001a_sector_audit.py` | archived | Deprecated: exploratory |
| `experiments/phase_001/study_001br1_dissociation.py` | archived | Deprecated: exploratory |
| `experiments/phase_001/study_001cr1_amplitude_audit.py` | archived | Deprecated: exploratory |
| `experiments/phase_001/study_001e_constraint_injection.py` | archived | Deprecated: exploratory |
| `experiments/phase_001/study_001f_architectural_substitution.py` | archived | Deprecated: exploratory |
| `experiments/phase_001/study_001g_mechanism_ablation.py` | archived | Deprecated: exploratory |
| `experiments/phase_001/study_001h_tradeoff.py` | archived | Deprecated: exploratory |
| `experiments/phase_001/study_001k_attractor_geometry.py` | archived | Deprecated: exploratory |
| `experiments/phase_001/study_001l_organizational_freedom.py` | archived | Deprecated: exploratory |
| `experiments/phase_001/study_001m_reversibility_calculus.py` | archived | Deprecated: exploratory |
| `experiments/phase_001/study_001n_replayability.py` | archived | Deprecated: exploratory |
| `experiments/phase_001/study_001o_gauge_equivariance.py` | archived | Deprecated: exploratory |
| `experiments/phase_001/study_001p_sectoral_entanglement.py` | archived | Deprecated: exploratory |

## Documentation

| File | Status | Reason |
|------|--------|--------|
| `docs/methodology/RESEARCH_TEMPLATE.md` | new | Operational research template |
| `docs/methodology/SGI_OPERATIONAL_TEMPLATE.md` | retained | Existing methodology |
| `docs/terminology/CANONICAL_TERMS.md` | new | Canonical terminology glossary |
| `docs/theory/CONDENSED_MATHEMATICAL_HISTORY.md` | retained | Mathematical history |
| `docs/json_schema.md` | new | JSON result schema |
| `docs/project_status.md` | new | Master orientation document |
| `docs/migration_manifest.md` | new | This file |

## Papers

| File | Status | Reason |
|------|--------|--------|
| `papers/phase_001/abstract.md` | new | Phase 001 manuscript |
| `papers/phase_001/introduction.md` | new | Phase 001 manuscript |
| `papers/phase_001/methods.md` | new | Phase 001 manuscript |
| `papers/phase_001/results.md` | new | Phase 001 manuscript |
| `papers/phase_001/discussion.md` | new | Phase 001 manuscript |
| `papers/phase_001/references.bib` | new | Phase 001 bibliography |
| `papers/phase_002/abstract.md` | new | Phase 002 manuscript |
| `papers/phase_002/introduction.md` | new | Phase 002 manuscript |
| `papers/phase_002/methods.md` | new | Phase 002 manuscript |
| `papers/phase_002/results.md` | new | Phase 002 manuscript |
| `papers/phase_002/discussion.md` | new | Phase 002 manuscript |
| `papers/figures/generate_figures.py` | new | Figure generation |

## Infrastructure

| File | Status | Reason |
|------|--------|--------|
| `README.md` | modified | Updated with all required sections |
| `LICENSE` | modified | Changed to Apache-2.0 |
| `CITATION.cff` | modified | Updated for Apache-2.0 |
| `pyproject.toml` | modified | Updated license |
| `requirements.txt` | retained | Dependencies unchanged |
| `.gitignore` | new | Standard Python gitignore |
| `Makefile` | new | Build automation |
| `scripts/generate_all_figures.py` | new | Figure pipeline |

## Results

| File | Status | Reason |
|------|--------|--------|
| `results/figures/fig01_g_vs_h.*` | new | Publication figure |
| `results/figures/fig02_transport_error.*` | new | Publication figure |
| `results/figures/fig03_fiber_entanglement.*` | new | Publication figure |
| `results/figures/fig04_transport_instability.*` | new | Publication figure |
| `results/figures/fig05_immune_fragility.*` | new | Publication figure |
| `results/figures/fig06_gxh_product.*` | new | Publication figure |
| `results/figures/fig07_correlation_comparison.*` | new | Publication figure |

## Tests

| File | Status | Reason |
|------|--------|--------|
| `tests/test_connection_formalism.py` | new | Geometry module tests |
| `tests/test_discrete_transport.py` | new | Transport algebra tests |
| `tests/test_reproducibility.py` | new | Seed and schema tests |
| `tests/test_figures.py` | new | Figure pipeline tests |
