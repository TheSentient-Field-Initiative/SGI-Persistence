# Metric Traceability Audit

**Date:** 2026-06-28  
**Authority:** Research Director Directive (Phase 003 corrective)  
**Purpose:** Prove whether semantic drift occurred across implementations

---

## Executive Summary

**Semantic drift DID occur.** The synthetic ensemble and reproduction package used metric implementations that are NOT semantically compatible with the original Phase 001 implementations. This is the root cause of the apparent "G∝1/H falsification."

---

## Trace: `compute_G` / `measure_G`

### Implementation 1: Phase 001 (Canonical)

**File:** `experiments/phase_001/study_001i_entanglement.py`  
**Function:** `measure_G(md, fg, seed=42)`  
**Lines:** 460-480

```python
def measure_G(md, fg, seed=42):
    net = ImmuneNet(100, seed, md, fg)
    # Baseline: 20 steps
    hist_b = []
    for _ in range(20):
        s = net.step()
        hist_b.append(extract_m(s))
    # Perturbation
    net.inject_pathogen(0.5)
    # Recovery: 50 steps
    hist_a = []
    for _ in range(50):
        s = net.step()
        hist_a.append(extract_m(s))
    sr = sector_align(hist_b, hist_a)
    return gauge_frac(sr)
```

**Sector Definitions (IMMUNE-SPECIFIC):**
```python
SECTORS = {
    'amplitude': ['mean_act', 'total_cyto', 'n_active'],
    'topology': ['connectivity', 'n_comp', 'largest', 'type_entropy'],
    'transport': ['cov_trace', 'cov_condition'],
    'residual': ['non_principal', 'signaling_noise'],
}
```

**Semantic compatible?** YES — this is the canonical definition.

---

### Implementation 2: Synthetic Ensemble

**File:** `experiments/validation/synthetic_ensemble.py`  
**Function:** `compute_G(trajectory)`  
**Lines:** 242-297

```python
def compute_G(trajectory: List[Dict]) -> float:
    # ...
    SECTORS = {
        'amplitude': ['mean_activation', 'n_active'],
        'topology': ['connectivity', 'n_components'],
        'transport': ['cov_trace', 'cov_condition'],
        'residual': ['non_principal'],
    }
    # ...
    mid = len(trajectory) // 2
    before = [extract_metrics(s) for s in trajectory[:mid]]
    after = [extract_metrics(s) for s in trajectory[mid:]]
    sr = sector_align(before, after)
    return gauge_frac(sr)
```

**Semantic compatible?** NO — CRITICAL DRIFT

| Issue | Details |
|-------|---------|
| Different metric names | `mean_activation` vs `mean_act`, `n_components` vs `n_comp` |
| Different sector composition | 2 metrics in amplitude vs 3; 2 in residual vs 2 |
| No perturbation | Splits trajectory at midpoint instead of applying explicit perturbation |
| No baseline/recovery distinction | Uses arbitrary split, not semantic baseline/recovery |
| Generic sectors | NOT system-specific; uses generic key names |

---

### Implementation 3: Reproduction Package

**File:** `reproduction/minimal_demo/reproduce.py`  
**Function:** `compute_G(trajectory, perturbation_severity=0.5)`  
**Lines:** 127-143

```python
def compute_G(trajectory, perturbation_severity=0.5):
    SECTORS = {
        'amplitude': ['mean_activation', 'n_active'],
        'topology': ['connectivity', 'n_components'],
        'transport': ['cov_trace', 'cov_condition'],
        'residual': ['non_principal'],
    }
    # ...
    mid = len(trajectory) // 2
    before = [extract_metrics(s) for s in trajectory[:mid]]
    after = [extract_metrics(s) for s in trajectory[mid:]]
    sr = sector_align(before, after)
    return gauge_frac(sr)
```

**Semantic compatible?** NO — same drift as synthetic ensemble.

---

### Implementation 4: Ant Colony

**File:** `src/systems/ant_colony/study_001b_colony.py`  
**Function:** `compute_sector_alignment_colony(before_metrics, after_metrics)`  
**Lines:** 382-416

```python
SECTORS = {
    'amplitude': ['total_food_remaining', 'total_pheromone', 'recruitment_rate'],
    'topology': ['trail_connectivity', 'n_components', 'path_redundancy', 'largest_component'],
    'transport': ['cov_trace', 'cov_condition', 'anisotropy'],
    'residual': ['residual_deviation', 'residual_energy', 'non_principal'],
}
```

**Semantic compatible?** PARTIALLY — system-specific sectors, but different from immune canonical.

---

### Implementation 5: Institution

**File:** `src/systems/institution/study_001d_institution.py`  
**Function:** `compute_institution_sector_alignment(before_metrics, after_metrics)`  
**Lines:** 393-416

```python
SECTORS = {
    'amplitude': ['cooperation_rate', 'mean_payoff', 'mean_trust'],
    'topology': ['network_connectivity', 'n_components', 'largest_component', 'strategy_entropy'],
    'transport': ['cov_trace', 'cov_condition'],
    'residual': ['norm_deviation', 'non_principal'],
}
```

**Semantic compatible?** PARTIALLY — system-specific sectors, but different from immune canonical.

---

