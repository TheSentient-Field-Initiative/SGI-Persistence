"""
SGI Post-Ω Study 001E: Constraint Injection Framework

First causal intervention study.
Target: distributed system (already characterized)
Goal: determine whether G can be induced through controlled constraints

Variants:
- baseline: no constraints
- bounded-only: hard clipping
- threshold-only: activation gating
- conservation-only: conserved flow
- combined: all three

Constraint densities: Φ ∈ {0.0, 0.25, 0.5, 0.75, 1.0}
"""

import numpy as np
import json
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

sys.path.insert(0, '/home/student/sgp_core_v2/post_omega_study_001')
from study_001 import (
    DistributedSystem, NodeRemoval, CommunicationDelay,
    ResourceStarvation, SchedulerDistortion, WorkloadType
)


# ═══════════════════════════════════════════════════════════════════
# Constraint Injection Layer
# ═══════════════════════════════════════════════════════════════════

class ConstraintInjector:
    """Injects dynamical constraints into a distributed system."""
    
    def __init__(self, system: DistributedSystem, 
                 bounded: bool = False, 
                 threshold: bool = False, 
                 conservation: bool = False,
                 constraint_density: float = 0.0):
        self.system = system
        self.bounded = bounded
        self.threshold = threshold
        self.conservation = conservation
        self.density = constraint_density
    
    def apply_constraints(self):
        """Apply active constraints to the system."""
        if self.bounded:
            self._apply_bounded()
        if self.threshold:
            self._apply_threshold()
        if self.conservation:
            self._apply_conservation()
    
    def _apply_bounded(self):
        """Hard clipping: constrain all state variables to [0, 1]."""
        for node in self.system.nodes.values():
            if not node.active:
                continue
            # Clip CPU and memory usage
            node.cpu_used = np.clip(node.cpu_used * (1 + self.density * 0.1), 0, node.cpu_capacity)
            node.memory_used = np.clip(node.memory_used * (1 + self.density * 0.1), 0, node.memory_capacity)
    
    def _apply_threshold(self):
        """Activation gating: only update if change exceeds threshold."""
        threshold = 0.1 * (1 - self.density)  # Higher density = lower threshold = more gating
        for node in self.system.nodes.values():
            if not node.active:
                continue
            # Skip updates if activity is below threshold
            if abs(node.cpu_used - node.cpu_capacity * 0.5) < threshold * node.cpu_capacity:
                node.cpu_used = node.cpu_capacity * 0.5  # Snap to midpoint
    
    def _apply_conservation(self):
        """Conservation law: total resources conserved across active nodes."""
        active_nodes = [n for n in self.system.nodes.values() if n.active]
        if not active_nodes:
            return
        
        total_cpu = sum(n.cpu_capacity for n in active_nodes)
        total_memory = sum(n.memory_capacity for n in active_nodes)
        total_cpu_used = sum(n.cpu_used for n in active_nodes)
        total_memory_used = sum(n.memory_used for n in active_nodes)
        
        # Redistribute to maintain conservation
        if total_cpu_used > 0 and total_memory_used > 0:
            target_cpu_ratio = total_cpu_used / len(active_nodes)
            target_memory_ratio = total_memory_used / len(active_nodes)
            
            conservation_strength = self.density * 0.5
            for node in active_nodes:
                node.cpu_used = node.cpu_used * (1 - conservation_strength) + target_cpu_ratio * conservation_strength
                node.memory_used = node.memory_used * (1 - conservation_strength) + target_memory_ratio * conservation_strength


# ═══════════════════════════════════════════════════════════════════
# Sector Audit (adapted from 001A)
# ═══════════════════════════════════════════════════════════════════

