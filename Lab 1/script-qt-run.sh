#!/bin/bash

cd qt
sudo python -m py_compile qt.py
sudo python -m py_compile radio.py
sudo python -m py_compile window.py
sudo python qt.pyc
