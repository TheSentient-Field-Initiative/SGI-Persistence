#!/usr/bin/env python3
"""
Phase 003C Division 3 — Dimensionality Stress Test

Sweep:
- 2D → 64D embeddings
- Sparse vs dense embeddings
- Orthogonal vs correlated coordinates

Question: does G/H survive representation scaling?
"""

import numpy as np
import json
import os
import sys
import time

# Add source paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'distributed'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'immune'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'ant_colony'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'systems', 'institution'))


def run_simulation(system_class, **kwargs):
    """Run a simulation and return trajectory."""
    system = system_class(**kwargs)
    for _ in range(50):
        system.step()
    return system.history


def trajectory_to_matrix(trajectory, max_dim=64):
    """Convert trajectory to matrix of shape (T, D)."""
    all_keys = set()
    for state in trajectory[:5]:
        all_keys.update(state.keys())
    all_keys.discard('timestep')
    all_keys.discard('cov_eigenvalues')

    keys = sorted(all_keys)[:max_dim]
    vectors = []
    for state in trajectory:
        v = [state.get(k, 0) for k in keys]
        vectors.append(v)

    return np.array(vectors), keys


def create_sparse_embedding(matrix, sparsity=0.5, seed=42):
    """Create sparse embedding by zeroing out random dimensions."""
    rng = np.random.RandomState(seed)
    mask = rng.random(matrix.shape[1]) > sparsity
    return matrix * mask


def create_orthogonal_embedding(matrix, seed=42):
    """Create orthogonal embedding via QR decomposition."""
    Q, R = np.linalg.qr(matrix.T)
    return (Q.T @ matrix.T).T


def create_correlated_embedding(matrix, correlation=0.9, seed=42):
    """Create correlated embedding by mixing dimensions."""
    rng = np.random.RandomState(seed)
    n_dim = matrix.shape[1]
    mix_matrix = np.eye(n_dim) * (1 - correlation) + correlation / n_dim
    return matrix @ mix_matrix


def compute_G_from_matrix(matrix, n_sectors=2):
    """Compute G from matrix using sector alignment."""
    if len(matrix) < 10:
        return 0.0

    mid = len(matrix) // 2
    before = matrix[:mid]
    after = matrix[mid:]

    surviving = 0
    dim_per_sector = matrix.shape[1] // n_sectors

    for i in range(n_sectors):
        start = i * dim_per_sector
        end = start + dim_per_sector
        bv = before[:, start:end]
        av = after[:, start:end]

        if bv.size == 0 or av.size == 0:
            continue

        def _cosine(a, b):
            na, nb = np.linalg.norm(a), np.linalg.norm(b)
            return float(np.dot(a.flatten(), b.flatten()) / (na * nb)) if na > 0 and nb > 0 else 0.0

        raw = _cosine(bv, av)
        bn = (bv - bv.mean(0)) / (bv.std(0) + 1e-8)
        an = (av - av.mean(0)) / (av.std(0) + 1e-8)
        norm = _cosine(bn, an)

        if (norm - raw) > -0.1:
            surviving += 1

    return surviving / n_sectors if n_sectors > 0 else 0.0


def compute_H_from_matrix(matrix, max_lag=5):
    """Compute H from matrix using autocorrelation."""
    if len(matrix) < max_lag + 1:
        return 0.0

    autocorrs = []
    for lag in range(1, min(max_lag + 1, len(matrix))):
        if lag < len(matrix):
            a = matrix[:-lag]
            b = matrix[lag:]
            if a.size > 0 and b.size > 0:
                na, nb = np.linalg.norm(a), np.linalg.norm(b)
                if na > 0 and nb > 0:
                    corr = np.dot(a.flatten(), b.flatten()) / (na * nb)
                    autocorrs.append(abs(corr))

    return np.mean(autocorrs) if autocorrs else 0.0


def main():
    start = time.time()

    print("=" * 60)
    print("Phase 003C Division 3 — Dimensionality Stress Test")
    print("=" * 60)

    from study_001 import DistributedSystem
    from study_001c_immune import ImmuneSignalingNetwork
    from study_001b_colony import AntColony
    from study_001d_institution import InstitutionNetwork

    # System configurations
    systems = {
        'distributed': {
            'class': DistributedSystem,
            'kwargs': {'n_nodes': 100, 'seed': 42},
        },
        'immune': {
            'class': ImmuneSignalingNetwork,
            'kwargs': {'n_cells': 100, 'seed': 42},
        },
        'ant_colony': {
            'class': AntColony,
            'kwargs': {'n_ants': 50, 'n_food': 100, 'seed': 42},
        },
        'institution': {
            'class': InstitutionNetwork,
            'kwargs': {'n_agents': 100, 'seed': 42},
        },
    }

    # Dimensionality sweep
    dimensions = [2, 4, 8, 16, 32, 64]

    results = {}

    for sys_name, config in systems.items():
        print(f"\n--- {sys_name} ---")

        # Run baseline simulation
        traj = run_simulation(config['class'], **config['kwargs'])
        matrix, keys = trajectory_to_matrix(traj, max_dim=64)

        sys_results = {'baseline': {'n_keys': len(keys), 'shape': list(matrix.shape)}}

        # Sweep dimensions
        dim_results = {}
        for dim in dimensions:
            if dim > matrix.shape[1]:
                continue

            sub_matrix = matrix[:, :dim]
            G = compute_G_from_matrix(sub_matrix)
            H = compute_H_from_matrix(sub_matrix)

            dim_results[dim] = {'G': G, 'H': H}
            print(f"  {dim}D: G={G:.4f}, H={H:.4f}")

        sys_results['dimensionality'] = dim_results

        # Sparse embeddings
        print("  Testing sparse embeddings...")
        sparse_results = {}
        for sparsity in [0.0, 0.25, 0.5, 0.75]:
            sparse_matrix = create_sparse_embedding(matrix, sparsity=sparsity)
            G = compute_G_from_matrix(sparse_matrix)
            H = compute_H_from_matrix(sparse_matrix)
            sparse_results[sparsity] = {'G': G, 'H': H}
            print(f"    sparsity={sparsity}: G={G:.4f}, H={H:.4f}")
        sys_results['sparse'] = sparse_results

        # Orthogonal embedding
        print("  Testing orthogonal embedding...")
        orth_matrix = create_orthogonal_embedding(matrix)
        G_orth = compute_G_from_matrix(orth_matrix)
        H_orth = compute_H_from_matrix(orth_matrix)
        sys_results['orthogonal'] = {'G': G_orth, 'H': H_orth}
        print(f"    orthogonal: G={G_orth:.4f}, H={H_orth:.4f}")

        # Correlated embedding
        print("  Testing correlated embedding...")
        corr_results = {}
        for corr in [0.0, 0.5, 0.9, 0.99]:
            corr_matrix = create_correlated_embedding(matrix, correlation=corr)
            G = compute_G_from_matrix(corr_matrix)
            H = compute_H_from_matrix(corr_matrix)
            corr_results[corr] = {'G': G, 'H': H}
            print(f"    correlation={corr}: G={G:.4f}, H={H:.4f}")
        sys_results['correlated'] = corr_results

        results[sys_name] = sys_results

    # Save results
    elapsed = time.time() - start
    output = {
        'results': results,
        'runtime_seconds': round(elapsed, 1),
    }

    outpath = os.path.join(os.path.dirname(__file__), 'dimensionality_stress_results.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nResults saved to {outpath}")
    print(f"Runtime: {elapsed:.1f} seconds")


if __name__ == '__main__':
    main()
