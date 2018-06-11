#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Modulo gráfico del laboratorio

author: Nahuel Ternouski
"""

import sys
from PyQt4 import QtGui
from window import Window

def main():
	app = QtGui.QApplication(sys.argv)
	mainWindow = Window()
	mainWindow.show()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()