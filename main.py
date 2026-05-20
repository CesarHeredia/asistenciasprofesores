import eel
import os
import sys

# Definimos la función que React llamará
@eel.expose
def export_data():
    print("Se ha solicitado exportar los datos desde React")
    return "Datos exportados exitosamente por Python!"

def start_app():
    # Buscamos la ruta base de la aplicación
    if getattr(sys, 'frozen', False):
        # Si estamos en el .exe compilado por PyInstaller
        base_path = sys._MEIPASS
        web_dir = os.path.join(base_path, 'front', 'dist')
    else:
        # En modo desarrollo
        web_dir = os.path.join(os.path.dirname(__file__), 'front', 'dist')
    
    if not os.path.exists(web_dir):
        print(f"Error: No se encontró el directorio '{web_dir}'.")
        print("Asegúrate de ejecutar 'npm run build' en la carpeta front primero.")
        return

    # Inicializamos Eel en la carpeta construida de React
    eel.init(web_dir)

    try:
        # Iniciamos la app abriendo index.html en una ventana local (Edge/Chrome)
        eel.start('index.html', size=(1200, 800), title="Sistema de Gestión de Asistencias USM")
    except (SystemExit, MemoryError, KeyboardInterrupt):
        # Manejar cierre de la app
        pass

if __name__ == '__main__':
    start_app()
