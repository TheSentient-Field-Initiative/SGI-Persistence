"""
SGI Post-Ω Study 001B.R1: Structural/Functional Dissociation Audit

Applies to BOTH systems (distributed system and ant colony).
For every perturbation, computes:
- Structural persistence: topology-sector survival
- Functional persistence: throughput/coordination recovery
- Coupling coefficient: correlation between structure and function

Primary question: Can structure persist while function collapses?
"""

import numpy as np
import json
import sys
sys.path.insert(0, '/home/student/sgp_core_v2/post_omega_study_001')

# ─── Load Existing Results ───

def load_distributed_system_results():
    """Load distributed system sector audit results."""
    with open('/home/student/sgp_core_v2/post_omega_study_001/sector_audit_results.json', 'r') as f:
        return json.load(f)

def load_ant_colony_results():
    """Load ant colony sector audit results."""
    with open('/home/student/sgp_core_v2/post_omega_study_001/colony_sector_audit_results.json', 'r') as f:
        return json.load(f)


# ─── Structural Persistence Metrics ───

def compute_structural_persistence(sector_data: dict) -> float:
    """Compute structural persistence score from topology sector data.
    
    Returns value in [0, 1]:
    - 1.0 = perfect structural persistence
    - 0.0 = complete structural collapse
    """
    topo = sector_data.get('topology', {})
    if 'error' in topo:
        return 0.0
    
    norm_survival = topo.get('normalization_survival', 0)
    raw_sim = topo.get('raw_similarity', 0)
    norm_sim = topo.get('normalized_similarity', 0)
    
    # Structural persistence = normalized similarity (not the delta)
    # We want to know: does the topology pattern survive?
    return max(0, norm_sim)


# ─── Functional Persistence Metrics ───

def compute_functional_persistence(sector_data: dict) -> float:
    """Compute functional persistence score from amplitude sector data.
    
    Returns value in [0, 1]:
    - 1.0 = perfect functional persistence
    - 0.0 = complete functional collapse
    """
    amp = sector_data.get('amplitude', {})
    if 'error' in amp:
        return 0.0
    
    norm_sim = amp.get('normalized_similarity', 0)
    range_pres = amp.get('range_preservation', 0)
    
    # Functional persistence = combination of normalized similarity and range preservation
    # Both matter: pattern and magnitude
    return max(0, (norm_sim + range_pres) / 2)


# ─── Coupling Coefficient ───

def compute_coupling_coefficient(structural: float, functional: float) -> float:
    """Compute coupling between structure and function.
    
    Returns value in [-1, 1]:
    - 1.0 = tightly coupled (both survive or both collapse)
    - 0.0 = uncoupled
    - -1.0 = anti-coupled (one survives, other collapses)
    """
    if structural == 0 and functional == 0:
        return 1.0  # Both collapsed = coupled
    if structural == 1.0 and functional == 1.0:
        return 1.0  # Both survived = coupled
    
    # For mixed cases, use signed distance from diagonal
    diff = structural - functional
    return -abs(diff)  # Negative = anti-coupled


# ─── Outcome Classification ───

def classify_outcome(structural: float, functional: float, threshold: float = 0.3) -> str:
    """Classify outcome as A, B, or C.
    
    Outcome A: Structure and function tightly coupled
    Outcome B: Structure survives while function collapses
    Outcome C: Function survives while structure collapses
    """
    struct_survived = structural > threshold
    func_survived = functional > threshold
    
    if struct_survived and func_survived:
        return "A"  # Both survive
    elif struct_survived and not func_survived:
        return "B"  # Structure persists, function collapses
    elif not struct_survived and func_survived:
        return "C"  # Function persists, structure collapses
    else:
        return "A_both_collapsed"  # Both collapsed = coupled failure


# ─── Main Audit ───

