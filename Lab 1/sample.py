# -*- coding: utf-8 -*-
from utils import *
import sys

FILE_CAPTURE = "FMcapture.npy"
FILE_SOUND = "soundFM.wav"

def main():
	f_station = int(105.3e6)	# Frecuencia de radio
	f_offset = 250000	        # Desplazamiento para capturar
	fs = int(1140000)           # Frecuencia de muestreo
	N = int(2**20)				# Numero de muestras

	print("El parametro ingresado es: ", sys.argv[1])
	if int(sys.argv[1]) == 0:
		print("\t Se tomaran muestras del doungle..\n")
		samples = GetSample(f_station, f_offset, fs, N, 40)
		np.save(FILE_CAPTURE, samples)
	elif int(sys.argv[1]) == 1:
		print("\t Se leerá del archivo ", FILE_CAPTURE, "..\n")
		samples = np.load(FILE_CAPTURE)

	print(" AHORAAA \n")
	# Convierte las muestras en numpy array
	xc = np.array(samples).astype("complex64")
	x_b = ToBaseBand(xc, f_offset, fs)
	x_filter, fs_y = FilterAndDownSample(x_b, fs)
	yd = Demodulation(x_filter, fs_y)
	DEP(yd, "yd DEP", "yd_DEP.pdf", fs_y)
	yd = FilterPreEmphasis(f_offset, fs_y, yd)
	SaveToAudioFile(yd, FILE_SOUND, fs_y)
	PlaySound(yd, fs_y)

main()
