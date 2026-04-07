@echo off
echo [*] Creando entorno virtual 'venv'...
python -m venv venv

echo [*] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [*] Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

echo [*] Descargando modelo de spaCy...
python -m spacy download en_core_web_sm

echo [✓] Entorno listo. Para activarlo manualmente: venv\Scripts\activate
pause
