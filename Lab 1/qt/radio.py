# -*- coding: utf-8 -*-

import sys
import time
import rtlsdr
import numpy as np
from scipy.signal import remez, lfilter, decimate, freqz
import sounddevice as sd
from threading import Semaphore, Thread, Lock
import Queue as queue

FS = 1140000			# Frecuencia de muestreo
# FS = 2.04e6
N_SAMPLE = 332800		# Cantidad de muestras
F_BW = 180e3
AUDIO_FREC = 44100.0
# AUDIO_FREC = 22050.0
N_TRAPS = 10
TIME_BUFFER = 7 		# En segundos
FRAMES = 3 				# Frames contatenado por muestra

class Streaming:
	def __init__(self, stationMHz):
		self.sdr = rtlsdr.RtlSdr()
		
		self.f_offset = 250000					# Desplazamiento para capturar
		self.f_station = stationMHz 			# Frecuencia de radio

		self.dec_rate = int(FS / F_BW)
		self.fs_y = FS / (self.dec_rate)
		self.coef = remez(N_TRAPS, [0, F_BW, F_BW*1.4, FS/2], [1, 0], Hz=FS)
		self.expShift = (-1.0j * 2.0 * np.pi * self.f_offset/FS)
		
		# Se configura los parametros
		self.dec_audio = int(self.fs_y / AUDIO_FREC)
		self.stream = sd.OutputStream(device='default', samplerate=int(self.fs_y / self.dec_audio), channels=1, dtype='float32')
		self.beginListening = 0

		self.soundQueue = queue.Queue()
		self.samplesQueue = queue.Queue()


	def __del__(self):
		print("Destructor del Streaming")
		self.sdr.close()
		del(self.sdr)

	
	def start(self):
		self.semaphorePlay = Semaphore(1)
		self.lockCapture = Lock()
		self.lockProcessing = Lock()
		self.lockListen = Lock()
		self.stopStreaming = False
		self.pauseStreaming = False

		self.setupSDR(FS, self.f_station - self.f_offset)

		self.cThread = Thread(target=self.captureSamples, name='Capturadora de muestras')
		self.pThread = Thread(target=self.processingSamples, name='Procesamiento de muestras')
		self.lThread = Thread(target=self.listen, name='Escucha')
		# Adquiero el semaforo antes de que empiece los hilos,
		# para que demodListen tenga datos para procesar
		self.semaphorePlay.acquire()
		self.stream.start()
		self.cThread.start()
		self.pThread.start()
		self.lThread.start()


	def play(self):
		"""
		Se llama solo una vez
		"""
		time.sleep(TIME_BUFFER)
		print("Reproduciendo..")
		self.semaphorePlay.release()


	def stop(self):
		self.stopStreaming = True
		if (self.pauseStreaming == True):
			self.semaphorePlay.release()
			self.lockCapture.release()
			self.lockProcessing.release()
			self.lockListen.release()
		self.cThread.join()
		self.pThread.join()
		self.lThread.join()
		print("Stop Streaming")
	
	
	def pauseOrPlay(self, station):
		"""
		Pausa o reanuda, no llamarlo sin antes hacer start()

		Devuelve: False si se reanuda, o True si se pausó
		"""
		if (self.pauseStreaming == True):
			# Si esta pausado lo saco de la pausa
			# y despierto los hilos con la variable condición
			self.pauseStreaming = False
			self.setupSDR(FS, station - self.f_offset)
			self.lockCapture.release()
			self.lockProcessing.release()
			self.lockListen.release()
			self.play()
			return False
		else:
			self.pauseStreaming = True
			print("Pause Streaming")
			return True


	def setupSDR(self, fs, fc, gain='auto'):
		"""
		Parametros:
			fs: 	Frecuencia de muestreo a captar
			fc: 	Frecuencia del centro de captura
			gain:	Ganancia
		"""
		self.sdr.sample_rate = fs
		self.sdr.center_freq = fc
		self.sdr.gain = gain


	def changeStation(self, MHz):
		self.f_station = MHz


	def captureSamples(self):
		while not (self.stopStreaming):
			frame = np.array(self.sdr.packed_bytes_to_iq(self.sdr.read_bytes(2*N_SAMPLE)))
			for i in range(FRAMES-1):
				frame = np.concatenate((frame, np.array(self.sdr.packed_bytes_to_iq(self.sdr.read_bytes(2*N_SAMPLE)))))
			self.samplesQueue.put(frame)
			if self.pauseStreaming:
				self.lockCapture.acquire()


	def processingSamples(self):
		# Proceso las muestras
		while not (self.stopStreaming):
			xc = self.samplesQueue.get().astype("complex64")
			# Paso a banda base y filtro
			x_filter = lfilter(self.coef, 1.0, xc * np.exp(self.expShift * np.arange(len(xc))))
			x_downsample = x_filter[0::self.dec_rate]
			# Demodulo
			yd_demod = np.angle(x_downsample[1:] * np.conj(x_downsample[:-1]))
			# Deemfasis
			#x_deemfasis = np.exp(-1/(self.fs_y * 75e-6))
			#yd = lfilter([1-x_deemfasis], [1, -x_deemfasis], yd_demod)
			# Diezmo para que pueda reproducir la placa de sonido
			self.soundQueue.put(decimate(yd_demod, self.dec_audio))
			if self.pauseStreaming:
				self.lockProcessing.acquire()


	def listen(self):
		self.semaphorePlay.acquire()
		while not (self.stopStreaming):
			# Cambio de float64 a 32 para stream.write
			self.stream.write(self.soundQueue.get().astype('float32'))
			if self.pauseStreaming:
				self.lockListen.acquire()
				self.semaphorePlay.acquire()


if __name__ == '__main__':
	s = Streaming(99.1e6)
	s.start()
	s.play()
	time.sleep(14)
	s.stop()
