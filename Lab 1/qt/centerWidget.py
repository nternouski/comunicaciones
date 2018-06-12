#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore

SPACING = 50

class CenterWidget(QtGui.QWidget):

	def __init__(self, parent, minFm, maxFm):
		super(CenterWidget, self).__init__(parent)

		self.parent = parent
		hLayoutUp = QtGui.QHBoxLayout()
		hLayoutDown = QtGui.QHBoxLayout()

		self.sl = QtGui.QSlider(QtCore.Qt.Horizontal)
		self.sl.setMinimum(minFm)
		self.sl.setMaximum(maxFm)
		self.sl.setValue(20)
		self.sl.setTickPosition(QtGui.QSlider.TicksBelow)
		self.sl.setTickInterval((maxFm - minFm)/20)
		self.spinbox = QtGui.QDoubleSpinBox()
		self.spinbox.setRange(minFm, maxFm)
		self.btnFMUp = QtGui.QPushButton("Subir (+100k)")
		self.btnFMDown = QtGui.QPushButton("Bajar (-100k)")
		self.sl.valueChanged[int].connect(self.update_spinbox)
		self.spinbox.valueChanged.connect(self.update_slider_position)
		self.btnFMUp.clicked.connect(lambda: self.addSpinboxDecimal())
		self.btnFMDown.clicked.connect(lambda: self.subSpinboxDecimal())

		self.update_slider_position(self.parent.DEFAULT_FREC_MHZ)
		self.update_spinbox(self.parent.DEFAULT_FREC_MHZ)

		hLayoutUp.addSpacing(SPACING)
		hLayoutUp.addWidget(self.sl)
		hLayoutUp.addWidget(self.spinbox)
		hLayoutUp.addWidget(self.btnFMUp)
		hLayoutUp.addWidget(self.btnFMDown)
		hLayoutUp.addSpacing(SPACING)

		self.btnVolumeUp = QtGui.QPushButton("Subir Volumen")
		self.btnVolumeDown = QtGui.QPushButton("Bajar Volumen")
		self.btnPlay = QtGui.QPushButton("Play")
		self.btnPausa = QtGui.QPushButton("Pausa")
		self.btnPlay.clicked.connect(lambda: self.parent.pausePlayRadio())
		self.btnPausa.clicked.connect(lambda: self.parent.pausePlayRadio())
		hLayoutDown.addSpacing(SPACING)
		hLayoutDown.addSpacing(SPACING)
		hLayoutDown.addWidget(self.btnPlay)
		hLayoutDown.addSpacing(SPACING)
		hLayoutDown.addWidget(self.btnPausa)
		hLayoutDown.addSpacing(SPACING)
		hLayoutDown.addSpacing(SPACING)
		# hLayoutDown.addSpacing(SPACING)
		# hLayoutDown.addWidget(self.btnVolumeUp)
		# hLayoutDown.addSpacing(SPACING)
		# hLayoutDown.addWidget(self.btnVolumeDown)
		# hLayoutDown.addSpacing(SPACING)
		# hLayoutDown.addSpacing(SPACING)

		gBoxFM = QtGui.QGroupBox("FM en MHz")
		gBoxFM.setLayout(hLayoutUp)
		gBoxPlayVolume = QtGui.QGroupBox("Play/Pausa - Volumen")
		gBoxPlayVolume.setLayout(hLayoutDown)

		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(gBoxPlayVolume)
		mainLayout.addWidget(gBoxFM)
		mainLayout.addStretch()

		self.setLayout(mainLayout)


	def update_spinbox(self, value):
		self.spinbox.setValue(float(value))
		self.parent.setStationFM(value*1e6)


	def update_slider_position(self, value):
		self.sl.setSliderPosition(value)
		self.parent.setStationFM(value*1e6)


	def addSpinboxDecimal(self):
		self.spinbox.setValue(self.spinbox.value() + 0.1)
		self.parent.setStationFM(self.spinbox.value()*1e6)


	def subSpinboxDecimal(self):
		self.spinbox.setValue(self.spinbox.value() - 0.1)
		self.parent.setStationFM(self.spinbox.value()*1e6)
