from PyQt5 import QtWidgets, uic
from ui.open_files_ui import Ui_openFilesDialog
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSignal


class OpenFilesDialog(QtWidgets.QDialog):

    data_ready = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.ui = Ui_openFilesDialog()
        self.ui.setupUi(self)

        self.pathIMAR = self.findChild(QtWidgets.QLineEdit, 'pathIMAR')
        self.pathXSENS = self.findChild(QtWidgets.QLineEdit, 'pathXSENS')
        self.pathTel = self.findChild(QtWidgets.QLineEdit, 'pathTelefono')
        self.pathOut = self.findChild(QtWidgets.QLineEdit, 'pathOut')

        self.browse_imar_file = self.findChild(QtWidgets.QToolButton,
                                               'toolButtonOpenFileIMAR')
        self.browse_xsens_file = self.findChild(QtWidgets.QToolButton,
                                                'toolButtonOpenFileXSENS')
        self.browse_tel_file = self.findChild(QtWidgets.QToolButton,
                                              'toolButtonOpenFileTelefono')

        self.browse_out_dir = self.findChild(QtWidgets.QToolButton,
                                             'toolButtonSelectOutDir')

        self.okButton = self.findChild(QtWidgets.QPushButton,
                                       'okButton')
        self.cancelButton = self.findChild(QtWidgets.QPushButton,
                                           'cancelButton')


        self.browse_imar_file.clicked.connect(lambda: self.browse_file('IMAR'))
        self.browse_xsens_file.clicked.connect(lambda: self.browse_file('XSENS'))
        self.browse_tel_file.clicked.connect(lambda: self.browse_file('TEL'))
        self.browse_out_dir.clicked.connect(lambda: self.browse_file('OUTDIR'))

        self.okButton.clicked.connect(self.ok_button_clicked)
        self.cancelButton.clicked.connect(self.reject)

    def get_input_data(self):
        input_path_dict = {}
        input_path_dict['IMAR'] = self.pathIMAR.text()
        input_path_dict['XSENS'] = self.pathXSENS.text()
        input_path_dict['TEL'] = self.pathTel.text()

        input_path_dict['OUTDIR'] = self.pathOut.text()

        return input_path_dict

    def browse_file(self, file):

        if file != 'OUTDIR':

            file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo",
                                                       "",
                                                       "Todos los archivos (*)")

            if file_path:
                if file == 'IMAR':
                    self.pathIMAR.setText(file_path)
                elif file == 'XSENS':
                    self.pathXSENS.setText(file_path)
                elif file == 'TEL':
                    self.pathTel.setText(file_path)
                else:
                    self.pathOut.setText(file_path)

        else:

            file_path = QFileDialog.getExistingDirectory(self,
                                                         "Seleccionar Carpeta",
                                                         "",
                                                         QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)

            self.pathOut.setText(file_path)

    def ok_button_clicked(self):
        data = self.get_input_data()
        self.data_ready.emit(data)
        self.accept()
