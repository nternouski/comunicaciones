#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from centerWidget import CenterWidget
from radio import Streaming
from threading import Thread

import time

MAX_FREC_FM = 108.9
MIN_FREC_FM = 88.0

class Window(QtGui.QMainWindow):

	DEFAULT_FREC_MHZ = 99.1

	def __init__(self, parent=None):
		super(Window, self).__init__(parent)

		self.resize(980, 520)
		self.setMinimumSize(QtCore.QSize(740, 300))
		self.setWindowTitle('Demodulador FM - Catedra E0311')
		self.center()

		self.__setMenuBar()
		self.statusBar = QtGui.QStatusBar()
		self.setStatusBar(self.statusBar)
		self.sThread = Thread(target=self.initStreaming, name='Inicialización y run Streaming')
		self.firstPlay = False
		
		# El cuerpo del demodulador
		self.centerWidget = CenterWidget(self, MIN_FREC_FM, MAX_FREC_FM)
		self.setCentralWidget(self.centerWidget)

		self.stationFM = int
		self.setStationFM(self.DEFAULT_FREC_MHZ * 1e6)
		self.volume = int(5)


	def __del__(self):
		if (self.firstPlay == False):
			del(self.streaming)


	def center(self):
		frameGm = self.frameGeometry()
		screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
		centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
		frameGm.moveCenter(centerPoint)
		self.move(frameGm.topLeft())


	def setStationFM(self, Hz):
		"""
		Setea la frecuencia de estación, unidades en Hz

		Parametros:
				Hz:	Frecuencia de estación FM
		"""
		self.stationFM = Hz


	def initStreaming(self):
		self.streaming = Streaming(self.stationFM)
		self.updateStatusBar(1)
		self.streaming.start()
		self.streaming.play()
		self.updateStatusBar(3)


	def updateStatusBar(self, typeStatus, gain=""):
		switcher = {
			1: "Init hilos y cargando Buffer...",
			2: "Cargando Buffer...",
			3: "Reproduciendo radio...",
			4: "Radio detenida.",
			5: "Limite maximo de volumen alcanzado.",
			6: "Limite minimo de volumen alcanzado.",
			7: "Volumen es: "
		}
		self.statusBar.showMessage(switcher.get(typeStatus, "") + str(gain))


	def pausePlayRadio(self):
		if (self.firstPlay == False):
			# Empieza la radio si es que se presiona play por primera vez
			self.updateStatusBar(0)
			self.sThread.start()
			self.firstPlay = True
		else:
			self.updateStatusBar(2)
			pause = self.streaming.pauseOrPlay(self.stationFM)
			if pause:
				self.updateStatusBar(4)
			else:
				self.updateStatusBar(3)


	def stopRadio(self):
		self.updateStatusBar(4)
		if (self.firstPlay == True):
			self.streaming.stop()
			self.sThread.join()


	def volumeUp(self):
		if (self.firstPlay == True):
			status, gain = self.streaming.changeGain(+1)
			if not status:
				self.updateStatusBar(6)
			else:
				self.updateStatusBar(7, gain)


	def volumeDown(self):
		if (self.firstPlay == True):
			status, gain = self.streaming.changeGain(-1)
			if not status:
				self.updateStatusBar(6)
			else:
				self.updateStatusBar(7, gain)


	def __setMenuBar(self):
		menuBar = self.menuBar()
		extractActionA = QtGui.QAction("&Acerca de", menuBar)
		extractActionA.setStatusTip(u'Ver información de la App')
		extractActionA.triggered.connect(self.__openAboutDialog)
		extractActionS = QtGui.QAction("&Salir", menuBar)
		extractActionS.setShortcut("Ctrl+Q")
		extractActionS.setStatusTip(u'Salir De la aplicación')
		extractActionS.triggered.connect(self.__closeApplication)

		menuBar.addMenu('&Archivo').addAction(extractActionS)
		menuBar.addMenu('&Mas Opciones').addAction(extractActionA)


	def __closeApplication(self):
		self.stopRadio()
		sys.exit()


	def __openAboutDialog(self):
		msg = QtGui.QMessageBox()
		msg.setIcon(QtGui.QMessageBox.Information)
		msg.setText("Demodulador FM")
		msg.setInformativeText(u"Autor: Nahuel Ternouski \n\nComunicaciones E0311\nAño 2018")
		msg.setWindowTitle("Autor")
		msg.setStandardButtons(QtGui.QMessageBox.Ok)
		msg.exec_()
