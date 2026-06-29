"""
Phase 003 Division A — Synthetic Ensemble Generator

Generate randomized organizational systems to test whether G ∝ 1/H
is statistically real or an artifact of limited system selection.

Systems vary:
- memory depth (0 = memoryless to 20)
- coupling topology (random, scale-free, small-world, none)
- adaptation rate (0.0 to 1.0)
- stochasticity (0.0 to 1.0)
- replay dependence (0.0 to 1.0)

Controls:
- memoryless systems (memory_depth = 0)
- purely stochastic systems (adaptation = 0, stochasticity = 1)
- shuffled-history systems (history shuffled each step)
"""

import numpy as np
import json
import os
import sys
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

sys.path.insert(0, '/home/student/SGI-Persistence/src')
from geometry.connection_formalism import build_bundle, state_to_vector
from geometry.discrete_transport import DiscreteTransportAlgebra


# ═══════════════════════════════════════════════════════════════════
# Synthetic System Generator
# ═══════════════════════════════════════════════════════════════════

@dataclass
class SyntheticSystemParams:
    """Parameters for a synthetic organizational system."""
    n_nodes: int = 50
    memory_depth: int = 10
    coupling_type: str = 'random'  # random, scale_free, small_world, none
    adaptation_rate: float = 0.5
    stochasticity: float = 0.3
    replay_dependence: float = 0.7
    n_timesteps: int = 50
    seed: int = 42


