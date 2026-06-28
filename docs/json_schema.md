# JSON Result Schema

All result JSON files in `data/canonical/` must conform to this schema.

## Standard Schema

```json
{
  "experiment": "string — unique experiment identifier",
  "phase": "string — phase number (001, 002A, 002B, 002C)",
  "system": "string — system class (distributed, immune, ant_colony, institution)",
  "metrics": {
    "G": "float — organizational replay stability",
    "H": "float — historical residue coupling",
    "T": "float — transport instability",
    "transport_error": "float — transport inconsistency",
    "fiber_entanglement": "float — replay transport coupling"
  },
  "parameters": {
    "memory_depth": "int — memory depth for fiber construction",
    "n_nodes": "int — number of nodes in system",
    "n_timesteps": "int — number of simulation timesteps",
    "perturbation_protocol": "string — perturbation type applied"
  },
  "seed": "int — random seed for reproducibility",
  "timestamp": "string — ISO 8601 timestamp of experiment",
  "version": "string — software version used"
}
```

## Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| experiment | string | Yes | Unique identifier, e.g. `study_001a` |
| phase | string | Yes | Phase and sub-phase, e.g. `002C` |
| system | string | Yes | System class name |
| metrics | object | Yes | All measured values (see below) |
| parameters | object | Yes | Experiment parameters |
| seed | int | Yes | Random seed |
| timestamp | string | Yes | ISO 8601 format |
| version | string | Yes | Semantic version |

## Metrics Fields

| Metric | Type | Description |
|--------|------|-------------|
| G | float | Organizational replay stability |
| H | float | Historical residue coupling |
| T | float | Transport instability |
| transport_error | float | Mean transport error across trajectory |
| fiber_entanglement | float | Mean replay transport coupling magnitude |
| holonomy | float | Mean holonomy (loop closure error) |
| noncommutativity | float | Mean relative noncommutativity |

## Example

```json
{
  "experiment": "phase_002c_transport_instability",
  "phase": "002C",
  "system": "distributed",
  "metrics": {
    "G": 0.250,
    "H": 0.396,
    "T": 0.963,
    "transport_error": 0.535,
    "fiber_entanglement": 0.980,
    "holonomy": 0.000,
    "noncommutativity": 0.000
  },
  "parameters": {
    "memory_depth": 10,
    "n_nodes": 100,
    "n_timesteps": 50,
    "perturbation_protocol": "none"
  },
  "seed": 42,
  "timestamp": "2026-06-28T00:00:00Z",
  "version": "0.2.0"
}
```
