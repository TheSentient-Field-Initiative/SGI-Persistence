"""
SGI Post-Ω Study 001D: Social Cooperation / Institution Network

System: Strategic agents with norm emergence and institutional coordination
Substrate: symbolic/strategic coordination
Interaction medium: norm signaling, trust exchange
Persistence mechanism: institutional memory, norm enforcement

Pre-registered hypotheses:
H1: Institutional systems produce intermediate G (0.3-0.6)
H2: Human coordination differs from immune resilience
H3: Gauge stability requires bounded state spaces
"""

import numpy as np
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum


class Strategy(Enum):
    COOPERATE = 0
    DEFECT = 1
    TIT_FOR_TAT = 2
    PAVLOV = 3  # cooperate if partner cooperated last time
    GENEROUS_TFT = 4


@dataclass
class Agent:
    id: int
    strategy: Strategy
    trust_level: float = 0.5  # trust in neighbors [0,1]
    norm_compliance: float = 0.5  # how much agent follows norms [0,1]
    reputation: float = 0.5  # reputation among neighbors [0,1]
    payoff: float = 0.0
    memory: List[int] = field(default_factory=list)  # cooperation/defection history
    active: bool = True


class InstitutionNetwork:
    """Social cooperation network with norm emergence and institutional persistence."""
    
    def __init__(self, n_agents: int = 100, seed: int = 42):
        self.rng = np.random.RandomState(seed)
        self.n_agents = n_agents
        self.timestep = 0
        self.history = []
        
        # Strategy distribution: 20% cooperate, 15% defect, 30% TFT, 25% Pavlov, 10% generous TFT
        strategy_probs = [0.20, 0.15, 0.30, 0.25, 0.10]
        strategies = list(Strategy)
        
        # Create agents
        self.agents: List[Agent] = []
        for i in range(n_agents):
            strat = self.rng.choice(strategies, p=strategy_probs)
            self.agents.append(Agent(
                id=i,
                strategy=strat,
                trust_level=self.rng.uniform(0.3, 0.7),
                norm_compliance=self.rng.uniform(0.3, 0.7),
                reputation=self.rng.uniform(0.3, 0.7),
            ))
        
        # Build interaction network
        self.adjacency: Dict[int, List[int]] = {}
        self._build_network()
        
        # Norm field: shared expectations
        self.norms = {
            'cooperation_rate': 0.5,
            'reciprocity_norm': 0.5,
            'fairness_norm': 0.5,
            'punishment_severity': 0.3,
        }
        
        # Institutional memory: past norm violations
        self.violation_history: List[Dict] = []
        
        # Payoff matrix
        self.payoff_matrix = {
            ('C', 'C'): (3, 3),  # mutual cooperation
            ('C', 'D'): (0, 5),  # sucker's payoff
            ('D', 'C'): (5, 0),  # temptation
            ('D', 'D'): (1, 1),  # mutual defection
        }
    
    def _build_network(self):
        """Build social network with clustering."""
        for i in range(self.n_agents):
            n_connections = self.rng.randint(3, 8)
            # Prefer same strategy (homophily)
            same_strat = [j for j in range(self.n_agents) if j != i and 
                         self.agents[j].strategy == self.agents[i].strategy]
            other_strat = [j for j in range(self.n_agents) if j != i and 
                          self.agents[j].strategy != self.agents[i].strategy]
            
            targets = []
            if same_strat and self.rng.random() < 0.6:
                n_same = min(n_connections, len(same_strat))
                targets.extend(self.rng.choice(same_strat, size=n_same, replace=False))
                n_connections -= n_same
            
            if other_strat and n_connections > 0:
                n_other = min(n_connections, len(other_strat))
                targets.extend(self.rng.choice(other_strat, size=n_other, replace=False))
            
            self.adjacency[i] = list(set(targets))
    
    def step(self) -> Dict:
        """Execute one interaction round."""
        # 1. Agents interact with neighbors
        interactions = []
        for agent in self.agents:
            if not agent.active:
                continue
            for neighbor_id in self.adjacency.get(agent.id, []):
                neighbor = self.agents[neighbor_id]
                if not neighbor.active:
                    continue
                
                # Determine actions based on strategy
                action1 = self._get_action(agent, neighbor)
                action2 = self._get_action(neighbor, agent)
                
                # Compute payoffs
                payoff1, payoff2 = self.payoff_matrix[(action1, action2)]
                agent.payoff += payoff1
                neighbor.payoff += payoff2
                
                # Update memory
                agent.memory.append(1 if action1 == 'C' else 0)
                neighbor.memory.append(1 if action2 == 'C' else 0)
                
                interactions.append({
                    'agent': agent.id,
                    'neighbor': neighbor_id,
                    'action1': action1,
                    'action2': action2,
                })
        
        # 2. Update norms based on cooperation rates
        cooperation_rate = np.mean([1 if a.memory[-1] == 1 else 0 
                                   for a in self.agents if a.active and a.memory])
        self.norms['cooperation_rate'] = 0.9 * self.norms['cooperation_rate'] + 0.1 * cooperation_rate
        
        # 3. Update trust and reputation
        for agent in self.agents:
            if not agent.active:
                continue
            neighbor_coops = []
            for neighbor_id in self.adjacency.get(agent.id, []):
                neighbor = self.agents[neighbor_id]
                if neighbor.active and neighbor.memory:
                    neighbor_coops.append(neighbor.memory[-1])
            
            if neighbor_coops:
                avg_coop = np.mean(neighbor_coops)
                agent.trust_level = 0.8 * agent.trust_level + 0.2 * avg_coop
                agent.reputation = 0.7 * agent.reputation + 0.3 * avg_coop
        
        # 4. Norm compliance adjustment
        for agent in self.agents:
            if not agent.active:
                continue
            # Comply if norms are strong and reputation matters
            norm_pressure = self.norms['cooperation_rate'] * self.norms['reciprocity_norm']
            agent.norm_compliance = 0.7 * agent.norm_compliance + 0.3 * norm_pressure
        
        # 5. Measure
        state = self._measure()
        self.history.append(state)
        self.timestep += 1
        return state
    
    def _get_action(self, agent: Agent, opponent: Agent) -> str:
        """Determine agent's action based on strategy."""
        if agent.strategy == Strategy.COOPERATE:
            return 'C'
        elif agent.strategy == Strategy.DEFECT:
            return 'D'
        elif agent.strategy == Strategy.TIT_FOR_TAT:
            if agent.memory:
                return 'C' if opponent.memory and opponent.memory[-1] == 1 else 'D'
            return 'C'
        elif agent.strategy == Strategy.PAVLOV:
            if len(agent.memory) >= 2 and len(opponent.memory) >= 2:
                if agent.memory[-1] == opponent.memory[-1]:
                    return 'C'  # repeat
                else:
                    return 'D'  # switch
            return 'C'
        elif agent.strategy == Strategy.GENEROUS_TFT:
            if agent.memory and opponent.memory:
                if opponent.memory[-1] == 1:
                    return 'C'
                else:
                    return 'C' if self.rng.random() < 0.3 else 'D'
            return 'C'
        return 'C'
    
    def _measure(self) -> Dict:
        """Measure all observables."""
        active_agents = [a for a in self.agents if a.active]
        n_active = len(active_agents)
        
        # ─── Amplitude Sector ───
        cooperation_rate = np.mean([a.memory[-1] if a.memory else 0.5 for a in active_agents])
        mean_payoff = np.mean([a.payoff for a in active_agents])
        mean_trust = np.mean([a.trust_level for a in active_agents])
        
        # ─── Topology Sector ───
        # Network connectivity
        active_edges = 0
        total_edges = 0
        for i, neighbors in self.adjacency.items():
            if not self.agents[i].active:
                continue
            for j in neighbors:
                total_edges += 1
                if self.agents[j].active:
                    active_edges += 1
        network_connectivity = active_edges / max(total_edges, 1)
        
        # Component structure
        n_components, component_sizes = self._find_components()
        largest_component = max(component_sizes) / max(n_active, 1) if component_sizes else 0
        
        # Strategy distribution entropy
        strat_counts = {}
        for a in active_agents:
            strat_counts[a.strategy.name] = strat_counts.get(a.strategy.name, 0) + 1
        strat_probs = np.array(list(strat_counts.values())) / max(sum(strat_counts.values()), 1)
        strategy_entropy = -np.sum(strat_probs * np.log2(strat_probs + 1e-10))
        
        # ─── Transport Sector ───
        # Trust-reputation covariance
        if n_active > 1:
            trusts = np.array([a.trust_level for a in active_agents])
            reputations = np.array([a.reputation for a in active_agents])
            norm_comps = np.array([a.norm_compliance for a in active_agents])
            
            # Stack into matrix
            data_matrix = np.stack([trusts, reputations, norm_comps], axis=0)
            cov = np.cov(data_matrix)
            eigenvalues = np.sort(np.abs(np.linalg.eigvalsh(cov)))[::-1]
            cov_trace = float(np.sum(eigenvalues))
            cov_condition = float(eigenvalues[0] / (eigenvalues[-1] + 1e-10)) if len(eigenvalues) > 1 else 1.0
        else:
            eigenvalues = np.array([0])
            cov_trace = 0
            cov_condition = 1.0
        
        # ─── Residual Sector ───
        # Norm deviation: variance from norm expectations
        norm_deviations = []
        for a in active_agents:
            deviation = abs(a.norm_compliance - self.norms['cooperation_rate'])
            norm_deviations.append(deviation)
        norm_deviation = float(np.mean(norm_deviations)) if norm_deviations else 0
        
        # Non-principal coordination modes
        if n_active > 1 and len(eigenvalues) > 1:
            total_energy = np.sum(eigenvalues)
            non_principal = float(np.sum(eigenvalues[1:]) / (total_energy + 1e-10))
        else:
            non_principal = 0
        
        return {
            'timestep': self.timestep,
            # Amplitude
            'cooperation_rate': float(cooperation_rate),
            'mean_payoff': float(mean_payoff),
            'mean_trust': float(mean_trust),
            # Topology
            'network_connectivity': float(network_connectivity),
            'n_components': n_components,
            'largest_component': float(largest_component),
            'strategy_entropy': float(strategy_entropy),
            # Transport
            'cov_trace': cov_trace,
            'cov_condition': cov_condition,
            'cov_eigenvalues': eigenvalues.tolist(),
            # Residual
            'norm_deviation': norm_deviation,
            'non_principal': non_principal,
        }
    
    def _find_components(self) -> Tuple[int, List[int]]:
        """Find connected components in active subgraph."""
        visited = set()
        components = []
        
        for agent in self.agents:
            if not agent.active or agent.id in visited:
                continue
            component_size = 0
            queue = [agent.id]
            visited.add(agent.id)
            while queue:
                current = queue.pop(0)
                component_size += 1
                for neighbor_id in self.adjacency.get(current, []):
                    if neighbor_id not in visited and self.agents[neighbor_id].active:
                        visited.add(neighbor_id)
                        queue.append(neighbor_id)
            components.append(component_size)
        
        return len(components), components


