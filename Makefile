.PHONY: figures test clean

figures:
	python scripts/generate_all_figures.py

test:
	python -m pytest tests/ -v

clean:
	rm -rf results/figures/*.pdf results/figures/*.svg results/figures/*.png
	rm -rf src/**/__pycache__ tests/__pycache__