def run_dissociation_audit():
    """Run the complete structural/functional dissociation audit."""
    print("=" * 70)
    print("SGI Post-Ω Study 001B.R1: Structural/Functional Dissociation Audit")
    print("=" * 70)
    
    # Load results
    ds_results = load_distributed_system_results()
    ac_results = load_ant_colony_results()
    
    # Perturbation mappings
    ds_perturbations = ['P1_node_removal', 'P2_communication_delay', 'P3_resource_starvation', 'P4_scheduler_distortion']
    ac_perturbations = ['P1_worker_removal', 'P2_trail_disruption', 'P3_nest_fragmentation', 'P4_resource_relocation']
    perturbation_labels = ['P1', 'P2', 'P3', 'P4']
    
    all_outcomes = {}
    
    for system_name, results, perturbations in [
        ('Distributed System', ds_results, ds_perturbations),
        ('Ant Colony', ac_results, ac_perturbations)
    ]:
        print(f"\n{'─' * 50}")
        print(f"System: {system_name}")
        print(f"{'─' * 50}")
        
        structural_scores = []
        functional_scores = []
        outcomes = []
        
        for label, pname in zip(perturbation_labels, perturbations):
            if pname not in results:
                print(f"  {label}: NO DATA")
                continue
            
            sector_data = results[pname].get('sectors', {})
            
            # Compute scores
            structural = compute_structural_persistence(sector_data)
            functional = compute_functional_persistence(sector_data)
            coupling = compute_coupling_coefficient(structural, functional)
            outcome = classify_outcome(structural, functional)
            
            structural_scores.append(structural)
            functional_scores.append(functional)
            outcomes.append(outcome)
            
            print(f"  {label}: structural={structural:.3f}  functional={functional:.3f}  "
                  f"coupling={coupling:+.3f}  outcome={outcome}")
        
        # Summary
        mean_structural = np.mean(structural_scores) if structural_scores else 0
        mean_functional = np.mean(functional_scores) if functional_scores else 0
        
        # Count outcomes
        outcome_counts = {}
        for o in outcomes:
            outcome_counts[o] = outcome_counts.get(o, 0) + 1
        
        print(f"\n  MEAN: structural={mean_structural:.3f}  functional={mean_functional:.3f}")
        print(f"  OUTCOMES: {outcome_counts}")
        
        # Classification
        if outcome_counts.get('B', 0) > 0:
            verdict = "STRUCTURE-FUNCTION DISSOCIATION PRESENT"
        elif outcome_counts.get('C', 0) > 0:
            verdict = "FUNCTION-STRUCTURE DISSOCIATION PRESENT"
        else:
            verdict = "STRUCTURE AND FUNCTION COUPLED"
        
        print(f"  VERDICT: {verdict}")
        
        all_outcomes[system_name] = {
            'structural_scores': structural_scores,
            'functional_scores': functional_scores,
            'outcomes': outcomes,
            'verdict': verdict,
        }
    
    # ─── Cross-System Comparison ───
    print(f"\n{'=' * 70}")
    print("CROSS-SYSTEM DISSOCIATION COMPARISON")
    print(f"{'=' * 70}")
    
    ds_outcomes = all_outcomes.get('Distributed System', {}).get('outcomes', [])
    ac_outcomes = all_outcomes.get('Ant Colony', {}).get('outcomes', [])
    
    for i, label in enumerate(perturbation_labels):
        ds_o = ds_outcomes[i] if i < len(ds_outcomes) else '?'
        ac_o = ac_outcomes[i] if i < len(ac_outcomes) else '?'
        match = "CONSISTENT" if ds_o == ac_o else "INCONSISTENT"
        print(f"  {label}: DS={ds_o}  AC={ac_o}  [{match}]")
    
    # Overall
    ds_b_count = ds_outcomes.count('B')
    ac_b_count = ac_outcomes.count('B')
    ds_c_count = ds_outcomes.count('C')
    ac_c_count = ac_outcomes.count('C')
    
    print(f"\n  DS: {ds_b_count}/4 structure-function dissociation (outcome B)")
    print(f"  AC: {ac_b_count}/4 structure-function dissociation (outcome B)")
    print(f"  DS: {ds_c_count}/4 function-structure dissociation (outcome C)")
    print(f"  AC: {ac_c_count}/4 function-structure dissociation (outcome C)")
    
    # ─── Scientific Verdict ───
    print(f"\n{'=' * 70}")
    print("SCIENTIFIC VERDICT")
    print(f"{'=' * 70}")
    
    total_b = ds_b_count + ac_b_count
    total_c = ds_c_count + ac_c_count
    total_perturbations = len(ds_outcomes) + len(ac_outcomes)
    
    if total_b > 0:
        print(f"  OUTCOME B DETECTED: {total_b}/{total_perturbations} cases show")
        print(f"  structure persists while function collapses.")
        print(f"  ")
        print(f"  IMPLICATION: Persistent geometry is insufficient for adaptive viability.")
        print(f"  This mirrors Ω.15 (geometry ≠ scale) at the operational level.")
    elif total_c > 0:
        print(f"  OUTCOME C DETECTED: {total_c}/{total_perturbations} cases show")
        print(f"  function persists while structure collapses.")
        print(f"  ")
        print(f"  IMPLICATION: Systems can maintain operation through dynamic reconfiguration.")
    else:
        print(f"  OUTCOME A DOMINANT: Structure and function are coupled.")
        print(f"  Topology persistence may explain operational recovery.")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/dissociation_audit_results.json', 'w') as f:
        json.dump(all_outcomes, f, indent=2, default=str)
    
    print(f"\nResults saved to dissociation_audit_results.json")
    print(f"{'=' * 70}")
    
    return all_outcomes


if __name__ == '__main__':
    run_dissociation_audit()
