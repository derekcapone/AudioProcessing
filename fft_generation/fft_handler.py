from enum import Enum
from typing import Tuple

import numpy as np
import numpy.typing as npt
from PySide6.QtCore import QObject, Signal, SignalInstance, QTimer, Slot
from scipy.io.wavfile import read

MS_IN_S = 1000  # 1000ms per second

# Default values for FFT calculations
DEFAULT_SAMPLE_RATE_HF = 5120  # Default sampling rate for FFT Handler
DEFAULT_SAMPLE_RATE_LF = DEFAULT_SAMPLE_RATE_HF / 2
DEFAULT_WINDOW_LENGTH_MS = 100  # Default window length in milliseconds
DEFAULT_WINDOW_OVERLAP = 0.75  # Default ratio for window overlap
DEFAULT_FFT_INTERVAL = 100  # Default interval between FFTs

# TODO: Move away from these defaults and allow for the array config message to set these values
NUMBER_LF_CHANNELS_PER_LINE = 40
NUMBER_HF_CHANNELS_PER_LINE = 32

DEFAULT_TOTAL_SENSORS_PER_LINE = NUMBER_LF_CHANNELS_PER_LINE + NUMBER_HF_CHANNELS_PER_LINE + NUMBER_LF_CHANNELS_PER_LINE
DEFAULT_NUMBER_LINES = 2

TOTAL_SAMPLES_PER_MESSAGE = DEFAULT_NUMBER_LINES * DEFAULT_TOTAL_SENSORS_PER_LINE * DEFAULT_SAMPLE_RATE_HF
TOTAL_SAMPLE_BYTES_PER_MESSAGE = TOTAL_SAMPLES_PER_MESSAGE * 4  # 4 bytes in each sample (float32)


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
    fft_amplitude = Signal(object, object)  # F FT amplitude to plot: <np.array(x_axis), np.array(y_axis)>
    fft_phase = Signal(object, object)  # FFT phase to plot: <np.array(x_axis), np.array(y_axis)>
    raw_data_signal = Signal(object)

    def __init__(self, sample_rate: float = DEFAULT_SAMPLE_RATE_HF, window_length_ms: int = DEFAULT_WINDOW_LENGTH_MS, window_overlap: float = DEFAULT_WINDOW_OVERLAP):
        super().__init__()

        # TODO: Update so that ArrayConfigMessage will change these values to values stored in message
        self.number_lines = DEFAULT_NUMBER_LINES
        self.total_sensors_per_line = DEFAULT_TOTAL_SENSORS_PER_LINE

        # Instantiate FFT Handler object for FFT calculations
        self.fft_handler = FftHandler(sample_rate, self.fft_amplitude, self.fft_phase)

        # Instantiate raw acoustic datat handler for caching and displaying raw acoustic data
        self.raw_data_handler = RawAcousticDataHandler()

        # TODO: Figure out how we are going to select sensors to display in FFTs
        self.active_fft_sensor_number = (0, 0)  # Default to 0th line, 0th sensor for FFTs
        self.active_fft_sensor_number = (0, 0)  # Default to 0th line, 0th sensor for FFTs

    def set_active_sensor(self, sensor_number: Tuple[int, int]):
        # Check validity of sensor number
        if sensor_number[0] >= DEFAULT_NUMBER_LINES or sensor_number[1] >= DEFAULT_TOTAL_SENSORS_PER_LINE:
            RuntimeError(f"Trying to access samples for non existent sensor. Sensor array bounds are ({DEFAULT_NUMBER_LINES},{DEFAULT_TOTAL_SENSORS_PER_LINE}), tried to access ({sensor_number[0]},{sensor_number[1]})")

        self.active_fft_sensor_number = sensor_number

    @Slot()
    def retrieve_acoustic_data(self, data_array: npt.NDArray):
        """
        Slot called to handle any time an Acoustic Data Message is received.
        De-interleaves acoustic data and adds to cached data, as well as adding new signal data to FFT Handler
        :return:
        """
        if not isinstance(data_array, np.ndarray):
            raise RuntimeError(f"retrieve_acoustic_data method requires np.ndarray type to process. Received type {type(data_array).__name__}")

        data_per_sample = np.reshape(data_array, (DEFAULT_NUMBER_LINES, DEFAULT_TOTAL_SENSORS_PER_LINE, -1))
        self.raw_data_signal.emit(data_per_sample)

        self.raw_data_handler.add_to_channels(data_per_sample)

        # TODO: Call FftHandler to calculate FFT on new data



