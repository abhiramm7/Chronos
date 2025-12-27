import pandas as pd
import numpy as np
import pytest
from core import shingle_timeseries, generate_target_timeseries, check_data_frequency


def generate_test_data(start: str, end: str, freq: str) -> pd.DataFrame:
    index = pd.date_range(start=pd.Timestamp(start), end=pd.Timestamp(end), freq=freq)
    data = pd.DataFrame(
        {"A": np.random.rand(len(index)), "B": np.random.rand(len(index))}, index=index
    )
    return data


def test_shingle_timeseries():
    data = generate_test_data(start="2025-01-01", end="2025-01-31", freq="6h")
    shingled_data = shingle_timeseries(data, window_size=pd.Timedelta("12h"))
    # check column names
    expected_columns = ["A_t-0", "A_t-1", "B_t-0", "B_t-1"]
    assert (
        list(shingled_data.columns) == expected_columns
    ), "Column names do not match expected shingled format."
    # check number of rows
    expected_rows = data.shape[0] - 2 + 1  # window size
    assert (
        shingled_data.shape[0] == expected_rows
    ), "Number of rows in shingled data is incorrect."
    # check values
    for i in shingled_data.index:
        for cols in ["A", "B"]:
            assert shingled_data.loc[i, f"{cols}_t-0"] == data.loc[i, cols]
            assert (
                shingled_data.loc[i, f"{cols}_t-1"]
                == data.loc[i - pd.Timedelta("6h"), cols]
            )
    print("All tests passed!")


def test_check_data_frequency():
    # Test with uniformly sampled data
    data = generate_test_data(start="2025-01-01", end="2025-01-10", freq="1h")
    freq = check_data_frequency(data)
    assert freq == pd.Timedelta("1h"), "Frequency should be 1 hour"

    # Test with different frequency
    data = generate_test_data(start="2025-01-01", end="2025-01-10", freq="15min")
    freq = check_data_frequency(data)
    assert freq == pd.Timedelta("15min"), "Frequency should be 15 minutes"


def test_check_data_frequency_non_uniform():
    # Test with non-uniformly sampled data
    index = pd.DatetimeIndex(
        ["2025-01-01 00:00:00", "2025-01-01 01:00:00", "2025-01-01 03:00:00"]
    )
    data = pd.DataFrame({"A": [1, 2, 3]}, index=index)

    with pytest.raises(ValueError, match="Data must be uniformly sampled"):
        check_data_frequency(data)


def test_generate_target_timeseries_dataframe():
    # Test with DataFrame input
    data = generate_test_data(start="2025-01-01", end="2025-01-10", freq="1h")
    single_col_data = data[["A"]]

    window_size = 3
    forecast_window = 2

    target_data, input_index = generate_target_timeseries(
        single_col_data, window_size=window_size, forcast_window=forecast_window
    )

    # Check that target_data starts at the correct position
    expected_start_index = single_col_data.index[window_size + forecast_window]
    assert (
        target_data.index[0] == expected_start_index
    ), "Target data should start at correct index"

    # Check input_index
    expected_input_index = single_col_data.index[window_size]
    assert (
        input_index[0] == expected_input_index
    ), "Input index should be at window_size position"


def test_generate_target_timeseries_series():
    # Test with Series input
    data = generate_test_data(start="2025-01-01", end="2025-01-10", freq="1h")
    series_data = data["A"]

    window_size = 4
    forecast_window = 1

    target_data, input_index = generate_target_timeseries(
        series_data, window_size=window_size, forcast_window=forecast_window
    )

    # Check that it's converted to DataFrame
    assert isinstance(target_data, pd.DataFrame), "Output should be a DataFrame"

    # Check dimensions
    assert target_data.shape[1] == 1, "Should have single column"


def test_generate_target_timeseries_timedelta():
    # Test with Timedelta window sizes
    data = generate_test_data(start="2025-01-01", end="2025-01-10", freq="6h")
    single_col_data = data[["A"]]

    window_size = pd.Timedelta("12h")
    forecast_window = pd.Timedelta("6h")

    target_data, input_index = generate_target_timeseries(
        single_col_data, window_size=window_size, forcast_window=forecast_window
    )

    # Check that conversion from Timedelta works correctly
    assert len(target_data) > 0, "Should have target data"
    assert len(input_index) > 0, "Should have input index"


def test_generate_target_timeseries_multi_column_error():
    # Test that multi-column DataFrame raises error
    data = generate_test_data(start="2025-01-01", end="2025-01-10", freq="1h")

    with pytest.raises(ValueError, match="Data must be a single column"):
        generate_target_timeseries(data, window_size=3, forcast_window=2)


if __name__ == "__main__":
    test_shingle_timeseries()
    test_check_data_frequency()
    test_check_data_frequency_non_uniform()
    test_generate_target_timeseries_dataframe()
    test_generate_target_timeseries_series()
    test_generate_target_timeseries_timedelta()
    test_generate_target_timeseries_multi_column_error()
    print("All tests passed!")
