import pandas as pd
from sklearn.decomposition import PCA
import os


def apply_pca(df, n_components=None):
    """
    Applies Principal Component Analysis (PCA) to the given DataFrame.

    Args:   df: Input DataFrame with numeric features.
            n_components: Number of principal components to keep.
                If None, all components are retained.

    Returns:
        tuple[pd.dataFrame, dict[str, Any]]:
            - Transformed dataFrame with principal components
            - Metadata containing explained variance and column mappings
    """

    numeric_df = df.select_dtypes(include=["float64", "int64"])
    pca = PCA(n_components=n_components)
    components = pca.fit_transform(numeric_df)

    col_names = [f"PC{i + 1}" for i in range(components.shape[1])]
    pca_df = pd.DataFrame(components, columns=col_names, index=df.index)

    metadata = {
        "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "n_components": components.shape[1],
        "original_columns": numeric_df.columns.tolist(),
        "pca_columns": col_names
    }

    return pca_df, metadata


if __name__ == "__main__":
    INPUT_FILE = "./backend/output/autoEDA_outliers_removed.csv"
    OUTPUT_FILE = "./backend/output/pca_transformed.csv"
    OUTPUT_LOG_FILE = "./backend/output/pca_transformed_log.csv"

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    df = pd.read_csv(INPUT_FILE)
    transformed_df, meta = apply_pca(df)

    transformed_df.to_csv(OUTPUT_FILE, index=False)
    pd.DataFrame([meta]).to_csv(OUTPUT_LOG_FILE, index=False)

    print("PCA transformation completed.")
    print("Explained Variance Ratio:", meta["explained_variance_ratio"])
    print("Output saved to:", OUTPUT_FILE)
