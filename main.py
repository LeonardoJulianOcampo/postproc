import sys
import os
import importlib
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QWidget, QListView
from PyQt5.QtWidgets import QTabWidget
from ui.main_window_ui import Ui_MainWindow
from PyQt5.QtCore import QStringListModel
from open_files_diag import OpenFilesDialog
from save_csv_diag import SaveToCSVDialog
from dataframe_operations.generate_db import DB
from utils.config import Configuration
from dataframe_operations.temp_align import tempAlign
from dataframe_operations.magn_align import magnAlign

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.cfg = Configuration('./cfg/config.cfg')
        self.cfg._read_config()

        self.columns2plot = []
        self.columns_available = []

        self.available_model = QStringListModel()
        self.selected_model = QStringListModel()

        self._save_csv_data_dict = {}

        self._init_ui_elements()
        self._init_data()
        self._setup_connections()
        self._setup_dataframe_ops()
        self._get_input_paths()

    def _init_ui_elements(self):
        self.tabTimeD = self.findChild(QTabWidget,
                                       'tabWidget')
        self.tabTimeD = self.tabTimeD.widget(0)
        self.tabTimeDPlot = self.tabTimeD.findChild(QWidget,
                                                    'timePlotWidget')
        self.tabTimeDPlot.showGrid(x=True, y=True)
        self.tabTimeDPlot.setBackground('w')
        self.tabTimeDPlot.setTitle('Gráfico:')

        self.list_availables = self.findChild(QListView,
                                              'listViewSeriesAvaliable')

        self.list_to_plot = self.findChild(QListView,
                                           'listViewSeriesToPlot')

        self.load2plot_button = self.findChild(QPushButton,
                                               'pushButtonLoadToPlot')

        self.move2availableButton = self.findChild(QPushButton,
                                                   'pushButtonRemoveToPlot')

        self.list2plot = self.findChild(QListView,
                                        'listViewSeriesToPlot')

        self.x_align = self.findChild(QDoubleSpinBox,
                                      'determineXAlign')
        self.y_align = self.findChild(QDoubleSpinBox,
                                      'determineYAlign')

        self.loadFromDiskButton = self.findChild(QPushButton,
                                                 'pushButtonLoadFromDisk')
        self.saveAsCSV = self.findChild(QPushButton,
                                        'pushButtonSaveAsCSV')

    def _init_data(self):
        self.input_paths_dict = {'in_dict': None, 'out_dict': None}
        self.out_dict = {name: os.getcwd() for name in ['IMAR', 'XSENS', 'TEL']}
        self.input_paths_dict['out_dict'] = self.out_dict

        self.reader_modules = 'file_readers.readers'
        self.reader_dict = {}
        self.data_sets = []
        self.columns_available = []
        self.list_availables.setModel(self.available_model)
        self.list_to_plot.setModel(self.selected_model)
        self._item_to_apply_op = None
        self.dataset_dict = {}

    def _setup_dataframe_ops(self):
        self._x_ops = tempAlign()
        self._y_ops = magnAlign()

    def _setup_connections(self):
        self.ui.actionConfigurar_directorios.triggered.connect(self.open_file_window)

        self.ui.pushButtonRefreshPlot.clicked.connect(self.plot)
        self.ui.PushButtonCleanPlot.clicked.connect(self.clean_plot)
        self.ui.actionSalir.triggered.connect(self.exit_program)
        self.load2plot_button.clicked.connect(self.move_to_selected)
        self.move2availableButton.clicked.connect(self.move_to_available)

        self.list_to_plot.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.x_align.valueChanged.connect(self._set_x_align)
        self.y_align.valueChanged.connect(self._set_y_align)

        self.loadFromDiskButton.clicked.connect(self._load_data_from_disk)
        self.saveAsCSV.clicked.connect(self.open_save_file_csv_window)

    def exit_program(self):
        sys.exit(app.exec_())

    def _get_input_paths(self):
        print('ejecutando get_input_paths')
        input_path_dict = {}
        for imu_name in self.cfg.get_config().keys():
            input_path_dict[imu_name] = self.cfg.get_config()[imu_name]['datasetpath']

        self.input_paths_dict['in_dict'] = input_path_dict

    def init_processing(self):
        for element in self.input_paths_dict['in_dict'].keys():
            if element not in ('OUTDIR', '', None):
                if self.input_paths_dict['in_dict'][element] != '':
                    module = importlib.import_module(self.reader_modules)
                    self.reader_dict[element] = getattr(module, element + 'FileReader')

        if self.reader_dict:
            for key in self.reader_dict.keys():

                reader = self.reader_dict[key](self.input_paths_dict['in_dict'][key],
                                               './output_files/')

                reader.check_files()
                reader.read_file()
                reader.format_file()
                reader.save_file()

                # self.data_sets[key] = reader.get_df()
                self.data_sets.append(reader.get_df())

            self.database = DB(self.data_sets, './output_files/')
            self.columns_available = self.database.get_column_names()
            self.db = self.database.get_db()
            self.load_columns()

    def load_columns(self):
        self.available_model.setStringList(self.columns_available)

    def _load_data_from_disk(self):
        self.init_processing()

    def _save_as_csv(self):
        self.database.save_range(self._save_csv_data_dict)

    def move_to_selected(self):

        sel_indexes = self.list_availables.selectionModel().selectedIndexes()
        if not sel_indexes:
            return

        sel_items = [index.data() for index in sel_indexes]

        current_selected = self.selected_model.stringList()
        current_selected = self.selected_model.setStringList(current_selected + sel_items)

        current_available = self.available_model.stringList()

        for item in sel_items:
            current_available.remove(item)

        self.available_model.setStringList(current_available)

    def move_to_available(self):

        selected_indexes = self.list_to_plot.selectionModel().selectedIndexes()
        if not selected_indexes:
            return

        selected_items = [index.data() for index in selected_indexes]
        current_available = self.available_model.stringList()
        self.available_model.setStringList(current_available + selected_items)

        current_selected = self.selected_model.stringList()
        for item in selected_items:
            current_selected.remove(item)
        self.selected_model.setStringList(current_selected)

    def on_selection_changed(self, selected, deselected):

        for index in selected.indexes():
            self._item_to_apply_op = index.data()

    def open_file_window(self):
        dialog = OpenFilesDialog()
        dialog.data_ready.connect(self.receive_paths_from_file_window)
        dialog.exec_()

    def open_save_file_csv_window(self):
        dialog = SaveToCSVDialog()
        dialog.data_ready.connect(self.receive_data_from_save_csv_window)
        dialog.exec_()

    def plot(self):
        #         try:
        #             if 'time' not in pandas_df.columns or 'roll' not in pandas_df.columns:
        #                 return
        #             x = pandas_df['time'].astype(float).tolist()
        #             y = pandas_df['roll'].astype(float).tolist()
        #
        #             self.tabTimeDPlot.clear()
        #             self.tabTimeDPlot.plot(x, y, pen='b')
        #
        #         except Exception as e:
        self.clean_plot()
        items_to_plot = self.selected_model.stringList()
        colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        num_c = len(colors)
        self.tabTimeDPlot.addLegend()
        for i, item in enumerate(items_to_plot):
            imu_name = item.split('_')[-1]
            t_data = self.db['time_' + imu_name].astype(float).to_list()
            p_data = self.db[item].astype(float).to_list()

            color = colors[i % num_c]
            self.tabTimeDPlot.plot(t_data, p_data, pen=color, name=item)

    def clean_plot(self):
        self.tabTimeDPlot.clear()

    def receive_paths_from_file_window(self, path_dict):
        self.input_paths_dict['in_dict'] = path_dict
        self.init_processing()

    def receive_data_from_save_csv_window(self, data_dict):
        self.database.save_range(data_dict)

    def _set_x_align(self):

        if self._item_to_apply_op is not None:
            print(f'x_align_value: {self.x_align.value()}')

            imu_name = self._item_to_apply_op.split('_')[1]
            print(f'imu_name: {imu_name}')
            offset = self.x_align.value()

            self.db['time_'+imu_name] = self._x_ops.set_manual_align(imu_name,
                                                                     self.db,
                                                                     offset)
            print(f"time_{imu_name}")

            # self.database.update_db('time_'+imu_name,
            #                        self.db['time_' + imu_name])
            # self.db = self.database.get_db()
            self.database.db = self.db.copy()
            self.clean_plot()
            self.plot()

    def _set_y_align(self):
        if self._item_to_apply_op is not None:
            print(f'y_align_value: {self.y_align.value()}')

            column_name = self._item_to_apply_op
            offset = self.y_align.value()
            self.db[column_name] = self._y_ops.set_manual_align(column_name,
                                                                self.db,
                                                                offset)
            # self.database.set_db(self.db)
            self.database.db = self.db.copy()
            self.clean_plot()
            self.plot()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
