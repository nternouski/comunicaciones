# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore


def setMenuBar(menuBar):
    __addMenuFile(menuBar)
    __addMenuAbout(menuBar)


def __addMenuAbout(menuBar):
    extractAction = QtGui.QAction("&Acerca de", menuBar)
    extractAction.setStatusTip(u'Ver información de la App')
    extractAction.triggered.connect(__openAboutDialog)

    menuBar.addMenu('&Mas Opciones').addAction(extractAction)


def __addMenuFile(menuBar):
    extractAction = QtGui.QAction("&Salir", menuBar)
    extractAction.setShortcut("Ctrl+Q")

    extractAction.setStatusTip(u'Salir De la aplicación')
    extractAction.triggered.connect(__close_application)

    menuBar.addMenu('&Archivo').addAction(extractAction)


def __close_application():
    sys.exit()


def __openAboutDialog():
    msg = QtGui.QMessageBox()
    msg.setIcon(QtGui.QMessageBox.Information)
    msg.setText("Demodulador FM")
    msg.setInformativeText(u"Autor: Nahuel Ternouski \n\nComunicaciones E0311\nAño 2018")
    msg.setWindowTitle("Autor")
    msg.setStandardButtons(QtGui.QMessageBox.Ok)
    msg.exec_()