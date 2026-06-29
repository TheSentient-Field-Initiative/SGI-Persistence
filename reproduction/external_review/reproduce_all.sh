#!/bin/bash
# ============================================================
# Phase 003G Division 5 — External Reproduction Hardening
# ============================================================
# Single-command execution of all repository components
# Usage: bash reproduce_all.sh
# ============================================================

set -e

echo "============================================================"
echo "SGI Persistence — Full Reproduction Script"
echo "============================================================"
echo "Started at: $(date)"
echo ""

# ============================================================
# 1. ENVIRONMENT CHECK
# ============================================================
echo "[1/8] Environment check..."
python3 --version
pip3 list | grep -E "numpy|scipy|sklearn|pandas" || true
echo ""

# ============================================================
# 2. TESTS
# ============================================================
echo "[2/8] Running test suite..."
cd /home/student/SGI-Persistence
python -m pytest tests/ -v --tb=short 2>&1 | tee results/reproduction_tests.log
echo "Tests completed: $(date)"
echo ""

# ============================================================
# 3. DETERMINISTIC REPRODUCTION
# ============================================================
echo "[3/8] Running deterministic reproduction..."
cd /home/student/SGI-Persistence
python reproduction/minimal_demo/reproduce.py 2>&1 | tee results/reproduction_deterministic.log
echo "Deterministic reproduction completed: $(date)"
echo ""

# ============================================================
# 4. ARTIFACT HASHING
# ============================================================
echo "[4/8] Computing artifact hashes..."
cd /home/student/SGI-Persistence
python scripts/hash_artifacts.py 2>&1 | tee results/reproduction_hashes.log
echo "Hashing completed: $(date)"
echo ""

# ============================================================
# 5. VALIDATION EXPERIMENTS
# ============================================================
echo "[5/8] Running validation experiments..."
cd /home/student/SGI-Persistence

echo "  [5.1] Collapse transitions..."
python experiments/validation/collapse_transitions.py 2>&1 | tee results/validation_collapse.log

echo "  [5.2] Effective dimensionality..."
python experiments/validation/effective_dimensionality.py 2>&1 | tee results/validation_dimensionality.log

echo "  [5.3] Observable survival..."
python experiments/validation/observable_survival.py 2>&1 | tee results/validation_survival.log

echo "  [5.4] Null observable controls..."
python experiments/validation/null_observable_controls.py 2>&1 | tee results/validation_null.log

echo "  [5.5] Collapse mechanics..."
python experiments/validation/collapse_mechanics.py 2>&1 | tee results/validation_mechanics.log

echo "  [5.6] Embedding singularity analysis..."
python experiments/validation/embedding_singularity_analysis.py 2>&1 | tee results/validation_singularity.log

echo "  [5.7] Observable competition..."
python experiments/validation/observable_competition.py 2>&1 | tee results/validation_competition.log

echo "  [5.8] Survivor observables..."
python experiments/validation/survivor_observables.py 2>&1 | tee results/validation_survivor.log

echo "  [5.9] Minimal representation tests..."
python experiments/validation/minimal_representation_tests.py 2>&1 | tee results/validation_minimal.log

echo "  [5.10] Failure boundary mapping..."
python experiments/validation/failure_boundary_mapping.py 2>&1 | tee results/validation_boundary.log

echo "Validation experiments completed: $(date)"
echo ""

# ============================================================
# 6. GENERATE FIGURES
# ============================================================
echo "[6/8] Generating figures..."
cd /home/student/SGI-Persistence
python papers/figures/generate_figures.py 2>&1 | tee results/figure_generation.log
echo "Figure generation completed: $(date)"
echo ""

# ============================================================
# 7. VERIFY EXPECTED RESULTS
# ============================================================
echo "[7/8] Verifying expected results..."
cd /home/student/SGI-Persistence/reproduction/external_review
python verify.py 2>&1 | tee ../../results/verification.log
echo "Verification completed: $(date)"
echo ""

# ============================================================
# 8. SUMMARY
# ============================================================
echo "[8/8] Generating summary..."
echo ""
echo "============================================================"
echo "REPRODUCTION COMPLETE"
echo "============================================================"
echo "Finished at: $(date)"
echo ""
echo "Results saved to:"
echo "  - results/reproduction_tests.log"
echo "  - results/reproduction_deterministic.log"
echo "  - results/reproduction_hashes.log"
echo "  - results/validation_*.log"
echo "  - results/figure_generation.log"
echo "  - results/verification.log"
echo ""
echo "To verify results:"
echo "  cat results/verification.log"
echo "  diff results/hashes/expected_results.json results/hashes/actual_results.json"
echo "============================================================"
