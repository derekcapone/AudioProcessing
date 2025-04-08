import numpy as np
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
from viewbox_handler import GeneralPlotWidget


class FftHandler:
    def __init__(self, plot_widget: GeneralPlotWidget, sample_rate: float):
        self.plot_widget = plot_widget  # Keep reference to plot widget to

        self.sample_rate = sample_rate  # Sample rate in Hz

        # Empty active signal, gets added to when data begins coming in
        self.sample_data = np.array([], dtype=np.float32)

        # FFT data of given sample
        self.fft_freqs =
        self.frequency_data = np.zeros(100)

        # TODO: Implement generation of time axis data
        # self.x_time_axis = self.x_time = np.linspace(0, float(self.num_samples) / self.sample_rate, self.num_samples)






##### Test functions #####
def read_wav_to_np_array(wav_file: str):
    wav_data = read(wav_file)
    sample_rate = float(wav_data[0])
    samples = np.array(wav_data[1], dtype=np.float32)
    return sample_rate, samples

def test_data_gen():
    wav_file_name = "/home/caponed/Desktop/Projects/AudioProcessingGui/fft_generation/sine_wave.wav"

    sample_rate, sample_data = read_wav_to_np_array(wav_file_name)
    print(f"Max {np.max(sample_data)}")
    print(f"sample_rate: {sample_rate}")
    print(f"Len Samples: {len(sample_data)}")
    return sample_rate, sample_data

if __name__ == "__main__":
    wav_file_name = "/home/caponed/Desktop/Projects/AudioProcessingGui/fft_generation/sine_wave.wav"

    sample_rate, sample_data = read_wav_to_np_array(wav_file_name)
    print(f"sample_rate: {sample_rate}")
    print(f"Len Samples: {len(sample_data)}")

    fft_handler = FftHandler()