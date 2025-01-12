from .BaseFileReader import FileReader
import pandas as pd
import csv

class IMARFileReader(FileReader):

    def __init__(self, input_file, output_file):
        super().__init__(input_file, output_file)
        self.imar_df = None

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
                    self._data.append(line.strip().split())

            self.imar_df = pd.DataFrame(self._data, columns=self._column_names)

            for column in self.imar_df.columns:
                try:
                    self.imar_df.columns[column] = pd.to_numeric(self.imar_df[column])
                except Exception:
                    pass

    def save_file(self, temporal=False):
        """
        Guarda el archivo leído pero con un formato dataframe de pandas
        """
        print(f'guardando en {self._output_dir} + imar.csv')
        with open(self._output_dir + 'imar.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self._column_names)
            writer.writerows(self._data)
        date = self._dateline.split(' ')[2].split('/')
        first_timestamp = self._first_timestamp_line.split(' ')[1].replace('+', '')
        df_out_date = pd.DataFrame({'day': [date[1]], 'month': [date[0]], 'year': [date[2]], 'second_of_week': first_timestamp})

    def get_df(self):
        return self.imar_df


class TELFileReader(FileReader):

    def __init__(self, input_file, output_file):
        super().__init__(input_file, output_file)

    def read_file(self):
        pass

    def save_file(self):
        pass


class XSENSFileReader(FileReader):

    def __init__(self, input_file, output_file):
        super().__init__(input_file, output_file)

    def read_file(self):
        pass

    def save_file(self):
        pass
