@echo off
title Build - Asistencia Profesores (.exe)
echo ============================================================
echo   GENERANDO EJECUTABLE - Gestion de Asistencia Academica
echo ============================================================
echo.

:: 1. Comprobar si Python está instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Descarga Python desde https://www.python.org/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)

:: 2. Crear entorno virtual si no existe
if not exist .venv (
    echo [1/4] Creando entorno virtual ^(.venv^)...
    python -m venv .venv
) else (
    echo [1/4] Entorno virtual ya existe.
)

:: 3. Activar entorno virtual
echo [2/4] Activando entorno virtual...
call .venv\Scripts\activate

:: 4. Instalar dependencias + PyInstaller
echo [3/4] Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

:: 5. Ejecutar PyInstaller con el .spec
echo [4/4] Empaquetando la aplicacion con PyInstaller...
echo Esto puede tardar varios minutos, por favor espere...
echo.
pyinstaller --clean --noconfirm AsistenciaProfesores.spec

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] La compilacion fallo. Revisa los mensajes de error arriba.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   COMPILACION EXITOSA
echo ============================================================
echo.
echo El ejecutable se encuentra en:
echo   dist\AsistenciaProfesores\AsistenciaProfesores.exe
echo.
echo Para distribuir la aplicacion, copia TODA la carpeta
echo "dist\AsistenciaProfesores" al equipo destino.
echo.
echo La primera vez que se ejecute, se creara automaticamente
echo la base de datos con datos de ejemplo.
echo ============================================================
pause
