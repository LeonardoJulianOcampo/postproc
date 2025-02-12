from .BaseFileReader import FileReader
import sys
sys.path.append("..")
from dataframe_operations import utils
import pandas as pd
import csv
import datetime
import os


class IMARFileReader(FileReader):

    def __init__(self, input_file, output_dir):
        super().__init__(input_file, output_dir)
        self.imar_df = None
        self.first_timestamp = None
        self.measure_date = None
        self._data = []
        self._time_utc_seconds = 0.0

    def read_file(self):
        """
        Lee el archivo fuente generado por la IMU
        """
        with open(self._input_file, 'r', encoding='latin-1') as file:
            firstline = True
            for line in file:
                if line.startswith("# Started:"):
                    self._dateline = line
                if line.startswith('#'):
                    if line.startswith('# Column'):
                        self._column_names.append(line.split(':')[1].strip().split(',')[1].strip())
                else:
                    if firstline:
                        self._first_timestamp_line = line
                        self._data.append(line.strip().split())
                        firstline = False
                    else:
                        self._data.append(line.strip().split())

            self.imar_df = pd.DataFrame(self._data, columns=self._column_names)
            self.imar_df = self.imar_df.astype(float)

            # proceso la linea de fecha para determinar la hora de inicio.abs
            date = self._dateline.split(' ')[2].split('/')
            first_timestamp = self._first_timestamp_line.split(' ')[1].replace('+', '')
            df_date = pd.DataFrame({'day': [date[1]], 'month': [date[0]], 'year': [date[2]], 'second_of_week': first_timestamp})

            day = int(df_date["day"])
            month = int(df_date["month"])
            year = int(df_date["year"])

            if "second_of_week" in df_date.columns:
                second_of_week = round(float(df_date["second_of_week"]), 2)
                days_week = datetime.date(year, month, day).weekday()
                print(f'days_week = {days_week}')
                self.compute_start_time(second_of_week, is_week=True, day_week=days_week)
            elif "second_of_day" in df_date.columns:
                second_of_day = round(float(df_date["second_of_day"]), 2)
                self.compute_start_time(second_of_day)
            else:
                raise ValueError("No se encontraron valores necesarios para el cálculo")

#            self.imar_df['time'] = self.imar_df['TINTRPL']
#            self.imar_df['time'] = self.imar_df['time'] - self.imar_df['TINTRPL'].iloc[0]
#            self.imar_df = self.imar_df.drop(['TINTRPL'], axis=1)

    def format_file(self):
        new_names = {
            'TINTRPL': 'time',
        }
        self.imar_df = self.imar_df.rename(columns=new_names)
        self.imar_df.columns = [col + '_imar' for col in self.imar_df.columns]
        self.imar_df['time_imar'] = self.imar_df['time_imar'] - self.imar_df['time_imar'].iloc[0]
        print(f'imar:self.utc_seconds={self._time_utc_seconds}')
        columns_to_unwrap = ['yaw_imar', 'pitch_imar', 'roll_imar']
        self.imar_df = utils.unwrap_columns(self.imar_df,
                                            columns_to_unwrap)
        print(f'imar_df={self.imar_df}')

    def save_file(self, temporal=False):
        """
        Guarda el archivo leído pero con un formato dataframe de pandas
        """
        print(f'guardando en {self._output_dir}')

        self.imar_df.to_csv(self._output_dir + '/imar.csv')

#        with open(self._output_dir + '/imar.csv', 'w', newline='') as file:
#            writer = csv.writer(file)
#            writer.writerow(self._column_names)
#            writer.writerows(self._data)

    def compute_start_time(self, seconds, is_week=False, day_week=1):
        print(f"in compute_start_time: is_week: {is_week}")
        if is_week:
            days_second = 86400
            seconds = seconds - (days_second * day_week)

        hours = seconds // 3600
        seconds_r = seconds % 3600
        minutes = seconds_r // 60
        seconds_f = seconds_r % 60

        seconds_utc = (hours % 24) * 3600 + minutes * 60 + seconds_f
        self._time_utc_seconds = seconds_utc

    def get_df(self):
        return {'imu_name': 'imar',
                'imu_df': self.imar_df,
                'start_utc_seconds': self._time_utc_seconds}


