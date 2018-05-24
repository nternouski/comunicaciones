#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from centerWidget import CenterWidget
from mainMenu import setMenuBar

MAX_FREC_FM = 108.9
MIN_FREC_FM = 88.0

class Window(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.resize(1280, 720)
        self.setMinimumSize(QtCore.QSize(640,400));
        self.setWindowTitle('Demodulador FM - Catedra E0311')
        self.center()
        self.statusBar()
        setMenuBar(self.menuBar())

        # El cuerpo del demodulador
        self.centerWidget = CenterWidget(self, MIN_FREC_FM, MAX_FREC_FM)
        self.setCentralWidget(self.centerWidget)

        self.show()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(
            QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def close_application(self):
        sys.exit()
