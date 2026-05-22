from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QComboBox, QFrame, 
                             QScrollArea, QGridLayout, QLineEdit, QCheckBox, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Asistencia - Panel de Control")
        # El diseño se ve bastante panorámico, ajustamos el tamaño
        self.resize(1300, 800)
        
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
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        
        # Layout Principal Horizontal (3 Columnas)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Columna Izquierda (Sidebar)
        left_sidebar = self.create_left_sidebar()
        main_layout.addWidget(left_sidebar)

        # 2. Columna Central (Tarjetas)
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, stretch=1) # El centro toma el mayor espacio disponible

        # 3. Columna Derecha (Filtros)
        right_sidebar = self.create_right_sidebar()
        main_layout.addWidget(right_sidebar)

    def create_left_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("LeftSidebar")
        sidebar.setFixedWidth(240)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 30, 0, 0)
        layout.setSpacing(0)

        # Logo "G"
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_label = QLabel("G")
        logo_label.setObjectName("LogoLabel")
        logo_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_container)
        layout.addSpacing(30)

        # Botones del menú
        btn_profesores = QPushButton("👥  Gestionar\n      profesores")
        btn_profesores.setObjectName("MenuButtonActive")
        btn_profesores.setFixedHeight(70)
        
        btn_horarios = QPushButton("📅  Gestionar\n      horarios")
        btn_horarios.setObjectName("MenuButton")
        btn_horarios.setFixedHeight(70)

        # Usaremos una 'M' literal para simular el tercer icono si es necesario
        btn_materias = QPushButton("M   Gestionar\n      Materias")
        btn_materias.setObjectName("MenuButton")
        btn_materias.setFixedHeight(70)

        layout.addWidget(btn_profesores)
        layout.addWidget(btn_horarios)
        layout.addWidget(btn_materias)
        
        layout.addStretch() # Empuja todo hacia arriba
        return sidebar

    def create_center_panel(self):
        panel = QFrame()
        panel.setObjectName("CenterPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 30)
        layout.setSpacing(30)

        # Título
        title = QLabel("SISTEMA DE ASISTENCIA - PANEL DE CONTROL")
        title.setObjectName("MainTitle")
        layout.addWidget(title)

        # Área de Scroll para las tarjetas
        scroll_area = QScrollArea()
        scroll_area.setObjectName("ScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        scroll_content.setObjectName("ScrollContent")
        grid_layout = QGridLayout(scroll_content)
        grid_layout.setSpacing(25)
        grid_layout.setContentsMargins(10, 10, 10, 10)

        # Agregar 4 tarjetas de ejemplo basadas en la imagen
        tarjetas_datos = [
            ("Dr. Carlos Rodríguez", "Algoritmos Avanzados", "101-B", "Ingeniería", "🧔🏽"),
            ("Dra. Ana Pérez", "Introducción a la Física", "205", "Ciencias Exactas", "👩🏻"),
            ("Lic. Sofía Martínez", "Historia del Arte", "310", "Humanidades", "👩🏽"),
            ("Ing. David Chen", "Programación de Sistemas", "G-01", "Ingeniería", "👨🏻")
        ]

        row, col = 0, 0
        for data in tarjetas_datos:
            card = self.create_profesor_card(*data)
            grid_layout.addWidget(card, row, col)
            col += 1
            if col > 1: # 2 columnas
                col = 0
                row += 1

        # Empujar las tarjetas hacia arriba si hay espacio vacío
        grid_layout.setRowStretch(row + 1, 1)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Botón "Ver más"
        ver_mas_btn = QPushButton("⬇️\nVer más profesores...")
        ver_mas_btn.setObjectName("VerMasBtn")
        ver_mas_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(ver_mas_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return panel

    def create_profesor_card(self, nombre, materia, aula, facultad, avatar_emoji):
        card = QFrame()
        card.setObjectName("ProfesorCard")
        # Aplicamos una política de tamaño para que se ajusten bien
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setMinimumHeight(200)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        # Header de la tarjeta (Avatar + Nombre)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        avatar_lbl = QLabel(avatar_emoji)
        avatar_lbl.setObjectName("Avatar")
        avatar_lbl.setFixedSize(60, 60)
        avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name_container = QWidget()
        name_layout = QVBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(2)
        
        lbl_profesor_title = QLabel("Profesor Name:")
        lbl_profesor_title.setObjectName("CardLabelSmall")
        lbl_nombre = QLabel(nombre)
        lbl_nombre.setObjectName("CardName")
        
        name_layout.addWidget(lbl_profesor_title)
        name_layout.addWidget(lbl_nombre)
        name_layout.addStretch()

        header_layout.addWidget(avatar_lbl)
        header_layout.addWidget(name_container)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Detalles
        def add_detail_row(label_text, value_text):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setObjectName("CardLabelBold")
            val = QLabel(value_text)
            val.setObjectName("CardValueNormal")
            row.addWidget(lbl)
            row.addWidget(val)
            row.addStretch()
            layout.addLayout(row)

        add_detail_row("Materia:", materia)
        add_detail_row("Aula:", aula)
        add_detail_row("Facultad:", facultad)

        return card

    def create_right_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("RightSidebar")
        sidebar.setFixedWidth(280)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(25, 40, 25, 40)
        layout.setSpacing(20)

        # Búsqueda
        search_input = QLineEdit()
        search_input.setObjectName("SearchInput")
        search_input.setPlaceholderText("BUSCAR")
        layout.addWidget(search_input)

        layout.addSpacing(10)

        # Filtros
        lbl_filtrar = QLabel("FILTRAR POR:")
        lbl_filtrar.setObjectName("FilterTitle")
        layout.addWidget(lbl_filtrar)

        def add_combo_filter(title):
            lbl = QLabel(title)
            lbl.setObjectName("FilterLabel")
            combo = QComboBox()
            combo.setObjectName("FilterCombo")
            combo.addItem(title)
            layout.addWidget(lbl)
            layout.addWidget(combo)

        add_combo_filter("Materia")
        add_combo_filter("Facultad")
        add_combo_filter("Edificio")

        layout.addSpacing(10)

        # Checkboxes
        for i in range(1, 5):
            cb = QCheckBox(f"Departamento {i}")
            cb.setObjectName("FilterCheck")
            layout.addWidget(cb)

        layout.addSpacing(15)

        # Estado Asistencia
        lbl_estado = QLabel("Estado de Asistencia:")
        lbl_estado.setObjectName("FilterTitle")
        layout.addWidget(lbl_estado)

        combo_estado1 = QComboBox()
        combo_estado1.setObjectName("FilterCombo")
        combo_estado1.addItem("Asistencia")
        
        combo_estado2 = QComboBox()
        combo_estado2.setObjectName("FilterCombo")
        combo_estado2.addItem("Asistencia")

        layout.addWidget(combo_estado1)
        layout.addWidget(combo_estado2)

        layout.addStretch()
        return sidebar