class XSENSFileReader(FileReader):

    def __init__(self, input_file, output_dir):
        super().__init__(input_file, output_dir)
        self._column_names = []
        self._data = []
        self._time_utc_seconds = None

    def read_file(self):

        firstline = True
        with open(self._input_file, 'r') as file:
            for line in file:
                if not line.startswith('//'):
                    if firstline is True:
                        self._column_names.extend(line.strip().split(' '))
                        print(f'column_names:{self._column_names}')
                        firstline = False
                    else:
                        self._data.append(line.strip().split(' '))

            self._xsens_df = pd.DataFrame(self._data, columns=self._column_names)
            self._time_utc_seconds = float(self._xsens_df['Second'].iloc[0])
            print(f'xsens: time_utc_seconds:{self._time_utc_seconds}')
            self._xsens_df = self._xsens_df.astype(float)

    def format_file(self):

        new_names = {
            'Second': 'time',
            'Yaw': 'yaw',
            'Pitch': 'pitch',
            'Roll': 'roll'
        }

        self._xsens_df = self._xsens_df.rename(columns=new_names)
        self._xsens_df.columns = [col + '_xsens' for col in self._xsens_df.columns]
        self._xsens_df['time_xsens'] = self._xsens_df['time_xsens'] - self._xsens_df['time_xsens'].iloc[0]
        columns_to_unwrap = ['yaw_xsens', 'pitch_xsens', 'roll_xsens']
        self._xsens_df = utils.unwrap_columns(self._xsens_df,
                                              columns_to_unwrap)

        print(f'self._xsens_df: {self._xsens_df}')
        print(f'xsens_columns:{self._xsens_df.columns}')

    def get_df(self):
        return {'imu_name': 'xsens',
                'imu_df': self._xsens_df,
                'start_utc_seconds': self._time_utc_seconds}

    def save_file(self):
        self._xsens_df.to_csv(self._output_dir + '/xsens.csv')


class TELFileReader(FileReader):

    def __init__(self, input_file, output_dir):
        super().__init__(input_file, output_dir)
        self._time_utc_seconds = 0.0
        self._time_hh_s = 0.0
        self._time_hh = 0.0
        self._time_mm_s = 0.0
        self._time_mm = 0.0
        self._time_ss = 0.0
        self._input_file_extension = input_file.split('.')[-1]
        self._time_utc_seconds = 0.0
        self.tel_df = None

    def compute_start_time(self):
        self._time_utc_seconds = self._time_hh_s + self._time_mm_s + self._time_ss
        return self._time_utc_seconds

    def read_file(self):
        if self._input_file_extension == 'xls':
            metadata_time = pd.read_excel(self._input_file, sheet_name=2)
            start_time = metadata_time.loc[0, 'system time text']
            start_time = start_time.split(' ')[1]
            start_time = start_time.split(':')

            self._time_hh = float(start_time[0]) + 3
            self._time_mm = float(start_time[1])
            self._time_ss = float(start_time[2])

            self._time_hh_s = self._time_hh * 3600
            self._time_mm_s = self._time_mm * 60

            self._time_utc_seconds = self._time_hh_s + self._time_mm_s + self._time_ss

            self.tel_df = pd.read_excel(self._input_file, sheet_name=0)

        elif self._input_file_extension == 'csv':
            self.tel_df = pd.read_csv(self._input_file)
            if os.path.isdir(self._in_dir + 'meta'):
                df_csv_meta_time = pd.read_csv(self._in_dir + 'meta/' + 'time' + 'csv')
                self._time = df_csv_meta_time['system time text'][0]
                self._time = self._time_utc.split(' ')
                self._time = self._time_utc[1]
                self._time = self._time_utc.split(':')

                for i in range(len(self._time_utc_seconds)):
                    self._time[i] = float(self._time[i])

                self._time_hh_s = (self._time[0] + 3.0) * 3600
                self._time_mm_s = self._time[1] * 60
                self._time_ss = self._time[2]
                self._time_utc_seconds = self._time_hh_s + self._time_mm_s + self._time_ss

    def format_file(self):
        new_names = {
            'Time (s)': 'time',
            'Yaw': 'yaw',
            'Pitch': 'pitch',
            'Roll': 'roll',
            }

        self.tel_df = self.tel_df.rename(columns=new_names)
        self.tel_df.columns = [col + '_tel' for col in self.tel_df.columns]
        columns_to_unwrap = ['yaw_tel', 'pitch_tel', 'roll_tel']
        self.tel_df = utils.unwrap_columns(self.tel_df,
                                           columns_to_unwrap)

    def get_df(self):
        return {'imu_name': 'tel',
                'imu_df': self.tel_df,
                'start_utc_seconds': self._time_utc_seconds}

    def save_file(self):
        self.tel_df.to_csv(self._output_dir + '/tel.csv')
