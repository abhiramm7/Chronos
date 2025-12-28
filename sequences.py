import typing
import pandas as pd


# shingling timeseries for feature engineering
def shingle_timeseries(
    data: pd.DataFrame, window_size: typing.Union[pd.Timedelta, int]
) -> pd.DataFrame:

    # check frequency to ensure uniform sampling
    freq = check_data_frequency(data)

    # TODO: handle window size better
    if isinstance(window_size, pd.Timedelta):
        window_size = window_size / freq
        window_size = int(window_size)

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


def generate_target_timeseries(
    data: typing.Union[pd.DataFrame, pd.Series],
    window_size: typing.Union[pd.Timedelta, int],
    forcast_window: typing.Union[pd.Timedelta, int],
) -> tuple[pd.DataFrame, pd.Index]:

    # check frequency to ensure uniform sampling
    freq = check_data_frequency(data)

    if isinstance(window_size, pd.Timedelta):
        window_size = window_size / freq
        window_size = int(window_size)

    if isinstance(forcast_window, pd.Timedelta):
        forcast_window = forcast_window / freq
        forcast_window = int(forcast_window)

    # check to ensure single column data
    if isinstance(data, pd.DataFrame):
        if data.shape[1] != 1:
            raise ValueError("Data must be a single column DataFrame or Series.")
    if isinstance(data, pd.Series):
        data = data.to_frame()

    # drop the initial rows that cannot be used for shingling
    target_data = data.iloc[window_size + forcast_window :, :]
    input_index = data.iloc[window_size:, :].index

    return target_data, input_index


def check_data_frequency(data: pd.DataFrame) -> pd.Timedelta:
    freq = data.index.diff().unique().dropna()
    if len(freq) != 1:
        raise ValueError("Data must be uniformly sampled.")
    return freq[0]
