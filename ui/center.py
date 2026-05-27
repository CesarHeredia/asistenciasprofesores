from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QWidget,
                             QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt


def create_center_panel(main_window):
    panel = QFrame()
    panel.setObjectName("CenterPanel")
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(40, 40, 40, 30)
    layout.setSpacing(30)

    title_layout = QHBoxLayout()
    title = QLabel("SISTEMA DE ASISTENCIA - PANEL DE CONTROL")
    title.setObjectName("MainTitle")

    main_window.clock_label = QLabel("00:00:00")
    main_window.clock_label.setObjectName("ClockLabel")
    main_window.clock_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #555;")

    title_layout.addWidget(title)
    title_layout.addStretch()
    title_layout.addWidget(main_window.clock_label)
    layout.addLayout(title_layout)

    scroll_area = QScrollArea()
    scroll_area.setObjectName("ScrollArea")
    scroll_area.setWidgetResizable(True)
    scroll_area.setFrameShape(QFrame.Shape.NoFrame)

    scroll_content = QWidget()
    scroll_content.setObjectName("ScrollContent")
    main_window.cards_grid_layout = QGridLayout(scroll_content)
    main_window.cards_grid_layout.setSpacing(25)
    main_window.cards_grid_layout.setContentsMargins(10, 10, 10, 10)

    main_window.update_profesores_cards()

    scroll_area.setWidget(scroll_content)
    layout.addWidget(scroll_area)

    # Botón "Ver más profesores"
    #ver_mas_btn = QPushButton("⬇️\nVer más profesores...")
    #ver_mas_btn.setObjectName("VerMasBtn")
    #ver_mas_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    #layout.addWidget(ver_mas_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    return panel


def create_profesor_card(main_window, nombre, materia, aula, avatar_emoji, presente=True):
    card = QFrame()
    card.setObjectName("ProfesorCard")
    card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    card.setMinimumHeight(200)

    layout = QVBoxLayout(card)
    layout.setContentsMargins(25, 25, 25, 25)
    layout.setSpacing(15)

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

    lbl_profesor_title = QLabel("Profesor:")
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
    if aula:
        add_detail_row("Aula:", aula)

    indicator_layout = QHBoxLayout()
    indicator_layout.addStretch()

    presence_dot = QLabel()
    presence_dot.setFixedSize(18, 18)
    color = "#2ecc71" if presente else "#95a5a6"
    tooltip = "Presente" if presente else "Ausente"
    presence_dot.setStyleSheet(f"""
            background-color: {color};
            border-radius: 9px;
            border: 2px solid rgba(0,0,0,0.15);
        """)
    presence_dot.setToolTip(tooltip)
    indicator_layout.addWidget(presence_dot)
    layout.addLayout(indicator_layout)

    return card
