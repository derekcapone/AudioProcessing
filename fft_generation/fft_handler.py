from enum import Enum
import numpy as np
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
from viewbox_handler import GeneralPlotWidget

MS_IN_S = 1000  # 1000ms per second

# Default values for FFT calculations
DEFAULT_SAMPLE_RATE = 44100  # Default sampling rate for FFT Handler
DEFAULT_WINDOW_LENGTH_MS = 100  # Default window length in milliseconds
DEFAULT_WINDOW_OVERLAP = 0.75  # Default ratio for window overlap

class WindowingFunctionEnum(Enum):
    """Window function types and their corresponding method calls"""
    HAMMING = np.hamming
    HANNING = np.hanning
    BARTLETT = np.bartlett
    BLACKMAN = np.blackman
    # KAISER = np.kaiser  # TODO: Figure out if we need this windowing method, need to pass in beta argument


class FftHandler:
    def __init__(self, plot_widget: GeneralPlotWidget, sample_rate: float, window_length_ms: int = DEFAULT_WINDOW_LENGTH_MS, window_overlap: float = DEFAULT_WINDOW_OVERLAP):
        if not isinstance(plot_widget, GeneralPlotWidget):
            raise TypeError(f"plot_widget needs to be of type GeneralPlotWidget, was of type {type(plot_widget)}")

        self.plot_widget = plot_widget  # Keep reference to plot widget to update when FFT calculations are made

        if sample_rate is None:
            raise RuntimeError(f"Need to set sample_rate parameter for {FftHandler.__name__} instance")

        self.sample_rate = sample_rate  # Sample rate in Hz
        self.window_length_ms = window_length_ms  # Window length in ms
        self.window_overlap = window_overlap  # window overlap ratio

        # Calculate window samples and hop samples
        # TODO: Investigate if window length should be divisible by base 2. (Simply rounding down for now)
        self.window_length_samples = int((window_length_ms/1000) * self.sample_rate)
        self.hop_length = int(self.window_length_samples * self.window_overlap)  # Samples to hop per window FFT calculation

        # Set up windowing, pre-calculate window samples for more efficient future calculations
        self.windowing_function = WindowingFunctionEnum.HANNING  # Default to Hanning function
        self.windowing_coefficients = self.windowing_function(self.window_length_samples)

        # Empty active signal, gets added to when data begins coming in
        self.sample_data = np.array([], dtype=np.float32)

        # Generate reusable time/frequency vectors for each window calculation
        self.time_vector, self.frequency_vector = self.generate_time_and_freq_vector()


    def add_signal(self, signal):
        """
        Adds sampled signal data to active signal for FFT Handler
        If adding this chunk of signal makes "len(sample_data)" > window_length_samples, FFT calculation is triggered
        Otherwise, adds signal and returns
        :param signal: Sampled signal to add to active signal in FFT Handler
        """
        # First add the signal to self.sample_data
        # TODO: Do not append, have preallocated buffer
        self.sample_data = np.append(self.sample_data, signal)

        if len(self.sample_data) < self.window_length_samples:
            # Not ready to calculate next FFT, returning
            print("Not enough data yet")
            return

        # Calculate FFT on next window of samples
        fft_data = self.fft_on_window(self.sample_data[:self.window_length_samples])
        amplitude = np.abs(fft_data)

        # Send calculated data to plot widget
        # TODO: Add to plot_widget here
        self.plot_widget.set_data(self.frequency_vector, amplitude)
        # TODO: Emit signal with other data potentially

        # "Hop" forward by trimming off the next "hop_length" samples
        self.sample_data = self.sample_data[self.hop_length:]


    def fft_on_window(self, window_signal):
        """
        Performs FFT on a signal that has already been separated into its temporal window.
        Note: Window function not yet applied to this signal.
        :param window_signal: Signal ready to have FFT performed on it
        :return: FFT values
        """
        # First multiply windowing coefficients
        intermediate_data = np.multiply(self.windowing_coefficients, window_signal)

        # Then calculate FFT
        return np.fft.fft(intermediate_data)


    def set_window_length(self, window_length_ms: int = DEFAULT_WINDOW_LENGTH_MS):
        """
        Sets window length and related attributes
        :param window_length_ms: Desired window length
        """
        self.window_length_ms = window_length_ms
        self.window_length_samples = int((window_length_ms / 1000) * self.sample_rate)
        self.hop_length = int(self.window_length_samples * self.window_overlap)  # Samples to hop per window FFT calculation

        # Recalculate windowing coefficients and generate new time vector
        self.windowing_coefficients = self.windowing_function(self.window_length_samples)
        self.time_vector, self.frequency_vector = self.generate_time_and_freq_vector()


    def set_windowing_function(self, windowing_func: WindowingFunctionEnum):
        """
        Updates windowing function to new value, recalculate the windowing coefficients.
        :param windowing_func: Windowing enumeration
        """
        self.windowing_function = windowing_func
        self.windowing_coefficients = self.windowing_function(self.window_length_samples)


    def generate_time_and_freq_vector(self):
        time_vector_extra = np.arange(0, self.window_length_ms / 1000.0, 1 / self.sample_rate)
        frequency_vector = np.fft.fftfreq(self.window_length_samples, d=1/self.sample_rate)
        return time_vector_extra[:self.window_length_samples], frequency_vector  # Truncate extra samples from rounding


##### Test functions #####
def read_wav_to_np_array(wav_file: str):
    wav_data = read(wav_file)
    sample_rate = float(wav_data[0])
    samples = np.array(wav_data[1], dtype=np.float32)
    return sample_rate, samples

def test_data_gen():
    wav_file_name = "/home/caponed/Desktop/Projects/AudioProcessingGui/fft_generation/sine_wave.wav"

    sample_rate, sample_data = read_wav_to_np_array(wav_file_name)
    return sample_rate, sample_data

if __name__ == "__main__":
    window_length = DEFAULT_WINDOW_LENGTH_MS
    window_overlap = 0.5

    sampling_rate, sample_data = test_data_gen()
    signal = np.array(sample_data)
    print(len(sample_data))

    fft_handler = FftHandler(None, sampling_rate, window_length, window_overlap)

    fft_handler.add_signal(signal[:4410])



