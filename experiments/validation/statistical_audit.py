"""
Phase 003 Division A — Statistical Audit

Compute:
- Bootstrap confidence intervals
- Permutation tests
- Effect sizes (Cohen's d)
- Sensitivity analyses
- Leave-one-domain-out validation

Input: ensemble_results.json from synthetic_ensemble.py
"""

import numpy as np
import json
import os
import sys

DATA_PATH = '/home/student/SGI-Persistence/experiments/validation/ensemble_results.json'
OUTPUT_DIR = '/home/student/SGI-Persistence/experiments/validation'


def load_ensemble():
    with open(DATA_PATH) as f:
        return json.load(f)


def bootstrap_correlation(x, y, n_bootstrap=10000, ci=0.95):
    """Bootstrap confidence interval for correlation."""
    rng = np.random.RandomState(42)
    n = len(x)
    correlations = []
    
    for _ in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        corr = np.corrcoef(x[idx], y[idx])[0, 1]
        if np.isfinite(corr):
            correlations.append(corr)
    
    correlations = np.array(correlations)
    alpha = (1 - ci) / 2
    lower = np.percentile(correlations, alpha * 100)
    upper = np.percentile(correlations, (1 - alpha) * 100)
    
    return {
        'mean': float(np.mean(correlations)),
        'std': float(np.std(correlations)),
        'ci_lower': float(lower),
        'ci_upper': float(upper),
        'ci_level': ci,
        'n_bootstrap': len(correlations),
    }


def permutation_test(x, y, n_permutations=10000):
    """Permutation test for correlation significance."""
    rng = np.random.RandomState(42)
    observed_corr = np.corrcoef(x, y)[0, 1]
    
    perm_correlations = []
    for _ in range(n_permutations):
        y_perm = rng.permutation(y)
        corr = np.corrcoef(x, y_perm)[0, 1]
        if np.isfinite(corr):
            perm_correlations.append(corr)
    
    perm_correlations = np.array(perm_correlations)
    p_value = np.mean(np.abs(perm_correlations) >= np.abs(observed_corr))
    
    return {
        'observed_correlation': float(observed_corr),
        'p_value': float(p_value),
        'n_permutations': len(perm_correlations),
        'significant_at_005': p_value < 0.05,
        'significant_at_001': p_value < 0.01,
    }


def cohens_d(group1, group2):
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std < 1e-10:
        return 0.0
    return float((np.mean(group1) - np.mean(group2)) / pooled_std)


def leave_one_domain_out(ensemble):
    """Leave-one-domain-out cross-validation."""
    domains = {}
    for r in ensemble:
        domain = r['params']['coupling_type']
        if domain not in domains:
            domains[domain] = []
        domains[domain].append(r)
    
    results = []
    for held_out in domains:
        train = [r for d, rs in domains.items() if d != held_out for r in rs]
        test = domains[held_out]
        
        # Compute correlation on train
        train_G = np.array([r['G'] for r in train])
        train_invH = np.array([1.0 / (r['H'] + 1e-10) for r in train])
        train_corr = np.corrcoef(train_G, train_invH)[0, 1]
        
        # Compute correlation on test
        test_G = np.array([r['G'] for r in test])
        test_invH = np.array([1.0 / (r['H'] + 1e-10) for r in test])
        test_corr = np.corrcoef(test_G, test_invH)[0, 1] if len(test) > 1 else 0.0
        
        results.append({
            'held_out_domain': held_out,
            'train_n': len(train),
            'test_n': len(test),
            'train_correlation': float(train_corr),
            'test_correlation': float(test_corr) if np.isfinite(test_corr) else 0.0,
        })
    
    return results


def sensitivity_analysis(ensemble):
    """Analyze sensitivity to each parameter."""
    params_keys = ['memory_depth', 'adaptation_rate', 'stochasticity', 'replay_dependence']
    results = {}
    
    for key in params_keys:
        values = np.array([r['params'][key] for r in ensemble])
        G = np.array([r['G'] for r in ensemble])
        invH = np.array([1.0 / (r['H'] + 1e-10) for r in ensemble])
        
        # Correlation between parameter and G
        corr_G = np.corrcoef(values, G)[0, 1]
        corr_invH = np.corrcoef(values, invH)[0, 1]
        
        results[key] = {
            'corr_with_G': float(corr_G) if np.isfinite(corr_G) else 0.0,
            'corr_with_invH': float(corr_invH) if np.isfinite(corr_invH) else 0.0,
        }
    
    return results


