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
	N = int(2**20)				# Numero de muestras
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
		yd = FilterDeEmphasis(f_offset, fs_y, yd)
		sd = PlaySound(yd, fs_y)
		#sd.wait()
	# to stop streaming:
	await sdr.stop()

	# done
	sdr.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(streaming())
