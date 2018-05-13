from rtlsdr import RtlSdr
import numpy as np
import scipy.signal as signal

import matplotlib
matplotlib.use('Agg')  # necessary for headless mode
# see http://stackoverflow.com/a/3054314/3524528
import matplotlib.pyplot as plt


def GetSample(F_station, F_offset, Fs, N):
	"""
	Genera una muestra de radio FM:
	
	Frecuencia de la Estacion:	F_station
	
	Frecuencia de muestreo: 	Fs
	
	Cantidad de muestras: 		N
	"""

	sdr = RtlSdr()

	Fc = F_station - F_offset  # Frecuencia del centro de captura
	
	# Se configura los parametros
	sdr.sample_rate = Fs
	sdr.center_freq = Fc
	sdr.gain = 'auto'
	# Lee las N muestras
	samples = sdr.read_samples(N)
	# Limpiar el dispositivo SDR
	sdr.close()  
	del(sdr)

	return samples