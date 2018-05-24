#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from mainMenu import setMenuBar

SPACING = 50


class CenterWidget(QtGui.QWidget):

    def __init__(self, parent, minFm, maxFm):
        super(CenterWidget, self).__init__(parent)

        hLayout = QtGui.QHBoxLayout()

        self.sl = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.sl.setMinimum(minFm)
        self.sl.setMaximum(maxFm)
        self.sl.setValue(20)
        self.sl.setTickPosition(QtGui.QSlider.TicksBelow)
        self.sl.setTickInterval((maxFm - minFm)/20)

        self.spinbox = QtGui.QDoubleSpinBox()
        self.spinbox.setRange(minFm, maxFm)

        self.btnUp = QtGui.QPushButton("Subir")
        self.btnDown = QtGui.QPushButton("Bajar")

        self.sl.valueChanged[int].connect(self.update_spinbox)
        self.spinbox.valueChanged.connect(self.update_slider_position)
        self.btnUp.clicked.connect(lambda: self.addDecimal())
        self.btnDown.clicked.connect(lambda: self.subDecimal())

        hLayout.addSpacing(SPACING)
        hLayout.addWidget(self.sl)
        hLayout.addWidget(self.spinbox)
        hLayout.addWidget(self.btnUp)
        hLayout.addWidget(self.btnDown)
        hLayout.addSpacing(SPACING)

        gBox = QtGui.QGroupBox("FM en MHz")
        gBox.setLayout(hLayout)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(gBox)
        mainLayout.addStretch()

        self.setLayout(mainLayout)

    def update_spinbox(self, value):
        self.spinbox.setValue(float(value))

    def update_slider_position(self, value):
        self.sl.setSliderPosition(value)

    def addDecimal(self):
        self.spinbox.setValue(self.spinbox.value() + 0.1)
    
    def subDecimal(self):
        self.spinbox.setValue(self.spinbox.value() - 0.1)
