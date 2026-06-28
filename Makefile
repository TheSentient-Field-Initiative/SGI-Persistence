.PHONY: figures tables test reproduce clean

figures:
	python scripts/generate_all_figures.py

tables:
	python scripts/generate_tables.py

test:
	python -m pytest tests/ -v

reproduce: test figures tables
	@echo "=== Reproduction complete ==="
	@echo "Figures: results/figures/"
	@echo "Tables: results/tables/"

clean:
	rm -rf results/figures/*.pdf results/figures/*.svg results/figures/*.png
	rm -rf results/tables/*.csv results/tables/*.tex results/tables/*.md
	rm -rf src/**/__pycache__ tests/__pycache__
