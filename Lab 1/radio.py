import asyncio
from rtlsdr import RtlSdr
from utils import *
import sounddevice as sd
import numpy as np

FILE_SOUND = "soundFM.wav"

async def streaming():
	sdr = RtlSdr()

	f_station = int(105.3e6) 	# Frecuencia de radio
	f_offset = 250000	       	# Desplazamiento para capturar
	fs = int(1140000) 			# Frecuencia de muestreo
	N = int(8192000)			# Numero de muestras
	fc = f_station - f_offset  # Frecuencia del centro de captura
	# Se configura los parametros
	sdr.sample_rate = fs
	sdr.center_freq = fc
	sdr.gain = 'auto'

	async for samples in sdr.stream():
		xc = np.array(samples).astype("complex64")
		x_baseband = ToBaseBand(xc, f_offset, fs)
		x_filter, fs_y = FilterAndDownSample(x_baseband, fs)
		yd = Demodulation(x_filter, fs_y)
		yd = FilterPreEmphasis(f_offset, fs_y, yd)
		audio_freq = 44100.0
		dec_audio = int(fs / audio_freq)
		fs_audio = fs / dec_audio
		sound = decimate(yd, dec_audio)
		# print("Frec audio audio_freq: ", audio_freq)
		# print("Frec audio dec_audio: ", dec_audio)
		# print("Frec audio fs_audio: ", fs_audio)
		# print("Frec audio fs: ", fs)
		# print("Frec audio el reproduc: ", int(fs_audio/5))
		sd.default.samplerate = int(fs_audio/4.5)
		sd.play(sound)
		sd.wait()
	# to stop streaming:
	await sdr.stop()

	# done
	sdr.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(streaming())
