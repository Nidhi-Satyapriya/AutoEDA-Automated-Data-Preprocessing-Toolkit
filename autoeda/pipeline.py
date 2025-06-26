"""
pipeline.py: Outlier Processing Pipeline for AutoEDA

This module provides a high-level function to orchestrate outlier detection, flagging, capping, and removal using the logic from outliers.py. It is designed for integration with CLI, backend, or notebook workflows.
"""

import os
import pandas as pd
from autoeda import outliers


def run_outlier_pipeline(scaled_csv_path, output_dir):
    """
    Run the full outlier processing pipeline on a scaled dataset.

    Parameters
    ----------
    scaled_csv_path : str
        Path to the scaled CSV file (input dataset).
    output_dir : str
        Directory to store all output files (flagged, capped, removed datasets, and reports).

    Returns
    -------
    dict
        Dictionary containing:
            - 'flagged_csv': Path to flagged dataset
            - 'capped_csv': Path to capped dataset
            - 'removed_csv': Path to dataset with outliers removed
            - 'summary_report': Path to outlier summary report (JSON/Markdown)
            - 'outlier_stats': Outlier statistics/metadata (dict)

    Raises
    ------
    FileNotFoundError: If the input file does not exist.
    ValueError: If the input file is malformed or cannot be loaded.

    Example
    -------
    >>> result = run_outlier_pipeline('output-files/autoEDA_scaled_output.csv', 'output-files/outlier_results')
    >>> print(result['flagged_csv'])
    """
    if not os.path.isfile(scaled_csv_path):
        raise FileNotFoundError(f"Input file not found: {scaled_csv_path}")

    os.makedirs(output_dir, exist_ok=True)

    try:
        df = pd.read_csv(scaled_csv_path)
    except Exception as e:
        raise ValueError(f"Failed to load input CSV: {e}")

    # Call the main orchestration function from outliers.py
    # Assumes outliers.process_outliers returns a dict with DataFrames and
    # stats
    results = outliers.process_outliers(df, output_dir)

    # Save DataFrames to disk
    flagged_csv = os.path.join(output_dir, 'flagged_outliers.csv')
    capped_csv = os.path.join(output_dir, 'capped_outliers.csv')
    removed_csv = os.path.join(output_dir, 'removed_outliers.csv')
    results['flagged'].to_csv(flagged_csv, index=False)
    results['capped'].to_csv(capped_csv, index=False)
    results['removed'].to_csv(removed_csv, index=False)

    # Save summary report
    summary_report = os.path.join(output_dir, 'outlier_summary.json')
    if 'summary' in results:
        import json
        with open(summary_report, 'w') as f:
            json.dump(results['summary'], f, indent=2)
    else:
        summary_report = None

    return {
        'flagged_csv': flagged_csv,
        'capped_csv': capped_csv,
        'removed_csv': removed_csv,
        'summary_report': summary_report,
        'outlier_stats': results.get('summary', {})
    }