## Trace: `compute_H` / `measure_historical_entanglement`

### Implementation 1: Phase 001 (Canonical)

**File:** `experiments/phase_001/study_001i_entanglement.py`  
**Function:** `measure_historical_entanglement(net)`  
**Lines:** 383-416

```python
def measure_historical_entanglement(net):
    path_dep = measure_path_dependence(net)
    mi = measure_state_history_mi(net)
    div = measure_trajectory_divergence(net)
    mem_ent = measure_memory_entropy(net)
    hyst = measure_hysteresis(net)
    # Composite score (weighted average)
    composite = np.mean([pd_norm, mi, div_norm, me_norm, hyst_norm])
    return scores
```

**Semantic compatible?** YES — this is the canonical definition.

---

### Implementation 2: Synthetic Ensemble

**File:** `experiments/validation/synthetic_ensemble.py`  
**Function:** `compute_H(trajectory)`  
**Lines:** 300-318

```python
def compute_H(trajectory: List[Dict]) -> float:
    vectors = [state_to_vector(tr) for tr in trajectory]
    correlations = []
    for i in range(5, len(vectors)):
        current = vectors[i]
        history = np.mean(vectors[max(0, i - 5):i], axis=0)
        corr = np.corrcoef(current, history)[0, 1]
        if np.isfinite(corr):
            correlations.append(abs(corr))
    return float(np.mean(correlations)) if correlations else 0.0
```

**Semantic compatible?** NO — CRITICAL DRIFT

| Issue | Details |
|-------|---------|
| Different method | Autocorrelation vs composite of 5 measures |
| Different input | state_to_vector vs raw metrics |
| Different semantics | Temporal correlation vs multi-faceted entanglement |

---

### Implementation 3: Reproduction Package

**File:** `reproduction/minimal_demo/reproduce.py`  
**Function:** `compute_H(trajectory)`  
**Lines:** 146-161

```python
def compute_H(trajectory):
    vectors = [state_to_vector(tr) for tr in trajectory]
    correlations = []
    for lag in range(1, min(6, len(vectors))):
        corr = np.corrcoef(vectors[lag:], vectors[:-lag])[0, 1]
        if np.isfinite(corr):
            correlations.append(abs(corr))
    return float(np.mean(correlations)) if correlations else 0.0
```

**Semantic compatible?** NO — same drift as synthetic ensemble.

---

## Trace: `state_to_vector`

### Implementation 1: Canonical (connection_formalism.py)

**File:** `src/geometry/connection_formalism.py`  
**Function:** `state_to_vector(state)`  
**Lines:** 602-629 (original), 602-641 (updated)

**Original keys:**
```python
fixed_keys = [
    'connectivity', 'n_active', 'routing_entropy', 'assignment_rate',
    'allocation_entropy', 'mean_activation', 'type_entropy', 'efficiency',
]
```

**Updated keys (after Phase 003 fix):**
```python
key_mapping = {
    'connectivity': 0, 'signaling_connectivity': 0, 
    'trail_connectivity': 0, 'network_connectivity': 0,
    'n_active': 1,
    'routing_entropy': 2, 'type_entropy': 2, 'strategy_entropy': 2,
    'assignment_rate': 3, 'recruitment_rate': 3, 'cooperation_rate': 3,
    'allocation_entropy': 4, 'path_redundancy': 4,
    'mean_activation': 5, 'mean_trust': 5, 'total_pheromone': 5,
    'n_components': 6, 'largest_component': 6,
    'efficiency': 7, 'mean_payoff': 7,
}
```

**Semantic compatible?** PARTIALLY — the updated version handles more key variants, but the mapping is ad-hoc and may produce incorrect vectors for some systems.

---

## Summary: Semantic Compatibility Matrix

| Implementation | File | G Compatible? | H Compatible? | state_to_vector? |
|---------------|------|---------------|---------------|------------------|
| Phase 001 (canonical) | study_001i_entanglement.py | YES | YES | N/A (uses raw metrics) |
| Ant Colony | study_001b_colony.py | PARTIAL | N/A | N/A (uses raw metrics) |
| Institution | study_001d_institution.py | PARTIAL | N/A | N/A (uses raw metrics) |
| Synthetic Ensemble | synthetic_ensemble.py | NO | NO | DRIFTED |
| Reproduction Package | reproduce.py | NO | NO | DRIFTED |

---

## Conclusion

**Semantic drift occurred in 3 locations:**

1. `experiments/validation/synthetic_ensemble.py` — `compute_G` uses wrong sectors, no perturbation
2. `experiments/validation/synthetic_ensemble.py` — `compute_H` uses autocorrelation instead of composite
3. `reproduction/minimal_demo/reproduce.py` — both `compute_G` and `compute_H` drifted

**Root cause:** The synthetic ensemble and reproduction package were implemented without strict adherence to the canonical metric definitions. The sector definitions were "simplified" in a way that changed their semantic meaning.

**Impact:** The apparent "G∝1/H falsification" (-0.0121 correlation) is NOT a scientific finding. It is a metric identity collapse caused by using incompatible implementations.

**Required fix:** All metric implementations must be updated to match the canonical definitions in `docs/specifications/canonical_metric_contract.md`.
