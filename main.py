import sys
import os
import importlib
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QTabWidget
from ui.main_window_ui import Ui_MainWindow
from open_files_diag import OpenFilesDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionConfigurar_directorios.triggered.connect(self.open_file_window)
        self.ui.actionSalir.triggered.connect(self.exit_program)
        self.tabTimeD = self.findChild(QTabWidget,
                                       'tabWidget')
        self.tabTimeD = self.tabTimeD.widget(0)
        self.tabTimeDPlot = self.tabTimeD.findChild(QWidget,
                                                    'timePlotWidget')
        self.tabTimeDPlot.showGrid(x=True, y=True)
        self.tabTimeDPlot.setBackground('w')
        self.tabTimeDPlot.setTitle('Gráfico:')

        self.input_paths_dict = {'in_dict': None,
                                 'out_dict': None}

        self.out_dict = {'IMAR': os.getcwd(),
                         'XSENS': os.getcwd(),
                         'TEL': os.getcwd()}

        self.input_paths_dict['out_dict'] = self.out_dict
        self.reader_modules = 'file_readers.readers'
        self.reader_lst = []
        self.data_sets = {}

    def exit_program(self):
        sys.exit(app.exec_())

    def init_processing(self):
        for element in self.input_paths_dict['in_dict'].keys():
            if element not in ('OUTDIR', '', None):
                if self.input_paths_dict['in_dict'][element] != '':
                    module = importlib.import_module(self.reader_modules)
                    self.reader_lst.append(getattr(module, element + 'FileReader'))
            if self.reader_lst:
                for obj in self.reader_lst:
                    reader = obj(self.input_paths_dict['in_dict'][element],
                                 self.input_paths_dict['in_dict']['OUTDIR'])
                    reader.check_files()
                    reader.read_file()
                    reader.save_file()
                    self.data_sets[element] = reader.get_df()

    def open_file_window(self):
        dialog = OpenFilesDialog()
        dialog.data_ready.connect(self.receive_paths_from_file_window)
        dialog.exec_()

    def plot(self, pandas_df):
        try:
            # Verificar que el DataFrame tiene las columnas necesarias
            if 'TINTRPL' not in pandas_df.columns or 'roll' not in pandas_df.columns:
                print("Error: Columnas requeridas no encontradas en el DataFrame")
                return
            # lista_flotantes = df['columna'].astype(float).tolist()
            # Convertir a numpy arrays eliminando valores no válidos
            x = pandas_df['TINTRPL'].astype(float).tolist()
            y = pandas_df['roll'].astype(float).tolist()

            self.tabTimeDPlot.clear()
            self.tabTimeDPlot.plot(x, y, pen='b')

        except Exception as e:
            print(f"Error al graficar: {str(e)}")

    def receive_paths_from_file_window(self, path_dict):
        self.input_paths_dict['in_dict'] = path_dict
        print(path_dict)
        process_files_diag = None
        self.init_processing()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
