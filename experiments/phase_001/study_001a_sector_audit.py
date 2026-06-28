"""
SGI Post-Ω Study 001A: Observable Sector Separation

No simulator changes. Pure metric decomposition.
Classify observables into amplitude/topology/transport/residual sectors.
Rerun perturbation experiments with sector-specific observables.
"""

import numpy as np
import json
import sys
sys.path.insert(0, '/home/student/sgp_core_v2/post_omega_study_001')
from study_001 import (
    DistributedSystem, NodeRemoval, CommunicationDelay,
    ResourceStarvation, SchedulerDistortion, WorkloadType
)

# ─── Sector Definitions ───
# Based on Ω.15 lesson: scale and geometry carry independent information.

SECTORS = {
    'amplitude': {
        'description': 'Magnitude-bearing observables. Expected to NOT survive normalization.',
        'metrics': ['assignment_rate', 'throughput', 'allocation_entropy'],
        'expected_survival': False,
    },
    'topology': {
        'description': 'Geometric/structural observables. Expected to survive normalization.',
        'metrics': ['connectivity', 'n_components', 'routing_entropy'],
        'expected_survival': True,
    },
    'transport': {
        'description': 'Covariance/eigenspace observables. Expected to survive normalization.',
        'metrics': ['cov_eigenvalues', 'cov_condition_number', 'cov_trace'],
        'expected_survival': True,
    },
    'residual': {
        'description': 'Residual structure after removing dominant components.',
        'metrics': ['residual_energy', 'residual_rank', 'residual_alignment'],
        'expected_survival': True,
    },
}


def extract_sector_metrics(state: dict) -> dict:
    """Extract all sector-specific metrics from a single state."""
    result = {}
    
    # Amplitude sector
    result['assignment_rate'] = state.get('assignment_rate', 0)
    result['throughput'] = state.get('assignment_rate', 0) * state.get('n_active', 0)
    result['allocation_entropy'] = state.get('allocation_entropy', 0)
    
    # Topology sector
    result['connectivity'] = state.get('connectivity', 0)
    result['n_components'] = state.get('n_components', 0)
    result['routing_entropy'] = state.get('routing_entropy', 0)
    
    # Transport sector
    eigenvalues = state.get('cov_eigenvalues', [0])
    if isinstance(eigenvalues, list) and len(eigenvalues) > 0:
        ev = np.array(eigenvalues)
        result['cov_eigenvalues'] = ev
        result['cov_trace'] = float(np.sum(ev))
        result['cov_condition_number'] = float(ev[0] / (ev[-1] + 1e-10)) if len(ev) > 1 else 1.0
        result['cov_top3_energy'] = float(np.sum(ev[:3]) / (np.sum(ev) + 1e-10))
    else:
        result['cov_eigenvalues'] = np.array([0])
        result['cov_trace'] = 0
        result['cov_condition_number'] = 1.0
        result['cov_top3_energy'] = 0
    
    # Residual sector (after removing top-3 eigenvectors)
    if isinstance(eigenvalues, list) and len(eigenvalues) > 3:
        ev = np.array(eigenvalues)
        total = np.sum(ev)
        residual = np.sum(ev[3:])
        result['residual_energy'] = float(residual / (total + 1e-10))
        result['residual_rank'] = int(np.sum(ev[3:] > 0.01 * ev[0]))
    else:
        result['residual_energy'] = 0
        result['residual_rank'] = 0
    
    return result


def compute_sector_alignment(before_metrics: list, after_metrics: list) -> dict:
    """Compute alignment of sector metrics before and after perturbation."""
    results = {}
    
    for sector_name, sector_def in SECTORS.items():
        metrics = sector_def['metrics']
        
        # Extract raw metric vectors
        before_vectors = []
        after_vectors = []
        
        for m in metrics:
            before_vals = [bm.get(m, 0) for bm in before_metrics]
            after_vals = [am.get(m, 0) for am in after_metrics]
            
            if isinstance(before_vals[0], np.ndarray):
                # For eigenvalue arrays, use trace and condition number
                before_vectors.append([np.sum(v) for v in before_vals])
                after_vectors.append([np.sum(v) for v in after_vals])
            else:
                before_vectors.append(before_vals)
                after_vectors.append(after_vals)
        
        before_arr = np.array(before_vectors).T  # (n_timesteps, n_metrics)
        after_arr = np.array(after_vectors).T
        
        if before_arr.size == 0 or after_arr.size == 0:
            results[sector_name] = {'error': 'no data'}
            continue
        
        # Truncate to same length
        min_len = min(len(before_arr), len(after_arr))
        before_arr = before_arr[:min_len]
        after_arr = after_arr[:min_len]
        
        # Raw similarity
        def cosine_sim(a, b):
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            if na == 0 or nb == 0:
                return 0.0
            return float(np.dot(a.flatten(), b.flatten()) / (na * nb))
        
        raw_sim = cosine_sim(before_arr, after_arr)
        
        # Normalized similarity
        before_norm = (before_arr - before_arr.mean(axis=0)) / (before_arr.std(axis=0) + 1e-8)
        after_norm = (after_arr - after_arr.mean(axis=0)) / (after_arr.std(axis=0) + 1e-8)
        norm_sim = cosine_sim(before_norm, after_norm)
        
        # Normalization survival
        norm_survival = norm_sim - raw_sim
        
        # Range preservation (are the values in the same range?)
        before_range = before_arr.max(axis=0) - before_arr.min(axis=0)
        after_range = after_arr.max(axis=0) - after_arr.min(axis=0)
        range_ratio = float(np.mean(after_range / (before_range + 1e-10)))
        
        results[sector_name] = {
            'raw_similarity': raw_sim,
            'normalized_similarity': norm_sim,
            'normalization_survival': norm_survival,
            'range_preservation': range_ratio,
            'expected_survival': sector_def['expected_survival'],
            'verdict': 'SURVIVES' if norm_survival > -0.1 else 'COLLAPSES',
        }
    
    return results


