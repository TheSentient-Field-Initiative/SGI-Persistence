# External Review Package

**Purpose:** Enable independent reviewers to reproduce and falsify our claims.

**Goal:** A reviewer can falsify the claim themselves. That increases credibility.

---

## Contents

| File | Description |
|------|-------------|
| `verify.py` | Main verification script |
| `expected_results.json` | Frozen expected outputs |
| `metric_traces.md` | Metric computation traces |
| `failure_modes.md` | Documented failure modes |
| `known_limitations.md` | Known limitations and caveats |

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run verification
python reproduction/external_review/verify.py

# Compare with expected results
python -c "
import json
with open('reproduction/external_review/expected_results.json') as f:
    expected = json.load(f)
with open('reproduction/external_review/verification_results.json') as f:
    actual = json.load(f)
for key in expected:
    if key in actual:
        match = abs(expected[key]['value'] - actual[key]['value']) < 0.01
        print(f'{key}: {\"PASS\" if match else \"FAIL\"} (expected={expected[key][\"value\"]:.4f}, actual={actual[key][\"value\"]:.4f})')
"
```

---

## What This Package Tests

1. **Metric identity:** Do our metric implementations match the canonical contract?
2. **Reproducibility:** Do we get the same results with fixed seeds?
3. **Known results:** Do our known results (G∝1/H correlation, transport separation) reproduce?
4. **Failure modes:** Do our documented failure modes actually occur?

---

## What This Package Does NOT Test

1. **Universal applicability:** We do NOT claim the results generalize beyond 4 systems.
2. **Theoretical foundations:** We do NOT claim the geometric formalism is the correct framework.
3. **Predictive power:** We do NOT claim G∝1/H is a predictive law.

---

## Reviewer Checklist

- [ ] `verify.py` runs without errors
- [ ] Expected results match within tolerance
- [ ] Metric traces are documented and reproducible
- [ ] Failure modes are demonstrated
- [ ] Known limitations are acknowledged
- [ ] No universal claims are made
