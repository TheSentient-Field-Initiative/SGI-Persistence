"""
Phase 003C Division 4 — Metric Consistency Tests

Verify:
- Same metric definitions used everywhere
- No local compute_G variants
- No hidden sector substitutions
- Registry compliance

Hard fail on drift.
"""

import pytest
import sys
import os
import ast
import re

# Add source paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def find_all_python_files(root_dir):
    """Find all Python files in directory tree."""
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f.endswith('.py'):
                python_files.append(os.path.join(root, f))
    return python_files


def find_compute_G_definitions(python_files):
    """Find all definitions of compute_G functions."""
    definitions = []
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if 'compute_G' in node.name or 'compute_g' in node.name:
                            definitions.append({
                                'file': filepath,
                                'line': node.lineno,
                                'name': node.name,
                            })
        except Exception as e:
            print(f"Warning: Could not parse {filepath}: {e}")
    return definitions


def find_sector_definitions(python_files):
    """Find all sector definition dictionaries."""
    definitions = []
    pattern = re.compile(r"['\"](?:amplitude|topology|transport|residual)['\"]")
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if pattern.search(line):
                        definitions.append({
                            'file': filepath,
                            'line': i + 1,
                            'content': line.strip()[:100],
                        })
        except Exception as e:
            print(f"Warning: Could not read {filepath}: {e}")
    return definitions


def find_state_to_vector_definitions(python_files):
    """Find all definitions of state_to_vector functions."""
    definitions = []
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if 'state_to_vector' in node.name:
                            definitions.append({
                                'file': filepath,
                                'line': node.lineno,
                                'name': node.name,
                            })
        except Exception as e:
            print(f"Warning: Could not parse {filepath}: {e}")
    return definitions


class TestMetricConsistency:
    """Test metric consistency across codebase."""

    def test_single_compute_G_definition(self):
        """Verify there is exactly one canonical compute_G definition."""
        root_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        python_files = find_all_python_files(root_dir)
        definitions = find_compute_G_definitions(python_files)

        # Filter to canonical definitions (in src/metrics/)
        canonical = [d for d in definitions if 'src/metrics/' in d['file']]

        assert len(canonical) == 1, (
            f"Expected exactly 1 canonical compute_G definition, found {len(canonical)}: "
            f"{[d['file'] for d in canonical]}"
        )

    def test_no_local_G_variants(self):
        """Verify no local compute_G variants exist outside src/metrics/."""
        root_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        python_files = find_all_python_files(root_dir)
        definitions = find_compute_G_definitions(python_files)

        # Filter to non-canonical definitions (exclude compute_gauge_fraction etc.)
        non_canonical = [d for d in definitions if 'src/metrics/' not in d['file']
                        and d['name'] == 'compute_G']

        assert len(non_canonical) == 0, (
            f"Found local compute_G variants outside src/metrics/: "
            f"{[(d['file'], d['line']) for d in non_canonical]}"
        )

    def test_single_state_to_vector_definition(self):
        """Verify there is exactly one canonical state_to_vector definition."""
        root_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        python_files = find_all_python_files(root_dir)
        definitions = find_state_to_vector_definitions(python_files)

        # Filter to canonical definitions (in src/geometry/)
        canonical = [d for d in definitions if 'src/geometry/' in d['file']]

        assert len(canonical) == 1, (
            f"Expected exactly 1 canonical state_to_vector definition, found {len(canonical)}: "
            f"{[d['file'] for d in canonical]}"
        )

    def test_sector_definitions_use_canonical_keys(self):
        """Verify sector definitions use canonical keys."""
        root_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
        python_files = find_all_python_files(root_dir)
        definitions = find_sector_definitions(python_files)

        canonical_keys = {'amplitude', 'topology', 'transport', 'residual'}

        for defn in definitions:
            # Extract key name from content
            match = re.search(r"['\"](\w+)['\"]", defn['content'])
            if match:
                key = match.group(1)
                assert key in canonical_keys, (
                    f"Non-canonical sector key '{key}' in {defn['file']}:{defn['line']}"
                )

    def test_metric_registry_exists(self):
        """Verify metric registry exists and is importable."""
        from src.metrics.registry import METRIC_REGISTRY

        assert 'G' in METRIC_REGISTRY, "G not in METRIC_REGISTRY"
        assert 'H' in METRIC_REGISTRY, "H not in METRIC_REGISTRY"
        assert 'TE' in METRIC_REGISTRY, "TE not in METRIC_REGISTRY"

    def test_metric_registry_has_required_fields(self):
        """Verify metric registry entries have required fields."""
        from src.metrics.registry import METRIC_REGISTRY

        required_fields = ['name', 'canonical_definition', 'implementation']

        for metric_name, metric_info in METRIC_REGISTRY.items():
            for field in required_fields:
                assert hasattr(metric_info, field), (
                    f"Metric '{metric_name}' missing required field '{field}'"
                )

    def test_embedding_registry_exists(self):
        """Verify embedding registry exists and is importable."""
        from src.embeddings import EMBEDDINGS

        assert 'distributed' in EMBEDDINGS, "distributed not in EMBEDDINGS"
        assert 'immune' in EMBEDDINGS, "immune not in EMBEDDINGS"
        assert 'ant_colony' in EMBEDDINGS, "ant_colony not in EMBEDDINGS"
        assert 'institution' in EMBEDDINGS, "institution not in EMBEDDINGS"

    def test_embedding_registry_has_required_fields(self):
        """Verify embedding registry entries have required fields."""
        from src.embeddings import EMBEDDINGS

        required_functions = ['embed', 'validate']

        for system_name, embedding_module in EMBEDDINGS.items():
            for func_name in required_functions:
                assert hasattr(embedding_module, func_name), (
                    f"Embedding '{system_name}' missing required function '{func_name}'"
                )

    def test_no_hIDDEN_sector_substitutions(self):
        """Verify no hidden sector substitutions in experiments."""
        root_dir = os.path.join(os.path.dirname(__file__), '..', 'experiments')
        if not os.path.exists(root_dir):
            pytest.skip("experiments directory not found")

        python_files = find_all_python_files(root_dir)
        definitions = find_sector_definitions(python_files)

        # Check for non-canonical sector keys
        canonical_keys = {'amplitude', 'topology', 'transport', 'residual'}

        for defn in definitions:
            match = re.search(r"['\"](\w+)['\"]", defn['content'])
            if match:
                key = match.group(1)
                assert key in canonical_keys, (
                    f"Non-canonical sector key '{key}' in experiment {defn['file']}:{defn['line']}"
                )

    def test_canonical_metric_contract_exists(self):
        """Verify canonical metric contract document exists."""
        contract_path = os.path.join(
            os.path.dirname(__file__), '..', 'docs', 'specifications', 'canonical_metric_contract.md'
        )
        assert os.path.exists(contract_path), f"Canonical metric contract not found at {contract_path}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
