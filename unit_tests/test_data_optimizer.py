import pandas as pd
import pytest
import sys
import os
from pandas.api.types import is_datetime64_any_dtype

from unittest.mock import patch, MagicMock
from autoeda.data_optimizer import optimize_csv



sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from autoeda.data_optimizer import optimize_dtypes
from autoeda.data_optimizer import optimize_csv


def test_categorical_conversion():

    df = pd.DataFrame({
        "small_category": [f'item_{i % 49}' for i in range(100)],  
        "large_category": [f'item_{i % 52}' for i in range(100)],  
        'numeric': list(range(100))  
    })
    optimized_df = optimize_dtypes(df)
    assert optimized_df['small_category'].dtype.name == 'category', "small_category should be converted to category"
    assert optimized_df['large_category'].dtype.name != 'category', "large_category should not be converted"
    assert optimized_df['numeric'].dtype.kind in ['i', 'f'], "numeric column should remain numeric"


def test_numerical_conversion():
    int_data=[3,45,32,2233,739281802301]
    float_data=[4.7,8.8,3,72.89213,9823.09329]
    date_data = ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']
    bad_date_data= ['not-a-date', '2023-02-30', '13-2023-01', 'someday', '']
    df=pd.DataFrame({
         'float_col': float_data,
        'int_col': int_data,
        'created_date': date_data,
        'bad_timestamp': bad_date_data
    })

    df_optimized=optimize_dtypes(df)
    assert df_optimized['float_col'].dtype.name in ['float32', 'float16']
    assert df_optimized['int_col'].dtype.name in ['int32','int16']
    assert is_datetime64_any_dtype(df_optimized['created_date']), "created_date should be datetime"
    assert not pd.api.types.is_datetime64_any_dtype(df_optimized['bad_timestamp']), "bad_timestamp should not be converted"

@patch("autoeda.data_optimizer.optimize_dtypes")
@patch("pandas.DataFrame.to_csv")
@patch("pandas.read_csv")
def test_optimize_csv(mock_read_csv, mock_to_csv, mock_optimize_dtypes):

    input_path = "dummy_input.csv"
    output_path = "dummy_output.csv"

    
    dummy_df = pd.DataFrame({
        'col1': ['A', 'B', 'A'],
        'col2': [1.0, 2.0, 3.0],
        'date_col': ['2023-01-01', '2023-01-02', '2023-01-03']
    })

    
    mock_read_csv.return_value = dummy_df
    mock_optimize_dtypes.return_value = dummy_df  

    
    optimize_csv(input_path, output_path)

    
    mock_read_csv.assert_called_once_with(input_path)
    mock_optimize_dtypes.assert_called_once_with(dummy_df)
    mock_to_csv.assert_called_once_with(output_path, index=False)






