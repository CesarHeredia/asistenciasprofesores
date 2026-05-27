from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea,
                             QGridLayout, QHBoxLayout, QPushButton)
from PyQt6.QtCore import Qt


def create_form_view(main_window):
    form_widget = QWidget()
    layout = QVBoxLayout(form_widget)
    layout.setContentsMargins(40, 40, 40, 40)

    main_window.form_title = QLabel("Añadir Registro")
    main_window.form_title.setObjectName("MainTitle")
    layout.addWidget(main_window.form_title)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

    scroll_content = QWidget()
    main_window.form_layout = QGridLayout(scroll_content)
    main_window.form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    scroll.setWidget(scroll_content)

    layout.addWidget(scroll)

    btn_layout = QHBoxLayout()
    btn_save = QPushButton("💾 Guardar")
    btn_save.setStyleSheet("color: white;")
    btn_save.clicked.connect(main_window.save_form_data)

    btn_cancel = QPushButton("❌ Cancelar")
    btn_cancel.setStyleSheet("color: white;")
    btn_cancel.clicked.connect(main_window.cancel_add_row)

    btn_layout.addStretch()
    btn_layout.addWidget(btn_save)
    btn_layout.addWidget(btn_cancel)

    layout.addLayout(btn_layout)
    return form_widget