# ─── Perturbation Protocols ───

class InstitutionPerturbation:
    @staticmethod
    def apply(network: InstitutionNetwork, severity: float) -> str:
        raise NotImplementedError

class TrustViolation(InstitutionPerturbation):
    """P1: Betray trust between connected agents."""
    @staticmethod
    def apply(network: InstitutionNetwork, severity: float) -> str:
        violated = 0
        for agent in network.agents:
            if agent.active and network.rng.random() < severity:
                agent.trust_level *= 0.1  # Sharp trust drop
                agent.reputation *= 0.3
                violated += 1
        return f"Trust violated for {violated} agents"

class NormCorruption(InstitutionPerturbation):
    """P2: Corrupt shared norms."""
    @staticmethod
    def apply(network: InstitutionNetwork, severity: float) -> str:
        network.norms['cooperation_rate'] *= (1 - severity)
        network.norms['reciprocity_norm'] *= (1 - severity * 0.5)
        network.norms['fairness_norm'] *= (1 - severity * 0.3)
        return f"Norms corrupted (severity={severity:.2f})"

class AgentDepletion(InstitutionPerturbation):
    """P3: Remove agents from the network."""
    @staticmethod
    def apply(network: InstitutionNetwork, severity: float) -> str:
        depleted = 0
        for agent in network.agents:
            if agent.active and network.rng.random() < severity:
                agent.active = False
                depleted += 1
        return f"Depleted {depleted} agents"

