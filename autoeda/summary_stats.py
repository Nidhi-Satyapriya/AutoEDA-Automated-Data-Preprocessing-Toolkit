import pandas as pd
import numpy as np
import os
import json


def load_and_clean_data(file_path, encoding):
    """
    Loads a csv file into a pandas DataFrame, removes duplicate rows, fills missing values in numeric columns with the mean, fills missing values in categorical columns with the mode, and strips whitespace from string columns.
    Args:
        file_path: Path to the CSV file.
        encoding: Encoding to use for reading the file.
    Returns:
        pandas.DataFrame: Cleaned DataFrame.
    """
    try:
        df = pd.read_csv(file_path, encoding=encoding)
    except Exception as e:
        raise ValueError(f"could not load file: {e}")

    # Remove duplicate rows
    df.drop_duplicates(inplace=True)

    # Fill missing values in numeric columns with (mean)
    for col in df.select_dtypes(include='number'):
        df[col] = df[col].fillna(df[col].mean())

    # Fill missing values in categorical columns (mode)
    for col in df.select_dtypes(include='object'):
        if df[col].isnull().any():
            df[col] = df[col].fillna(df[col].mode()[0])

    # Strip leading/trailing whitespace from string columns
    for col in df.select_dtypes(include='object'):
        df[col] = df[col].str.strip()

    return df


def split_numerical_categorical(df):
    """
    Splits a DataFrame's columns into numerical and categorical columns.
    Numerical columns are those with numeric data types, (here)excluding columns with 10 or fewer unique integer values, which are treated as encoded categorical columns.
    Args:
        df: Input DataFrame.
    Returns:
        Tuple: A tuple containing the numerical columns DataFrame and the categorical columns DataFrame.
    """
    # Get all columns with numeric data types
    numeric_cols = df.select_dtypes(include='number').columns

    numerical_cols = []
    encoded_categorical_cols = []

    # Heuristic: If the column has 10 or fewer unique integer values, treat as
    # categorical
    for col in numeric_cols:
        unique_vals = df[col].dropna().unique()
        if len(unique_vals) <= 10 and all(float(val).is_integer()
                                          for val in unique_vals):
            encoded_categorical_cols.append(col)
        else:
            numerical_cols.append(col)

    df_numerical = df[numerical_cols]
    df_categorical = df.select_dtypes(include='object')
    # Add detected encoded categorical columns to the categorical DataFrame
    df_categorical = pd.concat(
        [df_categorical, df[encoded_categorical_cols]], axis=1)

    return df_numerical, df_categorical

# only to be used on numerical data


def numerical_stats(num_df):
    """
    Calculate basic statistics for each numerical column in the DataFrame.
    Parameters:
        num_df: DataFrame containing numerical columns.
    Returns:
        dict: A dictionary where each key is a column name and the value is another dictionary with mean, median, min, max, std, and missing value count.
    """

    stats = {}
    for col in num_df.columns:
        stats[col] = {
            "mean": num_df[col].mean(),
            "median": num_df[col].median(),
            "min": num_df[col].min(),
            "max": num_df[col].max(),
            "std": num_df[col].std(),
            "missing": num_df[col].isnull().sum()
        }
    return stats

# returns most frequent values


def most_frequent_values(series):
    """
    Returns a list of the most frequent value(s) in a pandas Series.
    Parameters:
        series: The input pandas Series.
    Returns:
        list: List of the most frequent value(s).
    """
    freq = series.value_counts()
    return freq[freq == freq.max()].index.tolist()


def categorical_stats(cat_df):
    """
    Calculates summary statistics for each categorical column in the given DataFrame.
    Args:
        cat_df: DataFrame containing categorical columns.
    Returns:
        dict: A dictionary where each key is a column name and the value is a dictionary with the most frequent value and the number of unique values for that column.
    """
    stats = {}
    for col in cat_df.columns:
        stats[col] = {
            "most_frequent_value": most_frequent_values(cat_df[col]),
            "unique_counts": cat_df[col].nunique()
        }
    return stats

# calls numerical_stats and categorical_stats func


def full_stats(numerical_df, categorical_df):
    """
    Generates summary statistics for numerical and categorical DataFrames.
    Args:
        numerical_df: DataFrame containing numerical columns.
        categorical_df: DataFrame containing categorical columns.
    Returns:
        dict: Dictionary with summary statistics for numerical and categorical columns.
    """
    return {
        "Numerical Columns": numerical_stats(numerical_df),
        "Categorical Columns": categorical_stats(categorical_df)
    }


def convert_to_builtin_types(obj):
    """
    pandas and NumPy use specialized data types such as:
    -  `np.int64`, `np.float64`, `np.bool_`
    -  `np.ndarray`

    These types are not supported by Python's built-in `json` module.

    To handle this, we use the `convert_to_builtin_types()` function, which:

    - Converts NumPy integers to standard Python `int`
    - Converts NumPy floats to standard Python `float`
    - Converts NumPy booleans to Python `bool`
    - Converts NumPy arrays to Python lists
    - Recursively applies these conversions to values inside dictionaries

    This ensures that the final dictionary contains **only native Python types**, making it safe to export to JSON format.
    """
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.bool_)):
        return bool(obj)
    elif isinstance(obj, (np.ndarray, list)):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: convert_to_builtin_types(v) for k, v in obj.items()}
    else:
        return obj


def summarize_csv(
        file_or_path,
        output_dir="./notebooks/output-files/statistics_summary",
        encoding="utf-8",
        export_json=False):
    """
    Summarizes a CSV file by computing statistics for numerical and categorical columns.
    Args:
        file_or_path: Path to the CSV file or a file-like object.
        output_dir: Directory to save the JSON summary if export_json is True. Defaults to "./notebooks/output-files/statistics_summary".
        encoding: Encoding to use when reading the file. Defaults to "utf-8".
        export_json: Whether to export and save the summary as a JSON file. Defaults to False.
    Returns:
        dict: Summary statistics.
        str(optional): Path to the exported(saved) JSON file if export_json is True.
    """
    # check if we are dealing with a file path or a file object
    if isinstance(file_or_path, str):  # if a file path, open it
        filename = os.path.basename(file_or_path)
        df = load_and_clean_data(file_or_path, encoding=encoding)
    else:  # if a file object from an upload
        filename = file_or_path.filename  # extract the original filename
        df = load_and_clean_data(file_or_path, encoding=encoding)

    df_numerical, df_categorical = split_numerical_categorical(df)
    stats = convert_to_builtin_types(full_stats(df_numerical, df_categorical))

    if export_json:
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(filename)[0]
        json_export_path = os.path.join(
            output_dir, f"{base_name}_stats_summary.json")
        with open(json_export_path, "w") as f:
            json.dump(stats, f, indent=4)
        return stats, json_export_path

    return stats


if __name__ == "__main__":
    stats, out_path = summarize_csv(
        "./notebooks/sample_csv/titanic.csv", export_json=True)
    print(f"Exported summary stats to: {out_path}")
