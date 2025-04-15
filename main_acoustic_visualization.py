import numpy as np
from PySide6.QtCore import Slot, QAbstractTableModel
from PySide6.QtWidgets import QApplication, QMainWindow
from ui_generated.acoustic_vis import Ui_MainWindow
from fft_generation.fft_handler import FftHandler, AcousticHandler, SampleSignalGenerator

class TableModel(QAbstractTableModel):
    def __init__(self, number_hydrophone_lines: int, number_channels_per_line: int):
        super().__init__()

        self.number_hydrophone_lines = number_hydrophone_lines
        self.number_channels_per_line = number_channels_per_line
        self._data = np.empty((0, number_hydrophone_lines * number_channels_per_line))  # Keep reference of array to display







class RawDataVisualize(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Test sample signal generator and button connection
        self.sample_signal_gen = SampleSignalGenerator(interval_ms=1000)

        # Instantiate acoustic handler object
        self.acoustic_handler = AcousticHandler()
        self.sample_signal_gen.sample_signal.connect(self.acoustic_handler.retrieve_acoustic_data)

        self.model = TableModel(self.acoustic_handler.number_lines, self.acoustic_handler.total_sensors_per_line)
        self.sample_data_table.setModel(self.model)


    # def generate_column_headers(self):
    #     total_column_count = 1 + (self.acoustic_handler.number_lines * self.acoustic_handler.total_sensors_per_line)  # +1 because of "Sample Number" column
    #     self.sample_data_table.setColumnCount(total_column_count)
    #     self.sample_data_table.setColumnWidth(0, 110)
    #     self.sample_data_table.setHorizontalHeaderItem(0, QTableWidgetItem("Sample Number"))
    #
    #     # Set column headers and size
    #     for line_num in range(self.acoustic_handler.number_lines):
    #         for sensor_num in range(self.acoustic_handler.total_sensors_per_line):
    #             column_index = (line_num * self.acoustic_handler.total_sensors_per_line) + sensor_num + 1
    #             self.sample_data_table.setHorizontalHeaderItem(column_index, QTableWidgetItem(f"L{line_num}-CH{sensor_num}"))
    #             self.sample_data_table.setColumnWidth(column_index, 70)
    # @Slot()
    # def set_table_values(self, data_array):
    #     flattened_array = data_array.reshape(-1, data_array.shape[2])
    #     new_array_vals = flattened_array.T
    #
    #     row_position = self.sample_data_table.rowCount()
    #
    #     for i in range(new_array_vals.shape[0]):
    #
    #         row_to_add = row_position + i
    #         self.sample_data_table.insertRow(row_to_add)
    #
    #         for data, column in zip(new_array_vals[0], range(data_array.shape[0])):
    #             print(f"column: {column}, data: {data}")


# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = RawDataVisualize()
    window.show()
    app.exec()
