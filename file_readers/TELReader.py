from .BaseFileReader import FileReader


class SAMFileReader(FileReader):

    def __init__(self, input_file, output_file):
        super().__init__(input_file, output_file)

    def read_file(self):
        pass

    def save_file(self):
        pass
