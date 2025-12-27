import typing
import numpy as np
import pandas as pd


# shingling timeseries for feature engineering
def shingle_timeseries(
    data: pd.DataFrame, window_size: typing.Union[pd.Timedelta, int]
) -> pd.DataFrame:
    # determine if data is uniformly sampled
    freq = data.index.diff().unique().dropna()
    if len(freq) != 1:
        raise ValueError("Data must be uniformly sampled to apply shingling.")

    # TODO: handle window size better
    if isinstance(window_size, pd.Timedelta):
        window_size = window_size / freq
        window_size = int(window_size[0])

    shingled_data = pd.DataFrame()
    for column in data.columns:
        shingled_data_i = []
        index_i = []
        for i in range(window_size, data.shape[0] + 1):
            shingled_data_i.append(data[column].iloc[i - window_size : i].values)
            index_i.append(data.index[i - 1])
        shingled_columns = [
            f"{column}_t-{window_size-j-1}" for j in range(0, window_size)
        ]
        data_i = pd.DataFrame(shingled_data_i, columns=shingled_columns, index=index_i)
        shingled_data = pd.concat([shingled_data, data_i.iloc[:, ::-1]], axis=1)
    return shingled_data
