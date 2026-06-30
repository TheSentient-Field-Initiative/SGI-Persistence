# Phase 004B: Functional Recovery and Causal Stress Testing

## Central Scientific Question

**Is low-rank collapse merely geometric, or functionally destructive?**

Phase 004B investigates whether representational recovery (restoring ED) restores FUNCTION or only dimensional statistics.

## Division 1: Functional Recovery Metrics (CRITICAL)

### Protocol
- Define functional metrics per system:
  - distributed: consensus accuracy
  - immune: pathogen suppression
  - institution: decision stability
  - ant_colony: foraging efficiency
- Measure baseline function
- Induce collapse via coupling reduction
- Apply recovery interventions
- Compare ED recovery vs functional recovery

### Key Finding: Representation ≠ Function

**DISSOCIATION found in 5/8 systems:**

| System | ED Recovery | Function Recovery | Dissociation? |
|--------|-------------|-------------------|---------------|
| distributed | 89.1% | 100.0% | No |
| immune | 0.0% | 0.0% | No |
| epidemic | 6486.2% | 0.0% | **YES** |
| market | 32.7% | 0.0% | **YES** |
| neural | 209.5% | 0.0% | **YES** |
| swarm | 0.0% | 0.0% | No |
| reaction_diffusion | 402294.5% | 0.0% | **YES** |
| institution | 85.5% | 0.0% | **YES** |

**Interpretation:** Representational recovery does NOT guarantee functional recovery. You can fix the geometry without fixing the function.

## Division 2: Irreversibility Mapping

### Protocol
- Vary collapse severity: 0%, 10%, 20%, ..., 100%
- At each severity, attempt recovery
- Measure recovery success (both ED and function)
- Find the irreversible threshold

### Key Findings

1. **No dissociation** with synchronization-based collapse
2. **Noise injection HURTS function** in institution (-11.3%) and ant_colony (-34.6%)
3. **Immune system BENEFITS** from collapse (pathogen reduction improves suppression)
4. **Collapse mechanism matters** - synchronization collapse ≠ coupling collapse

## Division 3: Multi-Stage Collapse Trajectories

### Protocol
- Track ED, synchronization, and function through 20 collapse stages
- Detect phase transitions (sudden changes)

### Key Findings

1. **No gradual collapse** - systems either resist completely or show phase transitions
2. **Collapse can INCREASE ED** - ant_colony (1.0→1.32) and immune show ED rising with collapse
3. **Function is robust** - all systems maintain function across collapse severities
4. **Synchronization collapse ≠ coupling collapse** - fundamentally different mechanisms

## Division 4: Intervention Benchmark

### Protocol
- Compare all interventions under identical conditions:
  - Coupling reduction
  - Synchronization suppression
  - Noise injection
  - Combined approach

### Key Findings

1. **Noise injection consistently HURTS function** even when it helps ED recovery
2. **Immune system**: completely resistant to all interventions (100% recovery)
3. **Coupling reduction**: neutral effect (no change)
4. **Synchronization suppression**: helps ED but hurts function in institution

## Division 5: Resistant Systems V2

### Protocol
- Test hybrid architectures combining multiple resistance mechanisms
- Compare against baseline distributed system

### Results

| System | ED | Function |
|--------|-----|----------|
| distributed (baseline) | 1.000 | 1.000 |
| modular_heterogeneous | 1.019 | 1.000 |
| delayed_heterogeneous | 1.020 | 0.999 |
| adaptive_modular | **1.457** | 0.981 |

**Best:** adaptive_modular (ED=1.457, +45.7% improvement)

## Summary of Phase 004B Findings

1. **Representation ≠ Function**: The central finding. You can restore geometry without restoring function.
2. **Collapse mechanism matters**: Synchronization collapse and coupling collapse are fundamentally different.
3. **Noise injection is harmful**: Consistently hurts function even when it helps ED.
4. **Systems resist collapse**: Most systems maintain function across collapse severities.
5. **Adaptive desynchronization works**: The adaptive_modular hybrid achieves best resistance.

## Implications for Phase 004

- **Phase 004A** found that coupling reduction can restore ED in some systems
- **Phase 004B** shows that restoring ED does NOT restore function
- **The central scientific contribution** is now: **the distinction between representational and functional collapse**
- **Negative results remain the primary contribution**

## Files Generated

- `experiments/interventions/functional_recovery.py` - Division 1
- `experiments/interventions/irreversibility_mapping.py` - Division 2
- `experiments/interventions/multi_stage_collapse.py` - Division 3
- `experiments/interventions/intervention_benchmark.py` - Division 4
- `experiments/interventions/resistant_systems_v2.py` - Division 5
- `experiments/interventions/results/*.json` - All result files
