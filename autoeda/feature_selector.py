import pandas as pd
import numpy as np
import logging
import os
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure output directory exists globally for all functions
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
log_file_path = os.path.join(output_dir, "feature_selection_log.txt")


def remove_low_variance(df: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """
    Removes features from a DataFrame with variance below a given threshold.
    (Existing docstring and code)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")
    if not isinstance(threshold, (int, float)):
        raise TypeError("Input 'threshold' must be a numeric value.")
    if threshold < 0:
        raise ValueError("Input 'threshold' must be non-negative.")

    numeric_cols_df = df.select_dtypes(include=np.number)
    if numeric_cols_df.empty:
        logging.info(
            "No numeric columns found to calculate variance in remove_low_variance.")
        with open(log_file_path, "a") as f:
            f.write(f"Timestamp: {pd.Timestamp.now()}\n")
            f.write(f"Function: remove_low_variance\n")
            f.write(f"Parameters: threshold={threshold}\n")
            f.write(f"Action: No numeric columns found. No features removed.\n\n")
        return df

    variances = numeric_cols_df.var()
    low_variance_features = variances[variances < threshold].index.tolist()

    original_feature_count = len(df.columns)
    df_filtered = df.drop(columns=low_variance_features, errors='ignore')
    removed_count = len(low_variance_features)

    if removed_count > 0:
        log_message = f"remove_low_variance: Removed {removed_count} features with variance below {threshold}: {low_variance_features}"
        logging.info(log_message)
        with open(log_file_path, "a") as f:
            f.write(f"Timestamp: {pd.Timestamp.now()}\n")
            f.write(f"Function: remove_low_variance\n")
            f.write(f"Parameters: threshold={threshold}\n")
            f.write(f"Original feature count: {original_feature_count}\n")
            f.write(f"Removed feature count: {removed_count}\n")
            f.write(f"Removed features: {low_variance_features}\n\n")
    else:
        logging.info(
            f"remove_low_variance: No features removed with threshold {threshold}.")
        with open(log_file_path, "a") as f:
            f.write(f"Timestamp: {pd.Timestamp.now()}\n")
            f.write(f"Function: remove_low_variance\n")
            f.write(f"Parameters: threshold={threshold}\n")
            f.write(
                f"Action: No features met the low variance criteria. No features removed.\n\n")
    return df_filtered


def remove_highly_correlated(
        df: pd.DataFrame,
        threshold: float) -> pd.DataFrame:
    """
    Removes one feature from each pair of highly correlated features.
    (Existing docstring and code)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")
    if not isinstance(threshold, (int, float)):
        raise TypeError("Input 'threshold' must be a numeric value.")
    if not 0 <= threshold <= 1:
        raise ValueError("Input 'threshold' must be between 0 and 1.")

    numeric_df = df.select_dtypes(include=np.number)
    if numeric_df.shape[1] < 2:
        logging.info(
            "remove_highly_correlated: Not enough numeric features to calculate correlation.")
        with open(log_file_path, "a") as f:
            f.write(f"Timestamp: {pd.Timestamp.now()}\n")
            f.write(f"Function: remove_highly_correlated\n")
            f.write(f"Parameters: threshold={threshold}\n")
            f.write(
                f"Action: Not enough numeric features ({
                    numeric_df.shape[1]}) for correlation. No features removed.\n\n")
        return df

    corr_matrix = numeric_df.corr().abs()
    upper = corr_matrix.where(
        np.triu(
            np.ones(
                corr_matrix.shape),
            k=1).astype(bool))

    features_to_drop = set()
    for column in upper.columns:
        for index in upper.index:
            if upper.loc[index, column] > threshold:
                if index not in features_to_drop and column not in features_to_drop:
                    if index > column:
                        features_to_drop.add(index)
                    else:
                        features_to_drop.add(column)

    original_feature_count = len(df.columns)
    df_filtered = df.drop(columns=list(features_to_drop), errors='ignore')
    removed_count = len(features_to_drop)

    if removed_count > 0:
        log_message = f"remove_highly_correlated: Removed {removed_count} features (threshold > {threshold}): {
            sorted(
                list(features_to_drop))}"
        logging.info(log_message)
        with open(log_file_path, "a") as f:
            f.write(f"Timestamp: {pd.Timestamp.now()}\n")
            f.write(f"Function: remove_highly_correlated\n")
            f.write(f"Parameters: threshold={threshold}\n")
            f.write(f"Original feature count: {original_feature_count}\n")
            f.write(f"Removed feature count: {removed_count}\n")
            f.write(f"Removed features: {sorted(list(features_to_drop))}\n\n")
    else:
        logging.info(
            f"remove_highly_correlated: No features removed with threshold {threshold}.")
        with open(log_file_path, "a") as f:
            f.write(f"Timestamp: {pd.Timestamp.now()}\n")
            f.write(f"Function: remove_highly_correlated\n")
            f.write(f"Parameters: threshold={threshold}\n")
            f.write(
                f"Action: No pairs exceeded correlation threshold. No features removed.\n\n")
    return df_filtered


