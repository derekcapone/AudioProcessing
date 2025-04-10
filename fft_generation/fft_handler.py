from enum import Enum
import numpy as np
import numpy.typing as npt
from PySide6.QtCore import QObject, Signal, SignalInstance, QTimer
from scipy.io.wavfile import read

MS_IN_S = 1000  # 1000ms per second
# Default values for FFT calculations
DEFAULT_SAMPLE_RATE_HF = 5120  # Default sampling rate for FFT Handler
DEFAULT_SAMPLE_RATE_LF = DEFAULT_SAMPLE_RATE_HF / 2
DEFAULT_WINDOW_LENGTH_MS = 100  # Default window length in milliseconds
DEFAULT_WINDOW_OVERLAP = 0.75  # Default ratio for window overlap
DEFAULT_FFT_INTERVAL = 100  # Default interval between FFTs

# TODO: Move away from these defaults and allow for the array config message to set these values
DEFAULT_NUMBER_LF_CHANNELS = 8
DEFAULT_NUMBER_HF_CHANNELS = 3

class WindowingFunctionEnum(Enum):
    """Window function types and their corresponding method calls"""
    RECTANGULAR = lambda values: values
    HAMMING = np.hamming
    HANNING = np.hanning
    BARTLETT = np.bartlett
    BLACKMAN = np.blackman

class ScalingOptionsEnum(Enum):
    RAW = 0  # Range of -1.0 to 1.0
    VOLTS = 1  # Converted to Volts
    POWER = 2  # Converted to Power
    DBV_ROOT_HZ = 3  # Converted to DBV root Hz


class AcousticHandler(QObject):
    """
    Class used to handle all acoustic data processing
    Receives signals from server threads and delegates all acoustic handling of these
    """
    fft_amplitude = Signal(object, object)  # FFT amplitude to plot: <np.array(x_axis), np.array(y_axis)>
    fft_phase = Signal(object, object)  # FFT phase to plot: <np.array(x_axis), np.array(y_axis)>

    def __init__(self, sample_rate: float, window_length_ms: int = DEFAULT_WINDOW_LENGTH_MS, window_overlap: float = DEFAULT_WINDOW_OVERLAP):
        super().__init__()

        # Instantiate FFT Handler object for FFT calculations
        self.fft_handler = FftHandler(sample_rate, self.fft_amplitude, self.fft_phase)

        # Instantiate raw acoustic datat handler for caching and displaying raw acoustic data
        self.acoustic_data_handler = RawAcousticDataHandler()

        # TODO: Figure out how we are going to select sensors to display in FFTs
        self.active_sensor_number = 0

    def retrieve_acoustic_data(self):
        """
        # TODO: Implement when signal is set up for AcousticDataMessage reception
        Slot called to handle any time an Acoustic Data Message is received.
        De-interleaves acoustic data and adds to cached data, as well as adding new signal data to FFT Handler
        :return:
        """
        raise NotImplemented("retrieve_acoustic_data method not yet implemented")