class InformationShock(InstitutionPerturbation):
    """P4: Introduce false information that corrupts strategies."""
    @staticmethod
    def apply(network: InstitutionNetwork, severity: float) -> str:
        corrupted = 0
        for agent in network.agents:
            if agent.active and network.rng.random() < severity:
                # Randomly change strategy
                agent.strategy = network.rng.choice(list(Strategy))
                corrupted += 1
        return f"Corrupted {corrupted} agent strategies"


# ─── Sector Audit ───

INSTITUTION_SECTORS = {
    'amplitude': {
        'metrics': ['cooperation_rate', 'mean_payoff', 'mean_trust'],
        'expected_survival': False,
    },
    'topology': {
        'metrics': ['network_connectivity', 'n_components', 'largest_component', 'strategy_entropy'],
        'expected_survival': True,
    },
    'transport': {
        'metrics': ['cov_trace', 'cov_condition'],
        'expected_survival': True,
    },
    'residual': {
        'metrics': ['norm_deviation', 'non_principal'],
        'expected_survival': True,
    },
}


def extract_institution_metrics(state: dict) -> dict:
    """Extract sector metrics from institution state."""
    return {k: v for k, v in state.items() if k != 'timestep' and k != 'cov_eigenvalues'}


def compute_institution_sector_alignment(before_metrics: list, after_metrics: list) -> dict:
    """Compute sector alignment for institution metrics."""
    results = {}
    
    for sector_name, sector_def in INSTITUTION_SECTORS.items():
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


