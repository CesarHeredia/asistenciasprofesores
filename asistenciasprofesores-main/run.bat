@echo off
title Asistencia Profesores - Windows
echo ==========================================================
echo   CONFIGURANDO E INICIANDO ASISTENCIA PROFESORES (WINDOWS)
echo ==========================================================

:: 1. Comprobar si Python está instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python no esta instalado o no se encuentra en el PATH de Windows.
    echo Por favor, descarga e instala Python desde https://www.python.org/
    echo e IMPORTANTE: Asegúrate de marcar la casilla "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

:: 2. Crear entorno virtual si no existe
if not exist .venv (
    echo [1/4] Creando entorno virtual ^(.venv^)...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo AVISO: No se pudo crear el entorno virtual. Intentando instalar dependencias globalmente...
        pip install -r requirements.txt
        goto run_app
    )
) else (
    echo [1/4] Entorno virtual ^(.venv^) ya existente.
)

:: 3. Activar entorno virtual
echo [2/4] Activando entorno virtual ^(.venv^)...
call .venv\Scripts\activate

:: 4. Instalar dependencias
echo [3/4] Instalando/verificando dependencias desde requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt

:run_app
:: 5. Ejecutar la aplicación
echo [4/4] Iniciando la aplicacion...
python eel_main.py

if "%VIRTUAL_ENV%" neq "" (
    call deactivate
)
echo.
echo Aplicacion finalizada.
pause
