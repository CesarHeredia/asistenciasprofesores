#!/usr/bin/env bash
# ============================================================
#  Build - Asistencia Profesores (ejecutable Linux)
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "  GENERANDO EJECUTABLE - Gestión de Asistencia Académica"
echo "============================================================"
echo ""

# 1. Comprobar Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python3 no está instalado."
    echo "Instálalo con: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# 2. Crear entorno virtual
if [ ! -d ".venv" ]; then
    echo "[1/4] Creando entorno virtual (.venv)..."
    python3 -m venv .venv
else
    echo "[1/4] Entorno virtual ya existe."
fi

# 3. Activar entorno virtual
echo "[2/4] Activando entorno virtual..."
source .venv/bin/activate

# 4. Instalar dependencias
echo "[3/4] Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# 5. Compilar
echo "[4/4] Empaquetando la aplicación con PyInstaller..."
echo "Esto puede tardar varios minutos, por favor espere..."
echo ""
pyinstaller --clean --noconfirm AsistenciaProfesores.spec

echo ""
echo "============================================================"
echo "  COMPILACIÓN EXITOSA"
echo "============================================================"
echo ""
echo "El ejecutable se encuentra en:"
echo "  dist/AsistenciaProfesores/AsistenciaProfesores"
echo ""
echo "Para ejecutar:"
echo "  ./dist/AsistenciaProfesores/AsistenciaProfesores"
echo ""
echo "Para distribuir, copia TODA la carpeta"
echo "  dist/AsistenciaProfesores/"
echo "============================================================"
