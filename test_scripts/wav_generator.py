import numpy as np
import scipy.io.wavfile as wav

# Parameters
sample_rate = 44100  # Hz (samples per second)
duration = 2.0       # seconds
frequency = 440.0    # Hz (A4 note)

# Generate time values
t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

# Generate sine wave
amplitude = 1.0  # Max value for 16-bit PCM
sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)

# Convert to 16-bit PCM format
sine_wave = sine_wave.astype(np.float32)

# Write to WAV file
wav.write("../fft_generation/sine_wave.wav", sample_rate, sine_wave)