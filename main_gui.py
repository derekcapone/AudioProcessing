import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from viewbox_handler import GeneralPlotWidget
from ui_generated.grapher import Ui_MainWindow
from fft_generation.fft_handler import FftHandler, read_wav_to_np_array, test_data_gen

class AudioFFTApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Get audio sample data
        self.sample_rate, self.sample_data = test_data_gen()
        self.num_samples = len(self.sample_data)
        self.x_time = np.linspace(0, float(self.num_samples) / self.sample_rate, self.num_samples)

        self.new_plot_widget = GeneralPlotWidget()
        self.new_plot_widget.set_data(self.x_time, self.sample_data)

        # Add to layout
        self.verticalLayout.addWidget(self.new_plot_widget.widget_container)


# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = AudioFFTApp()
    window.show()
    app.exec()
