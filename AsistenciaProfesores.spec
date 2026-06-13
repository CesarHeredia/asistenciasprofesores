# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller .spec para Gestión de Asistencia Académica.
Genera un ejecutable de escritorio portable (--onedir).

Uso:
    pyinstaller AsistenciaProfesores.spec
"""
import os

# Ruta raíz del proyecto (donde está este .spec)
# SPECPATH puede fallar con rutas que contienen espacios, usamos abspath directo
ROOT = SPECPATH

block_cipher = None

a = Analysis(
    [os.path.join(ROOT, 'eel_main.py')],
    pathex=[ROOT],
    binaries=[],
    datas=[
        # ── Archivos de datos que se empaquetan dentro del bundle ──
        # Frontend completo (HTML, CSS, JS, imágenes)
        (os.path.join(ROOT, 'front'), 'front'),
        # Módulo backend (.py + base de datos real con los datos actuales)
        (os.path.join(ROOT, 'backend', 'backend.py'), os.path.join('backend')),
        (os.path.join(ROOT, 'backend', 'db', 'gestion_academica.db'), os.path.join('backend', 'db')),
        (os.path.join(ROOT, 'backend', 'db', 'Database'), os.path.join('backend', 'db')),
    ],
    hiddenimports=[
        # Eel y sus dependencias internas
        'eel',
        'bottle',
        'bottle_websocket',
        'gevent',
        'geventwebsocket',
        'geventwebsocket.handler',
        # PyWebView y backend Qt
        'webview',
        'webview.platforms.qt',
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebEngineCore',
        'PyQt6.QtNetwork',
        'qtpy',
        # Backend del proyecto
        'backend',
        'backend.backend',
        # Stdlib
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
    ],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AsistenciaProfesores',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                  # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Usar .ico si existe (Windows), sino .png (Linux)
    icon=os.path.join(ROOT, 'front', 'scr', 'image', 'usmlgoretina-1.ico')
         if os.path.exists(os.path.join(ROOT, 'front', 'scr', 'image', 'usmlgoretina-1.ico'))
         else os.path.join(ROOT, 'front', 'scr', 'image', 'usmlgoretina-1.png'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AsistenciaProfesores',
)
