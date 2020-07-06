#!/bin/bash

# Upgrade youtube-dl repeatedly because it is updated frequently.
pip3 install --upgrade youtube-dl

cd /app
python3 -u main.py
