# External Replication Matrix

**Phase 003H Division 5 — HIGH PRIORITY**

---

## 1. Purpose

For every major result, provide:
- Exact command
- Expected output
- Tolerance
- Failure conditions
- Runtime
- Seed requirements

Goal: Make external audit frictionless.

---

## 2. Test Suite Replication

### 2.1 Run All Tests

**Command:**
```bash
cd /home/student/SGI-Persistence
python -m pytest tests/ -v
```

**Expected Output:**
```
63 passed in X.XXs
```

**Tolerance:** All 63 tests must pass

**Failure Conditions:** Any test failure

**Runtime:** ~10 seconds

**Seed Requirements:** None (tests use fixed seeds)

---

### 2.2 Deterministic Reproduction

**Command:**
```bash
cd /home/student/SGI-Persistence
python reproduction/minimal_demo/reproduce.py
```

**Expected Output:**
```
Correlation: -0.8430
```

**Tolerance:** Correlation must be -0.8430 ± 0.0001

**Failure Conditions:** Correlation outside tolerance

**Runtime:** ~1 second

**Seed Requirements:** Fixed seed (42)

---

## 3. Validation Experiments

### 3.1 Collapse Transitions

**Command:**
```bash
cd /home/student/SGI-Persistence
python experiments/validation/collapse_transitions.py
```

**Expected Output:**
```
distributed: G_critical=0.50, H_critical=1.00
immune: G_critical=0.15, H_critical=1.00
ant_colony: G_critical=0.90, H_critical=0.80
institution: G_critical=0.10, H_critical=0.55
```

**Tolerance:** Critical thresholds ±0.05

**Failure Conditions:** Thresholds outside tolerance

**Runtime:** ~30 seconds

**Seed Requirements:** Fixed seed (42)

---

### 3.2 Effective Dimensionality

**Command:**
```bash
cd /home/student/SGI-Persistence
python experiments/validation/effective_dimensionality.py
```

**Expected Output:**
```
distributed: participation_ratio=1.0036
immune: participation_ratio=1.0083
ant_colony: participation_ratio=1.0136
institution: participation_ratio=1.0000
```

**Tolerance:** Participation ratio ±0.01

**Failure Conditions:** Participation ratio > 1.5

**Runtime:** ~10 seconds

**Seed Requirements:** Fixed seed (42)

---

### 3.3 Observable Survival

**Command:**
```bash
cd /home/student/SGI-Persistence
python experiments/validation/observable_survival.py
```

**Expected Output:**
```
G survival: 47%
H survival: 67%
```

**Tolerance:** Survival rates ±5%

**Failure Conditions:** Survival rates outside tolerance

**Runtime:** ~30 seconds

**Seed Requirements:** Fixed seed (42)

---

### 3.4 Null Observable Controls

**Command:**
```bash
cd /home/student/SGI-Persistence
python experiments/validation/null_observable_controls.py
```

**Expected Output:**
```
distributed: G_outperforms_null=False, H_outperforms_null=False
immune: G_outperforms_null=True, H_outperforms_null=False
ant_colony: G_outperforms_null=False, H_outperforms_null=False
institution: G_outperforms_null=False, H_outperforms_null=False
```

**Tolerance:** Exact match

**Failure Conditions:** Any deviation from expected

**Runtime:** ~10 seconds

**Seed Requirements:** Fixed seed (42)

---

### 3.5 Survivor Observables

**Command:**
```bash
cd /home/student/SGI-Persistence
python experiments/validation/survivor_observables.py
```

**Expected Output:**
```
Survival counts:
  variance_mean: 4/4
  lagged_stability: 4/4
  persistence: 4/4
  transition_density: 4/4
```

**Tolerance:** Exact match

**Failure Conditions:** Any observable fails in any system

**Runtime:** ~5 seconds

**Seed Requirements:** Fixed seed (42)

---

### 3.6 Survivor Stability Atlas

**Command:**
```bash
cd /home/student/SGI-Persistence
python experiments/validation/survivor_stability_atlas.py
```

**Expected Output:**
```
Robustness rankings:
  lagged_stability: 0.968
  variance_mean: 0.925
  persistence: 0.085
  transition_density: 0.004
```

**Tolerance:** Robustness scores ±0.05

**Failure Conditions:** Rankings change

**Runtime:** ~10 seconds

**Seed Requirements:** Fixed seed (42)

---

### 3.7 Cross-System Generalization

**Command:**
```bash
cd /home/student/SGI-Persistence
python experiments/validation/cross_system_generalization.py
```

**Expected Output:**
```
Generalization rankings:
  persistence: 1.000
  transition_density: 1.000
  lagged_stability: 0.167
  variance_mean: 0.000
```

**Tolerance:** Generalization scores ±0.1

**Failure Conditions:** Rankings change

**Runtime:** ~5 seconds

**Seed Requirements:** Fixed seed (42)

---

### 3.8 Survivor Compression

**Command:**
```bash
cd /home/student/SGI-Persistence
python experiments/validation/survivor_compression.py
```

**Expected Output:**
```
Compression tolerance:
  lagged_stability: min_PCA=1, min_quant=2
  variance_mean: min_PCA=8-13, min_quant=2
```

**Tolerance:** Exact match

**Failure Conditions:** Compression tolerance changes

**Runtime:** ~5 seconds

**Seed Requirements:** Fixed seed (42)

---

## 4. Artifact Hashing

### 4.1 Compute Hashes

**Command:**
```bash
cd /home/student/SGI-Persistence
python scripts/hash_artifacts.py
```

**Expected Output:**
```
Hashes computed for all artifacts
```

**Tolerance:** All hashes match

**Failure Conditions:** Any hash mismatch

**Runtime:** ~5 seconds

**Seed Requirements:** None

---

### 4.2 Verify Hashes

**Command:**
```bash
cd /home/student/SGI-Persistence
python reproduction/external_review/verify.py
```

**Expected Output:**
```
All artifacts verified
```

**Tolerance:** All artifacts match

**Failure Conditions:** Any artifact mismatch

**Runtime:** ~5 seconds

**Seed Requirements:** None

---

## 5. Full Reproduction

### 5.1 Reproduce Everything

**Command:**
```bash
cd /home/student/SGI-Persistence
bash reproduction/external_review/reproduce_all.sh
```

**Expected Output:**
```
REPRODUCTION COMPLETE
```

**Tolerance:** All components pass

**Failure Conditions:** Any component failure

**Runtime:** ~5 minutes

**Seed Requirements:** None

---

## 6. Failure Conditions

### 6.1 Critical Failures

- Any test failure
- Correlation outside tolerance
- Participation ratio > 1.5
- Survival rates outside tolerance
- Rankings change

### 6.2 Warning Conditions

- Runtime > 2x expected
- Hash mismatches
- Tolerance warnings

---

## 7. Contact

For questions about replication:
- Repository: https://github.com/TheSentient-Field-Initiative/SGI-Persistence
- Issues: https://github.com/TheSentient-Field-Initiative/SGI-Persistence/issues
