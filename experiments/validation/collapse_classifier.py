#!/usr/bin/env python3
"""
Phase 003J Division 1: Collapse Classifier
Predict whether a system will exhibit low-rank collapse.

Potential predictors:
- coupling density
- feedback locality
- memory depth
- synchronization
- sparsity
- update determinism
- entropy production

Usage:
    python experiments/validation/collapse_classifier.py
"""

import numpy as np
import json
import os
import sys
import time
from collections import defaultdict

# Add source paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'distributed'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'immune'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'ant_colony'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'institution'))

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_SEEDS = 5
NUM_TIMESTEPS = 200
ED_THRESHOLD = 2.0  # Systems with ED < 2.0 are classified as LOW-RANK


# ============================================================
# SYNTHETIC SYSTEMS (from Phase 003I Division 2)
# ============================================================

class EpidemicSystem:
    def __init__(self, n_nodes=100, seed=42):
        self.n_nodes = n_nodes
        self.rng = np.random.RandomState(seed)
        self.state = self.rng.choice(['S', 'I', 'R'], size=n_nodes, p=[0.7, 0.2, 0.1])
        self.adjacency = self._create_random_graph()
        self.history = []

    def _create_random_graph(self):
        adj = np.zeros((self.n_nodes, self.n_nodes))
        for i in range(self.n_nodes):
            n_neighbors = self.rng.randint(2, 6)
            neighbors = self.rng.choice(self.n_nodes, n_neighbors, replace=False)
            adj[i, neighbors] = 1
            adj[neighbors, i] = 1
        return adj

    def step(self):
        new_state = self.state.copy()
        for i in range(self.n_nodes):
            if self.state[i] == 'S':
                infected_neighbors = np.sum(self.adjacency[i, self.state == 'I'])
                if infected_neighbors > 0 and self.rng.random() < 0.3 * infected_neighbors / 5:
                    new_state[i] = 'I'
            elif self.state[i] == 'I':
                if self.rng.random() < 0.1:
                    new_state[i] = 'R'
        self.state = new_state
        state_map = {'S': 0, 'I': 1, 'R': 2}
        numerical = np.array([state_map[s] for s in self.state], dtype=float)
        record = {'timestep': len(self.history)}
        for i, val in enumerate(numerical):
            record[f'node_{i}'] = float(val)
        self.history.append(record)
        return record


class NeuralSystem:
    def __init__(self, n_neurons=100, seed=42):
        self.n_neurons = n_neurons
        self.rng = np.random.RandomState(seed)
        self.weights = self.rng.randn(n_neurons, n_neurons) * 0.1
        self.activity = self.rng.randn(n_neurons) * 0.5
        self.history = []

    def step(self):
        noise = self.rng.randn(self.n_neurons) * 0.01
        self.activity = np.tanh(self.weights @ self.activity + noise)
        outer = np.outer(self.activity, self.activity)
        self.weights = self.weights * 0.9 + 0.01 * outer
        self.weights = np.clip(self.weights, -2, 2)
        record = {'timestep': len(self.history)}
        for i, val in enumerate(self.activity):
            record[f'neuron_{i}'] = float(val)
        self.history.append(record)
        return record


class MarketSystem:
    def __init__(self, n_agents=100, seed=42):
        self.n_agents = n_agents
        self.rng = np.random.RandomState(seed)
        self.wealth = self.rng.uniform(10, 100, n_agents)
        self.strategy = self.rng.choice(['bull', 'bear', 'neutral'], n_agents)
        self.price = 50.0
        self.history = []

    def step(self):
        demand = sum(1 if s == 'bull' else -1 if s == 'bear' else 0 for s in self.strategy)
        self.price += 0.1 * demand / self.n_agents + self.rng.randn() * 0.5
        self.price = max(1, self.price)
        for i in range(self.n_agents):
            if self.rng.random() < 0.1:
                if self.price > 60:
                    self.strategy[i] = 'bear'
                elif self.price < 40:
                    self.strategy[i] = 'bull'
                else:
                    self.strategy[i] = self.rng.choice(['bull', 'bear', 'neutral'])
            if self.strategy[i] == 'bull':
                self.wealth[i] *= (1 + 0.1 * self.rng.randn())
            elif self.strategy[i] == 'bear':
                self.wealth[i] *= (1 - 0.1 * self.rng.randn())
            self.wealth[i] = max(0, self.wealth[i])
        record = {'timestep': len(self.history)}
        for i, val in enumerate(self.wealth):
            record[f'agent_{i}'] = float(val)
        self.history.append(record)
        return record