def run_sector_audit():
    """Run the complete observable sector separation audit."""
    print("=" * 70)
    print("SGI Post-Ω Study 001A: Observable Sector Separation")
    print("=" * 70)
    
    all_results = {}
    
    perturbations = {
        'P1_node_removal': (NodeRemoval, 0.3),
        'P2_communication_delay': (CommunicationDelay, 0.5),
        'P3_resource_starvation': (ResourceStarvation, 0.4),
        'P4_scheduler_distortion': (SchedulerDistortion, 0.3),
    }
    
    for pname, (protocol, severity) in perturbations.items():
        print(f"\n{'─' * 50}")
        print(f"Perturbation: {pname} (severity={severity})")
        print(f"{'─' * 50}")
        
        # Reset system
        system = DistributedSystem(n_nodes=100, seed=42)
        system.generate_tasks(n_tasks=100)
        
        # Establish baseline (20 timesteps)
        history_before = []
        for _ in range(20):
            state = system.step()
            history_before.append(extract_sector_metrics(state))
        
        # Apply perturbation
        description = protocol.apply(system, severity)
        print(f"  Applied: {description}")
        
        # Measure recovery (50 timesteps)
        history_after = []
        for _ in range(50):
            state = system.step()
            history_after.append(extract_sector_metrics(state))
        
        # Compute sector alignment
        sector_results = compute_sector_alignment(history_before, history_after)
        
        all_results[pname] = {
            'description': description,
            'sectors': sector_results,
        }
        
        # Print sector results
        for sector_name, sr in sector_results.items():
            if 'error' in sr:
                print(f"  {sector_name}: {sr['error']}")
                continue
            
            expected = "✓ expected" if sr['expected_survival'] else "✗ expected to collapse"
            actual = sr['verdict']
            match = "MATCH" if (sr['expected_survival'] and actual == 'SURVIVES') or \
                               (not sr['expected_survival'] and actual == 'COLLAPSES') else "MISMATCH"
            
            print(f"  {sector_name:12s}: raw={sr['raw_similarity']:.4f}  "
                  f"norm={sr['normalized_similarity']:.4f}  "
                  f"Δ={sr['normalization_survival']:+.4f}  "
                  f"range={sr['range_preservation']:.3f}  "
                  f"→ {actual}  ({expected}) [{match}]")
    
    # ─── Cross-Perturbation Summary ───
    print(f"\n{'=' * 70}")
    print("SECTOR SUMMARY ACROSS PERTURBATIONS")
    print(f"{'=' * 70}")
    
    for sector_name in SECTORS:
        survivals = []
        collapses = []
        mismatches = []
        
        for pname, data in all_results.items():
            sr = data['sectors'].get(sector_name, {})
            if 'error' in sr:
                continue
            verdict = sr['verdict']
            expected = sr['expected_survival']
            
            if verdict == 'SURVIVES':
                survivals.append(pname)
            else:
                collapses.append(pname)
            
            if (expected and verdict == 'COLLAPSES') or (not expected and verdict == 'SURVIVES'):
                mismatches.append(pname)
        
        print(f"\n  {sector_name}:")
        print(f"    Survives:  {len(survivals)}/4 — {survivals}")
        print(f"    Collapses: {len(collapses)}/4 — {collapses}")
        if mismatches:
            print(f"    MISMATCHES: {mismatches} (expected opposite)")
        else:
            print(f"    All predictions correct")
    
    # ─── Verdict ───
    print(f"\n{'=' * 70}")
    print("SECTOR VERDICT")
    print(f"{'=' * 70}")
    
    for sector_name, sector_def in SECTORS.items():
        all_match = True
        for pname, data in all_results.items():
            sr = data['sectors'].get(sector_name, {})
            if 'error' in sr:
                continue
            expected = sr['expected_survival']
            actual = sr['verdict'] == 'SURVIVES'
            if expected != actual:
                all_match = False
                break
        
        status = "CONFIRMED" if all_match else "DISPUTED"
        print(f"  {sector_name:12s}: {status} — {sector_def['description']}")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/sector_audit_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\nResults saved to sector_audit_results.json")
    print(f"{'=' * 70}")
    
    return all_results


if __name__ == '__main__':
    run_sector_audit()