class FftHandler:
    def __init__(self, sample_rate: float, fft_amp_signal: SignalInstance, fft_phase_signal: SignalInstance, window_length_ms: int = DEFAULT_WINDOW_LENGTH_MS, window_overlap: float = DEFAULT_WINDOW_OVERLAP):
        if sample_rate is None:
            raise RuntimeError(f"Need to set sample_rate parameter for {FftHandler.__name__} instance")

        self.sample_rate = sample_rate  # Sample rate in Hz
        self.window_length_ms = window_length_ms  # Window length in ms
        self.window_overlap = window_overlap  # window overlap ratio

        # FFT signals for GUI plotting
        self.fft_amp_signal = fft_amp_signal
        self.fft_phase_signal = fft_phase_signal

        # Calculate window samples and hop samples
        # TODO: Investigate if window length should be divisible by base 2. (Simply rounding down for now)
        self.window_length_samples = int((window_length_ms/1000) * self.sample_rate)
        self.hop_length = int(self.window_length_samples * self.window_overlap)  # Samples to hop per window FFT calculation

        # Set up windowing, pre-calculate window samples for more efficient future calculations
        self.windowing_function = WindowingFunctionEnum.RECTANGULAR  # Default to Hanning function
        self.windowing_coefficients = self.windowing_function(self.window_length_samples)

        # Empty active signal, gets added to when data begins coming in
        self.sample_data = np.array([], dtype=np.float32)

        # Generate reusable time/frequency vectors for each window calculation
        self.time_vector, self.frequency_vector = self.generate_time_and_freq_vector()

        # Timer instance to adhere to set interval
        self.interval_timer = QTimer()


    def add_signal(self, signal):
        """
        Adds sampled signal data to active signal for FFT Handler
        If adding this chunk of signal makes "len(sample_data)" > window_length_samples, FFT calculation is triggered
        Otherwise, adds signal and returns
        :param signal: Sampled signal to add to active signal in FFT Handler
        """
        # First add the signal to self.sample_data
        # TODO: Do not append, have pre-allocated buffer
        self.sample_data = np.append(self.sample_data, signal)

        if len(self.sample_data) < self.window_length_samples:
            # Not ready to calculate next FFT, returning
            print("Not enough data yet")
            return

        # Calculate FFT on next window of samples
        fft_data = self.fft_on_window(self.sample_data[:self.window_length_samples])
        amplitude = np.abs(fft_data)
        phase = np.angle(fft_data)

        # Emit signals
        self.fft_amp_signal.emit(self.frequency_vector, amplitude)
        self.fft_phase_signal.emit(self.frequency_vector, phase)

        # "Hop" forward by trimming off the next "hop_length" samples
        # TODO: Moving window is likely unnecessary
        self.sample_data = self.sample_data[self.hop_length:]


    def fft_on_window(self, window_signal):
        """
        Performs FFT on a signal that has already been separated into its temporal window.
        First applies windowing function to data signal, then performs the FFT calculation
        :param window_signal: Signal ready to have FFT performed on it
        :return: FFT values
        """
        intermediate_data = np.multiply(self.windowing_coefficients, window_signal)
        return np.fft.fft(intermediate_data)


    def set_window_length(self, window_length_ms: int = DEFAULT_WINDOW_LENGTH_MS):
        """
        Sets window length and related attributes
        :param window_length_ms: Desired window length
        """
        self.window_length_ms = window_length_ms
        self.window_length_samples = int((window_length_ms / 1000) * self.sample_rate)
        self.hop_length = int(self.window_length_samples * self.window_overlap)  # Samples to hop per window FFT calculation

        # Recalculate windowing coefficients and generate new time/frequency vector
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


class RawAcousticDataHandler:
    """
    TODO: Implement this to handle raw acoustic data
    This class should be used to store all acoustic data that is generated from server threads
    This class should interface in some way with the raw data GUI aspect
    This class should provide functionality for exporting raw acoustic data
    """
    def __init__(self, number_lf_channels: int = DEFAULT_NUMBER_LF_CHANNELS, number_hf_channels: int = DEFAULT_NUMBER_HF_CHANNELS):
        self.number_lf_channels = number_lf_channels
        self.number_hf_channels = number_hf_channels

        # Create arrays for low frequency and high frequency sensor data
        self.lf_channels = np.empty((self.number_lf_channels, 0))
        self.hf_channels = np.empty((self.number_hf_channels, 0))

    def add_to_channels(self, lf_channel_data: npt.NDArray, hf_channel_data: npt.NDArray):
        # First verify sizes of arrays
        if self.number_lf_channels != lf_channel_data.shape[0]:
            raise RuntimeError(f"Array shape for new data does not match number of LF channels. Expected {self.number_lf_channels}, got {lf_channel_data.shape[0]}")
        elif self.number_hf_channels != hf_channel_data.shape[0]:
            raise RuntimeError(f"Array shape for new data does not match number of HF channels. Expected {self.number_hf_channels}, got {hf_channel_data.shape[0]}")

        # Append data to cached channel data
        self.lf_channels = np.hstack((self.lf_channels, lf_channel_data))
        self.hf_channels = np.hstack((self.hf_channels, hf_channel_data))

    def export_cached_acoustic_data(self):
        """
        TODO: Implement this method
        This method will take all active data and export it to a file as desired
        :return:
        """
        raise NotImplemented("export_cached_acoustic_data is not yet implemented")


##### Test functions #####
def test_data_gen():
    sample_rate = DEFAULT_SAMPLE_RATE_LF
    signal_duration_s = 3.0  # 3 Second signal

    t = np.linspace(0, signal_duration_s, int(signal_duration_s * sample_rate), endpoint=False)

    # Signal 1
    amplitude1 = 2.0
    frequency1 = 440
    signal1 = amplitude1 * np.sin(2 * np.pi * frequency1 * t)

    # Signal 2
    amplitude2 = 1.0
    frequency2 = 800
    signal2 = amplitude2 * np.sin(2 * np.pi * frequency2 * t)

    # Noise
    noise_signal = np.random.normal(0, 1, len(t))

    # Generate full signal
    signal_samples = signal1 + signal2 + noise_signal

    return sample_rate, signal_samples

if __name__ == "__main__":
    sampling_rate, sample_data = test_data_gen()