import pandas as pd


class DB:

    def __init__(self, pd_dataframes_list, output_dir):
        self._output_dir = output_dir
        self._output_file = self._output_dir + '/db.csv'
        self.pd_dataframes = pd_dataframes_list
        self.db_columns_name = []
        self.db = None

        print(f'out_file={self._output_file}')

        self.compute_abs_timestart()
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

        for d in self.pd_dataframes:
            time_diff = d['start_utc_seconds'] - min_time
            time_key = 'time_' + d['imu_name']
            d['imu_df'][time_key] = d['imu_df'][time_key] + time_diff

    def save_as_csv(self):
        self.db.to_csv(self._output_dir + '/db.csv')