def control_comparison(controls):
    """Compare G-H relation in controls vs ensemble."""
    by_type = {}
    for c in controls:
        t = c['control_type']
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(c)
    
    results = {}
    for ctype, rs in by_type.items():
        G = np.array([r['G'] for r in rs])
        invH = np.array([1.0 / (r['H'] + 1e-10) for r in rs])
        corr = np.corrcoef(G, invH)[0, 1] if len(rs) > 1 else 0.0
        
        results[ctype] = {
            'n': len(rs),
            'mean_G': float(np.mean(G)),
            'mean_H': float(np.mean([r['H'] for r in rs])),
            'mean_GH': float(np.mean([r['GH'] for r in rs])),
            'G_invH_correlation': float(corr) if np.isfinite(corr) else 0.0,
        }
    
    return results


def main():
    print("Phase 003 Division A — Statistical Audit")
    print("=" * 60)
    
    data = load_ensemble()
    ensemble = data['ensemble']
    controls = data['controls']
    
    # Extract arrays
    G = np.array([r['G'] for r in ensemble])
    H = np.array([r['H'] for r in ensemble])
    invH = 1.0 / (H + 1e-10)
    
    print(f"\nEnsemble: {len(ensemble)} systems")
    print(f"Controls: {len(controls)} systems")
    
    # 1. Bootstrap confidence interval
    print("\n1. Bootstrap CI for Corr(G, 1/H)...")
    bootstrap = bootstrap_correlation(G, invH)
    print(f"   Mean: {bootstrap['mean']:.4f}")
    print(f"   95% CI: [{bootstrap['ci_lower']:.4f}, {bootstrap['ci_upper']:.4f}]")
    
    # 2. Permutation test
    print("\n2. Permutation test...")
    permutation = permutation_test(G, invH)
    print(f"   Observed r: {permutation['observed_correlation']:.4f}")
    print(f"   p-value: {permutation['p_value']:.6f}")
    print(f"   Significant at 0.05: {permutation['significant_at_005']}")
    
    # 3. Effect sizes
    print("\n3. Effect sizes (Cohen's d)...")
    high_H = G[H > np.median(H)]
    low_H = G[H <= np.median(H)]
    d = cohens_d(high_H, low_H)
    print(f"   High-H vs Low-H G: d = {d:.4f}")
    
    # 4. Leave-one-domain-out
    print("\n4. Leave-one-domain-out validation...")
    loo = leave_one_domain_out(ensemble)
    for r in loo:
        print(f"   {r['held_out_domain']}: train={r['train_correlation']:.4f}, test={r['test_correlation']:.4f}")
    
    # 5. Sensitivity analysis
    print("\n5. Sensitivity analysis...")
    sensitivity = sensitivity_analysis(ensemble)
    for key, vals in sensitivity.items():
        print(f"   {key}: corr(G)={vals['corr_with_G']:.4f}, corr(1/H)={vals['corr_with_invH']:.4f}")
    
    # 6. Control comparison
    print("\n6. Control comparison...")
    control_comp = control_comparison(controls)
    for ctype, vals in control_comp.items():
        print(f"   {ctype}: n={vals['n']}, G={vals['mean_G']:.4f}, H={vals['mean_H']:.4f}, r(G,1/H)={vals['G_invH_correlation']:.4f}")
    
    # Save results (convert numpy types)
    def convert(obj):
        if isinstance(obj, (np.bool_, np.integer)):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj
    
    output = {
        'bootstrap': {k: convert(v) for k, v in bootstrap.items()},
        'permutation': {k: convert(v) for k, v in permutation.items()},
        'effect_size': {'cohens_d_high_vs_low_H': float(d)},
        'leave_one_domain_out': loo,
        'sensitivity': sensitivity,
        'control_comparison': control_comp,
    }
    
    outpath = os.path.join(OUTPUT_DIR, 'statistical_audit.json')
    with open(outpath, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved to {outpath}")
    
    # Summary
    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)
    print(f"Corr(G, 1/H) = {bootstrap['mean']:.4f} [{bootstrap['ci_lower']:.4f}, {bootstrap['ci_upper']:.4f}]")
    print(f"Permutation p = {permutation['p_value']:.6f}")
    print(f"Effect size d = {d:.4f}")
    print(f"Leave-one-domain-out mean test r = {np.mean([r['test_correlation'] for r in loo]):.4f}")
    
    # Verdict
    if permutation['significant_at_005'] and bootstrap['ci_lower'] > 0.3:
        print("\nVERDICT: G ∝ 1/H SURVIVES statistical validation.")
    elif permutation['significant_at_005']:
        print("\nVERDICT: G ∝ 1/H is statistically significant but effect size is moderate.")
    else:
        print("\nVERDICT: G ∝ 1/H DOES NOT survive statistical validation.")


if __name__ == '__main__':
    main()
