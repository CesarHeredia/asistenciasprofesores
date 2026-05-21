from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QComboBox, QTabWidget, 
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit)
from PyQt6.QtCore import Qt
from datetime import datetime
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestión de Asistencias USM")
        self.resize(1200, 800)
        
        # Cargar estilos
        self.load_styles()
        self.setup_ui()

    def load_styles(self):
        try:
            style_path = os.path.join(os.path.dirname(__file__), "styles.qss")
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"No se pudo cargar el archivo de estilos: {e}")

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. Header ---
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(40, 20, 40, 20)

        # Header Izquierda
        left_header_layout = QVBoxLayout()
        title_label = QLabel("Sistema de Gestión de Asistencias USM")
        title_label.setObjectName("AppTitle")
        
        # Fecha en español
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        now = datetime.now()
        date_str = f"{dias[now.weekday()]}, {now.day} de {meses[now.month-1]} {now.year}"
        
        date_label = QLabel(date_str)
        date_label.setObjectName("AppDate")
        left_header_layout.addWidget(title_label)
        left_header_layout.addWidget(date_label)

        # Header Derecha
        right_header_layout = QHBoxLayout()
        date_combo = QComboBox()
        date_combo.addItems(["Hoy", "Ayer", "Esta semana"])
        
        export_btn = QPushButton("Exportar")
        
        right_header_layout.addWidget(date_combo)
        right_header_layout.addWidget(export_btn)
        right_header_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        header_layout.addLayout(left_header_layout)
        header_layout.addLayout(right_header_layout)
        main_layout.addWidget(header_frame)

        # --- 2. Contenedor Principal (Cuerpo) ---
        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(40, 30, 40, 30)
        
        # Pestañas
        self.tabs = QTabWidget()
        self.tab_asistencias = QWidget()
        self.tab_empleados = QWidget()
        
        self.tabs.addTab(self.tab_asistencias, "Asistencias")
        self.tabs.addTab(self.tab_empleados, "Gestión de Empleados")
        
        self.setup_asistencias_tab()
        self.setup_empleados_tab()
        
        body_layout.addWidget(self.tabs)
        main_layout.addWidget(body_widget)

    def create_summary_card(self, title, value, subtitle):
        card = QFrame()
        card.setObjectName("CardFrame")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        
        title_lbl = QLabel(title)
        title_lbl.setObjectName("CardTitle")
        
        value_lbl = QLabel(str(value))
        value_lbl.setObjectName("CardValue")
        
        sub_lbl = QLabel(subtitle)
        sub_lbl.setObjectName("CardSubtitle")
        
        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)
        layout.addWidget(sub_lbl)
        return card

    def setup_asistencias_tab(self):
        layout = QVBoxLayout(self.tab_asistencias)
        layout.setContentsMargins(0, 20, 0, 0)
        layout.setSpacing(24)

        # Tarjetas Superiores
        cards_layout = QHBoxLayout()
        cards_layout.addWidget(self.create_summary_card("Total Empleados", "0", "Empleados registrados"))
        cards_layout.addWidget(self.create_summary_card("Presentes Hoy", "0", "0% de asistencia"))
        cards_layout.addWidget(self.create_summary_card("Ausentes", "0", "0% del total"))
        cards_layout.addWidget(self.create_summary_card("Tardanzas", "0", "0% del total"))
        layout.addLayout(cards_layout)

        # Tarjeta de la Tabla Principal
        table_card = QFrame()
        table_card.setObjectName("CardFrame")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Registro de Asistencias - Hoy")
        title.setObjectName("CardTitle")
        title.setStyleSheet("font-size: 14pt; color: #1C54FF;")
        
        search_input = QLineEdit()
        search_input.setObjectName("SearchInput")
        search_input.setPlaceholderText("Buscar por nombre o departamento...")
        
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(["Empleado", "Departamento", "Entrada", "Salida", "Estado"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        table_layout.addWidget(title)
        table_layout.addSpacing(15)
        table_layout.addWidget(search_input)
        table_layout.addWidget(table)
        
        layout.addWidget(table_card)

    def setup_empleados_tab(self):
        layout = QVBoxLayout(self.tab_empleados)
        layout.setContentsMargins(0, 20, 0, 0)

        # Tarjeta de la Tabla Principal
        table_card = QFrame()
        table_card.setObjectName("CardFrame")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(30, 30, 30, 30)
        
        top_layout = QHBoxLayout()
        title = QLabel("Gestión de Empleados")
        title.setObjectName("CardTitle")
        title.setStyleSheet("font-size: 14pt; color: #1C54FF;")
        
        add_btn = QPushButton("+ Agregar Empleado")
        add_btn.setObjectName("PrimaryButton")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        top_layout.addWidget(title)
        top_layout.addStretch()
        top_layout.addWidget(add_btn)
        
        search_input = QLineEdit()
        search_input.setObjectName("SearchInput")
        search_input.setPlaceholderText("Buscar por nombre o departamento...")
        
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(["Nombre", "Departamento", "Teléfono", "Estado", "Acciones"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        table_layout.addLayout(top_layout)
        table_layout.addSpacing(15)
        table_layout.addWidget(search_input)
        table_layout.addWidget(table)
        
        layout.addWidget(table_card)
