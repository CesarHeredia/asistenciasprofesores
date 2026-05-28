#!/bin/bash

# Evitar fallos inmediatos si hay algún error (opcional, pero controlado para permitir fallback)
set -e

echo "=========================================================="
echo "  CONFIGURANDO E INICIANDO ASISTENCIA PROFESORES (LINUX)"
echo "=========================================================="

# 1. Comprobar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado. Por favor, instálalo antes de continuar."
    exit 1
fi

# 2. Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "[1/4] Creando entorno virtual (.venv)..."
    if ! python3 -m venv .venv 2>/dev/null; then
        echo "--------------------------------------------------------"
        echo "AVISO: No se pudo crear el entorno virtual automáticamente."
        echo "En sistemas basados en Debian/Ubuntu (como Ubuntu/Mint), puedes necesitar instalar:"
        echo "  sudo apt update && sudo apt install python3-venv"
        echo "--------------------------------------------------------"
        echo "Intentando instalar dependencias a nivel de usuario como alternativa..."
        pip3 install --user -r requirements.txt --break-system-packages 2>/dev/null || pip3 install --user -r requirements.txt
        echo "[4/4] Iniciando la aplicación..."
        python3 eel_main.py
        exit 0
    fi
else
    echo "[1/4] Entorno virtual (.venv) ya existente."
fi

# 3. Activar entorno virtual
echo "[2/4] Activando entorno virtual (.venv)..."
source .venv/bin/activate

# 4. Actualizar pip e instalar dependencias
echo "[3/4] Instalando/verificando dependencias desde requirements.txt..."
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Ejecutar la aplicación Eel
echo "[4/4] Iniciando la aplicación..."
python eel_main.py

# Desactivar venv al finalizar
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi
