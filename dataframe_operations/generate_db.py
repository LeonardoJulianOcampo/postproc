import pandas as pd


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
        print('**************************')
        print('*in compute_abs_timestart*')

        for d in self.pd_dataframes:
            time_diff = d['start_utc_seconds'] - min_time
            print(f'time_diff:{time_diff}')
            time_key = 'time_' + d['imu_name']
            if time_diff > 0:
                d['imu_df'][time_key] = d['imu_df'][time_key] + time_diff
            if time_diff < 0:
                d['imu_df'][time_key] = d['imu_df'][time_key] - time_diff

            print(f"d['imu_df'][time_key]={d['imu_df'][time_key]}")

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

    def save_range(self, data_dict):
        min_time = data_dict['time_range'][0]
        max_time = data_dict['time_range'][1]
        columns_to_drop = []

        db_cropped = self.db[(self.db['time_imar'] >= min_time) &
                             (self.db['time_imar'] <= max_time)]

        for column_name in db_cropped.columns:
            if not column_name.startswith(('time', 'roll', 'yaw', 'pitch')):
                columns_to_drop.append(column_name)

        db_cropped = db_cropped.drop(columns_to_drop, axis=1)
        print(f'guardando en {self._output_dir} + {data_dict["name"]} + .csv')
        print(f'columns to drop is: {columns_to_drop}')
        db_cropped.to_csv(self._output_dir + data_dict['name'] + '.csv')
