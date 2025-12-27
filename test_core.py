import pandas as pd
import numpy as np
from core import shingle_timeseries


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


if __name__ == "__main__":
    test_shingle_timeseries()
