from .BaseFileReader import FileReader
import pandas as pd
import csv
import datetime


class IMARFileReader(FileReader):

    def __init__(self, input_file, output_file):
        super().__init__(input_file, output_file)
        self.imar_df = None
        self.first_timestamp = None
        self.measure_date = None
        self._data = []

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
                seconds_utc = self.compute_start_time(second_of_week, is_week=True, day_week=days_week)
            elif "second_of_day" in df_date.columns:
                second_of_day = round(float(df_date["second_of_day"]), 2)
                seconds_utc = self.compute_start_time(second_of_day)
            else:
                raise ValueError("No se encontraron valores necesarios para el cálculo")

            print(f'seconds: {seconds_utc}')
            self.imar_df['time'] = self.imar_df['TINTRPL']
            self.imar_df['time'] = self.imar_df['time'] - self.imar_df['TINTRPL'].iloc[0]
            self.imar_df['time'] = self.imar_df['time'] + seconds_utc
            self.imar_df = self.imar_df.drop(['TINTRPL'], axis=1)
            print(f"datos de tiempo: {df_date}")
            print(f"columns: {self.imar_df}")

    def save_file(self, temporal=False):
        """
        Guarda el archivo leído pero con un formato dataframe de pandas
        """
        print(f'guardando en {self._output_dir}/imar.csv')
        with open(self._output_dir + '/imar.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self._column_names)
            writer.writerows(self._data)

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

        return seconds_utc

    def get_df(self):
        return self.imar_df


class XSENSFileReader(FileReader):

    def __init__(self, input_file, output_file):
        super().__init__(input_file, output_file)

    def read_file(self):
        with open(self._input_file, 'r') as file:
            lines = file.readlines
            filtered_lines = [line for line in lines if not lines.strip().startswith('//')]
        column_names = filtered_lines[0]
        self._xsens_df = pd.Dataframe(filtered_lines[0:], column_names=filtered_lines[0])

    def format_file(self):
        self._xsens_df = self._xsens_df.rename(columns={'second': 'time'})
        print(f'self._xsens_df: {self._xsens_df}')

    def get_df(self):
        return self._xsens_df

    def save_file(self):
        self._xsens_df = pd.to_csv(self._output_file)


class TELFileReader(FileReader):

    def __init__(self, input_file, output_file):
        super().__init__(input_file, output_file)

    def read_file(self):
        pass

    def save_file(self):
        pass