class EcologicalSystem:
    def __init__(self, n_patches=100, seed=42):
        self.n_patches = n_patches
        self.rng = np.random.RandomState(seed)
        self.prey = self.rng.uniform(20, 80, n_patches)
        self.predators = self.rng.uniform(10, 30, n_patches)
        self.history = []

    def step(self):
        noise_prey = self.rng.randn(self.n_patches) * 0.5
        noise_pred = self.rng.randn(self.n_patches) * 0.2
        d_prey = 0.5 * self.prey - 0.02 * self.prey * self.predators + noise_prey
        d_pred = 0.5 * self.prey * self.predators - 0.3 * self.predators + noise_pred
        self.prey = np.clip(self.prey + d_prey, 0, 200)
        self.predators = np.clip(self.predators + d_pred, 0, 100)
        record = {'timestep': len(self.history)}
        for i in range(self.n_patches):
            record[f'prey_{i}'] = float(self.prey[i])
            record[f'predator_{i}'] = float(self.predators[i])
        self.history.append(record)
        return record


def trajectory_to_matrix(trajectory, max_dim=64):
    all_keys = set()
    for state in trajectory[:5]:
        all_keys.update(state.keys())
    all_keys.discard('timestep')
    all_keys.discard('cov_eigenvalues')  # Skip list values
    keys = sorted(all_keys)[:max_dim]
    vectors = []
    for state in trajectory:
        v = []
        for k in keys:
            val = state.get(k, 0)
            # Ensure numeric
            if isinstance(val, (list, tuple, np.ndarray)):
                v.append(0.0)  # Skip complex values
            elif isinstance(val, str):
                v.append(0.0)
            else:
                v.append(float(val))
        vectors.append(v)
    return np.array(vectors), keys


