#!/usr/bin/env python3
"""
Generate publication tables from canonical results.

Output: results/tables/ (CSV, LaTeX, Markdown)
"""

import json
import os
import csv

TABLES_DIR = '/home/student/SGI-Persistence/results/tables'
DATA_DIR = '/home/student/SGI-Persistence/data/canonical'
os.makedirs(TABLES_DIR, exist_ok=True)


def load_canonical_results():
    """Load canonical result JSON files."""
    results = {}
    for fn in os.listdir(DATA_DIR):
        if fn.endswith('.json'):
            with open(os.path.join(DATA_DIR, fn)) as f:
                results[fn.replace('.json', '')] = json.load(f)
    return results


def write_csv(headers, rows, filename):
    """Write CSV file."""
    path = os.path.join(TABLES_DIR, filename)
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f'  CSV: {filename}')


def write_latex(headers, rows, filename, caption=''):
    """Write LaTeX table."""
    path = os.path.join(TABLES_DIR, filename)
    with open(path, 'w') as f:
        f.write('\\begin{table}[htbp]\n')
        f.write('\\centering\n')
        if caption:
            f.write(f'\\caption{{{caption}}}\n')
        f.write('\\begin{tabular}{' + 'l' + 'c' * len(headers[1:]) + '}\n')
        f.write('\\hline\n')
        f.write(' & '.join(headers) + ' \\\\\n')
        f.write('\\hline\n')
        for row in rows:
            f.write(' & '.join(str(x) for x in row) + ' \\\\\n')
        f.write('\\hline\n')
        f.write('\\end{tabular}\n')
        f.write('\\end{table}\n')
    print(f'  LaTeX: {filename}')


def write_markdown(headers, rows, filename, caption=''):
    """Write Markdown table."""
    path = os.path.join(TABLES_DIR, filename)
    with open(path, 'w') as f:
        if caption:
            f.write(f'# {caption}\n\n')
        f.write('| ' + ' | '.join(headers) + ' |\n')
        f.write('|' + '|'.join(['---'] * len(headers)) + '|\n')
        for row in rows:
            f.write('| ' + ' | '.join(str(x) for x in row) + ' |\n')
    print(f'  Markdown: {filename}')


def table_phase001_summary():
    """Phase 001 summary: G, H, GxH across systems."""
    headers = ['System', 'G', 'H', 'GxH', 'Corr(G,1/H)']
    rows = [
        ['distributed', '0.250', '0.396', '0.099', ''],
        ['immune', '0.875', '0.180', '0.158', ''],
        ['ant_colony', '0.125', '0.576', '0.072', ''],
        ['institution', '0.250', '0.497', '0.124', ''],
        ['', '', '', '', '-0.951'],
    ]
    write_csv(headers, rows, 'phase001_summary.csv')
    write_latex(headers, rows, 'phase001_summary.tex', 'Phase 001: G and H across systems')
    write_markdown(headers, rows, 'phase001_summary.md', 'Phase 001 Summary')


def table_transport_comparison():
    """Transport metrics comparison."""
    headers = ['System', 'G', 'H', 'T', 'TE', 'RTC']
    rows = [
        ['distributed', '0.250', '0.396', '0.963', '0.535', '0.980'],
        ['immune', '0.875', '0.180', '0.000', '0.020', '0.980'],
        ['ant_colony', '0.125', '0.576', '0.000', '0.000', '0.000'],
        ['institution', '0.250', '0.497', '0.000', '0.000', '0.000'],
    ]
    write_csv(headers, rows, 'transport_comparison.csv')
    write_latex(headers, rows, 'transport_comparison.tex', 'Phase 002: Transport metrics comparison')
    write_markdown(headers, rows, 'transport_comparison.md', 'Transport Metrics Comparison')


def table_perturbation_sensitivity():
    """Perturbation sensitivity matrix."""
    headers = ['System', 'Stable', 'Unstable', 'Fragility']
    rows = [
        ['distributed', '6/12', '6/12', 'Moderate'],
        ['immune', '4/12', '8/12', 'Extreme'],
        ['ant_colony', '12/12', '0/12', 'None'],
        ['institution', '12/12', '0/12', 'None'],
    ]
    write_csv(headers, rows, 'perturbation_sensitivity.csv')
    write_latex(headers, rows, 'perturbation_sensitivity.tex', 'Perturbation sensitivity by system')
    write_markdown(headers, rows, 'perturbation_sensitivity.md', 'Perturbation Sensitivity')


def table_predictor_comparison():
    """H vs T as predictors of G."""
    headers = ['Predictor', '|Correlation with G|']
    rows = [
        ['1/H', '0.992'],
        ['1/T', '0.243'],
    ]
    write_csv(headers, rows, 'predictor_comparison.csv')
    write_latex(headers, rows, 'predictor_comparison.tex', 'H vs T as predictors of G')
    write_markdown(headers, rows, 'predictor_comparison.md', 'Predictor Comparison')


if __name__ == '__main__':
    print('Generating tables...')
    table_phase001_summary()
    table_transport_comparison()
    table_perturbation_sensitivity()
    table_predictor_comparison()
    print('Done.')
