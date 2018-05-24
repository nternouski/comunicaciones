# -*- coding: utf-8 -*-
from utils import *
import sys
import sounddevice as sd

FILE_CAPTURE = "FMcapture.npy"
FILE_SOUND = "soundFM.wav"

f_station = int(105.3e6)    # Frecuencia de radio
f_offset = 250000	        # Desplazamiento para capturar
fs = int(1140000)           # Frecuencia de muestreo
N = int(8192000)            # Numero de muestras

print("El parametro ingresado es: ", sys.argv[1])
if int(sys.argv[1]) == 0:
    samples = GetSample(f_station, f_offset, fs, N, 40)
    np.save(FILE_CAPTURE, samples)
elif int(sys.argv[1]) == 1:
    samples = np.load(FILE_CAPTURE)

# Convierte las muestras en numpy array
xc = np.array(samples).astype("complex64")

x_b = ToBaseBand(xc, f_offset, fs)

x_filter, fs_y = FilterAndDownSample(x_b, fs)

yd = Demodulation(x_filter, fs_y)

DEP(yd, "yd DEP", "yd_DEP.pdf", fs_y)

yd = FilterPreEmphasis(f_offset, fs_y, yd)

SaveToAudioFile(yd, FILE_SOUND, fs_y)

audio_freq = 44100.0
dec_audio = int(fs / audio_freq)
fs_audio = fs / dec_audio
sound = decimate(yd, dec_audio)
print("Frec audio audio_freq: ", audio_freq)
print("Frec audio dec_audio: ", dec_audio)
print("Frec audio fs_audio: ", fs_audio)
print("Frec audio fs: ", fs)
print("Frec audio el reproduc: ", int(fs_audio/5))
sd.default.samplerate = int(fs_audio/5)
sd.play(sound)
sd.wait()