def extract_sector_metrics(state: dict) -> dict:
    """Extract sector metrics from state."""
    result = {}
    
    # Amplitude
    result['assignment_rate'] = state.get('assignment_rate', 0)
    result['throughput'] = state.get('assignment_rate', 0) * state.get('n_active', 0)
    result['allocation_entropy'] = state.get('allocation_entropy', 0)
    
    # Topology
    result['connectivity'] = state.get('connectivity', 0)
    result['n_components'] = state.get('n_components', 0)
    result['routing_entropy'] = state.get('routing_entropy', 0)
    
    # Transport
    eigenvalues = state.get('cov_eigenvalues', [0])
    if isinstance(eigenvalues, list) and len(eigenvalues) > 0:
        ev = np.array(eigenvalues)
        result['cov_trace'] = float(np.sum(np.abs(ev)))
        result['cov_condition'] = float(ev[0] / (ev[-1] + 1e-10)) if len(ev) > 1 else 1.0
    else:
        result['cov_trace'] = 0
        result['cov_condition'] = 1.0
    
    # Residual
    if isinstance(eigenvalues, list) and len(eigenvalues) > 3:
        ev = np.array(eigenvalues)
        total = np.sum(np.abs(ev))
        residual = np.sum(np.abs(ev[3:]))
        result['residual_energy'] = float(residual / (total + 1e-10))
    else:
        result['residual_energy'] = 0
    
    return result


def compute_sector_alignment(before_metrics: list, after_metrics: list) -> dict:
    """Compute sector alignment."""
    sectors = {
        'amplitude': ['assignment_rate', 'throughput', 'allocation_entropy'],
        'topology': ['connectivity', 'n_components', 'routing_entropy'],
        'transport': ['cov_trace', 'cov_condition'],
        'residual': ['residual_energy'],
    }
    
    results = {}
    
    for sector_name, metrics in sectors.items():
        before_vectors = []
        after_vectors = []
        
        for m in metrics:
            before_vals = [bm.get(m, 0) for bm in before_metrics]
            after_vals = [am.get(m, 0) for am in after_metrics]
            before_vectors.append(before_vals)
            after_vectors.append(after_vals)
        
        before_arr = np.array(before_vectors).T
        after_arr = np.array(after_vectors).T
        
        if before_arr.size == 0 or after_arr.size == 0:
            results[sector_name] = {'error': 'no data'}
            continue
        
        min_len = min(len(before_arr), len(after_arr))
        before_arr = before_arr[:min_len]
        after_arr = after_arr[:min_len]
        
        def cosine_sim(a, b):
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            if na == 0 or nb == 0:
                return 0.0
            return float(np.dot(a.flatten(), b.flatten()) / (na * nb))
        
        raw_sim = cosine_sim(before_arr, after_arr)
        
        before_norm = (before_arr - before_arr.mean(axis=0)) / (before_arr.std(axis=0) + 1e-8)
        after_norm = (after_arr - after_arr.mean(axis=0)) / (after_arr.std(axis=0) + 1e-8)
        norm_sim = cosine_sim(before_norm, after_norm)
        
        norm_survival = norm_sim - raw_sim
        
        results[sector_name] = {
            'raw_similarity': raw_sim,
            'normalized_similarity': norm_sim,
            'normalization_survival': norm_survival,
            'verdict': 'SURVIVES' if norm_survival > -0.1 else 'COLLAPSES',
        }
    
    return results


def compute_gauge_fraction(sector_data: dict) -> float:
    """Compute gauge-stable persistence fraction."""
    sectors = ['amplitude', 'topology', 'transport', 'residual']
    surviving = 0
    total = 0
    
    for sector in sectors:
        data = sector_data.get(sector, {})
        if 'error' in data:
            continue
        total += 1
        if data.get('verdict') == 'SURVIVES':
            surviving += 1
    
    return surviving / max(total, 1)


# ═══════════════════════════════════════════════════════════════════
# Experimental Framework
# ═══════════════════════════════════════════════════════════════════

def run_single_experiment(variant: str, constraint_density: float, 
                          perturbation_protocol, severity: float,
                          seed: int = 42) -> dict:
    """Run a single experimental condition."""
    # Create system
    system = DistributedSystem(n_nodes=100, seed=seed)
    system.generate_tasks(n_tasks=100)
    
    # Create constraint injector
    injector = ConstraintInjector(
        system,
        bounded=(variant in ['bounded-only', 'combined']),
        threshold=(variant in ['threshold-only', 'combined']),
        conservation=(variant in ['conservation-only', 'combined']),
        constraint_density=constraint_density
    )
    
    # Establish baseline (20 timesteps)
    history_before = []
    for _ in range(20):
        injector.apply_constraints()
        state = system.step()
        history_before.append(extract_sector_metrics(state))
    
    # Apply perturbation
    perturbation_protocol.apply(system, severity)
    
    # Measure recovery (50 timesteps)
    history_after = []
    for _ in range(50):
        injector.apply_constraints()
        state = system.step()
        history_after.append(extract_sector_metrics(state))
    
    # Compute sector alignment
    sector_results = compute_sector_alignment(history_before, history_after)
    
    # Compute gauge fraction
    G = compute_gauge_fraction(sector_results)
    
    # Compute structural persistence
    topo = sector_results.get('topology', {})
    S = max(0, topo.get('normalized_similarity', 0))
    
    # Compute functional persistence
    amp = sector_results.get('amplitude', {})
    F = max(0, amp.get('normalized_similarity', 0))
    
    return {
        'variant': variant,
        'constraint_density': constraint_density,
        'G': G,
        'S': S,
        'F': F,
        'sectors': sector_results,
    }


