# Compilación del Ejecutable (.exe) para Windows (Nativo)

Esta aplicación ahora es un programa nativo de escritorio construido con **PyQt6**. 

Para crear el archivo ejecutable (`.exe`), asegúrate de realizar este proceso en un sistema operativo Windows para garantizar máxima compatibilidad.

## Pasos a seguir en Windows:

### 1. Clonar o copiar el proyecto
Asegúrate de tener esta carpeta (`asistenciasprofesores`) en tu máquina Windows.

### 2. Instalar Python
Si no lo tienes, instala Python desde python.org. Asegúrate de marcar **"Add Python to PATH"**.

### 3. Instalar dependencias
Abre una terminal (PowerShell o Símbolo del Sistema) en la carpeta del proyecto y ejecuta:
```bash
pip install -r requirements.txt
```
*(Esto instalará PyQt6 y PyInstaller)*

### 4. Generar el Ejecutable
A diferencia de las apps web, con PyQt6 el proceso es sumamente directo. Ejecuta el siguiente comando:

```bash
pyinstaller --noconsole --onefile main.py
```

**Explicación:**
- `--noconsole`: Oculta la ventana negra (consola) para que solo se vea tu interfaz gráfica.
- `--onefile`: Empaqueta todas las librerías de PyQt6 y tu código en un único archivo `.exe`.

**Importante: Empaquetar los estilos**
Para que los estilos (`styles.qss`) funcionen en el ejecutable final, asegúrate de que el archivo `.qss` esté junto al `.exe`, O usa este comando para incluirlo dentro del `.exe`:
```bash
pyinstaller --noconsole --onefile --add-data "styles.qss;." main.py
```

### 5. Resultado
Cuando termine el proceso, verás una carpeta llamada `dist`. Dentro estará tu `main.exe`. Puedes renombrarlo a `AsistenciasApp.exe`. ¡Listo para usar!
