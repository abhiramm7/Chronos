import typing
import pandas as pd


def normalize(data: typing.Union[pd.Series, pd.DataFrame], normalization_method: str) -> tuple[typing.Union[pd.Series, pd.DataFrame], dict]:
    if normalization_method == 'min_max':
        normalized_data, normalization_parameters = min_max_normalization(data)
    elif normalization_method == 'mean_std':
        normalized_data, normalization_parameters = mean_std_normalization(data)
    else:
        raise ValueError(f"Normalization method '{normalization_method}' is not supported.")
    return normalized_data, normalization_parameters


def min_max_normalization(data: typing.Union[pd.DataFrame]) -> tuple[typing.Union[pd.DataFrame], dict]:
    normalization_parameters = {}
    normalized_data = pd.DataFrame()
    for column in data.columns:
        normalization_parameters[column] = {}
        normalization_parameters[column]['min'] = data[column].min()
        normalization_parameters[column]['max'] = data[column].max()
        normalization_parameters[column]['mean'] = data.mean()
        normalized_data_i = (data.iloc[:, column] - normalization_parameters['mean']) / (normalization_parameters['max'] - normalization_parameters['min'])
        normalized_data = pd.concat([normalized_data, normalized_data_i], axis=1)
    return normalized_data, normalization_parameters


def mean_std_normalization(data: typing.Union[pd.DataFrame]) -> tuple[typing.Union[pd.DataFrame], dict]:
    normalization_parameters = {}
    normalized_data = pd.DataFrame()
    for column in data.columns:
        normalization_parameters[column] = {}
        normalization_parameters[column]['mean'] = data[column].mean()
        normalization_parameters[column]['std'] = data[column].std()
        normalized_data_i = (data.iloc[:, column] - normalization_parameters['mean']) / normalization_parameters['std']
        normalized_data = pd.concat([normalized_data, normalized_data_i], axis=1)
    return normalized_data, normalization_parameters