def run_constraint_injection_study():
    """Run the complete constraint injection study."""
    print("=" * 70)
    print("Study 001E: Constraint Injection Framework")
    print("=" * 70)
    
    # Pre-registered hypotheses
    print("\n  CAUSAL HYPOTHESES:")
    print("  H1: Bounded activation increases G")
    print("  H2: Threshold gating increases cross-sector stability")
    print("  H3: Conservation laws increase topology persistence")
    print("  ")
    print("  CRITICAL TEST: Does G rise continuously or discontinuously?")
    
    # Experimental design
    variants = ['baseline', 'bounded-only', 'threshold-only', 'conservation-only', 'combined']
    densities = [0.0, 0.25, 0.5, 0.75, 1.0]
    perturbation = NodeRemoval
    severity = 0.3
    
    all_results = []
    
    for variant in variants:
        print(f"\n{'─' * 50}")
        print(f"Variant: {variant}")
        print(f"{'─' * 50}")
        
        for density in densities:
            result = run_single_experiment(variant, density, perturbation, severity)
            all_results.append(result)
            
            print(f"  Φ={density:.2f}: G={result['G']:.3f}  S={result['S']:.3f}  F={result['F']:.3f}")
    
    # ─── G(Φ) Curve Analysis ───
    print(f"\n{'=' * 70}")
    print("G(Φ) CURVE ANALYSIS")
    print(f"{'=' * 70}")
    
    # Group by variant
    variant_curves = {}
    for result in all_results:
        variant = result['variant']
        if variant not in variant_curves:
            variant_curves[variant] = {'densities': [], 'G': [], 'S': [], 'F': []}
        variant_curves[variant]['densities'].append(result['constraint_density'])
        variant_curves[variant]['G'].append(result['G'])
        variant_curves[variant]['S'].append(result['S'])
        variant_curves[variant]['F'].append(result['F'])
    
    # Compute G range for each variant
    for variant, data in variant_curves.items():
        G_min = min(data['G'])
        G_max = max(data['G'])
        G_range = G_max - G_min
        
        # Classify transition type
        G_values = data['G']
        diffs = np.diff(G_values)
        max_jump = max(diffs) if len(diffs) > 0 else 0
        
        if G_range < 0.1:
            transition = "NONE"
        elif max_jump > 0.3:
            transition = "DISCONTINUOUS"
        else:
            transition = "CONTINUOUS"
        
        print(f"\n  {variant}:")
        print(f"    G range: [{G_min:.3f}, {G_max:.3f}] (Δ={G_range:.3f})")
        print(f"    Max jump: {max_jump:.3f}")
        print(f"    Transition: {transition}")
    
    # ─── Causal Hypothesis Tests ───
    print(f"\n{'=' * 70}")
    print("CAUSAL HYPOTHESIS TESTS")
    print(f"{'=' * 70}")
    
    # H1: Bounded activation increases G
    baseline_G = [r['G'] for r in all_results if r['variant'] == 'baseline']
    bounded_G = [r['G'] for r in all_results if r['variant'] == 'bounded-only']
    h1_effect = np.mean(bounded_G) - np.mean(baseline_G)
    print(f"\n  H1: Bounded activation increases G")
    print(f"      Baseline G={np.mean(baseline_G):.3f}, Bounded G={np.mean(bounded_G):.3f}")
    print(f"      Effect: {h1_effect:+.3f} → {'SUPPORTED' if h1_effect > 0.1 else 'NOT SUPPORTED'}")
    
    # H2: Threshold gating increases cross-sector stability
    threshold_G = [r['G'] for r in all_results if r['variant'] == 'threshold-only']
    h2_effect = np.mean(threshold_G) - np.mean(baseline_G)
    print(f"\n  H2: Threshold gating increases cross-sector stability")
    print(f"      Baseline G={np.mean(baseline_G):.3f}, Threshold G={np.mean(threshold_G):.3f}")
    print(f"      Effect: {h2_effect:+.3f} → {'SUPPORTED' if h2_effect > 0.1 else 'NOT SUPPORTED'}")
    
    # H3: Conservation laws increase topology persistence
    conservation_S = [r['S'] for r in all_results if r['variant'] == 'conservation-only']
    baseline_S = [r['S'] for r in all_results if r['variant'] == 'baseline']
    h3_effect = np.mean(conservation_S) - np.mean(baseline_S)
    print(f"\n  H3: Conservation laws increase topology persistence")
    print(f"      Baseline S={np.mean(baseline_S):.3f}, Conservation S={np.mean(conservation_S):.3f}")
    print(f"      Effect: {h3_effect:+.3f} → {'SUPPORTED' if h3_effect > 0.1 else 'NOT SUPPORTED'}")
    
    # ─── Combined Effect ───
    combined_G = [r['G'] for r in all_results if r['variant'] == 'combined']
    combined_S = [r['S'] for r in all_results if r['variant'] == 'combined']
    combined_F = [r['F'] for r in all_results if r['variant'] == 'combined']
    
    print(f"\n  COMBINED EFFECT:")
    print(f"    G={np.mean(combined_G):.3f} (baseline: {np.mean(baseline_G):.3f})")
    print(f"    S={np.mean(combined_S):.3f} (baseline: {np.mean(baseline_S):.3f})")
    print(f"    F={np.mean(combined_F):.3f}")
    
    # ─── Regime Transition Analysis ───
    print(f"\n{'=' * 70}")
    print("REGIME TRANSITION ANALYSIS")
    print(f"{'=' * 70}")
    
    # Load existing systems
    with open('/home/student/sgp_core_v2/post_omega_study_001/gauge_geometry_results.json', 'r') as f:
        geometry = json.load(f)
    
    # Add constraint-injected systems
    for variant in ['bounded-only', 'threshold-only', 'conservation-only', 'combined']:
        variant_data = variant_curves[variant]
        # Take the highest density result
        max_idx = variant_data['densities'].index(max(variant_data['densities']))
        
        geometry[f'Constraint-{variant}'] = {
            'S': float(variant_data['S'][max_idx]),
            'F': float(variant_data['F'][max_idx]),
            'G': float(variant_data['G'][max_idx]),
            'regime': 'engineered',
        }
    
    print(f"\n  PERSISTENCE ALLOCATION LANDSCAPE (all systems):")
    for name, data in geometry.items():
        print(f"    {name:25s}: S={data['S']:.3f}  F={data['F']:.3f}  G={data['G']:.3f}  regime={data['regime']}")
    
    # ─── Scientific Verdict ───
    print(f"\n{'=' * 70}")
    print("SCIENTIFIC VERDICT")
    print(f"{'=' * 70}")
    
    max_G_achieved = max(r['G'] for r in all_results)
    immune_G = geometry.get('Immune System', {}).get('G', 0)
    
    print(f"\n  Maximum G achieved: {max_G_achieved:.3f}")
    print(f"  Immune system G: {immune_G:.3f}")
    print(f"  ")
    
    if max_G_achieved > immune_G * 0.8:
        print(f"  OUTCOME A: Engineered gauge stability")
        print(f"  High-G persistence is constructible through constraints.")
    elif max_G_achieved < 0.4:
        print(f"  OUTCOME B: Structural barrier")
        print(f"  Immune systems possess deeper organizational principles.")
    else:
        print(f"  OUTCOME C: Partial engineering")
        print(f"  G can be increased but not to immune levels.")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/constraint_injection_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    with open('/home/student/sgp_core_v2/post_omega_study_001/gauge_geometry_results.json', 'w') as f:
        json.dump(geometry, f, indent=2)
    
    print(f"\nResults saved")
    print(f"{'=' * 70}")
    
    return all_results, geometry


if __name__ == '__main__':
    run_constraint_injection_study()
