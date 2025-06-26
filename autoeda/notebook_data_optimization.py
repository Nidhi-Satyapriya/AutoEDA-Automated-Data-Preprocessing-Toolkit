import pandas as pd
import numpy as np
import logging

# Get a logger for this module
logger = logging.getLogger(__name__)


def optimize_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimizes the data types of a pandas DataFrame to reduce memory usage.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The DataFrame with optimized data types.
    """
    logger.info("Starting data type optimization.")
    processed_date_cols = set()

    # Convert date-like columns first
    for col in df.columns:
        if any(x in col.lower() for x in ['date', 'time', 'timestamp']):
            if df[col].dtype == 'object':  # Only attempt conversion if it's an object type
                # Mark as processed for date conversion attempt
                processed_date_cols.add(col)
                try:
                    logger.info(
                        f"Attempting to convert column '{col}' to datetime objects.")
                    df[col] = pd.to_datetime(df[col])
                    logger.info(
                        f"Successfully converted column '{col}' to datetime.")
                except Exception as e:
                    logger.warning(
                        f"Could not convert column '{col}' to datetime: {e}. It will remain an object type.")
                    # If conversion fails, it remains object.
                    pass

    # Convert object columns with low cardinality to category
    # Exclude columns that were identified as date-like but failed conversion,
    # they should remain object.
    for col in df.select_dtypes(include='object'):
        if col not in processed_date_cols or pd.api.types.is_datetime64_any_dtype(
                df[col]):
            # If it's not a processed date col OR it was successfully converted to datetime (which means it's not object anymore)
            # This check might be redundant for the second part if
            # select_dtypes(include='object') is efficient
            if df[col].nunique() < 50:
                # Additional check: ensure it's not a date-like column that
                # failed conversion
                is_failed_date_col = any(
                    x in col.lower() for x in [
                        'date',
                        'time',
                        'timestamp']) and col in processed_date_cols and not pd.api.types.is_datetime64_any_dtype(
                    df[col])
                if not is_failed_date_col:
                    logger.info(f"Converting column '{col}' to category type.")
                    df[col] = df[col].astype('category')
                else:
                    logger.info(
                        f"Skipping category conversion for failed date column '{col}'.")

    # Downcast numeric columns
    for col in df.select_dtypes(include=['float']):
        logger.info(f"Downcasting float column '{col}'.")
        df[col] = pd.to_numeric(df[col], downcast='float')
    for col in df.select_dtypes(include=['int']):
        logger.info(f"Downcasting integer column '{col}'.")
        df[col] = pd.to_numeric(df[col], downcast='integer')

    logger.info("Data type optimization complete.")
    return df
