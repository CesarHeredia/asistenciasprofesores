from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QGridLayout, QComboBox, QLineEdit, QHeaderView)
from PyQt6.QtGui import QColor, QIntValidator
from PyQt6.QtCore import Qt


def create_schedule_view(main_window):
    panel = QFrame()
    panel.setObjectName("CenterPanel")
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(40, 40, 40, 30)
    layout.setSpacing(20)

    header_layout = QHBoxLayout()
    main_window.lbl_schedule_title = QLabel("HORARIO SEMANAL")
    main_window.lbl_schedule_title.setObjectName("MainTitle")
    main_window.lbl_schedule_title.setStyleSheet("color: gray;")

    btn_volver = QPushButton("Volver a Profesores")
    btn_volver.setFixedWidth(180)
    btn_volver.setStyleSheet("color: white;")
    btn_volver.clicked.connect(lambda: main_window.show_db_view("profesor"))

    header_layout.addWidget(main_window.lbl_schedule_title)
    header_layout.addStretch()
    header_layout.addWidget(btn_volver)
    layout.addLayout(header_layout)

    info_layout = QHBoxLayout()
    info_layout.addStretch()
    lbl_info = QLabel("Arrastra el ratón sobre los bloques vacíos para asignar un horario")
    lbl_info.setStyleSheet("color: gray; margin-bottom: 10px;")
    info_layout.addWidget(lbl_info)
    layout.addLayout(info_layout)

    main_window.schedule_table = QTableWidget(14, 5)
    main_window.schedule_table.setHorizontalHeaderLabels(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"])

    main_window.time_slots = [
        "07:00 - 07:45", "07:45 - 08:30", "08:30 - 09:15", "09:15 - 10:00",
        "10:00 - 10:45", "10:45 - 11:30", "11:30 - 12:15", "12:15 - 13:00",
        "13:00 - 13:45", "13:45 - 14:30", "14:30 - 15:15", "15:15 - 16:00",
        "16:00 - 16:45", "16:45 - 17:30"
    ]
    main_window.schedule_table.setVerticalHeaderLabels(main_window.time_slots)
    main_window.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    main_window.schedule_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
    main_window.schedule_table.verticalHeader().setDefaultSectionSize(65)

    main_window.schedule_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: black;
                border: 1px solid #eee;
                gridline-color: #f0f0f0;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: white;
                color: gray;
                font-weight: normal;
                padding: 4px;
                border: none;
                border-bottom: 1px solid #eee;
                border-right: 1px solid #eee;
            }
            QTableWidget::item {
                border: 1px solid #f9f9f9;
            }
            QTableWidget::item:selected {
                background-color: transparent;
            }
        """)

    main_window.schedule_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    main_window.schedule_table.setSelectionMode(QTableWidget.SelectionMode.ContiguousSelection)
    main_window.schedule_table.viewport().installEventFilter(main_window)
    main_window.schedule_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    layout.addWidget(main_window.schedule_table)
    main_window.current_profesor_id = None
    return panel


def create_schedule_form_view(main_window):
    panel = QFrame()
    panel.setObjectName("CenterPanel")
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(40, 40, 40, 30)
    layout.setSpacing(20)

    lbl_title = QLabel("Asignar Horario")
    lbl_title.setObjectName("MainTitle")
    lbl_title.setStyleSheet("color: black; font-size: 24px; font-weight: bold;")

    main_window.lbl_schedule_form_range = QLabel("")
    main_window.lbl_schedule_form_range.setStyleSheet("color: gray; font-size: 16px; margin-bottom: 20px;")

    layout.addWidget(lbl_title)
    layout.addWidget(main_window.lbl_schedule_form_range)

    form_layout = QGridLayout()
    form_layout.setSpacing(20)

    lbl_materia = QLabel("Materia:")
    lbl_materia.setStyleSheet("color: black; font-size: 16px;")
    main_window.combo_schedule_form_materia = QComboBox()
    main_window.combo_schedule_form_materia.setFixedHeight(40)
    main_window.combo_schedule_form_materia.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                color: black;
                background-color: white;
            }
        """)

    lbl_aula = QLabel("Número de Aula:")
    lbl_aula.setStyleSheet("color: black; font-size: 16px;")
    main_window.input_schedule_form_aula = QLineEdit()
    main_window.input_schedule_form_aula.setPlaceholderText("Ej. 123 (máx 3 dígitos numéricos)")
    main_window.input_schedule_form_aula.setFixedHeight(40)
    main_window.input_schedule_form_aula.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                color: black;
                background-color: white;
            }
        """)

    validator = QIntValidator()
    main_window.input_schedule_form_aula.setValidator(validator)
    main_window.input_schedule_form_aula.setMaxLength(3)

    form_layout.addWidget(lbl_materia, 0, 0)
    form_layout.addWidget(main_window.combo_schedule_form_materia, 0, 1)
    form_layout.addWidget(lbl_aula, 1, 0)
    form_layout.addWidget(main_window.input_schedule_form_aula, 1, 1)

    layout.addLayout(form_layout)
    layout.addStretch()

    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.HLine)
    separator.setStyleSheet("background-color: #ddd; max-height: 1px; margin: 5px 0;")
    layout.addWidget(separator)

    main_window.btn_delete_schedule = QPushButton("🗑️  Eliminar bloque(s) de horario")
    main_window.btn_delete_schedule.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                max-width: 300px;
            }
            QPushButton:hover { background-color: #e74c3c; }
            QPushButton:pressed { background-color: #922b21; }
        """)
    main_window.btn_delete_schedule.clicked.connect(main_window.delete_schedule_form)
    layout.addWidget(main_window.btn_delete_schedule, alignment=Qt.AlignmentFlag.AlignLeft)

    btn_layout = QHBoxLayout()
    btn_layout.addStretch()

    btn_cancel = QPushButton("Cancelar")
    btn_cancel.setObjectName("MenuButton")
    btn_cancel.setStyleSheet("color: white;")
    btn_cancel.clicked.connect(main_window.cancel_schedule_form)

    btn_save = QPushButton("Guardar")
    btn_save.setObjectName("MenuButtonActive")
    btn_save.setStyleSheet("color: white;")
    btn_save.clicked.connect(main_window.save_schedule_form)

    btn_layout.addWidget(btn_cancel)
    btn_layout.addWidget(btn_save)
    layout.addLayout(btn_layout)

    main_window.pending_schedule = {}
    return panel
