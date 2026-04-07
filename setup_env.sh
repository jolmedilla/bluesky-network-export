#!/bin/bash

echo "[*] Creando entorno virtual 'venv'..."
python3 -m venv venv
source venv/bin/activate

echo "[*] Instalando dependencias desde requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

echo "[*] Descargando modelo spaCy (en_core_web_sm)..."
python -m spacy download en_core_web_sm

echo "[✓] Entorno listo. Activa con: source venv/bin/activate"
