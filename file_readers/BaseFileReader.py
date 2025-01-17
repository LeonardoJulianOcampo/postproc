from abc import ABC, abstractmethod
import os


class FileReader:

    def __init__(self, input_file, output_dir):

        self._input_file = input_file
        self._output_dir = output_dir
        self._column_names = []
        self._data = []
        self._dateline = None
        self._first_timestamp_line = None

    def check_files(self):
        if not os.path.isfile(self._input_file):
            raise FileNotFoundError(f"No se encuentra el archivo {self._input_file}")
        else:
            print('archivo encontrado')

        if not os.path.isdir(self._output_dir):
            os.makedirs(self._output_dir)

    @abstractmethod
    def read_file(self):
        """
        Lee el archivo de origen, y devuelve un dataframe de pandas.
        el procesamiento necesario tambien se incluye en este metodo
        """

    @abstractmethod
    def format_file(self):
        pass

    @abstractmethod
    def save_file(self, temporal=False):
        pass

    @abstractmethod
    def compute_start_time(self):
        """
        Método que devuelve el timestamp inicial en base a datos como
        fecha y hora a un valor estandar dado por segundos transcurridos
        desde las 00:00hs del día de efectuada la medición hasta el
        instante de la medición en formato UTC
        """

        pass
