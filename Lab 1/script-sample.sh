#!/bin/bash

#####
#	Parametros:
# 		0 -> indica generar una muestra y guardarlo en un archivo
#		1 -> indica levantar un archivo previamente guardado y probar
#####
sudo python3 sample.py $1
# aplay soundFM.wav -r 47500 -f S16_LE -t wav -c 1
