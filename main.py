import sys
import os
import importlib
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QWidget, QListView
from PyQt5.QtWidgets import QTabWidget
from ui.main_window_ui import Ui_MainWindow
from PyQt5.core import QStringListModel
from open_files_diag import OpenFilesDialog
from dataframe_operations.generate_db import DB


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionConfigurar_directorios.triggered.connect(self.open_file_window)
        self.ui.pushButtonRefreshPlot.clicked.connect(self.plot)
        self.ui.actionSalir.triggered.connect(self.exit_program)
        self.tabTimeD = self.findChild(QTabWidget,
                                       'tabWidget')
        self.tabTimeD = self.tabTimeD.widget(0)
        self.tabTimeDPlot = self.tabTimeD.findChild(QWidget,
                                                    'timePlotWidget')
        self.tabTimeDPlot.showGrid(x=True, y=True)
        self.tabTimeDPlot.setBackground('w')
        self.tabTimeDPlot.setTitle('Gráfico:')

        self.list_availables = self.findChild(QListView,
                                              'listViewSeriesAvailable')

        self.input_paths_dict = {'in_dict': None,
                                 'out_dict': None}

        self.out_dict = {'IMAR': os.getcwd(),
                         'XSENS': os.getcwd(),
                         'TEL': os.getcwd()}

        self.input_paths_dict['out_dict'] = self.out_dict
        self.reader_modules = 'file_readers.readers'
        self.reader_dict = {}
        self.data_sets = []

    def exit_program(self):
        sys.exit(app.exec_())

    def init_processing(self):
        for element in self.input_paths_dict['in_dict'].keys():
            if element not in ('OUTDIR', '', None):
                if self.input_paths_dict['in_dict'][element] != '':
                    module = importlib.import_module(self.reader_modules)
                    self.reader_dict[element] = getattr(module, element + 'FileReader')

        if self.reader_dict:
            for key in self.reader_dict.keys():

                reader = self.reader_dict[key](self.input_paths_dict['in_dict'][key],
                                               self.input_paths_dict['in_dict']['OUTDIR'])

                print(f'imu:{key}')
                print(f'file:{self.input_paths_dict["in_dict"][key]}')
                reader.check_files()
                reader.read_file()
                reader.format_file()
                reader.save_file()

                # self.data_sets[key] = reader.get_df()
                self.data_sets.append(reader.get_df())
                print(f"self.data_sets[{key}]= {self.data_sets}")

            database = DB(self.data_sets, self.input_paths_dict['in_dict']['OUTDIR'])
            database.save_as_csv()

    def open_file_window(self):
        dialog = OpenFilesDialog()
        dialog.data_ready.connect(self.receive_paths_from_file_window)
        dialog.exec_()

    def plot(self):
        try:
            if 'time' not in pandas_df.columns or 'roll' not in pandas_df.columns:
                return
            x = pandas_df['time'].astype(float).tolist()
            y = pandas_df['roll'].astype(float).tolist()

            self.tabTimeDPlot.clear()
            self.tabTimeDPlot.plot(x, y, pen='b')

        except Exception as e:
            print(f"Error al graficar: {str(e)}")

    def receive_paths_from_file_window(self, path_dict):
        self.input_paths_dict['in_dict'] = path_dict
        process_files_diag = None
        self.init_processing()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
