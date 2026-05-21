import sys
from PyQt6.QtWidgets import QApplication
from ui_main import MainWindow

def main():
    # Inicializa la aplicación Qt
    app = QApplication(sys.argv)
    
    # Intentamos establecer una fuente limpia por defecto
    font = app.font()
    font.setFamily("Segoe UI") # Ideal para Windows
    font.setPointSize(10)
    app.setFont(font)
    
    # Crea y muestra la ventana principal
    window = MainWindow()
    window.show()
    
    # Inicia el bucle de eventos
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
