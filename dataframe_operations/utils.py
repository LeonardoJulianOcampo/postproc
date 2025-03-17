import numpy as np
import pandas as pd


def unwrap_columns(dataframe, column_names, ang_unit='degree'):
    if ang_unit == 'degree':
        for column in column_names:
            dataframe[column] = np.deg2rad(dataframe[column].to_numpy())
            dataframe[column] = np.unwrap(dataframe[column].to_numpy())
            dataframe[column] = np.rad2deg(dataframe[column].to_numpy())

    if ang_unit == 'radians':
        for column in column_names:
            dataframe[column] = np.unwrap(dataframe[column].to_numpy())
            dataframe[column] = np.rad2deg(dataframe[column].to_numpy())

    return dataframe


def align_samples(dataframe):

    for column in dataframe.columns:
        if column.startwith('time'):
            pass


def fix_discontinuities(pandas_df, threshold):
    pandas_df = pandas_df.drop(columns=['Latitude_xsens', 'Longitude_xsens'])

    diff_columns = {column + '_diff': pandas_df[column].diff()
                    for column in pandas_df.columns if not column.startswith('time')}

    work_df = pd.concat([pandas_df, pd.DataFrame(diff_columns)], axis=1)

    for column in work_df.columns:
        if column.endswith('_diff'):
            base_col = column.rsplit('_', 1)[0]
            mask = (work_df[column] > 0) & (work_df[column] > abs(threshold))
            work_df.loc[mask, base_col] -= work_df.loc[mask, column]

    work_df = work_df.drop(columns=[col for col in work_df.columns if col.endswith('_diff')])

    return work_df
