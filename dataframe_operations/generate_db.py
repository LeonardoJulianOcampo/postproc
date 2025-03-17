import pandas as pd
import numpy as np
from functools import reduce

class DB:

    def __init__(self, pd_dataframes_list, output_dir):
        self._output_dir = output_dir
        self._output_file = self._output_dir + '/db.csv'
        self.pd_dataframes = pd_dataframes_list
        self.db_columns_name = []
        self.db = None

        print(f'out_file={self._output_file}')

        #self.compute_abs_timestart()
        #self.add_start_time()
        self.set_magn_to_zero()
        self.generate_db()

    def generate_db(self):
        df_list = []
        for df_dict in self.pd_dataframes:
            df_list.append(df_dict['imu_df'])

        self.db = pd.concat(df_list, axis=1, join='outer')

    def get_db(self):
        return self.db

    def set_db(self, db):
        self.db = db.copy()

    def get_column_names(self):
        return self.db.columns

    def compute_abs_timestart(self):
        """
        Determine the start of each dataset relative to the
        beginning of the measurement day at 00:00 hours
        (UTC time), expressed in seconds. Then, calculate the
        time differences and insert them into the 'time'
        column of each dataset.
        """
        min_time = min(d['start_utc_seconds'] for d in self.pd_dataframes)

        for d in self.pd_dataframes:
            time_diff = d['start_utc_seconds'] - min_time
            time_key = 'time_' + d['imu_name']
            if time_diff > 0:
                d['imu_df'][time_key] = d['imu_df'][time_key] + time_diff
            if time_diff < 0:
                d['imu_df'][time_key] = d['imu_df'][time_key] - time_diff

    def update_db(self, column_name, column_values):
        self.db[column_name] = column_values

    def set_magn_to_zero(self):
        for d in self.pd_dataframes:
            for column in d['imu_df'].columns:
                if not column.startswith('time_'):
                    offset = d['imu_df'][column].iloc[0]
                    d['imu_df'][column] = d['imu_df'][column] - offset

    def add_start_time(self):
        for d in self.pd_dataframes:
            time_start = d['start_utc_seconds']
            time_key = 'time_' + d['imu_name']
            d['imu_df'][time_key] = d['imu_df'][time_key] + time_start

    def save_as_csv(self):
        self.db.to_csv(self._output_dir + 'db.csv')

#    def save_range(self, data_dict):
#        min_time = data_dict['time_range'][0]
#        max_time = data_dict['time_range'][1]
#        columns_to_drop = []
#
#        # db_cropped = self.db[(self.db['time_imar'] >= min_time) &
#        #                     (self.db['time_imar'] <= max_time)]
#
#        idx_inf = self.db[self.db['time_imar'] == min_time].index[0]
#        idx_sup = self.db[self.db['time_imar'] == max_time].index[0]
#
#        db_cropped = self.db.loc[idx_inf:idx_sup]
#
#        for column_name in db_cropped.columns:
#            if not column_name.startswith(('time', 'roll', 'yaw', 'pitch')):
#                columns_to_drop.append(column_name)
#
#        db_cropped = db_cropped.drop(columns_to_drop, axis=1)
#        print(f'guardando en {self._output_dir}{data_dict["name"]}.csv')
#        db_cropped.to_csv(self._output_dir + data_dict['name'] + '.csv')

    def save_range(self, data_dict):
        min_time = data_dict['time_range'][0]
        max_time = data_dict['time_range'][1]
        columns_to_drop = []
        imu_list = []
        imu_dbs = []

        db = self.db.copy()

        for column_name in db.columns:
            if not column_name.startswith(('time', 'roll', 'yaw', 'pitch')):
                columns_to_drop.append(column_name)

        db_cropped = self.db.drop(columns_to_drop, axis=1)

        for column_name in db_cropped.columns:
            imu_name = column_name.split('_')[1]
            if imu_name not in imu_list:
                imu_list.append(imu_name)

        print(f'lista de imus detectadas: {imu_list}')
        print(f'db_cropped.columns: {db_cropped.columns}')

        for imu in imu_list:
            new_df = pd.DataFrame()
            for column_name in db_cropped.columns:
                if column_name.endswith(imu):
                    new_df[column_name] = db_cropped[column_name]
                    if column_name.startswith('time_'):
                        new_df.rename(inplace=True, columns={"time_" + imu: 'time'})
                        print(f'renombrando columna time_{imu} por time')
                        new_df = new_df.dropna(how="all")
            imu_dbs.append(new_df)
            print('df agregado a imu_dbs')

        imu_dbs[0] = pd.merge_ordered(imu_dbs[0], imu_dbs[1], on='time', how='outer')
        imu_dbs[2].to_csv(self._output_dir + 'tel_data' + '.csv')
        imu_dbs[0] = pd.merge_ordered(imu_dbs[0], imu_dbs[2], on='time', how='outer')

        merged_df = imu_dbs[0].copy()

        for column in merged_df.columns:
            if not column.startswith("time"):
                merged_df[column] = merged_df[column].interpolate(method='linear')
                print(f'column: {column} interpolated')

        df_cropped = merged_df[(merged_df['time'] >= min_time) &
                               (merged_df['time'] <= max_time)]

        df_cropped.to_csv(self._output_dir + data_dict['name'] + '.csv')
        return df_cropped