class SyntheticEnsembleGenerator:
    """
    Generate synthetic organizational systems with controlled parameters.
    
    Each system produces a trajectory of state dicts suitable for
    build_bundle() and transport analysis.
    """
    
    def __init__(self, base_seed: int = 42):
        self.base_seed = base_seed
    
    def generate_system(self, params: SyntheticSystemParams) -> List[Dict]:
        """Generate a single synthetic system trajectory."""
        rng = np.random.RandomState(params.seed)
        n = params.n_nodes
        t = params.n_timesteps
        
        # Build coupling matrix
        coupling = self._build_coupling(n, params.coupling_type, rng)
        
        # Initialize state
        state = rng.uniform(0.1, 1.0, n)
        trajectory = []
        
        for step in range(t):
            # Record observable state
            obs = self._observe(state, rng)
            trajectory.append(obs)
            
            # Update state
            if params.stochasticity > 0:
                noise = rng.randn(n) * params.stochasticity * 0.1
            else:
                noise = np.zeros(n)
            
            # Coupling: state influenced by neighbors
            coupled = coupling @ state / (np.sum(coupling, axis=1) + 1e-10)
            
            # Memory: blend with history
            if params.memory_depth > 0 and len(trajectory) >= params.memory_depth:
                history_raw = []
                for tr in trajectory[-params.memory_depth:]:
                    if '_raw' in tr:
                        history_raw.append(tr['_raw'])
                history_mean = np.mean(history_raw, axis=0) if history_raw else state
                memory_blend = params.replay_dependence * history_mean + (1 - params.replay_dependence) * state
            else:
                memory_blend = state
            
            # Adaptation
            state = (1 - params.adaptation_rate) * state + \
                    params.adaptation_rate * coupled + \
                    noise + \
                    0.1 * (memory_blend - state)
            
            state = np.clip(state, 0.01, 10.0)
            
            # Store raw for memory computation
            trajectory[-1]['_raw'] = state.copy()
        
        # Clean _raw from output
        for obs in trajectory:
            obs.pop('_raw', None)
        
        return trajectory
    
    def _build_coupling(self, n: int, ctype: str, rng: np.random.RandomState) -> np.ndarray:
        """Build coupling matrix based on topology type."""
        if ctype == 'none':
            return np.eye(n)
        
        elif ctype == 'random':
            C = rng.random((n, n))
            C = (C + C.T) / 2
            C = (C > 0.7).astype(float)
            np.fill_diagonal(C, 0)
            return C + np.eye(n)
        
        elif ctype == 'scale_free':
            # Barabasi-Albert approximation
            C = np.zeros((n, n))
            m = 3
            for i in range(m, n):
                probs = np.sum(C[:i], axis=0) + 1e-10
                probs = probs[:i]
                probs = probs / probs.sum()
                targets = rng.choice(i, size=min(m, i), replace=False, p=probs)
                for t in targets:
                    C[i, t] = 1
                    C[t, i] = 1
            np.fill_diagonal(C, 1)
            return C
        
        elif ctype == 'small_world':
            # Watts-Strogatz approximation
            C = np.zeros((n, n))
            k = 4
            for i in range(n):
                for j in range(1, k // 2 + 1):
                    C[i, (i + j) % n] = 1
                    C[i, (i - j) % n] = 1
            # Rewire
            for i in range(n):
                for j in range(n):
                    if C[i, j] == 1 and rng.random() < 0.1:
                        C[i, j] = 0
                        new_j = rng.randint(0, n)
                        C[i, new_j] = 1
                        C[new_j, i] = 1
            np.fill_diagonal(C, 1)
            return C
        
        return np.eye(n)
    
    def _observe(self, state: np.ndarray, rng: np.random.RandomState) -> Dict:
        """Convert raw state to observable dict."""
        n = len(state)
        return {
            'connectivity': float(np.mean(state)),
            'n_active': float(np.sum(state > 0.5)),
            'routing_entropy': float(-np.sum(state / np.sum(state) * np.log(state / np.sum(state) + 1e-10))),
            'assignment_rate': float(np.mean(np.abs(np.diff(state)))),
            'allocation_entropy': float(rng.uniform(0, 2)),
            'mean_activation': float(np.mean(state)),
            'type_entropy': float(rng.uniform(0, 1.5)),
            'efficiency': float(1.0 / (1.0 + np.std(state))),
        }
    
    def generate_ensemble(self, n_systems: int = 100) -> List[Tuple[SyntheticSystemParams, List[Dict]]]:
        """Generate full ensemble of synthetic systems."""
        ensemble = []
        
        for i in range(n_systems):
            params = SyntheticSystemParams(
                seed=self.base_seed + i,
                memory_depth=int(np.random.choice([0, 2, 5, 10, 15, 20])),
                coupling_type=np.random.choice(['random', 'scale_free', 'small_world', 'none']),
                adaptation_rate=np.random.uniform(0.0, 1.0),
                stochasticity=np.random.uniform(0.0, 1.0),
                replay_dependence=np.random.uniform(0.0, 1.0),
            )
            trajectory = self.generate_system(params)
            ensemble.append((params, trajectory))
        
        return ensemble
    
    def generate_controls(self, n_per_class: int = 20) -> List[Tuple[str, SyntheticSystemParams, List[Dict]]]:
        """Generate control systems."""
        controls = []
        
        # Memoryless systems
        for i in range(n_per_class):
            params = SyntheticSystemParams(
                seed=self.base_seed + 1000 + i,
                memory_depth=0,
                replay_dependence=0.0,
            )
            trajectory = self.generate_system(params)
            controls.append(('memoryless', params, trajectory))
        
        # Purely stochastic systems
        for i in range(n_per_class):
            params = SyntheticSystemParams(
                seed=self.base_seed + 2000 + i,
                adaptation_rate=0.0,
                stochasticity=1.0,
                replay_dependence=0.0,
            )
            trajectory = self.generate_system(params)
            controls.append(('pure_stochastic', params, trajectory))
        
        # Shuffled-history systems
        for i in range(n_per_class):
            params = SyntheticSystemParams(
                seed=self.base_seed + 3000 + i,
                memory_depth=10,
                replay_dependence=0.7,
            )
            trajectory = self.generate_system(params)
            # Shuffle history: randomize order of trajectory
            rng = np.random.RandomState(params.seed + 500)
            indices = np.arange(len(trajectory))
            rng.shuffle(indices)
            trajectory = [trajectory[j] for j in indices]
            controls.append(('shuffled_history', params, trajectory))
        
        return controls


# ═══════════════════════════════════════════════════════════════════
# Metric Computation
# ═══════════════════════════════════════════════════════════════════

def compute_G(trajectory: List[Dict]) -> float:
    """Compute organizational replay stability using sector alignment.
    
    This matches the original G computation from study_001i_entanglement.py.
    """
    if len(trajectory) < 10:
        return 0.0
    
    # Sector definitions
    SECTORS = {
        'amplitude': ['mean_activation', 'n_active'],
        'topology': ['connectivity', 'n_components'],
        'transport': ['cov_trace', 'cov_condition'],
        'residual': ['non_principal'],
    }
    
    def extract_metrics(s):
        return {k: v for k, v in s.items() if k not in ('timestep', 'cov_eigenvalues')}
    
    def sector_align(before, after):
        results = {}
        for sn, metrics in SECTORS.items():
            bv = np.array([[bm.get(m, 0) for bm in before] for m in metrics]).T
            av = np.array([[am.get(m, 0) for am in after] for m in metrics]).T
            if bv.size == 0 or av.size == 0:
                results[sn] = {'error': 'no data'}
                continue
            ml = min(len(bv), len(av))
            bv, av = bv[:ml], av[:ml]
            
            def cs(a, b):
                na, nb = np.linalg.norm(a), np.linalg.norm(b)
                return float(np.dot(a.flatten(), b.flatten()) / (na * nb)) if na > 0 and nb > 0 else 0.0
            
            raw = cs(bv, av)
            bn = (bv - bv.mean(0)) / (bv.std(0) + 1e-8)
            an = (av - av.mean(0)) / (av.std(0) + 1e-8)
            norm = cs(bn, an)
            results[sn] = {
                'verdict': 'SURVIVES' if norm - raw > -0.1 else 'COLLAPSES',
                'norm_survival': norm - raw
            }
        return results
    
    def gauge_frac(sd):
        surv = sum(1 for s in SECTORS.keys() 
                   if sd.get(s, {}).get('verdict') == 'SURVIVES')
        return surv / len(SECTORS)
    
    # Split into before/after
    mid = len(trajectory) // 2
    before = [extract_metrics(s) for s in trajectory[:mid]]
    after = [extract_metrics(s) for s in trajectory[mid:]]
    
    sr = sector_align(before, after)
    return gauge_frac(sr)


def compute_H(trajectory: List[Dict]) -> float:
    """Compute historical residue coupling."""
    if len(trajectory) < 10:
        return 0.0
    
    vectors = [state_to_vector(tr) for tr in trajectory]
    correlations = []
    
    for i in range(5, len(vectors)):
        current = vectors[i]
        history = np.mean(vectors[max(0, i - 5):i], axis=0)
        corr = np.corrcoef(current, history)[0, 1]
        if np.isfinite(corr):
            correlations.append(abs(corr))
    
    return float(np.mean(correlations)) if correlations else 0.0


def compute_TE(trajectory: List[Dict]) -> float:
    """Compute transport error."""
    try:
        states, fibers, connection = build_bundle(trajectory, memory_depth=5)
        errors = []
        for i in range(len(states) - 1):
            te = connection.compute_transport_error(fibers[i], fibers[i + 1])
            errors.append(te)
        return float(np.mean(errors)) if errors else 0.0
    except Exception:
        return 0.0


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main():
    print("Phase 003 Division A — Synthetic Ensemble Generator")
    print("=" * 60)
    
    generator = SyntheticEnsembleGenerator(base_seed=42)
    
    # Generate ensemble
    print("\nGenerating 100 synthetic systems...")
    ensemble = generator.generate_ensemble(n_systems=100)
    print(f"  Generated {len(ensemble)} systems")
    
    # Generate controls
    print("\nGenerating control systems...")
    controls = generator.generate_controls(n_per_class=20)
    print(f"  Generated {len(controls)} controls")
    
    # Compute metrics
    print("\nComputing metrics...")
    results = []
    
    for i, (params, traj) in enumerate(ensemble):
        G = compute_G(traj)
        H = compute_H(traj)
        TE = compute_TE(traj)
        results.append({
            'system_id': f'synthetic_{i:03d}',
            'params': {
                'memory_depth': params.memory_depth,
                'coupling_type': params.coupling_type,
                'adaptation_rate': round(params.adaptation_rate, 3),
                'stochasticity': round(params.stochasticity, 3),
                'replay_dependence': round(params.replay_dependence, 3),
            },
            'G': round(G, 4),
            'H': round(H, 4),
            'TE': round(TE, 4),
            'GH': round(G * H, 4),
        })
        if (i + 1) % 20 == 0:
            print(f"  Processed {i + 1}/100")
    
    # Compute controls
    control_results = []
    for ctype, params, traj in controls:
        G = compute_G(traj)
        H = compute_H(traj)
        TE = compute_TE(traj)
        control_results.append({
            'control_type': ctype,
            'G': round(G, 4),
            'H': round(H, 4),
            'TE': round(TE, 4),
            'GH': round(G * H, 4),
        })
    
    # Save results
    output = {
        'ensemble': results,
        'controls': control_results,
        'summary': {
            'n_systems': len(results),
            'n_controls': len(control_results),
            'ensemble_GH_correlation': float(np.corrcoef(
                [r['G'] for r in results],
                [1.0 / (r['H'] + 1e-10) for r in results]
            )[0, 1]),
        }
    }
    
    outpath = '/home/student/SGI-Persistence/experiments/validation/ensemble_results.json'
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to {outpath}")
    print(f"Ensemble G-1/H correlation: {output['summary']['ensemble_GH_correlation']:.4f}")
    
    return output


if __name__ == '__main__':
    main()
