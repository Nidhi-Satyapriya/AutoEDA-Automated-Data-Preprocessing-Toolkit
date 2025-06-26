import pandas as pd
import logging
import os

# Configure logging to file: optimized_log.txt
# This will create optimized_log.txt if it doesn't exist, or append to it.
logging.basicConfig(filename='optimized_log.txt',
                    filemode='a',  # Append to the log file
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    force=True)  # force=True is important if re-running in same session


def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimizes the data types of a Pandas DataFrame.

    Args:
        df: The input DataFrame.

    Returns:
        A new DataFrame with optimized data types.
    """
    df_optimized = df.copy()
    logging.info("Starting data type optimization.")

    for col in df_optimized.columns:
        col_dtype = df_optimized[col].dtype
        original_memory = df_optimized[col].memory_usage(deep=True)

        try:
            # Categorical Conversion
            if col_dtype == 'object':
                num_unique_values = df_optimized[col].nunique()
                if num_unique_values < 50:
                    df_optimized[col] = df_optimized[col].astype('category')
                    logging.info(
                        f"Column '{col}': Converted to category. Unique values: {num_unique_values}.")
                # else: # Optional: log if not converted
                #     logging.info(f"Column '{col}': Not converted to category. Unique values: {num_unique_values} >= 50.")

            # Numeric Downcasting (Floats)
            elif col_dtype == 'float64':
                df_optimized[col] = pd.to_numeric(
                    df_optimized[col], downcast='float')
                logging.info(
                    f"Column '{col}': Downcast to float32 (or smaller if possible via to_numeric).")

            # Numeric Downcasting (Integers)
            elif col_dtype == 'int64':
                df_optimized[col] = pd.to_numeric(
                    df_optimized[col], downcast='integer')
                logging.info(
                    f"Column '{col}': Downcast to int32 or smaller (e.g., int16, int8).")

            # Datetime Parsing
            # Check if column name suggests it's a date/time column
            if any(keyword in col.lower()
                   for keyword in ['date', 'time', 'timestamp']):
                # Attempt conversion only if not already datetime and not
                # category (which might have been converted from object)
                if not pd.api.types.is_datetime64_any_dtype(
                        df_optimized[col]) and df_optimized[col].dtype != 'category':
                    try:
                        # Try to infer datetime format first for flexibility
                        df_optimized[col] = pd.to_datetime(
                            df_optimized[col], errors='raise')
                        logging.info(f"Column '{col}': Converted to datetime.")
                    except Exception as e_dt:
                        # If direct conversion fails, log it. Could add more
                        # specific format attempts here if needed.
                        logging.warning(
                            f"Column '{col}': Could not convert to datetime using infer_datetime_format. Error: {e_dt}")
        except Exception as e:
            logging.error(
                f"Column '{col}': Error during optimization. Original dtype: {col_dtype}. Error: {e}")
            continue  # Continue to the next column

        optimized_memory = df_optimized[col].memory_usage(deep=True)
        if original_memory != optimized_memory:  # Log only if memory changed
            logging.info(
                f"Column '{col}': Memory usage changed from {original_memory} to {optimized_memory} bytes.")

    logging.info("Data type optimization finished.")
    return df_optimized


def optimize_csv(input_path: str, output_path: str) -> None:
    """
    Reads a CSV, optimizes its data types, and saves it to a new CSV.

    Args:
        input_path: Path to the input CSV file.
        output_path: Path to save the optimized CSV file.
    """
    logging.info(f"Starting CSV optimization for {input_path}...")
    try:
        # Read CSV
        try:
            df = pd.read_csv(input_path)
            logging.info(f"Successfully read CSV from {input_path}.")
        except FileNotFoundError:
            logging.error(f"Input file not found: {input_path}")
            print(f"Error: Input file not found at {input_path}")
            return
        except Exception as e:
            logging.error(f"Error reading CSV from {input_path}: {e}")
            print(f"Error reading CSV from {input_path}: {e}")
            return

        # Log original memory usage
        original_memory_usage = df.memory_usage(deep=True).sum()
        logging.info(
            f"Original DataFrame memory usage: {original_memory_usage / (1024 * 1024):.2f} MB")
        print(
            f"Original DataFrame memory usage: {original_memory_usage / (1024 * 1024):.2f} MB")

        # Apply optimize_dtypes
        df_optimized = optimize_dtypes(df)

        # Log optimized memory usage
        optimized_memory_usage = df_optimized.memory_usage(deep=True).sum()
        logging.info(
            f"Optimized DataFrame memory usage: {optimized_memory_usage / (1024 * 1024):.2f} MB")
        print(
            f"Optimized DataFrame memory usage: {optimized_memory_usage / (1024 * 1024):.2f} MB")

        # Save optimized DataFrame to output_path
        # Ensure output directory exists (though pandas usually handles this for simple paths)
        # For robustness, one might explicitly create
        # os.path.dirname(output_path)
        try:
            df_optimized.to_csv(output_path, index=False)
            logging.info(f"Successfully saved optimized CSV to {output_path}.")
            print(f"Optimized CSV saved to {output_path}")
        except Exception as e:
            logging.error(f"Error saving optimized CSV to {output_path}: {e}")
            print(f"Error saving optimized CSV to {output_path}: {e}")

    except Exception as e:
        logging.error(f"An unexpected error occurred in optimize_csv: {e}")
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    print("Running data_optimizer.py script directly...")

    # Define input and output paths
    # These paths are placeholders. Ensure these files/directories exist or can be created.
    # For actual execution, 'backend/output/null_value_removed.csv' should exist.
    # The 'backend/output/' directory should exist for the output file.

    # Create dummy input directories and file if they don't exist for
    # demonstration
    input_dir = "backend/output"
    output_dir = "backend/output"  # Same for this example

    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    input_csv_path = os.path.join(input_dir, 'null_value_removed.csv')
    output_csv_path = os.path.join(output_dir, 'data_optimized.csv')

    # Create a dummy input CSV if it doesn't exist, to allow the script to run
    # without error
    if not os.path.exists(input_csv_path):
        print(f"Creating dummy input file: {input_csv_path}")
        dummy_data = {
            'col_object': ['A', 'B', 'A', 'C', 'B'] * 10,  # < 50 unique
            'col_float64': [1.0, 2.0, 3.0, 4.0, 5.0] * 10,
            'col_int64': [100, 200, 300, 400, 500] * 10,
            'col_date_string': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'] * 10,
            # Not a date column by name
            'col_to_ignore_dt': [1, 2, 3, 4, 5] * 10,
            # 50 unique, won't convert to category
            'col_high_cardinality_object': [f'item_{i}' for i in range(50)]
        }
        dummy_df = pd.DataFrame(dummy_data)
        dummy_df.to_csv(input_csv_path, index=False)
        print(f"Dummy input file {input_csv_path} created with sample data.")

    print(
        f"Attempting to optimize {input_csv_path} and save to {output_csv_path}")
    optimize_csv(input_csv_path, output_csv_path)
    print("Script execution finished.")