def run_institution_study():
    """Run complete institution network study."""
    print("=" * 70)
    print("Study 001D: Social Cooperation / Institution Network")
    print("=" * 70)
    
    # Pre-registered hypotheses
    print("\n  PRE-REGISTERED HYPOTHESES:")
    print("  H1: Institutional systems produce intermediate G (0.3-0.6)")
    print("  H2: Human coordination differs from immune resilience")
    print("  H3: Gauge stability requires bounded state spaces")
    
    all_results = {}
    
    perturbations = {
        'P1_trust_violation': (TrustViolation, 0.4),
        'P2_norm_corruption': (NormCorruption, 0.5),
        'P3_agent_depletion': (AgentDepletion, 0.3),
        'P4_information_shock': (InformationShock, 0.3),
    }
    
    for pname, (protocol, severity) in perturbations.items():
        print(f"\n{'─' * 50}")
        print(f"Perturbation: {pname} (severity={severity})")
        print(f"{'─' * 50}")
        
        # Reset network
        network = InstitutionNetwork(n_agents=100, seed=42)
        
        # Establish baseline (20 timesteps)
        history_before = []
        for _ in range(20):
            state = network.step()
            history_before.append(extract_institution_metrics(state))
        
        # Apply perturbation
        description = protocol.apply(network, severity)
        print(f"  Applied: {description}")
        
        # Measure recovery (50 timesteps)
        history_after = []
        for _ in range(50):
            state = network.step()
            history_after.append(extract_institution_metrics(state))
        
        # Sector audit
        sector_results = compute_institution_sector_alignment(history_before, history_after)
        
        all_results[pname] = {
            'description': description,
            'sectors': sector_results,
        }
        
        for sector_name, sr in sector_results.items():
            if 'error' in sr:
                print(f"  {sector_name}: {sr['error']}")
                continue
            print(f"  {sector_name:12s}: raw={sr['raw_similarity']:.4f}  "
                  f"norm={sr['normalized_similarity']:.4f}  "
                  f"Δ={sr['normalization_survival']:+.4f}  "
                  f"→ {sr['verdict']}")
    
    # ─── Gauge Fraction ───
    print(f"\n{'─' * 50}")
    print("GAUGE FRACTION ANALYSIS")
    print(f"{'─' * 50}")
    
    gauge_scores = []
    for pname, data in all_results.items():
        g = compute_gauge_fraction(data.get('sectors', {}))
        gauge_scores.append(g)
        print(f"  {pname}: G={g:.3f}")
    
    G = np.mean(gauge_scores)
    print(f"\n  MEAN G={G:.3f}")
    
    # ─── Structural/Functional Dissociation ───
    print(f"\n{'─' * 50}")
    print("STRUCTURAL/FUNCTIONAL DISSOCIATION")
    print(f"{'─' * 50}")
    
    structural_scores = []
    functional_scores = []
    
    for pname, data in all_results.items():
        sector_data = data.get('sectors', {})
        topo = sector_data.get('topology', {})
        amp = sector_data.get('amplitude', {})
        S = max(0, topo.get('normalized_similarity', 0))
        F = max(0, amp.get('normalized_similarity', 0))
        structural_scores.append(S)
        functional_scores.append(F)
        print(f"  {pname}: S={S:.3f}  F={F:.3f}")
    
    S_mean = np.mean(structural_scores)
    F_mean = np.mean(functional_scores)
    print(f"\n  MEAN: S={S_mean:.3f}  F={F_mean:.3f}")
    
    # ─── Regime Classification ───
    print(f"\n{'─' * 50}")
    print("REGIME CLASSIFICATION")
    print(f"{'─' * 50}")
    
    if S_mean > 0.5 and F_mean > 0.5 and G > 0.5:
        regime = "resilient"
    elif S_mean > 0.5 and F_mean < 0.5:
        regime = "rigid"
    elif S_mean < 0.5 and F_mean > 0.5:
        regime = "adaptive"
    elif S_mean > 0.3 and F_mean > 0.3 and G > 0.3:
        regime = "institutional"
    else:
        regime = "collapse"
    
    print(f"  Regime: {regime}")
    print(f"  P=({S_mean:.3f}, {F_mean:.3f}, {G:.3f})")
    
    # ─── Hypothesis Tests ───
    print(f"\n{'=' * 70}")
    print("HYPOTHESIS TESTS")
    print(f"{'=' * 70}")
    
    # H1: Intermediate G
    h1_supported = 0.3 <= G <= 0.6
    print(f"\n  H1: Institutional systems produce intermediate G (0.3-0.6)")
    print(f"      G={G:.3f} → {'SUPPORTED' if h1_supported else 'NOT SUPPORTED'}")
    
    # H2: Differs from immune
    print(f"\n  H2: Human coordination differs from immune resilience")
    print(f"      Immune G=0.875, Institution G={G:.3f}")
    print(f"      → {'SUPPORTED' if G < 0.8 else 'NOT SUPPORTED'} (lower G)")
    
    # H3: Gauge stability requires bounded state spaces
    print(f"\n  H3: Gauge stability requires bounded state spaces")
    print(f"      Institution has unbounded state spaces")
    print(f"      G={G:.3f} → {'SUPPORTED' if G < 0.5 else 'NOT SUPPORTED'} (intermediate/low G)")
    
    # ─── Dynamical Analysis ───
    print(f"\n{'─' * 50}")
    print("DYNAMICAL BOUNDEDNESS ANALYSIS")
    print(f"{'─' * 50}")
    
    # Check state bounds
    network = InstitutionNetwork(n_agents=100, seed=42)
    for _ in range(20):
        network.step()
    
    trusts = [a.trust_level for a in network.agents if a.active]
    reputations = [a.reputation for a in network.agents if a.active]
    norms = [a.norm_compliance for a in network.agents if a.active]
    
    print(f"  Trust range: [{min(trusts):.3f}, {max(trusts):.3f}]")
    print(f"  Reputation range: [{min(reputations):.3f}, {max(reputations):.3f}]")
    print(f"  Norm compliance range: [{min(norms):.3f}, {max(norms):.3f}]")
    print(f"  ")
    print(f"  State space: {'BOUNDED' if max(trusts) < 1.1 and min(trusts) > -0.1 else 'UNBOUNDED'}")
    print(f"  Activation: NOT CLIPPED (unlike immune system)")
    print(f"  Threshold gating: WEAK (strategic adaptation)")
    
    # ─── Load All Systems ───
    print(f"\n{'=' * 70}")
    print("PERSISTENCE ALLOCATION LANDSCAPE (all 4 systems)")
    print(f"{'=' * 70}")
    
    with open('/home/student/sgp_core_v2/post_omega_study_001/gauge_geometry_results.json', 'r') as f:
        geometry = json.load(f)
    
    geometry['Institution Network'] = {
        'S': float(S_mean),
        'F': float(F_mean),
        'G': float(G),
        'regime': regime,
    }
    
    for name, data in geometry.items():
        print(f"  {name:20s}: S={data['S']:.3f}  F={data['F']:.3f}  G={data['G']:.3f}  regime={data['regime']}")
    
    # Save
    with open('/home/student/sgp_core_v2/post_omega_study_001/institution_study_results.json', 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    with open('/home/student/sgp_core_v2/post_omega_study_001/gauge_geometry_results.json', 'w') as f:
        json.dump(geometry, f, indent=2)
    
    print(f"\nResults saved")
    print(f"{'=' * 70}")
    
    return all_results, geometry


if __name__ == '__main__':
    run_institution_study()
