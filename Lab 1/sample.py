# -*- coding: utf-8 -*-

from utils import *
import sys
import time

FILE_CAPTURE = "FMcapture.npy"
FILE_SOUND = "soundFM.wav"

def main():
	f_station = int(99.1e6)	# Frecuencia de radio
	f_offset = 250000	        # Desplazamiento para capturar
	fs = int(1140000)           # Frecuencia de muestreo
	N = int(2**22)				# Numero de muestras
	# N = int(332800)			# Numero de muestras

	if not (len(sys.argv) == 2): 
		print("Ingrese un numero: 0 o 1..")
		sys.exit(1)

	print("El parametro ingresado es: ", sys.argv[1])
	if int(sys.argv[1]) == 0:
		print("\t Se tomaran muestras del doungle..\n")
		samples = GetSample(f_station, f_offset, fs, N, 'auto')
		np.save(FILE_CAPTURE, samples)
	elif int(sys.argv[1]) == 1:
		print("\t Se leerá del archivo ", FILE_CAPTURE, "..\n")
		samples = np.load(FILE_CAPTURE)

	print("- Se mide el tiempo para N =", N, '(%.3f' %(N/fs), "s). \n")
	start_time = time.time()
	# Convierte las muestras en numpy array
	xc = np.array(samples).astype("complex64")
	x_b = ToBaseBand(xc, f_offset, fs)
	DEP(x_b, "xb DEP", "xb_DEP.pdf", fs)
	x_filter, fs_y = FilterAndDownSample(x_b, fs)
	yd = Demodulation(x_filter, fs_y)
	DEP(yd, "yd DEP", "yd_DEP.pdf", fs_y, True)
	yd = FilterDeEmphasis(fs_y, yd)
	finish_time = time.time() - start_time
	print("-- Tiempo de computo:", '%.3f' %finish_time, "seg --")
	SaveToAudioFile(yd, FILE_SOUND, fs_y)
	PlaySound(yd, fs_y)

main()
