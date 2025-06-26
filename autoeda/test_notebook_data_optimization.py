import unittest
import pandas as pd
import numpy as np
from notebook_data_optimization import optimize_data


class TestDataOptimization(unittest.TestCase):

    def test_optimize_data(self):
        # Create a sample DataFrame
        df = pd.DataFrame({
            'id': range(1, 101),
            'category_low_cardinality': ['A', 'B'] * 50,
            'category_high_cardinality': [f'item_{i}' for i in range(100)],
            'float_values': np.random.rand(100) * 100,
            'int_values': np.random.randint(0, 1000, 100),
            'date_strings': pd.date_range('2024-01-01', periods=100, freq='D').astype(str)
        })
        df['float_values_copy'] = df['float_values'].copy()
        df['int_values_copy'] = df['int_values'].copy()

        # Apply optimization
        # Use a copy to avoid modifying original df for assertions
        df_optimized = optimize_data(df.copy())

        # Assertions
        # Check category conversion
        self.assertEqual(
            df_optimized['category_low_cardinality'].dtype.name,
            'category')
        self.assertEqual(
            df_optimized['category_high_cardinality'].dtype.name,
            'object')  # Should remain object

        # Check numeric downcasting
        self.assertTrue(str(df_optimized['float_values'].dtype).startswith(
            'float32'))  # or float16 depending on data
        # e.g. int8, int16, int32
        self.assertTrue(
            str(df_optimized['int_values'].dtype).startswith('int'))

        # Check date conversion
        self.assertTrue(
            pd.api.types.is_datetime64_any_dtype(
                df_optimized['date_strings']))

        # Check that values are not altered significantly for numeric types (simple check)
        # Compare values of float_values and float_values_copy
        np.testing.assert_allclose(
            df_optimized['float_values'].to_numpy(),
            df_optimized['float_values_copy'].to_numpy(),
            rtol=1e-5)
        self.assertEqual(df_optimized['float_values'].dtype, np.float32)
        self.assertEqual(df_optimized['float_values_copy'].dtype, np.float32)

        # Ensure original int values are preserved by comparing with original
        # df values cast to the new dtype
        pd.testing.assert_series_equal(
            df_optimized['int_values'],
            df['int_values_copy'].astype(
                df_optimized['int_values'].dtype),
            check_dtype=True,
            check_names=False)

    def test_optimize_data_empty_df(self):
        df = pd.DataFrame()
        df_optimized = optimize_data(df.copy())
        self.assertTrue(df_optimized.empty)

    def test_optimize_data_all_numeric(self):
        df = pd.DataFrame({
            'A': np.array([1, 2, 3], dtype='int64'),
            'B': np.array([1.0, 2.0, 3.0], dtype='float64')
        })
        df_optimized = optimize_data(df.copy())
        self.assertTrue(str(df_optimized['A'].dtype).startswith('int'))
        self.assertTrue(str(df_optimized['B'].dtype).startswith('float32'))

    def test_optimize_data_with_non_convertible_date(self):
        df = pd.DataFrame({
            'date_col_valid': ['2023-01-01', '2023-01-02'],
            'date_col_invalid': ['2023-01-01', 'not_a_date']
        })
        df_optimized = optimize_data(df.copy())
        self.assertTrue(
            pd.api.types.is_datetime64_any_dtype(
                df_optimized['date_col_valid']))
        self.assertEqual(df_optimized['date_col_invalid'].dtype.name, 'object')


if __name__ == '__main__':
    unittest.main()
