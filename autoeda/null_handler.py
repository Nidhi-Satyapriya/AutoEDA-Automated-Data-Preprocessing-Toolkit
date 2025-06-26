import pandas as pd
import numpy as np
import os
from typing import Dict, Callable
import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# --------------*NULL HANDLING STRATEGIES*------------------


def drop_nulls(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna()


def replace_with_fixed(df: pd.DataFrame, value=0) -> pd.DataFrame:
    return df.fillna(value)


def replace_with_mean(df: pd.DataFrame) -> pd.DataFrame:
    df_filled = df.copy()
    for col in df_filled.select_dtypes(include=[np.number]):
        df_filled[col] = df_filled[col].fillna(df_filled[col].mean())
    return df_filled


def replace_with_median(df: pd.DataFrame) -> pd.DataFrame:
    df_filled = df.copy()
    for col in df_filled.select_dtypes(include=[np.number]):
        df_filled[col] = df_filled[col].fillna(df_filled[col].median())
    return df_filled


def replace_with_mode(df: pd.DataFrame) -> pd.DataFrame:
    df_filled = df.copy()
    for col in df.columns:
        if df[col].isnull().any():
            mode_val = df[col].mode()
            if not mode_val.empty:
                df_filled[col] = df_filled[col].fillna(mode_val.iloc[0])
            elif df[col].dtype in ['object', 'category']:
                df_filled[col] = df_filled[col].fillna("Unknown")
            else:
                df_filled[col] = df_filled[col].fillna(0)
    return df_filled


def forward_fill(df: pd.DataFrame) -> pd.DataFrame:
    return df.ffill()


def backward_fill(df: pd.DataFrame) -> pd.DataFrame:
    return df.bfill()

# ------------------*EVALUATION & STRATEGY SELECTION*----------------------


def evaluate_methods(original_df: pd.DataFrame,
                     cleaned_versions: Dict[str,
                                            pd.DataFrame],
                     log_lines: list) -> str:
    original_nulls = original_df.isnull().sum().sum()
    original_shape = original_df.shape
    best_score = float("-inf")
    best_method = None

    for name, df in cleaned_versions.items():
        remaining_nulls = df.isnull().sum().sum()
        nulls_removed = original_nulls - remaining_nulls
        row_ratio = df.shape[0] / original_shape[0] if original_shape[0] else 0
        col_ratio = df.shape[1] / original_shape[1] if original_shape[1] else 0

        score = ((nulls_removed / original_nulls if original_nulls >
                  0 else 1.0) * 0.5 + row_ratio * 0.25 + col_ratio * 0.25)

        log_lines.append(f"Method tried: {name}")
        log_lines.append(f" - Nulls removed: {nulls_removed}")
        log_lines.append(f" - Remaining nulls: {remaining_nulls}")
        log_lines.append(f" - Shape after cleaning: {df.shape}")
        log_lines.append(f" - Strategy score: {score:.4f}\n")

        if score > best_score:
            best_score = score
            best_method = name

    log_lines.append(f"✅ Best strategy selected: {best_method}\n")
    return best_method

# ------------------------* MAIN ENTRYPOINT *-------------------------------


def process_csv(input_path: str, output_path: str) -> None:
    if not os.path.exists(input_path):
        logging.error(f"Input file not found: {input_path}")
        return

    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        logging.error(f"Failed to read CSV: {e}")
        return

    if df.empty:
        logging.warning("Input CSV is empty. No processing done.")
        return

    logging.info(f"Input CSV loaded: {input_path}")
    logging.info(
        f"Initial Shape: {
            df.shape}, Null Count: {
            df.isnull().sum().sum()}")

    log_lines = []
    log_lines.append(f"Processing file: {input_path}")
    log_lines.append(f"Initial shape: {df.shape}")
    log_lines.append(f"Total null values: {df.isnull().sum().sum()}\n")

    strategies: Dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
        "drop_nulls": drop_nulls,
        "replace_with_fixed": lambda d: replace_with_fixed(d, 0),
        "replace_with_mean": replace_with_mean,
        "replace_with_median": replace_with_median,
        "replace_with_mode": replace_with_mode,
        "forward_fill": forward_fill,
        "backward_fill": backward_fill,
    }

    cleaned_versions = {name: func(df.copy())
                        for name, func in strategies.items()}

    best_method = evaluate_methods(df, cleaned_versions, log_lines)
    best_df = cleaned_versions[best_method]

    logging.info(f"Best strategy selected: {best_method}")
    logging.info(
        f"Cleaned Data Shape: {
            best_df.shape}, Nulls Remaining: {
            best_df.isnull().sum().sum()}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    best_df.to_csv(output_path, index=False)
    logging.info(f"Cleaned CSV saved at: {output_path}")

    # Save log file
    log_file_path = os.path.join(
        os.path.dirname(output_path),
        "null_handling_log.txt")
    with open(log_file_path, "w") as f:
        f.write("\n".join(log_lines))
    logging.info(f"Decision-making log saved at: {log_file_path}")
