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
        self.samples_read = 0

        self.new_plot_widget = GeneralPlotWidget()

        self.fft_handler = FftHandler(self.new_plot_widget, self.sample_rate)

        # Add to layout
        self.verticalLayout.addWidget(self.new_plot_widget.widget_container)
        button = QPushButton("Add Signal data")
        self.verticalLayout.addWidget(button)
        button.clicked.connect(self.generate_signal)

    def generate_signal(self):
        # Generate signal and send to FFT Handler
        samples_to_read = self.fft_handler.window_length_samples
        signal_to_send = self.sample_data[self.samples_read:self.samples_read + samples_to_read]
        self.samples_read += samples_to_read
        self.fft_handler.add_signal(signal_to_send)


# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = AudioFFTApp()
    window.show()
    app.exec()
