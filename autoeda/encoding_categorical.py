"""
Module for encoding categorical features.
Provides functions for label encoding and one-hot encoding.
"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder
import logging
import os

# Set up logging to file in backend/output
OUTPUT_DIR = "backend/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
LOG_FILE = os.path.join(OUTPUT_DIR, "encoding_log.txt")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def label_encode(df, columns):
    """
    Applies Label Encoding to the specified columns in the dataframe.
    """
    df = df.copy()
    le = LabelEncoder()
    for col in columns:
        if df[col].dtype == 'object':
            df[col] = le.fit_transform(df[col].astype(str))
            logging.info(f"Label encoding applied on column: {col}")
        else:
            logging.warning(f"Skipped column (non-object dtype): {col}")
    return df

def one_hot_encode(df, columns):
    """
    Applies One-Hot Encoding to the specified columns in the dataframe.
    """
    df = df.copy()
    df = pd.get_dummies(df, columns=columns)
    logging.info(f"One-hot encoding applied on columns: {columns}")
    return df
