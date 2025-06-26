import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from scipy.stats import skew
import json
import os
from pathlib import Path


def process_scaling(
        df: pd.DataFrame,
        output_dir: str = "../backend/output") -> None:
    """
    Processes scaling for numeric columns in the DataFrame, selects best scaler per column based on skewness,
    applies the scaling, and saves the scaled data and a report to backend/output.

    Args:
        df: Input DataFrame with data to scale.
        output_dir: Output directory path (default: ./backend/output).
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Identify numeric columns
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    # Filter columns: non-binary (nunique > 2) and not too many missing (<50%)
    filtered_cols = [
        col for col in numeric_cols
        if df[col].nunique() > 2 and df[col].isnull().mean() < 0.5
    ]

    # Initialize structures
    scaled_df = pd.DataFrame(index=df.index)
    scaler_report = {}

    # Process each column
    for col in filtered_cols:
        col_data = df[col]
        notna_mask = col_data.notna()

        scalers = {
            'StandardScaler': StandardScaler(),
            'MinMaxScaler': MinMaxScaler(),
            'RobustScaler': RobustScaler()
        }

        best_scaler_name = None
        best_skewness = float('inf')
        best_scaled_data = None

        # Evaluate each scaler
        for name, scaler in scalers.items():
            try:
                # Handle non-NaN values
                non_missing = col_data[notna_mask].values.reshape(-1, 1)
                scaled_vals = scaler.fit_transform(non_missing)
                col_skew = abs(skew(scaled_vals.flatten()))

                # Update best scaler if skewness is lower
                if col_skew < best_skewness:
                    best_skewness = col_skew
                    best_scaler_name = name
                    best_scaled_data = scaled_vals.flatten()

            except Exception as e:
                print(
                    f"⚠️ Skipped scaler '{name}' for column '{col}': {
                        str(e)}")
                continue

        # Reconstruct full column with NaNs preserved
        full_col = pd.Series(np.nan, index=col_data.index)
        full_col[notna_mask] = best_scaled_data

        scaled_df[col] = full_col
        scaler_report[col] = best_scaler_name

    # Save scaled data to backend/output
    scaled_path = os.path.join(output_dir, "autoEDA_scaled_output.csv")
    scaled_df.to_csv(scaled_path, index=False)

    # Save scaler report to backend/output
    report_path = os.path.join(output_dir, "scaling_report.json")
    with open(report_path, 'w') as f:
        json.dump(scaler_report, f, indent=4)

    print(f"✅ Scaled data saved to: {scaled_path}")
    print(f"📋 Scaler report saved to: {report_path}")


if __name__ == "__main__":
    # Load your file
    df = pd.read_csv("laptopData.csv")

    process_scaling(df)
