.PHONY: figures tables test reproduce clean deterministic hash

figures:
	python scripts/generate_all_figures.py

tables:
	python scripts/generate_tables.py

test:
	python -m pytest tests/ -v

deterministic:
	PYTHONHASHSEED=42 python -m pytest tests/ -v --tb=short
	PYTHONHASHSEED=42 python scripts/generate_all_figures.py
	PYTHONHASHSEED=42 python scripts/generate_tables.py
	@echo "=== Deterministic replay complete ==="

hash:
	python scripts/hash_artifacts.py

reproduce: test figures tables
	@echo "=== Reproduction complete ==="
	@echo "Figures: results/figures/"
	@echo "Tables: results/tables/"

clean:
	rm -rf results/figures/*.pdf results/figures/*.svg results/figures/*.png
	rm -rf results/tables/*.csv results/tables/*.tex results/tables/*.md
	rm -rf results/hashes/*.json
	rm -rf src/**/__pycache__ tests/__pycache__
