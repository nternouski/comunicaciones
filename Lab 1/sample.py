from utils import *


F_station = int(90.9e6)   	# Frecuencia de radio
F_offset = 250000         	# Desplazamiento para capturar
# We capture at an offset to avoid DC spike
Fs = int(1140000) 			# Frecuencia de muestreo
N = int(8192000)			# Numero de muestras

samples = GetSample(F_station, F_offset, Fs, N)

# Convierte las muestras en numpy array
x1 = np.array(samples).astype("complex64")

# To mix the data down, generate a digital complex exponential
# (with the same length as x1) with phase -F_offset/Fs
fc1 = np.exp(-1.0j * 2.0 * np.pi * (F_offset/Fs) * np.arange(len(x1)))
# Now, just multiply x1 and the digital complex expontential
x2 = x1 * fc1


# An FM broadcast signal has  a bandwidth of 200 kHz
f_bw = 200000
dec_rate = int(Fs / f_bw)
x4 = signal.decimate(x2, dec_rate)
# Calculate the new sampling rate
Fs_y = Fs/dec_rate


# Polar discriminator
y5 = x4[1:] * np.conj(x4[:-1])
x5 = np.angle(y5)

# The de-emphasis filter
# Given a signal 'x5' (in a numpy array) with sampling rate Fs_y
d = Fs_y * 75e-6   # Calculate the # of samples to hit the -3dB point
x = np.exp(-1/d)   # Calculate the decay between each sample
b = [1-x]          # Create the filter coefficients
a = [1, -x]
x6 = signal.lfilter(b, a, x5)

# Find a decimation rate to achieve audio sampling rate between 44-48 kHz
audio_freq = 44100.0
dec_audio = int(Fs_y/audio_freq)
Fs_audio = Fs_y / dec_audio

x7 = signal.decimate(x6, dec_audio)


# Scale audio to adjust volume
x7 *= 10000 / np.max(np.abs(x7))
# Save to file as 16-bit signed single-channel audio samples
x7.astype("int16").tofile("wbfm-mono.raw")


print(Fs_audio)
