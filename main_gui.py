import numpy as np
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from viewbox_handler import GeneralPlotWidget
from ui_generated.grapher import Ui_MainWindow
from fft_generation.fft_handler import FftHandler, AcousticHandler, test_data_gen

class AudioFFTApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.resize(1500, 1200)

        # Get audio sample data
        self.sample_rate, self.sample_data = test_data_gen()
        self.samples_read = 0

        # Initialize plot widgets for amplitude and phase
        self.amplitude_plot_widget = GeneralPlotWidget("Frequency (Hz)", "Amplitude")
        self.phase_plot_widget = GeneralPlotWidget("Frequency (Hz)", "Phase")

        self.acoustic_handler = AcousticHandler(self.sample_rate)
        self.acoustic_handler.fft_amplitude.connect(self.amplitude_plot_widget.set_data)
        self.acoustic_handler.fft_phase.connect(self.phase_plot_widget.set_data)

        # Add to layout
        self.verticalLayout.addWidget(self.amplitude_plot_widget.widget_container)
        self.verticalLayout.addWidget(self.phase_plot_widget.widget_container)

        #### Generate test data #####
        button = QPushButton("Add Signal data")
        self.verticalLayout.addWidget(button)
        button.clicked.connect(self.generate_signal)

    def generate_signal(self):
        # Generate signal and send to FFT Handler
        samples_to_read = self.acoustic_handler.fft_handler.window_length_samples
        signal_to_send = self.sample_data[self.samples_read:self.samples_read + samples_to_read]
        self.samples_read += samples_to_read
        self.acoustic_handler.fft_handler.add_signal(signal_to_send)


# Run the application
if __name__ == "__main__":
    app = QApplication([])
    window = AudioFFTApp()
    window.show()
    app.exec()
