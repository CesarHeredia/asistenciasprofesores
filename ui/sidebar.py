from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QWidget, QHBoxLayout,
                             QLabel, QPushButton, QComboBox, QCheckBox, QLineEdit)
from PyQt6.QtCore import Qt


def create_left_sidebar(main_window):
    sidebar = QFrame()
    sidebar.setObjectName("LeftSidebar")
    sidebar.setFixedWidth(240)
    layout = QVBoxLayout(sidebar)
    layout.setContentsMargins(0, 30, 0, 0)
    layout.setSpacing(0)

    logo_container = QWidget()
    logo_layout = QHBoxLayout(logo_container)
    logo_label = QLabel("G")
    logo_label.setObjectName("LogoLabel")
    logo_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(logo_container)
    layout.addSpacing(30)

    main_window.btn_profesores = QPushButton(" Gestionar\n      profesores")
    main_window.btn_profesores.setObjectName("MenuButton")
    main_window.btn_profesores.setFixedHeight(70)
    main_window.btn_profesores.clicked.connect(lambda: main_window.show_db_view("profesor"))

    main_window.btn_materias = QPushButton("  Gestionar\n      Materias")
    main_window.btn_materias.setObjectName("MenuButton")
    main_window.btn_materias.setFixedHeight(70)
    main_window.btn_materias.clicked.connect(lambda: main_window.show_db_view("materia"))

    layout.addWidget(main_window.btn_profesores)
    layout.addWidget(main_window.btn_materias)
    layout.addStretch()
    return sidebar


def create_right_sidebar():
    sidebar = QFrame()
    sidebar.setObjectName("RightSidebar")
    sidebar.setFixedWidth(280)
    layout = QVBoxLayout(sidebar)
    layout.setContentsMargins(25, 40, 25, 40)
    layout.setSpacing(20)

    search_input = QLineEdit()
    search_input.setObjectName("SearchInput")
    search_input.setPlaceholderText("BUSCAR")
    layout.addWidget(search_input)

    layout.addSpacing(10)

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

    #for i in range(1, 5):
    #    cb = QCheckBox(f"Departamento {i}")
    #    cb.setObjectName("FilterCheck")
    #    layout.addWidget(cb)

    #layout.addSpacing(15)

    lbl_estado = QLabel("Estado de Asistencia:")
    lbl_estado.setObjectName("FilterTitle")
    layout.addWidget(lbl_estado)

    combo_estado1 = QComboBox()
    combo_estado1.setObjectName("FilterCombo")
    combo_estado1.addItem("Asistencia")

    #combo_estado2 = QComboBox()
    #combo_estado2.setObjectName("FilterCombo")
    #combo_estado2.addItem("Asistencia")

    layout.addWidget(combo_estado1)
    #layout.addWidget(combo_estado2)
    layout.addStretch()
    return sidebar
