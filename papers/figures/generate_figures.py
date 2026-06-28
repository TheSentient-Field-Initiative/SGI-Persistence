"""
Publication-Grade Figure Generation for SGI Persistence Program.

Generates the key figures for the Phase 001 and Phase 002 papers.
All figures are saved as PDF, SVG, and PNG.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from pathlib import Path

# Output directory
FIGURES_DIR = Path('/home/student/SGI-Persistence/results/figures')
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Color scheme
COLORS = {
    'distributed': '#2196F3',
    'immune': '#F44336',
    'ant_colony': '#4CAF50',
    'institution': '#FF9800',
}

def save_figure(fig, name):
    """Save figure in PDF, SVG, and PNG formats."""
    for fmt in ['pdf', 'svg', 'png']:
        fig.savefig(FIGURES_DIR / f'{name}.{fmt}', 
                   format=fmt, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f'  Saved: {name}')

# ─── Figure 1: G vs H (Phase 001) ───

def fig01_g_vs_h():
    """The central empirical law: G ∝ 1/H."""
    systems = ['distributed', 'immune', 'ant_colony', 'institution']
    G = np.array([0.250, 0.875, 0.125, 0.250])
    H = np.array([0.396, 0.180, 0.576, 0.497])
    
    fig, ax = plt.subplots(figsize=(6, 5))
    
    for i, sys in enumerate(systems):
        ax.scatter(H[i], G[i], c=COLORS[sys], s=120, zorder=5, 
                  edgecolors='black', linewidth=0.5, label=sys)
    
    # Fit line
    H_fit = np.linspace(0.15, 0.65, 100)
    G_fit = 0.15 / H_fit  # G ∝ 1/H
    ax.plot(H_fit, G_fit, 'k--', alpha=0.6, label=r'$G \propto 1/H$')
    
    ax.set_xlabel('Historical Residue Coupling (H)', fontsize=12)
    ax.set_ylabel('Organizational Replay Stability (G)', fontsize=12)
    ax.set_title(r'Phase 001: $G \propto 1/H$ ($r = -0.951$)', fontsize=13)
    ax.legend(fontsize=9, loc='upper right')
    ax.set_xlim(0.1, 0.65)
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, alpha=0.3)
    
    save_figure(fig, 'fig01_g_vs_h')

# ─── Figure 2: Transport Error Separation (Phase 002B) ───

def fig02_transport_error():
    """Transport error separates all four systems."""
    systems = ['distributed', 'immune', 'ant_colony', 'institution']
    TE = [0.535, 0.020, 0.000, 0.000]
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    bars = ax.bar(systems, TE, color=[COLORS[s] for s in systems], 
                  edgecolor='black', linewidth=0.5)
    
    ax.set_ylabel('Transport Error', fontsize=12)
    ax.set_title('Phase 002B: Transport Error Separates Systems', fontsize=13)
    ax.set_ylim(0, 0.65)
    ax.grid(True, axis='y', alpha=0.3)
    
    # Add value labels
    for bar, val in zip(bars, TE):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.01,
                f'{val:.3f}', ha='center', va='bottom', fontsize=10)
    
    save_figure(fig, 'fig02_transport_error')

# ─── Figure 3: Fiber Entanglement (Phase 002B) ───

def fig03_fiber_entanglement():
    """Fiber entanglement: 122.5x improvement over scalar proxies."""
    systems = ['distributed', 'immune', 'ant_colony', 'institution']
    RTC = [0.980, 0.980, 0.000, 0.000]
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    bars = ax.bar(systems, RTC, color=[COLORS[s] for s in systems], 
                  edgecolor='black', linewidth=0.5)
    
    ax.set_ylabel('Replay Transport Coupling', fontsize=12)
    ax.set_title('Phase 002B: Fiber Entanglement (122.5x Improvement)', fontsize=13)
    ax.set_ylim(0, 1.2)
    ax.grid(True, axis='y', alpha=0.3)
    
    for bar, val in zip(bars, RTC):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontsize=10)
    
    save_figure(fig, 'fig03_fiber_entanglement')

# ─── Figure 4: Transport Instability (Phase 002C) ───

def fig04_transport_instability():
    """Transport instability: T separates distributed from others."""
    systems = ['distributed', 'immune', 'ant_colony', 'institution']
    T = [0.963, 0.000, 0.000, 0.000]
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    bars = ax.bar(systems, T, color=[COLORS[s] for s in systems], 
                  edgecolor='black', linewidth=0.5)
    
    ax.set_ylabel('Transport Instability (T)', fontsize=12)
    ax.set_title('Phase 002C: Transport Instability', fontsize=13)
    ax.set_ylim(0, 1.2)
    ax.grid(True, axis='y', alpha=0.3)
    
    for bar, val in zip(bars, T):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontsize=10)
    
    save_figure(fig, 'fig04_transport_instability')

# ─── Figure 5: Immune Fragility (Phase 002C) ───

def fig05_immune_fragility():
    """Immune system fragility under structural perturbation."""
    perturbations = ['Baseline', 'Node\nDeletion', 'Topology\nRewire', 'Residue\nInjection']
    T_values = [1e-10, 1e10, 1e10, 1e10]
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    colors = ['#4CAF50', '#F44336', '#F44336', '#F44336']
    bars = ax.bar(perturbations, T_values, color=colors, 
                  edgecolor='black', linewidth=0.5)
    
    ax.set_ylabel('Transport Instability (T)', fontsize=12)
    ax.set_title('Phase 002C: Immune System Fragility', fontsize=13)
    ax.set_yscale('log')
    ax.set_ylim(1e-15, 1e15)
    ax.grid(True, axis='y', alpha=0.3)
    
    save_figure(fig, 'fig05_immune_fragility')

# ─── Figure 6: G×H Product (Phase 001) ───

def fig06_gxh_product():
    """G×H product across systems."""
    systems = ['distributed', 'immune', 'ant_colony', 'institution']
    G = np.array([0.250, 0.875, 0.125, 0.250])
    H = np.array([0.396, 0.180, 0.576, 0.497])
    GH = G * H
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    bars = ax.bar(systems, GH, color=[COLORS[s] for s in systems], 
                  edgecolor='black', linewidth=0.5)
    
    ax.set_ylabel('G × H', fontsize=12)
    ax.set_title(r'Phase 001: $G \times H$ Product', fontsize=13)
    ax.grid(True, axis='y', alpha=0.3)
    
    for bar, val in zip(bars, GH):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.003,
                f'{val:.3f}', ha='center', va='bottom', fontsize=10)
    
    save_figure(fig, 'fig06_gxh_product')

# ─── Figure 7: Correlation Comparison ───

def fig07_correlation_comparison():
    """1/H vs 1/T as predictors of G."""
    metrics = [r'$1/H$', r'$1/T$']
    correlations = [0.992, 0.243]
    
    fig, ax = plt.subplots(figsize=(5, 4))
    
    colors = ['#2196F3', '#9E9E9E']
    bars = ax.bar(metrics, correlations, color=colors, 
                  edgecolor='black', linewidth=0.5, width=0.5)
    
    ax.set_ylabel('|Correlation with G|', fontsize=12)
    ax.set_title('Phase 002C: H Outperforms T as Predictor', fontsize=13)
    ax.set_ylim(0, 1.2)
    ax.grid(True, axis='y', alpha=0.3)
    
    for bar, val in zip(bars, correlations):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontsize=11)
    
    save_figure(fig, 'fig07_correlation_comparison')

# ─── Generate All Figures ───

if __name__ == '__main__':
    print('Generating publication-grade figures...')
    fig01_g_vs_h()
    fig02_transport_error()
    fig03_fiber_entanglement()
    fig04_transport_instability()
    fig05_immune_fragility()
    fig06_gxh_product()
    fig07_correlation_comparison()
    print('Done.')
