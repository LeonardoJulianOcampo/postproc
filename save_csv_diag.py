from PyQt5 import QtWidgets, uic
from ui.save_as_csv_dialog_ui import Ui_Dialog
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSignal


class SaveToCSVDialog(QtWidgets.QDialog):

    data_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.pushButtonOk.clicked.connect(self.ok_button_clicked)
        self.ui.pushButtonCancel.clicked.connect(self.reject)

        self.out_data = {}

    def ok_button_clicked(self):
        file_name = self.ui.lineEditFileName.text()
        time_range = self.ui.lineEditExportTimeRange.text()
        time_range = time_range.split(',')
        time_range_list = []

        for element in time_range:
            time_range_list.append(float(element))

        self.out_data['name'] = file_name
        self.out_data['time_range'] = time_range_list
        print(f'{self.out_data}')
        self.data_ready.emit(self.out_data)
        self.accept()
