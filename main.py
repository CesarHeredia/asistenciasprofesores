import sys
# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtSql import QSqlDatabase
from ui_main import MainWindow

def main():
    # Inicializa la aplicación Qt
    app = QApplication(sys.argv)
    
    # Conectar a la base de datos SQLite
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('gestion_academica.db')
    if not db.open():
        QMessageBox.critical(None, "Error de Base de Datos", 
                             f"No se pudo abrir la base de datos: {db.lastError().text()}")
        sys.exit(1)
        
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
