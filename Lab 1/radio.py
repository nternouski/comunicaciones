# -*- coding: utf-8 -*-

import sys

import time
import rtlsdr
import numpy as np
from scipy.signal import hilbert, remez, lfilter, decimate, freqz
from scipy.io import wavfile
import sounddevice as sd
from threading import Semaphore, Thread

F_BW = 180e3
N_TRAPS = 50
AUDIO_FREC = 44100.0

class Streaming:
	def __init__(self):
		self.sdr = rtlsdr.RtlSdr()
		self.semaphoreNewSample = Semaphore(1)
		self.semaphorePlay = Semaphore(1)
		self.semaphoreAccessSample = Semaphore(1)

		self.fs = int(1140000)					# Frecuencia de muestreo
		self.f_offset = 250000					# Desplazamiento para capturar
		#self.N = int(2**20)						# Numero de muestras
		self.N = int(332800)
		self.f_station = int(99.1e6) 			# Frecuencia de radio
		fc = self.f_station - self.f_offset		# Frecuencia del centro de captura
		
		self.changeStation = False
		self.samples = None
		self.sound = None

		self.dec_rate = int(self.fs / F_BW)
		self.fs_y = self.fs / (self.dec_rate)
		self.coef = remez(N_TRAPS, [0, F_BW, F_BW*1.4, self.fs/2], [1, 0], Hz=self.fs)
		# Se configura los parametros
		self.sdr.sample_rate = self.fs
		self.sdr.center_freq = fc
		self.sdr.gain = 'auto'

		self.sd = sd
		self.dec_audio = int(self.fs_y / AUDIO_FREC)
		self.sd.samplerate = int(self.fs_y / self.dec_audio) # fs_audio
		self.stream = sd.OutputStream(device='default', samplerate=self.sd.samplerate, channels=1, dtype='float32')
		self.stream.start()


	def start(self):
		cs = Thread(target=self.captureSamples, name='Capturadora de muestras')
		p = Thread(target=self.processingSample, name='Procesamiento de muestras')
		l = Thread(target=self.listen, name='Escucha')
		# Adquiero el semaforo antes de que empiece los hilos,
		# para que demodListen tenga datos para procesar
		self.semaphoreNewSample.acquire()
		self.semaphorePlay.acquire()
		cs.start()
		p.start()
		l.start()
		time.sleep(12)
		self.changeStation = True


	def stop(self):
		self.sdr.close()
		del(self.sdr)


	def captureSamples(self):
		while not (self.changeStation):
			start_time = time.time() ###################################
			self.setSampleAtomically(self.sdr.read_samples(self.N))
			self.semaphoreNewSample.release()
			finish_time = time.time() - start_time #####################
			# print("-- T captura:", finish_time)
		# Por si el demodListen se quedo esperando por otra muestra y
		# este no lo libera
		print("Sali While capture")
		self.semaphoreNewSample.release()
		print("-Salgo del capturar")


	def processingSample(self):
		while not (self.changeStation):
			self.semaphoreNewSample.acquire()
			start_time = time.time() ###################################
			xc = np.array(self.getSampleAtomically()).astype("complex64")
			# Paso a banda base
			x_baseband = xc * np.exp((-1.0j * 2.0 * np.pi * self.f_offset/self.fs) * np.arange(len(xc)))
			# Filtro y downsample
			x_filter = lfilter(self.coef, 1.0, x_baseband)
			x_downsample = x_filter[0::self.dec_rate]
			# Demodulo
			yd_demod = np.angle(x_downsample[1:] * np.conj(x_downsample[:-1]))
			# Deemfasis
			x_deemfasis = np.exp(-1/(self.fs_y * 75e-6))
			yd = lfilter([1-x_deemfasis], [1, -x_deemfasis], yd_demod)
			# Diezmo para que pueda reproducir la placa de sonido
			self.sound = decimate(yd, self.dec_audio)

			finish_time = time.time() - start_time #####################
			# print("-- T procesando:", finish_time)
			self.semaphorePlay.release()
		# Idem para el listener que quedo esperando para mas muestras
		self.semaphorePlay.release()
		print("-Salgo del Processing")

	def listen(self):
		while not (self.changeStation):
			self.semaphorePlay.acquire()
			start_time = time.time() ##################################			
			# self.sd.play(self.sound)
			# self.sd.wait()
			self.stream.write(self.sound.astype('float32'))
			finish_time = time.time() - start_time #####################
			# print("-- T escuchando:", finish_time)
		print("-Salgo del Listen")


	def getSampleAtomically(self):
		self.semaphoreAccessSample.acquire()
		aux = self.samples
		self.semaphoreAccessSample.release()
		return aux


	def setSampleAtomically(self, data):
		self.semaphoreAccessSample.acquire()
		self.samples = data
		self.semaphoreAccessSample.release()


if __name__ == '__main__':
	s = Streaming()
	s.start()
	s.stop()