def compute_effective_dimensionality(matrix):
    if len(matrix) > matrix.shape[1]:
        try:
            cov = np.cov(matrix.T)
            eigenvalues = np.linalg.eigvalsh(cov)
            eigenvalues = eigenvalues[eigenvalues > 1e-10]
            if len(eigenvalues) > 0:
                participation_ratio = (np.sum(eigenvalues) ** 2) / np.sum(eigenvalues ** 2)
                return float(participation_ratio)
        except:
            pass
    return 1.0


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def extract_system_features(system_class, system_kwargs, seed):
    """Extract features that might predict collapse."""
    features = {}
    system = system_class(seed=seed, **system_kwargs)
    trajectory = []
    for _ in range(NUM_TIMESTEPS):
        trajectory.append(system.step())

    matrix, keys = trajectory_to_matrix(trajectory)

    # 1. Coupling density (from trajectory correlations)
    corr_matrix = np.corrcoef(matrix.T)
    features['coupling_density'] = float(np.mean(np.abs(corr_matrix) > 0.3))

    # 2. Feedback locality (from autocorrelation decay)
    if len(matrix) > 10:
        autocorrs = []
        for dim in range(min(5, matrix.shape[1])):
            c = np.correlate(matrix[:, dim] - np.mean(matrix[:, dim]),
                             matrix[:, dim] - np.mean(matrix[:, dim]), mode='full')
            c = c / c[0] if c[0] > 0 else c
            half_point = np.argmax(c[len(c)//2:] < 0.5)
            autocorrs.append(half_point)
        features['feedback_locality'] = float(np.mean(autocorrs))
    else:
        features['feedback_locality'] = 1.0

    # 3. Memory depth (from mutual information decay)
    if len(matrix) > 20:
        mi_decay = []
        for lag in range(1, min(21, len(matrix) // 4)):
            mi = np.mean([np.corrcoef(matrix[:-lag, d], matrix[lag:, d])[0, 1]**2
                         for d in range(matrix.shape[1])])
            if not np.isnan(mi):
                mi_decay.append(mi)
        if mi_decay:
            threshold = 0.1 * mi_decay[0] if mi_decay[0] > 0 else 0.01
            memory_depth = next((i for i, v in enumerate(mi_decay) if v < threshold), len(mi_decay))
            features['memory_depth'] = float(memory_depth)
        else:
            features['memory_depth'] = 0.0
    else:
        features['memory_depth'] = 0.0

    # 4. Synchronization (from pairwise correlations)
    if len(matrix) > 10:
        corr_matrix = np.corrcoef(matrix.T)
        np.fill_diagonal(corr_matrix, 0)
        sync_val = np.mean(np.abs(corr_matrix))
        features['synchronization'] = float(sync_val) if not np.isnan(sync_val) else 0.0
    else:
        features['synchronization'] = 0.0

    # 5. Sparsity (fraction of near-zero values)
    features['sparsity'] = float(np.mean(np.abs(matrix) < 0.01))

    # 6. Update determinism (from conditional variance)
    if len(matrix) > 10:
        conditional_vars = []
        for d in range(min(5, matrix.shape[1])):
            x = matrix[:-1, d]
            y = matrix[1:, d]
            if x.max() > x.min():
                bins = np.linspace(x.min(), x.max(), 10)
                bin_indices = np.digitize(x, bins)
                for b in range(1, len(bins)):
                    mask = bin_indices == b
                    if np.sum(mask) > 1:
                        conditional_vars.append(np.var(y[mask]))
        if conditional_vars:
            features['update_determinism'] = 1.0 / (1.0 + np.mean(conditional_vars))
        else:
            features['update_determinism'] = 0.5
    else:
        features['update_determinism'] = 0.5

    # 7. Entropy production
    if len(matrix) > 10:
        entropy_rates = []
        for d in range(min(5, matrix.shape[1])):
            values = matrix[:, d]
            hist, _ = np.histogram(values, bins=20, density=True)
            hist = hist[hist > 0]
            entropy = -np.sum(hist * np.log(hist + 1e-10))
            entropy_rates.append(entropy)
        features['entropy_production'] = float(np.mean(entropy_rates))
    else:
        features['entropy_production'] = 0.0

    # 8. State space dimensionality
    features['nominal_dimensionality'] = float(matrix.shape[1])

    # 9. Trajectory complexity
    if len(matrix) > 10:
        diffs = np.diff(matrix, axis=0)
        trajectory_length = np.sum(np.sqrt(np.sum(diffs**2, axis=1)))
        features['trajectory_complexity'] = float(trajectory_length / len(matrix))
    else:
        features['trajectory_complexity'] = 0.0

    # 10. Covariance condition number
    if len(matrix) > matrix.shape[1]:
        try:
            cov = np.cov(matrix.T)
            eigenvalues = np.linalg.eigvalsh(cov)
            eigenvalues = eigenvalues[eigenvalues > 1e-10]
            if len(eigenvalues) > 0 and eigenvalues[0] > 0:
                features['log_condition_number'] = float(np.log10(eigenvalues[-1] / eigenvalues[0]))
            else:
                features['log_condition_number'] = 10.0
        except:
            features['log_condition_number'] = 10.0
    else:
        features['log_condition_number'] = 0.0

    # Compute effective dimensionality (target)
    ed = compute_effective_dimensionality(matrix)
    features['effective_dimensionality'] = ed
    features['is_low_rank'] = 1 if ed < ED_THRESHOLD else 0

    return features


# ============================================================
# CLASSIFIER
# ============================================================

def train_simple_classifier(features_list):
    """Train a simple interpretable classifier (logistic regression)."""
    # Extract features and labels (exclude metadata)
    exclude_keys = ('effective_dimensionality', 'is_low_rank', 'system', 'seed')
    feature_names = [k for k in features_list[0] if k not in exclude_keys]
    X = np.array([[f[k] for k in feature_names] for f in features_list])
    y = np.array([f['is_low_rank'] for f in features_list])

    # Handle NaN values
    X = np.nan_to_num(X, nan=0.0)

    # Normalize features
    X_mean = np.mean(X, axis=0)
    X_std = np.std(X, axis=0)
    X_std[X_std == 0] = 1
    X_norm = (X - X_mean) / X_std

    # Simple logistic regression using gradient descent
    weights = np.zeros(len(feature_names))
    bias = 0.0
    lr = 0.1
    epochs = 1000

    for _ in range(epochs):
        # Forward pass
        logits = X_norm @ weights + bias
        predictions = 1 / (1 + np.exp(-np.clip(logits, -500, 500)))

        # Compute gradients
        error = predictions - y
        dw = np.mean(error[:, np.newaxis] * X_norm, axis=0)
        db = np.mean(error)

        # Update weights
        weights -= lr * dw
        bias -= lr * db

    # Compute feature importance (absolute weight)
    importance = np.abs(weights)
    importance = importance / np.sum(importance)

    # Sort by importance
    sorted_indices = np.argsort(importance)[::-1]
    sorted_features = [(feature_names[i], importance[i], weights[i]) for i in sorted_indices]

    return {
        'weights': weights.tolist(),
        'bias': float(bias),
        'feature_names': feature_names,
        'feature_importance': sorted_features,
        'X_mean': X_mean.tolist(),
        'X_std': X_std.tolist()
    }


def predict_collapse概率(classifier, features):
    """Predict collapse probability for a new system."""
    feature_names = classifier['feature_names']
    x = np.array([features[k] for k in feature_names])
    x_norm = (x - np.array(classifier['X_mean'])) / np.array(classifier['X_std'])
    logit = np.dot(x_norm, classifier['weights']) + classifier['bias']
    probability = 1 / (1 + np.exp(-np.clip(logit, -500, 500)))
    return float(probability)


if __name__ == "__main__":
    print("=" * 70)
    print("PHASE 003J DIVISION 1: COLLAPSE CLASSIFIER")
    print("=" * 70)
    print(f"Systems: 8 (4 original + 4 synthetic)")
    print(f"Seeds: {NUM_SEEDS}")
    print(f"ED threshold: {ED_THRESHOLD}")

    start_time = time.time()

    from study_001 import DistributedSystem
    from study_001c_immune import ImmuneSignalingNetwork
    from study_001b_colony import AntColony
    from study_001d_institution import InstitutionNetwork

    systems = {
        "distributed": {"class": DistributedSystem, "kwargs": {"n_nodes": 100}},
        "immune": {"class": ImmuneSignalingNetwork, "kwargs": {"n_cells": 100}},
        "ant_colony": {"class": AntColony, "kwargs": {"n_ants": 50, "n_food": 100}},
        "institution": {"class": InstitutionNetwork, "kwargs": {"n_agents": 100}},
        "epidemic": {"class": EpidemicSystem, "kwargs": {"n_nodes": 100}},
        "neural": {"class": NeuralSystem, "kwargs": {"n_neurons": 100}},
        "market": {"class": MarketSystem, "kwargs": {"n_agents": 100}},
        "ecological": {"class": EcologicalSystem, "kwargs": {"n_patches": 100}},
    }

    # Extract features for all systems
    all_features = []
    system_features = {}

    for sys_name, sys_info in systems.items():
        print(f"\nExtracting features for {sys_name}...")
        sys_features = []
        for seed in range(NUM_SEEDS):
            try:
                features = extract_system_features(sys_info["class"], sys_info["kwargs"], seed)
                features['system'] = sys_name
                features['seed'] = seed
                sys_features.append(features)
                all_features.append(features)
            except Exception as e:
                print(f"  Seed {seed}: ERROR - {e}")

        if sys_features:
            avg_ed = np.mean([f['effective_dimensionality'] for f in sys_features])
            avg_lr = np.mean([f['is_low_rank'] for f in sys_features])
            system_features[sys_name] = {
                'features': sys_features,
                'avg_ed': float(avg_ed),
                'is_low_rank': bool(avg_lr > 0.5)
            }
            print(f"  Avg ED: {avg_ed:.4f}, Low-rank: {avg_lr > 0.5}")

    # Train classifier
    print(f"\nTraining classifier on {len(all_features)} samples...")
    classifier = train_simple_classifier(all_features)

    # Print feature importance
    print(f"\nFEATURE IMPORTANCE:")
    for name, importance, weight in classifier['feature_importance']:
        direction = "increases" if weight > 0 else "decreases"
        print(f"  {name}: {importance:.4f} ({direction} collapse)")

    # Predict for each system
    print(f"\nCOLLAPSE PROBABILITY MAP:")
    collapse_map = {}
    for sys_name, sys_data in system_features.items():
        avg_features = {}
        for key in sys_data['features'][0]:
            if key in ('system', 'seed', 'effective_dimensionality', 'is_low_rank'):
                continue
            values = [f[key] for f in sys_data['features']]
            avg_features[key] = float(np.mean(values))

        prob = predict_collapse概率(classifier, avg_features)
        status = "COLLAPSE" if prob > 0.5 else "NO COLLAPSE"
        collapse_map[sys_name] = {
            'probability': prob,
            'predicted': prob > 0.5,
            'actual': sys_data['is_low_rank'],
            'correct': (prob > 0.5) == sys_data['is_low_rank']
        }
        print(f"  {sys_name}: P(collapse)={prob:.4f} [{status}]")

    # Compute accuracy
    correct = sum(1 for v in collapse_map.values() if v['correct'])
    accuracy = correct / len(collapse_map)
    print(f"\nAccuracy: {correct}/{len(collapse_map)} = {accuracy:.2%}")

    # Save results
    output = {
        "metadata": {
            "num_systems": len(systems),
            "num_seeds": NUM_SEEDS,
            "ed_threshold": ED_THRESHOLD,
            "total_time": time.time() - start_time
        },
        "classifier": classifier,
        "collapse_map": collapse_map,
        "system_features": {k: {'avg_ed': v['avg_ed'], 'is_low_rank': v['is_low_rank']}
                           for k, v in system_features.items()}
    }

    output_file = os.path.join(OUTPUT_DIR, "collapse_classifier_results.json")
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n{'=' * 70}")
    print(f"COLLAPSE CLASSIFIER COMPLETE")
    print(f"{'=' * 70}")
    print(f"Total runtime: {output['metadata']['total_time']:.1f}s")
    print(f"Results saved to: {output_file}")
