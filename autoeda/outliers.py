import pandas as pd
import numpy as np
from scipy.stats import zscore
import json
import os

def process_outliers(df_input: pd.DataFrame, base_output_dir: str):
    """
    Detects, flags, caps, and removes outliers from a DataFrame.

    Parameters:
    ----------
    df_input : pd.DataFrame
        The input DataFrame with numeric columns for outlier processing.
    base_output_dir : str
        The directory where output files (CSV and JSON reports) will be saved.

    Returns:
    -------
    dict
        A dictionary containing:
        - 'flagged_df': DataFrame with outlier flags.
        - 'capped_df': DataFrame with outliers capped (Winsorized).
        - 'removed_df': DataFrame with outliers removed.
        - 'summary': Dictionary containing the outlier report data.
        - 'paths': Dictionary with paths to the saved files:
            - 'flagged_csv': Path to the flagged outliers CSV.
            - 'capped_csv': Path to the capped outliers CSV.
            - 'removed_csv': Path to the removed outliers CSV.
            - 'report_json': Path to the JSON outlier report.
            - 'summary_csv': Path to the tabular summary CSV.
    """
    os.makedirs(base_output_dir, exist_ok=True)

    # Work on a copy to avoid modifying the original DataFrame
    df = df_input.copy()
    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()

    # Containers for results
    detection_methods = {}
    outliers_detected_count = {}
    rows_with_outliers = set()
    outlier_flags_df = pd.DataFrame(index=df.index)

    # Detect Skewness and apply outlier detection
    for col in numeric_cols:
        # Fill NaNs to avoid zscore errors and issues with quantile
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].median()) # Or some other appropriate strategy

        skew_val = df[col].skew()

        if abs(skew_val) < 1.0:
            # Z-score method
            method = "Z-score"
            if df[col].std() == 0: # Avoid division by zero if all values are the same
                z_scores_col = np.zeros_like(df[col], dtype=float)
                outliers = np.zeros_like(df[col], dtype=bool)
                lower_b = df[col].mean() # No real bounds if std is 0
                upper_b = df[col].mean()
            else:
                z_scores_col = zscore(df[col])
                outliers = np.abs(z_scores_col) > 3
                lower_b = df[col].mean() - 3 * df[col].std()
                upper_b = df[col].mean() + 3 * df[col].std()
        else:
            # IQR method
            method = "IQR"
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_b = Q1 - 1.5 * IQR
            upper_b = Q3 + 1.5 * IQR
            outliers = (df[col] < lower_b) | (df[col] > upper_b)

        detection_methods[col] = method
        outliers_detected_count[col] = int(outliers.sum())
        rows_with_outliers.update(df[outliers].index)
        outlier_flags_df[f"{col}_is_outlier"] = outliers.astype(int)

    # Create flagged dataset
    flagged_df = pd.concat([df_input.copy(), outlier_flags_df], axis=1) # Use original df_input for concatenation
    flagged_csv_path = os.path.join(base_output_dir, "autoEDA_outliers_flagged.csv")
    flagged_df.to_csv(flagged_csv_path, index=False)

    # Outlier Capping (Winsorization)
    capped_df = df.copy() # Use the NaN-filled 'df' for capping calculations
    for col in numeric_cols:
        # Re-calculate bounds based on the (potentially NaN-filled and now processed) column
        skew_val = capped_df[col].skew() # Skew might change slightly if NaNs were filled
        if abs(skew_val) < 1.0:
            if capped_df[col].std() == 0:
                lower_b_cap = capped_df[col].mean()
                upper_b_cap = capped_df[col].mean()
            else:
                lower_b_cap = capped_df[col].mean() - 3 * capped_df[col].std()
                upper_b_cap = capped_df[col].mean() + 3 * capped_df[col].std()
        else:
            Q1_cap = capped_df[col].quantile(0.25)
            Q3_cap = capped_df[col].quantile(0.75)
            IQR_cap = Q3_cap - Q1_cap
            lower_b_cap = Q1_cap - 1.5 * IQR_cap
            upper_b_cap = Q3_cap + 1.5 * IQR_cap
        
        capped_df[col] = np.clip(capped_df[col], lower_b_cap, upper_b_cap)
    
    # If df_input had non-numeric columns, ensure they are present in capped_df
    for col in df_input.columns:
        if col not in capped_df.columns:
            capped_df[col] = df_input[col]


    capped_csv_path = os.path.join(base_output_dir, "autoEDA_outliers_capped.csv")
    capped_df.to_csv(capped_csv_path, index=False)

    # Outlier Removal - use original df_input to drop rows
    removed_df = df_input.copy().drop(index=list(rows_with_outliers))
    removed_csv_path = os.path.join(base_output_dir, "autoEDA_outliers_removed.csv")
    removed_df.to_csv(removed_csv_path, index=False)

    # Generate JSON report
    report_summary = {
        "detection_methods": detection_methods,
        "outliers_detected_count": outliers_detected_count,
        "total_rows_with_outliers": len(rows_with_outliers),
        "output_files": {
            "flagged": os.path.basename(flagged_csv_path),
            "capped": os.path.basename(capped_csv_path),
            "removed": os.path.basename(removed_csv_path)
        }
    }
    report_json_path = os.path.join(base_output_dir, "autoEDA_outlier_report.json")
    with open(report_json_path, "w") as f:
        json.dump(report_summary, f, indent=2)

    # Save tabular summary report
    summary_report_df = pd.DataFrame({
        "Column": list(detection_methods.keys()),
        "Detection_Method": list(detection_methods.values()),
        "Outliers_Detected": list(outliers_detected_count.values())
    })
    summary_csv_path = os.path.join(base_output_dir, "autoEDA_outlier_summary.csv")
    summary_report_df.to_csv(summary_csv_path, index=False)

    print(f"✅ Outlier processing complete. Outputs in {base_output_dir}")
    print(f"📄 Reports saved: {os.path.basename(report_json_path)}, {os.path.basename(summary_csv_path)}")

    return {
        'flagged_df': flagged_df,
        'capped_df': capped_df,
        'removed_df': removed_df,
        'summary': report_summary,
        'paths': {
            'flagged_csv': flagged_csv_path,
            'capped_csv': capped_csv_path,
            'removed_csv': removed_csv_path,
            'report_json': report_json_path,
            'summary_csv': summary_csv_path,
        }
    }