def select_by_model_importance(
        df: pd.DataFrame,
        target_series: pd.Series,
        task_type: str,
        threshold: float = 0.01) -> pd.DataFrame:
    """
    Selects features based on importance from a tree-based model.
    (Existing docstring and code)
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input 'df' must be a pandas DataFrame.")
    if not isinstance(target_series, pd.Series):
        raise TypeError("Input 'target_series' must be a pandas Series.")
    if df.shape[0] != target_series.shape[0]:  # Check after potential y NaN drop
        # This check might need to be reconsidered if y NaNs are dropped before this call
        # For now, assume df and target_series are aligned initially
        pass  # Re-evaluate if issues arise with pre-dropped NaNs in y
    if df.empty:  # If df became empty due to y NaN drops before this function
        logging.warning(
            "select_by_model_importance: Input DataFrame 'df' is empty. Returning empty DataFrame.")
        return pd.DataFrame()

    if task_type not in ['classification', 'regression']:
        raise ValueError("task_type must be 'classification' or 'regression'.")
    if not isinstance(threshold, (int, float)) or not 0 <= threshold <= 1:
        raise ValueError(
            "Input 'threshold' must be a numeric value between 0 and 1.")

    X = df.copy()
    y = target_series.copy()  # y is already aligned with X from the caller

    # This was moved to run_feature_selection, as y should be clean before this step
    # if y.isnull().any():
    #     nan_indices = y[y.isnull()].index
    #     y = y.drop(index=nan_indices)
    #     X = X.drop(index=nan_indices) # X must be aligned with y
    #     logging.info(f"select_by_model_importance: Dropped {len(nan_indices)} rows due to NaNs in target variable.")

    if X.empty or y.empty:
        logging.warning(
            "select_by_model_importance: DataFrame or target is empty. Returning original DataFrame.")
        # Log this specific scenario
        return df  # Return original df structure if X became empty

    numeric_features = X.select_dtypes(include=np.number).columns.tolist()
    non_numeric_features = X.select_dtypes(exclude=np.number).columns.tolist()

    if not numeric_features:
        logging.warning(
            "select_by_model_importance: No numeric features for model training. Keeping non-numeric features.")
        with open(log_file_path, "a") as f:
            f.write(f"Timestamp: {pd.Timestamp.now()}\n")
            f.write(f"Function: select_by_model_importance\n")
            f.write(
                f"Parameters: task_type='{task_type}', threshold={threshold}\n")
            f.write(
                f"Action: No numeric features for model training. No features selected/removed by model. Non-numeric features kept.\n\n")
        return X  # Return X as is, which contains numeric + non-numeric potentially

    X_numeric = X[numeric_features]
    imputer = SimpleImputer(strategy='median')
    X_imputed_np = imputer.fit_transform(X_numeric)
    X_imputed_df = pd.DataFrame(
        X_imputed_np,
        columns=numeric_features,
        index=X_numeric.index)

    if task_type == 'classification':
        model = RandomForestClassifier(
            random_state=42, n_estimators=100, n_jobs=-1)
    else:  # regression
        model = RandomForestRegressor(
            random_state=42, n_estimators=100, n_jobs=-1)

    model.fit(X_imputed_df, y)
    importances = pd.Series(
        model.feature_importances_,
        index=X_imputed_df.columns)
    features_to_drop_model = importances[importances <
                                         threshold].index.tolist()

    numeric_kept = [
        col for col in numeric_features if col not in features_to_drop_model]
    # Combine selected numeric with all original non-numeric
    final_kept_cols = numeric_kept + non_numeric_features

    # Select from original df to maintain datatypes and values
    df_filtered = df[final_kept_cols].copy()

    removed_count = len(features_to_drop_model)

    if removed_count > 0:
        log_message = (f"select_by_model_importance: Removed {removed_count} numeric features "
                       f"(importance < {threshold}): {features_to_drop_model}")
        logging.info(log_message)
        with open(log_file_path, "a") as f:
            f.write(f"Timestamp: {pd.Timestamp.now()}\n")
            f.write(f"Function: select_by_model_importance\n")
            f.write(
                f"Parameters: task_type='{task_type}', threshold={threshold}\n")
            f.write(
                f"Numeric feature count for model: {
                    len(numeric_features)}\n")
            f.write(f"Removed numeric feature count: {removed_count}\n")
            f.write(f"Removed numeric features: {features_to_drop_model}\n\n")
    else:
        logging.info(
            f"select_by_model_importance: No numeric features removed by model importance with threshold {threshold}.")
        with open(log_file_path, "a") as f:
            f.write(f"Timestamp: {pd.Timestamp.now()}\n")
            f.write(f"Function: select_by_model_importance\n")
            f.write(
                f"Parameters: task_type='{task_type}', threshold={threshold}\n")
            f.write(
                f"Action: No numeric features met removal criteria by model. Non-numeric features kept.\n\n")
    return df_filtered


def run_feature_selection(
        input_path: str,
        output_path: str,
        target_column: str,
        task_type: str,
        low_variance_threshold: float = 0.01,
        correlation_threshold: float = 0.9,
        importance_threshold: float = 0.01):
    """
    Runs a pipeline of feature selection methods and saves the result.

    Args:
        input_path (str): Path to the input CSV file.
        output_path (str): Path to save the CSV file with selected features.
        target_column (str): Name of the target variable column.
        task_type (str): 'classification' or 'regression'.
        low_variance_threshold (float): Threshold for remove_low_variance.
        correlation_threshold (float): Threshold for remove_highly_correlated.
        importance_threshold (float): Threshold for select_by_model_importance.
    """
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        logging.error(
            f"run_feature_selection: Input file not found at {input_path}")
        return
    except Exception as e:
        logging.error(
            f"run_feature_selection: Error reading CSV from {input_path}: {e}")
        return

    if target_column not in df.columns:
        logging.error(
            f"run_feature_selection: Target column '{target_column}' not found in the DataFrame.")
        return

    if df.empty:
        logging.warning(
            f"run_feature_selection: Input DataFrame from {input_path} is empty. No selection performed.")
        # Save empty or original df? For now, save original.
        try:
            df.to_csv(output_path, index=False)
            logging.info(
                f"run_feature_selection: Empty input DataFrame saved to {output_path}")
        except Exception as e:
            logging.error(
                f"run_feature_selection: Error saving empty DataFrame to {output_path}: {e}")
        return

    y = df[target_column].copy()
    X = df.drop(columns=[target_column]).copy()
    original_feature_count = X.shape[1]
    logging.info(
        f"run_feature_selection: Started with {original_feature_count} features.")
    summary_log = [f"Feature Selection Pipeline Summary for {input_path}:\n"]
    summary_log.append(f"Timestamp: {pd.Timestamp.now()}")
    summary_log.append(
        f"Parameters: LV_threshold={low_variance_threshold}, Corr_threshold={correlation_threshold}, Imp_threshold={importance_threshold}, Task={task_type}")
    summary_log.append(f"Initial number of features: {original_feature_count}")

    # Handle NaNs in target by removing corresponding rows in X and y BEFORE
    # any selection
    if y.isnull().any():
        nan_indices = y[y.isnull()].index
        y.drop(index=nan_indices, inplace=True)
        X.drop(index=nan_indices, inplace=True)
        X.reset_index(drop=True, inplace=True)  # Reset index for X
        y.reset_index(drop=True, inplace=True)  # Reset index for y
        logging.info(
            f"run_feature_selection: Dropped {
                len(nan_indices)} rows due to NaNs in target '{target_column}'. X and y aligned.")
        summary_log.append(
            f"Dropped {
                len(nan_indices)} rows due to NaNs in target '{target_column}'.")

    if X.empty or y.empty:
        logging.warning(
            f"run_feature_selection: DataFrame became empty after handling NaNs in target. Saving an empty feature set (only target if applicable).")
        # Decide what to save: empty df, or df with only target column if y is not empty.
        # For consistency, save X (which is empty) and y.
        final_df = pd.concat([X, y], axis=1)
        try:
            final_df.to_csv(output_path, index=False)
            logging.info(
                f"run_feature_selection: DataFrame (empty features) saved to {output_path}")
        except Exception as e:
            logging.error(
                f"run_feature_selection: Error saving DataFrame to {output_path}: {e}")
        summary_log.append(
            "Result: DataFrame empty after target NaN handling.")
        with open(log_file_path, "a") as f:
            f.write("\n" + "\n".join(summary_log) + "\n\n")
        return

    # 1. Remove Low Variance
    X_after_lv = remove_low_variance(X, threshold=low_variance_threshold)
    lv_removed_count = X.shape[1] - X_after_lv.shape[1]
    summary_log.append(
        f"After remove_low_variance: {
            X_after_lv.shape[1]} features remaining. ({lv_removed_count} removed)")
    logging.info(
        f"run_feature_selection: After low variance removal, {
            X_after_lv.shape[1]} features remaining.")

    # 2. Remove Highly Correlated
    X_after_corr = remove_highly_correlated(
        X_after_lv, threshold=correlation_threshold)
    corr_removed_count = X_after_lv.shape[1] - X_after_corr.shape[1]
    summary_log.append(
        f"After remove_highly_correlated: {
            X_after_corr.shape[1]} features remaining. ({corr_removed_count} removed)")
    logging.info(
        f"run_feature_selection: After high correlation removal, {
            X_after_corr.shape[1]} features remaining.")

    # 3. Select by Model Importance
    # Ensure y is aligned with X_after_corr if rows were dropped in previous steps (they are not, but good practice)
    # However, select_by_model_importance expects y to be aligned with the df it receives
    # This alignment is critical and was handled by removing NaN target rows
    # from both X and y earlier.
    X_after_importance = select_by_model_importance(
        X_after_corr, y, task_type, threshold=importance_threshold)
    imp_removed_count = X_after_corr.shape[1] - X_after_importance.shape[1]
    summary_log.append(
        f"After select_by_model_importance: {
            X_after_importance.shape[1]} features remaining. ({imp_removed_count} removed)")
    logging.info(
        f"run_feature_selection: After model importance selection, {
            X_after_importance.shape[1]} features remaining.")

    # Combine selected features with the target column
    # Ensure y's index is aligned with X_after_importance if X_after_importance is a subset of original X rows
    # Since y was already aligned with the full X (after NaN removal), and feature selection only drops columns,
    # their indices should still align.
    final_df = pd.concat([X_after_importance, y], axis=1)

    try:
        final_df.to_csv(output_path, index=False)
        logging.info(
            f"run_feature_selection: Successfully saved DataFrame with {
                final_df.shape[1] -
                1} selected features and target to {output_path}")
        summary_log.append(
            f"Final selected feature count: {
                X_after_importance.shape[1]}")
        summary_log.append(f"Output saved to: {output_path}")
    except Exception as e:
        logging.error(
            f"run_feature_selection: Error saving final DataFrame to {output_path}: {e}")
        summary_log.append(f"Error saving output to {output_path}: {e}")

    with open(log_file_path, "a") as f:
        f.write("\n" + "\n".join(summary_log) + "\n\n")


if __name__ == '__main__':
    # --- Setup for Example Usage ---
    if not os.path.exists("output"):
        os.makedirs("output")

    # Clear previous log file for fresh test output (optional)
    if os.path.exists(log_file_path):
        with open(log_file_path, "w") as f:  # "w" to overwrite for main test
            f.write("Feature Selection Log\n" + "=" * 30 + "\n\n")

    logging.info("--- Starting Main Pipeline Test for feature_selector.py ---")

    # Create a sample CSV for testing run_feature_selection
    sample_data = {
        'ID': range(100),
        'LowVar_Col': [1] * 100,  # Zero variance
        'MedVar_Col': np.random.rand(100),
        'HighVar_Col': np.random.rand(100) * 100,
        'Corr_Col1': np.linspace(0, 1, 100),
        # Highly correlated with Corr_Col1
        'Corr_Col2': np.linspace(0, 1, 100) + np.random.rand(100) * 0.05,
        # Negatively correlated
        'Corr_Col3': np.linspace(1, 0, 100) + np.random.rand(100) * 0.1,
        'Imp_Feat1': np.random.rand(100),
        'Imp_Feat2_Weak': np.random.rand(100) * 0.1,  # Weak importance
        # Very weak importance
        'Imp_Feat3_VeryWeak': np.random.rand(100) * 0.01,
        'Cat_Feat': np.random.choice(['A', 'B', 'C'], size=100),
        'Target_Reg': np.zeros(100)  # Placeholder, will be populated
    }
    sample_df = pd.DataFrame(sample_data)
    # Create a regression target related to some features
    sample_df['Target_Reg'] = (2 * sample_df['HighVar_Col'] +
                               3 * sample_df['Corr_Col1'] +
                               0.5 * sample_df['Imp_Feat1'] +
                               np.random.normal(0, 5, 100))
    # Create a classification target
    sample_df['Target_Class'] = (
        sample_df['Target_Reg'] > sample_df['Target_Reg'].median()).astype(int)

    # Introduce some NaNs
    sample_df.loc[0:5, 'MedVar_Col'] = np.nan
    sample_df.loc[10:15, 'Target_Reg'] = np.nan  # NaNs in regression target
    # NaNs in classification target (though less common to impute target for
    # classif)
    sample_df.loc[20:25, 'Target_Class'] = np.nan

    sample_input_path = os.path.join(output_dir, "sample_input.csv")
    sample_df.to_csv(sample_input_path, index=False)
    logging.info(
        f"Created sample input CSV: {sample_input_path} with {
            sample_df.shape[0]} rows and {
            sample_df.shape[1]} columns.")

    # --- Test run_feature_selection for Regression ---
    reg_output_path = os.path.join(output_dir, "sample_output_regression.csv")
    logging.info(f"\n--- Running Feature Selection for REGRESSION ---")
    print(f"\n--- Running Feature Selection for REGRESSION (Target: Target_Reg) ---")
    print(f"Input: {sample_input_path}, Output: {reg_output_path}")
    run_feature_selection(
        input_path=sample_input_path,
        output_path=reg_output_path,
        target_column='Target_Reg',
        task_type='regression',
        low_variance_threshold=0.01,
        correlation_threshold=0.85,
        importance_threshold=0.05
    )
    if os.path.exists(reg_output_path):
        df_out_reg = pd.read_csv(reg_output_path)
        print(
            f"Regression output saved to {reg_output_path}. Shape: {
                df_out_reg.shape}")
        print(f"Selected columns: {df_out_reg.columns.tolist()}")

    # --- Test run_feature_selection for Classification ---
    clf_output_path = os.path.join(
        output_dir, "sample_output_classification.csv")
    logging.info(f"\n--- Running Feature Selection for CLASSIFICATION ---")
    print(f"\n--- Running Feature Selection for CLASSIFICATION (Target: Target_Class) ---")
    print(f"Input: {sample_input_path}, Output: {clf_output_path}")
    run_feature_selection(
        input_path=sample_input_path,
        output_path=clf_output_path,
        target_column='Target_Class',
        task_type='classification',
        low_variance_threshold=0.01,
        correlation_threshold=0.85,
        importance_threshold=0.05
    )
    if os.path.exists(clf_output_path):
        df_out_clf = pd.read_csv(clf_output_path)
        print(
            f"Classification output saved to {clf_output_path}. Shape: {
                df_out_clf.shape}")
        print(f"Selected columns: {df_out_clf.columns.tolist()}")

    logging.info("--- Finished Main Pipeline Test for feature_selector.py ---")
    print(
        f"\nCheck '{log_file_path}' for detailed logs from all function calls.")
