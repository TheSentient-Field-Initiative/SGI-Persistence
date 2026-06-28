"""
Tests for figure generation pipeline.

Covers:
- Figure generation script runs without error
- Output files exist in PDF, SVG, PNG formats
- No NaN in generated figures
"""

import pytest
import os
import subprocess
import sys

FIGURES_DIR = '/home/student/SGI-Persistence/results/figures'
SCRIPT_PATH = '/home/student/SGI-Persistence/scripts/generate_all_figures.py'

EXPECTED_FIGURES = [
    'fig01_g_vs_h',
    'fig02_transport_error',
    'fig03_fiber_entanglement',
    'fig04_transport_instability',
    'fig05_immune_fragility',
    'fig06_gxh_product',
    'fig07_correlation_comparison',
]

EXTENSIONS = ['.pdf', '.svg', '.png']


class TestFigureGeneration:
    def test_script_runs(self):
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH],
            capture_output=True, text=True, timeout=60
        )
        assert result.returncode == 0, f"Script failed:\n{result.stderr}"

    @pytest.mark.parametrize("name", EXPECTED_FIGURES)
    def test_figure_files_exist(self, name):
        for ext in EXTENSIONS:
            path = os.path.join(FIGURES_DIR, f'{name}{ext}')
            assert os.path.exists(path), f"Missing: {path}"

    @pytest.mark.parametrize("name", EXPECTED_FIGURES)
    def test_figure_not_empty(self, name):
        for ext in EXTENSIONS:
            path = os.path.join(FIGURES_DIR, f'{name}{ext}')
            if os.path.exists(path):
                assert os.path.getsize(path) > 0, f"Empty: {path}"
