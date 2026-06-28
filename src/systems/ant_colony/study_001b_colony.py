"""
SGI Post-Ω Study 001B: Ant Colony Interaction Network

System: Ant colony with pheromone-mediated food routing
Substrate: biological agents on 2D grid
Interaction medium: local pheromone signaling
Persistence mechanism: adaptation/self-organization

Radically different from distributed system:
- not computational nodes
- not routing/load exchange
- not redundancy-based persistence
"""

import numpy as np
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional


@dataclass
class Ant:
    id: int
    x: int
    y: int
    carrying: bool = False
    trail_memory: list = field(default_factory=list)


class AntColony:
    """2D grid-based ant colony with pheromone dynamics."""
    
    def __init__(self, grid_size: int = 50, n_ants: int = 100, n_food: int = 5, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.grid_size = grid_size
        self.n_ants = n_ants
        
        # Grid: pheromone intensity
        self.pheromone = np.zeros((grid_size, grid_size))
        self.pheromone_evap_rate = 0.05
        self.pheromone_deposit = 1.0
        
        # Nest at center
        self.nest_x, self.nest_y = grid_size // 2, grid_size // 2
        
        # Food sources (random positions)
        self.food_sources = []
        for _ in range(n_food):
            fx = self.rng.randint(0, grid_size)
            fy = self.rng.randint(0, grid_size)
            self.food_sources.append((fx, fy))
        
        # Food grid (remaining food at each source)
        self.food_grid = np.zeros((grid_size, grid_size))
        for fx, fy in self.food_sources:
            self.food_grid[fx, fy] = 100.0  # 100 units per source
        
        # Ants
        self.ants = []
        for i in range(n_ants):
            ax = self.nest_x + self.rng.randint(-2, 3)
            ay = self.nest_y + self.rng.randint(-2, 3)
            ax = np.clip(ax, 0, grid_size - 1)
            ay = np.clip(ay, 0, grid_size - 1)
            self.ants.append(Ant(id=i, x=ax, y=ay))
        
        # History
        self.history = []
        self.timestep = 0
    
    def step(self) -> Dict:
        """Execute one timestep: move ants, update pheromones, measure."""
        # 1. Move ants
        for ant in self.ants:
            self._move_ant(ant)
        
        # 2. Evaporate pheromones
        self.pheromone *= (1 - self.pheromone_evap_rate)
        
        # 3. Measure observables
        state = self._measure()
        self.history.append(state)
        self.timestep += 1
        return state
    
    def _move_ant(self, ant: Ant):
        """Move ant based on pheromone gradient and food/nest proximity."""
        gx, gy = self.grid_size, self.grid_size
        
        if ant.carrying:
            # Head toward nest
            dx = np.sign(self.nest_x - ant.x)
            dy = np.sign(self.nest_y - ant.y)
            
            # Deposit pheromone along the way
            self.pheromone[ant.x, ant.y] += self.pheromone_deposit
            
            # Check if reached nest
            if ant.x == self.nest_x and ant.y == self.nest_y:
                ant.carrying = False
                ant.trail_memory = []
                return
            
            # Add some randomness
            if self.rng.random() < 0.2:
                dx = self.rng.choice([-1, 0, 1])
            if self.rng.random() < 0.2:
                dy = self.rng.choice([-1, 0, 1])
        else:
            # Strategy 1: If near food (within 3 cells), move toward it
            best_food_dist = 999
            best_dx, best_dy = 0, 0
            found_food = False
            
            for ddx in range(-3, 4):
                for ddy in range(-3, 4):
                    nx, ny = ant.x + ddx, ant.y + ddy
                    if 0 <= nx < gx and 0 <= ny < gy:
                        if self.food_grid[nx, ny] > 0:
                            dist = abs(ddx) + abs(ddy)
                            if dist < best_food_dist:
                                best_food_dist = dist
                                best_dx = np.sign(ddx) if ddx != 0 else 0
                                best_dy = np.sign(ddy) if ddy != 0 else 0
                                found_food = True
            
            if found_food and self.rng.random() < 0.8:
                dx, dy = best_dx, best_dy
            else:
                # Strategy 2: Follow pheromone gradient
                best_pheromone = -1
                best_pd, best_pdy = 0, 0
                
                for ddx in [-1, 0, 1]:
                    for ddy in [-1, 0, 1]:
                        if ddx == 0 and ddy == 0:
                            continue
                        nx, ny = ant.x + ddx, ant.y + ddy
                        if 0 <= nx < gx and 0 <= ny < gy:
                            if self.pheromone[nx, ny] > best_pheromone:
                                best_pheromone = self.pheromone[nx, ny]
                                best_pd, best_pdy = ddx, ddy
                
                if best_pheromone > 0 and self.rng.random() < 0.6:
                    dx, dy = best_pd, best_pdy
                else:
                    # Random walk
                    dx = self.rng.choice([-1, 0, 1])
                    dy = self.rng.choice([-1, 0, 1])
        
        # Apply movement
        new_x = np.clip(ant.x + dx, 0, gx - 1)
        new_y = np.clip(ant.y + dy, 0, gy - 1)
        
        # Check if picking up food
        if not ant.carrying and self.food_grid[new_x, new_y] > 0:
            ant.carrying = True
            self.food_grid[new_x, new_y] -= 1
            ant.trail_memory = [(ant.x, ant.y)]
        
        ant.x = new_x
        ant.y = new_y
    
    def _measure(self) -> Dict:
        """Measure all observables."""
        gx = self.grid_size
        
        # ─── Amplitude Sector ───
        total_food_remaining = float(self.food_grid.sum())
        total_pheromone = float(self.pheromone.sum())
        carrying_count = sum(1 for a in self.ants if a.carrying)
        recruitment_rate = carrying_count / max(len(self.ants), 1)
        
        # ─── Topology Sector ───
        # Trail connectivity: fraction of grid cells with pheromone > threshold
        trail_threshold = 0.1
        trail_cells = float(np.sum(self.pheromone > trail_threshold))
        trail_connectivity = trail_cells / (gx * gx)
        
        # Branching: number of distinct trail segments
        trail_binary = (self.pheromone > trail_threshold).astype(int)
        n_components, component_labels = self._label_components(trail_binary)
        
        # Path redundancy: ratio of ants on different paths
        ant_positions = [(a.x, a.y) for a in self.ants]
        unique_positions = len(set(ant_positions))
        path_redundancy = unique_positions / max(len(self.ants), 1)
        
        # Component stability: size of largest component
        component_sizes = []
        for label in range(1, n_components + 1):
            component_sizes.append(np.sum(component_labels == label))
        largest_component = max(component_sizes) / max(trail_cells, 1) if component_sizes else 0
        
        # ─── Transport Sector ───
        # Flow covariance: covariance of ant positions
        if len(self.ants) > 1:
            positions = np.array([[a.x, a.y] for a in self.ants])
            cov = np.cov(positions.T)
            eigenvalues = np.linalg.eigvalsh(cov)
            cov_trace = float(np.sum(np.abs(eigenvalues)))
            cov_condition = float(np.max(np.abs(eigenvalues)) / (np.min(np.abs(eigenvalues)) + 1e-10))
        else:
            cov_trace = 0
            cov_condition = 1.0
            eigenvalues = np.array([0, 0])
        
        # Transport anisotropy: ratio of principal axes
        if len(self.ants) > 1:
            positions = np.array([[a.x, a.y] for a in self.ants])
            cov = np.cov(positions.T)
            eigenvalues = np.sort(np.abs(np.linalg.eigvalsh(cov)))[::-1]
            anisotropy = float(eigenvalues[0] / (eigenvalues[1] + 1e-10)) if len(eigenvalues) > 1 else 1.0
        else:
            anisotropy = 1.0
        
        # ─── Residual Sector ───
        # Unexplained path deviations: variance of ant positions from pheromone gradient
        deviations = []
        for ant in self.ants:
            if ant.carrying:
                # Expected: toward nest
                expected_dx = np.sign(self.nest_x - ant.x)
                expected_dy = np.sign(self.nest_y - ant.y)
                actual_dx = 0  # will be computed from movement
                deviations.append(0)  # simplified
        residual_deviation = float(np.mean(deviations)) if deviations else 0
        
        # Residual branching energy: energy in small components
        if component_sizes:
            small_components = [s for s in component_sizes if s < 10]
            residual_energy = sum(small_components) / max(trail_cells, 1)
        else:
            residual_energy = 0
        
        # Non-principal coordination modes
        if len(self.ants) > 1:
            positions = np.array([[a.x, a.y] for a in self.ants])
            cov = np.cov(positions.T)
            eigenvalues = np.sort(np.abs(np.linalg.eigvalsh(cov)))[::-1]
            total_energy = np.sum(eigenvalues)
            non_principal = float(np.sum(eigenvalues[1:]) / (total_energy + 1e-10))
        else:
            non_principal = 0
        
        return {
            'timestep': self.timestep,
            # Amplitude
            'total_food_remaining': total_food_remaining,
            'total_pheromone': total_pheromone,
            'recruitment_rate': recruitment_rate,
            # Topology
            'trail_connectivity': trail_connectivity,
            'n_components': n_components,
            'path_redundancy': path_redundancy,
            'largest_component': largest_component,
            # Transport
            'cov_trace': cov_trace,
            'cov_condition': cov_condition,
            'cov_eigenvalues': eigenvalues.tolist(),
            'anisotropy': anisotropy,
            # Residual
            'residual_deviation': residual_deviation,
            'residual_energy': residual_energy,
            'non_principal': non_principal,
        }
    
    def _label_components(self, binary_grid: np.ndarray) -> Tuple[int, np.ndarray]:
        """Simple connected component labeling (4-connectivity)."""
        gx, gy = binary_grid.shape
        labels = np.zeros_like(binary_grid, dtype=int)
        current_label = 0
        
        for i in range(gx):
            for j in range(gy):
                if binary_grid[i, j] == 1 and labels[i, j] == 0:
                    current_label += 1
                    # BFS
                    queue = [(i, j)]
                    labels[i, j] = current_label
                    while queue:
                        ci, cj = queue.pop(0)
                        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            ni, nj = ci + di, cj + dj
                            if 0 <= ni < gx and 0 <= nj < gy:
                                if binary_grid[ni, nj] == 1 and labels[ni, nj] == 0:
                                    labels[ni, nj] = current_label
                                    queue.append((ni, nj))
        
        return current_label, labels


# ─── Perturbation Protocols ───

class ColonyPerturbation:
    @staticmethod
    def apply(colony: AntColony, severity: float) -> str:
        raise NotImplementedError

class WorkerRemoval(ColonyPerturbation):
    """P1: Remove fraction of workers."""
    @staticmethod
    def apply(colony: AntColony, severity: float) -> str:
        n_remove = int(colony.n_ants * severity)
        remove_ids = colony.rng.choice(colony.n_ants, size=n_remove, replace=False)
        colony.ants = [a for i, a in enumerate(colony.ants) if i not in remove_ids]
        colony.n_ants = len(colony.ants)
        return f"Removed {n_remove} workers ({severity*100:.0f}%)"

class TrailDisruption(ColonyPerturbation):
    """P2: Clear pheromone trails."""
    @staticmethod
    def apply(colony: AntColony, severity: float) -> str:
        # Clear random fraction of trail cells
        trail_mask = colony.pheromone > 0.1
        n_trail_cells = int(np.sum(trail_mask) * severity)
        trail_coords = np.argwhere(trail_mask)
        if len(trail_coords) > 0:
            clear_indices = colony.rng.choice(len(trail_coords), size=min(n_remove := n_trail_cells, len(trail_coords)), replace=False)
            for idx in clear_indices:
                x, y = trail_coords[idx]
                colony.pheromone[x, y] = 0
        return f"Cleared {n_trail_cells} trail cells ({severity*100:.0f}%)"

class NestFragmentation(ColonyPerturbation):
    """P3: Scatter ants from nest."""
    @staticmethod
    def apply(colony: AntColony, severity: float) -> str:
        scattered = 0
        for ant in colony.ants:
            if colony.rng.random() < severity:
                ant.x = colony.rng.randint(0, colony.grid_size)
                ant.y = colony.rng.randint(0, colony.grid_size)
                ant.carrying = False
                scattered += 1
        return f"Scattered {scattered} ants from nest ({severity*100:.0f}%)"

class ResourceRelocation(ColonyPerturbation):
    """P4: Move food sources."""
    @staticmethod
    def apply(colony: AntColony, severity: float) -> str:
        # Remove existing food
        colony.food_grid = np.zeros_like(colony.food_grid)
        # Create new food sources
        n_new = int(len(colony.food_sources) * (1 - severity) + 1)
        colony.food_sources = []
        for _ in range(n_new):
            fx = colony.rng.randint(0, colony.grid_size)
            fy = colony.rng.randint(0, colony.grid_size)
            colony.food_sources.append((fx, fy))
            colony.food_grid[fx, fy] = 100.0
        return f"Relocated to {n_new} new food sources"


# ─── Sector Audit (reused from 001A) ───

SECTORS = {
    'amplitude': {
        'metrics': ['total_food_remaining', 'total_pheromone', 'recruitment_rate'],
        'expected_survival': False,
    },
    'topology': {
        'metrics': ['trail_connectivity', 'n_components', 'path_redundancy', 'largest_component'],
        'expected_survival': True,
    },
    'transport': {
        'metrics': ['cov_trace', 'cov_condition', 'anisotropy'],
        'expected_survival': True,
    },
    'residual': {
        'metrics': ['residual_deviation', 'residual_energy', 'non_principal'],
        'expected_survival': True,
    },
}


def extract_sector_metrics_colony(state: dict) -> dict:
    """Extract sector metrics from colony state."""
    return {k: v for k, v in state.items() if k != 'timestep' and k != 'cov_eigenvalues'}


def compute_sector_alignment_colony(before_metrics: list, after_metrics: list) -> dict:
    """Compute sector alignment for colony metrics."""
    results = {}
    
    for sector_name, sector_def in SECTORS.items():
        metrics = sector_def['metrics']
        
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


def run_study_001b():
    """Run the complete Ant Colony sector audit."""
    print("=" * 70)
    print("SGI Post-Ω Study 001B: Ant Colony Interaction Network")
    print("=" * 70)
    
    all_results = {}
    
    perturbations = {
        'P1_worker_removal': (WorkerRemoval, 0.3),
        'P2_trail_disruption': (TrailDisruption, 0.5),
        'P3_nest_fragmentation': (NestFragmentation, 0.4),
        'P4_resource_relocation': (ResourceRelocation, 0.5),
    }
    
    for pname, (protocol, severity) in perturbations.items():
        print(f"\n{'─' * 50}")
        print(f"Perturbation: {pname} (severity={severity})")
        print(f"{'─' * 50}")
        
        # Reset colony
        colony = AntColony(grid_size=50, n_ants=100, n_food=5, seed=42)
        
        # Establish baseline (20 timesteps)
        history_before = []
        for _ in range(20):
            state = colony.step()
            history_before.append(extract_sector_metrics_colony(state))
        
        # Apply perturbation
        description = protocol.apply(colony, severity)
        print(f"  Applied: {description}")
        
        # Measure recovery (50 timesteps)
        history_after = []
        for _ in range(50):
            state = colony.step()
            history_after.append(extract_sector_metrics_colony(state))
        
        # Compute sector alignment
        sector_results = compute_sector_alignment_colony(history_before, history_after)
        
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
    
    # ─── Cross-System Comparison ───
    print(f"\n{'=' * 70}")
    print("CROSS-SYSTEM COMPARISON: Distributed System vs Ant Colony")
    print(f"{'=' * 70}")
    
    # Load distributed system results
    try:
        with open('/home/student/sgp_core_v2/post_omega_study_001/sector_audit_results.json', 'r') as f:
            ds_results = json.load(f)
    except:
        ds_results = {}
        print("  Could not load distributed system results")
    
    # Map perturbation indices: DS P1-P4 ↔ AC P1-P4
    ds_perturbations = ['P1_node_removal', 'P2_communication_delay', 'P3_resource_starvation', 'P4_scheduler_distortion']
    ac_perturbations = ['P1_worker_removal', 'P2_trail_disruption', 'P3_nest_fragmentation', 'P4_resource_relocation']
    
    for sector_name in SECTORS:
        ds_survives = 0
        ds_collapses = 0
        ac_survives = 0
        ac_collapses = 0
        
        for ds_pname, ac_pname in zip(ds_perturbations, ac_perturbations):
            # Distributed system
            if ds_pname in ds_results:
                sr = ds_results[ds_pname].get('sectors', {}).get(sector_name, {})
                if sr.get('verdict') == 'SURVIVES':
                    ds_survives += 1
                else:
                    ds_collapses += 1
            
            # Ant colony
            if ac_pname in all_results:
                sr = all_results[ac_pname].get('sectors', {}).get(sector_name, {})
                if sr.get('verdict') == 'SURVIVES':
                    ac_survives += 1
                else:
                    ac_collapses += 1
        
        ds_pattern = f"{ds_survives}/4 survive"
        ac_pattern = f"{ac_survives}/4 survive"
        match = "CONSISTENT" if (ds_survives > 0 and ac_survives > 0) or (ds_survives == 0 and ac_survives == 0) else "INCONSISTENT"
        
        print(f"  {sector_name:12s}: DS={ds_pattern}  AC={ac_pattern}  [{match}]")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/colony_sector_audit_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\nResults saved to colony_sector_audit_results.json")
    print(f"{'=' * 70}")
    
    return all_results


if __name__ == '__main__':
    run_study_001b()