if __name__ == "__main__":
    # Example of running this module standalone
    # Create a dummy DataFrame for testing
    data = {
        'Numeric1': np.random.randn(100).tolist() + [10, 12, -11], # Some outliers
        'Numeric2': np.random.rand(103).tolist(),
        'Numeric3_skewed': np.random.exponential(1, 100).tolist() + [50, 55, 60], # Skewed with outliers
        'Category': ['A']*50 + ['B']*53,
        'Numeric4_with_nan': [1,2,3,np.nan]*25 + [4,5,np.nan] # 103 items
    }
    # Ensure all lists have the same length for DataFrame creation
    max_len = max(len(v) for v in data.values())
    for k in data:
        if len(data[k]) < max_len:
            data[k].extend([np.nan] * (max_len - len(data[k]))) # Pad with NaN or appropriate value

    sample_df = pd.DataFrame(data)
    
    print("Sample DataFrame for standalone outlier processing:")
    print(sample_df.head())
    print(f"\nShape of sample DataFrame: {sample_df.shape}")
    print(f"\nNaN counts per column:\n{sample_df.isnull().sum()}")


    # Define a directory for outputs when running standalone
    standalone_output_dir = "backend/output/standalone_outlier_tests"
    if not os.path.exists(standalone_output_dir):
        os.makedirs(standalone_output_dir)

    print(f"\nStarting standalone outlier processing. Output will be in: {standalone_output_dir}")
    
    results = process_outliers(sample_df, standalone_output_dir)

    print("\nStandalone outlier processing finished.")
    print(f"Flagged DataFrame shape: {results['flagged_df'].shape}")
    print(f"Capped DataFrame shape: {results['capped_df'].shape}")
    print(f"Removed DataFrame shape: {results['removed_df'].shape}")
    print(f"Summary report: {results['summary']}")
    print(f"File paths: {results['paths']}")

    # Verify one of the output files exists
    if os.path.exists(results['paths']['removed_csv']):
        print(f"\nSuccessfully created: {results['paths']['removed_csv']}")
        loaded_removed_df = pd.read_csv(results['paths']['removed_csv'])
        print(f"  Loaded removed_df shape: {loaded_removed_df.shape}")
    else:
        print(f"\nERROR: File not found {results['paths']['removed_csv']}")
