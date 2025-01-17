import numpy as np


def unwrap_columns(dataframe, column_names):
    for column in column_names:
        dataframe[column] = np.unwrap(dataframe[column].to_numpy())
        dataframe[column] = np.rad2deg(dataframe[column].to_numpy())

    return dataframe

def align_samples(dataframe):

    for column in dataframe.columns:
        if column.startwith('time'):
            pass
