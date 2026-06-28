#!/usr/bin/env python3
"""
Master figure generation script for SGI Persistence Program.

Regenerates ALL publication-grade figures from raw results.
Run from repository root: python scripts/generate_all_figures.py

Output: results/figures/ (PDF + SVG + PNG for each figure)
"""

import sys
import os

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Delegate to the figures module
exec(open(os.path.join(os.path.dirname(__file__), '..', 'papers', 'figures', 'generate_figures.py')).read())
