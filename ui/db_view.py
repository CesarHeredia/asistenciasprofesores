from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableView, QHeaderView)
from PyQt6.QtCore import Qt


def create_db_view(main_window):
    panel = QFrame()
    panel.setObjectName("CenterPanel")
    layout = QVBoxLayout(panel)
    layout.setContentsMargins(40, 40, 40, 30)
    layout.setSpacing(20)

    header_layout = QHBoxLayout()
    main_window.lbl_db_title = QLabel("Gestion USM")
    main_window.lbl_db_title.setObjectName("MainTitle")

    btn_volver = QPushButton("Volver")
    btn_volver.setFixedWidth(100)
    btn_volver.setStyleSheet("color: white;")
    btn_volver.clicked.connect(main_window.show_main_view)

    header_layout.addWidget(main_window.lbl_db_title)
    header_layout.addStretch()
    header_layout.addWidget(btn_volver)
    layout.addLayout(header_layout)

    controls_layout = QHBoxLayout()
    controls_layout.addStretch()

    btn_add = QPushButton("➕ Añadir Fila")
    btn_add.setStyleSheet("color: white;")
    btn_add.clicked.connect(main_window.show_add_form)
    controls_layout.addWidget(btn_add)

    layout.addLayout(controls_layout)

    main_window.table_view = QTableView()
    main_window.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    main_window.table_view.setStyleSheet("""
            QTableView {
                background-color: white;
                color: black;
                border: 1px solid #ccc;
                gridline-color: #a0a0a0;
            }
            QHeaderView::section {
                background-color: black;
                color: white;
                font-weight: bold;
                padding: 4px;
            }
            QTableView::item {
                padding: 5px;
                color: black;
            }
            QTableView::item:selected {
                background-color: #e0f0ff;
                color: black;
            }
        """)

    main_window.table_view.setMouseTracking(True)
    main_window.btn_inline_del = QPushButton("🗑️", main_window.table_view.viewport())
    main_window.btn_inline_del.setFixedSize(28, 28)
    main_window.btn_inline_del.setStyleSheet("""
            QPushButton {
                background-color: #ff4c4c;
                color: white;
                border-radius: 14px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #ff1c1c;
            }
        """)
    main_window.btn_inline_del.hide()
    main_window.btn_inline_del.clicked.connect(main_window.inline_delete_row)

    main_window.table_view.entered.connect(main_window.on_table_hover)
    main_window.table_view.viewport().installEventFilter(main_window)
    main_window.table_view.clicked.connect(main_window.on_db_table_clicked)

    layout.addWidget(main_window.table_view)

    main_window.db_model = None
    return panel