class FftHandler:
    """
    Class used to perform FFT calculations on provided signal data based on provided parameters
    This class has no indication of timing intervals for FFT. It simply performs FFTs on the passed in signal
    When FFTs calculations are complete, signals are emitted for
    """
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
    def __init__(self, number_lines: int = DEFAULT_NUMBER_LINES, number_lf_channels_per_line: int = NUMBER_LF_CHANNELS_PER_LINE, number_hf_channels_per_line: int = NUMBER_HF_CHANNELS_PER_LINE):
        self.number_lines = number_lines
        self.number_lf_channels_per_line = number_lf_channels_per_line
        self.number_hf_channels_per_line = number_hf_channels_per_line
        self.total_sensors_per_line = self.number_lf_channels_per_line + self.number_hf_channels_per_line + self.number_lf_channels_per_line

        # Create arrays for low frequency and high frequency sensor data
        self.lf_channels = np.empty((self.number_lf_channels_per_line, 0))
        self.hf_channels = np.empty((self.number_hf_channels_per_line, 0))

        # Create data cache for all samples
        self.sample_data = np.empty((self.number_lines, self.total_sensors_per_line, 0))

    def add_to_channels(self, new_sample_data: npt.NDArray):
        # First verify size of array
        if new_sample_data.shape[0] != self.number_lines or new_sample_data.shape[1] != self.total_sensors_per_line:
            raise RuntimeError(f"Sample data shape does not match expected shape. Expected ({self.number_lines},{self.total_sensors_per_line},n) but got {new_sample_data.shape}")

        # Append data to cached sample data
        self.sample_data = np.concatenate((self.sample_data, new_sample_data), axis=2)

    def get_channel_data(self, sensor_number: Tuple[int, int]):
        if sensor_number[0] >= DEFAULT_NUMBER_LINES or sensor_number[1] >= DEFAULT_TOTAL_SENSORS_PER_LINE:
            RuntimeError(f"Trying to access samples for non existent sensor. Sensor array bounds are ({DEFAULT_NUMBER_LINES},{DEFAULT_TOTAL_SENSORS_PER_LINE}), tried to access ({sensor_number[0]},{sensor_number[1]})")
        line_num = sensor_number[0]
        sensor_number = sensor_number[1]
        return self.sample_data[line_num][sensor_number]


    def export_cached_acoustic_data(self):
        """
        TODO: Implement this method
        This method will take all active data and export it to a file as desired
        :return:
        """
        raise NotImplemented("export_cached_acoustic_data is not yet implemented")


##### Test functions #####
class SampleSignalGenerator(QObject):
    sample_signal = Signal(object)

    def __init__(self, interval_ms=1000, parent=None):
        super().__init__(parent)
        self.data_array = generate_sample_data()

        self.timer = QTimer(self)
        self.timer.setInterval(interval_ms)
        self.timer.timeout.connect(self.emit_data)
        self.timer.start()

    def emit_data(self):
        self.sample_signal.emit(self.data_array)


def generate_sample_data():
    per_line_array = []
    for i in range(DEFAULT_TOTAL_SENSORS_PER_LINE):
        per_line_array += DEFAULT_SAMPLE_RATE_HF * [float(i)]

    per_line_array += per_line_array
    data_array = np.array(per_line_array, dtype=np.float32)
    return data_array


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
    # Instantiate acoustic handler
    acoustic_handler = AcousticHandler(DEFAULT_SAMPLE_RATE_HF)

    # Generate test data for samples
    array_samples = generate_sample_data()

    acoustic_handler.retrieve_acoustic_data(array_samples)
    acoustic_handler.retrieve_acoustic_data(array_samples)

    sensor_tuple = (0, 0)
    channel_data = acoustic_handler.raw_data_handler.get_channel_data(sensor_tuple)
    print(f"Channel data: {channel_data}")


