# pyrefly: ignore [missing-import]
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QComboBox, QFrame, 
                             QScrollArea, QGridLayout, QLineEdit, QCheckBox, QSpacerItem, QSizePolicy, QStackedWidget, QTableView, QHeaderView, QMessageBox, QTableWidget, QTableWidgetItem)
from PyQt6.QtGui import QColor, QIntValidator
# pyrefly: ignore [missing-import]
from PyQt6.QtCore import Qt, QSize, QEvent, QTimer, QTime
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Asistencia - Panel de Control")
        # El diseño se ve bastante panorámico, ajustamos el tamaño
        self.resize(1300, 800)
        
        self.load_styles()
        self.setup_ui()
        self.setup_clock()

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

        # Contenedor dinámico (StackedWidget) para el lado derecho
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, stretch=1)

        # Página 1: Vista Original (Centro + Derecha)
        page1_widget = QWidget()
        page1_layout = QHBoxLayout(page1_widget)
        page1_layout.setContentsMargins(0, 0, 0, 0)
        page1_layout.setSpacing(0)

        # 2. Columna Central (Tarjetas)
        center_panel = self.create_center_panel()
        page1_layout.addWidget(center_panel, stretch=1) # El centro toma el mayor espacio disponible

        # 3. Columna Derecha (Filtros)
        right_sidebar = self.create_right_sidebar()
        page1_layout.addWidget(right_sidebar)
        
        self.stacked_widget.addWidget(page1_widget)

        # Página 2: Vista de Base de Datos
        self.db_view = self.create_db_view()
        self.stacked_widget.addWidget(self.db_view)

        # Página 3: Formulario dinámico para añadir
        self.form_view = self.create_form_view()
        self.stacked_widget.addWidget(self.form_view)

        # Página 4: Vista de Horario Semanal
        self.schedule_view = self.create_schedule_view()
        self.stacked_widget.addWidget(self.schedule_view)

        # Página 5: Formulario de Asignación de Horario
        self.schedule_form_view = self.create_schedule_form_view()
        self.stacked_widget.addWidget(self.schedule_form_view)

    def setup_clock(self):
        self.last_minute = -1
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000) # Update every second
        self.update_clock() # Initial call

    def update_clock(self):
        current_time = QTime.currentTime()
        time_text = current_time.toString("HH:mm:ss")
        if hasattr(self, 'clock_label'):
            self.clock_label.setText(time_text)
            
        current_minute = current_time.minute()
        # Solo actualiza las tarjetas automáticamente si el usuario está en la página principal
        if current_minute != self.last_minute:
            self.last_minute = current_minute
            if hasattr(self, 'cards_grid_layout') and hasattr(self, 'stacked_widget'):
                if self.stacked_widget.currentIndex() == 0:
                    self.update_profesores_cards()

    def update_profesores_cards(self):
        if not hasattr(self, 'cards_grid_layout'):
            return
            
        # Clear existing cards
        while self.cards_grid_layout.count():
            item = self.cards_grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        import datetime
        now = datetime.datetime.now()
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dia_actual = dias[now.weekday()]
        hora_actual = now.strftime("%H:%M")

        query = QSqlDatabase.database().exec(f"""
            SELECT p.id_profesor, p.nb_profesor, p.ap_profesor,
                   m.nb_materia, h.num_aula
            FROM profesor p
            LEFT JOIN horario h ON p.id_profesor = h.id_profesor
                AND h.dia_semana = '{dia_actual}'
                AND h.hora_inicio <= '{hora_actual}'
                AND h.hora_fin >= '{hora_actual}'
            LEFT JOIN materia m ON h.id_materia = m.id_materia
        """)
        
        tarjetas_datos = []
        while query.next():
            nb_profesor = query.value(1)
            ap_profesor = query.value(2)
            nombre_completo = f"{nb_profesor} {ap_profesor}"
            
            nb_materia = query.value(3)
            num_aula = query.value(4)
            
            if nb_materia:
                materia = nb_materia
                aula = num_aula if num_aula else "Sin Aula"
            else:
                materia = "Horalibre"
                aula = None
                
            tarjetas_datos.append((nombre_completo, materia, aula, "", True))
            
        row, col = 0, 0
        for data in tarjetas_datos:
            card = self.create_profesor_card(*data)
            self.cards_grid_layout.addWidget(card, row, col)
            col += 1
            if col > 1: # 2 columnas
                col = 0
                row += 1

        self.cards_grid_layout.setRowStretch(row + 1, 1)

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
        self.btn_profesores = QPushButton("👥  Gestionar\n      profesores")
        self.btn_profesores.setObjectName("MenuButton")
        self.btn_profesores.setFixedHeight(70)
        self.btn_profesores.clicked.connect(lambda: self.show_db_view("profesor"))
        
        # Usaremos una 'M' literal para simular el tercer icono si es necesario
        self.btn_materias = QPushButton("M   Gestionar\n      Materias")
        self.btn_materias.setObjectName("MenuButton")
        self.btn_materias.setFixedHeight(70)
        self.btn_materias.clicked.connect(lambda: self.show_db_view("materia"))

        layout.addWidget(self.btn_profesores)
        layout.addWidget(self.btn_materias)
        
        layout.addStretch() # Empuja todo hacia arriba
        return sidebar

    def create_center_panel(self):
        panel = QFrame()
        panel.setObjectName("CenterPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 30)
        layout.setSpacing(30)

        # Título y Reloj
        title_layout = QHBoxLayout()
        title = QLabel("SISTEMA DE ASISTENCIA - PANEL DE CONTROL")
        title.setObjectName("MainTitle")
        
        self.clock_label = QLabel("00:00:00")
        self.clock_label.setObjectName("ClockLabel")
        self.clock_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #555;")
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(self.clock_label)
        
        layout.addLayout(title_layout)

        # Área de Scroll para las tarjetas
        scroll_area = QScrollArea()
        scroll_area.setObjectName("ScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        scroll_content.setObjectName("ScrollContent")
        self.cards_grid_layout = QGridLayout(scroll_content)
        self.cards_grid_layout.setSpacing(25)
        self.cards_grid_layout.setContentsMargins(10, 10, 10, 10)

        # No es necesario llamar update_profesores_cards aquí si ya se llamará por el setup_clock.
        # Pero podemos inicializarlas manualmente para que aparezcan al instante.
        self.update_profesores_cards()

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        # Botón "Ver más"
        ver_mas_btn = QPushButton("⬇️\nVer más profesores...")
        ver_mas_btn.setObjectName("VerMasBtn")
        ver_mas_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(ver_mas_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return panel

    def create_profesor_card(self, nombre, materia, aula, avatar_emoji, presente=True):
        card = QFrame()
        card.setObjectName("ProfesorCard")
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
        if aula:
            add_detail_row("Aula:", aula)

        # Indicador de presencia en esquina inferior derecha
        indicator_layout = QHBoxLayout()
        indicator_layout.addStretch()
        
        presence_dot = QLabel()
        presence_dot.setFixedSize(18, 18)
        color = "#2ecc71" if presente else "#95a5a6"  # Verde o Gris
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

    def update_sidebar_active(self, active_view):
        if hasattr(self, 'btn_profesores') and hasattr(self, 'btn_materias'):
            self.btn_profesores.setObjectName("MenuButtonActive" if active_view == "profesor" else "MenuButton")
            self.btn_materias.setObjectName("MenuButtonActive" if active_view == "materia" else "MenuButton")
            
            # Refrescar estilos
            self.btn_profesores.style().unpolish(self.btn_profesores)
            self.btn_profesores.style().polish(self.btn_profesores)
            self.btn_materias.style().unpolish(self.btn_materias)
            self.btn_materias.style().polish(self.btn_materias)

    def show_db_view(self, table_name="materia"):
        self.stacked_widget.setCurrentIndex(1)
        self.load_table_data(table_name)
        self.update_sidebar_active(table_name)

    def show_main_view(self):
        self.stacked_widget.setCurrentIndex(0)
        self.update_sidebar_active(None)
        # Forzar actualización inmediata al volver al inicio
        if hasattr(self, 'cards_grid_layout'):
            self.last_minute = -1  # Resetear para que el timer vuelva a comparar en el próximo tick
            self.update_profesores_cards()

    def create_db_view(self):
        panel = QFrame()
        panel.setObjectName("CenterPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 30)
        layout.setSpacing(20)

        # Título y Botón Volver
        header_layout = QHBoxLayout()
        self.lbl_db_title = QLabel("Gestion USM")
        self.lbl_db_title.setObjectName("MainTitle")
        
        btn_volver = QPushButton("Volver")
        btn_volver.setFixedWidth(100)
        btn_volver.setStyleSheet("color: white;")
        btn_volver.clicked.connect(self.show_main_view)
        
        header_layout.addWidget(self.lbl_db_title)
        header_layout.addStretch()
        header_layout.addWidget(btn_volver)
        layout.addLayout(header_layout)

        # Controles de BD
        controls_layout = QHBoxLayout()
        controls_layout.addStretch()
        
        btn_add = QPushButton("➕ Añadir Fila")
        btn_add.setStyleSheet("color: white;")
        btn_add.clicked.connect(self.show_add_form)
        
        controls_layout.addWidget(btn_add)
        
        layout.addLayout(controls_layout)

        # Tabla
        self.table_view = QTableView()
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Aplicamos un estilo a la tabla para que se vea bonita y parezca un excel
        self.table_view.setStyleSheet("""
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
        
        self.table_view.setMouseTracking(True)
        self.btn_inline_del = QPushButton("🗑️", self.table_view.viewport())
        self.btn_inline_del.setFixedSize(28, 28)
        self.btn_inline_del.setStyleSheet("""
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
        self.btn_inline_del.hide()
        self.btn_inline_del.clicked.connect(self.inline_delete_row)
        
        self.table_view.entered.connect(self.on_table_hover)
        self.table_view.viewport().installEventFilter(self)
        self.table_view.clicked.connect(self.on_db_table_clicked)
        
        layout.addWidget(self.table_view)

        # Inicializar modelo
        self.db_model = None

        return panel

    def on_db_table_clicked(self, index):
        if not index.isValid(): return
        
        if self.db_model and self.db_model.tableName() == "profesor":
            row = index.row()
            id_profesor = self.db_model.record(row).value("id_profesor")
            nb_profesor = self.db_model.record(row).value("nb_profesor")
            
            if id_profesor is not None and nb_profesor is not None:
                self.show_schedule_view(id_profesor, str(nb_profesor))

    def load_table_data(self, table_name):
        self.lbl_db_title.setText(f"Gestion USM - {table_name.capitalize()}")
        if not QSqlDatabase.database().isOpen():
            QMessageBox.warning(self, "Error", "La base de datos no está conectada.")
            return

        self.db_model = QSqlTableModel()
        self.db_model.setTable(table_name)
        self.db_model.setEditStrategy(QSqlTableModel.EditStrategy.OnFieldChange)
        self.db_model.select()
        
        # Mapeo de nombres de columnas a nombres amigables
        nombres_amigables = {
            
            "nb_profesor": "Nombre",
            "ap_profesor": "Apellidos",
            "nb_materia": "Materia",
            "facultad": "Facultad",
            "departamento": "Departamento",
            "edificio": "Edificio",
            "dia": "Día",
            "hora_inicio": "Hora Inicio",
            "hora_fin": "Hora Fin",
            "estado": "Estado"
        }
        
        for i in range(self.db_model.columnCount()):
            col_name = self.db_model.headerData(i, Qt.Orientation.Horizontal)
            if col_name in nombres_amigables:
                self.db_model.setHeaderData(i, Qt.Orientation.Horizontal, nombres_amigables[col_name])
        
        self.table_view.setModel(self.db_model)
        self.table_view.hideColumn(0)

    def create_form_view(self):
        form_widget = QWidget()
        layout = QVBoxLayout(form_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        
        self.form_title = QLabel("Añadir Registro")
        self.form_title.setObjectName("MainTitle")
        layout.addWidget(self.form_title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        scroll_content = QWidget()
        self.form_layout = QGridLayout(scroll_content)
        self.form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(scroll_content)
        
        layout.addWidget(scroll)
        
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Guardar")
        btn_save.setStyleSheet("color: white;")
        btn_save.clicked.connect(self.save_form_data)
        
        btn_cancel = QPushButton("❌ Cancelar")
        btn_cancel.setStyleSheet("color: white;")
        btn_cancel.clicked.connect(self.cancel_add_row)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
        return form_widget

    def show_add_form(self):
        if not self.db_model:
            return
            
        table_name = self.db_model.tableName()
        self.form_title.setText(f"Añadir a {table_name.capitalize()}")
        
        # Limpiar layout
        while self.form_layout.count():
            child = self.form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        self.form_inputs = {}
        row_idx = 0
        
        nombres_amigables = {
            "nb_profesor": "Nombre",
            "ap_profesor": "Apellidos",
            "nb_materia": "Materia",
            "facultad": "Facultad",
            "departamento": "Departamento",
            "edificio": "Edificio",
            "dia": "Día",
            "hora_inicio": "Hora Inicio",
            "hora_fin": "Hora Fin",
            "estado": "Estado"
        }
        
        for i in range(self.db_model.columnCount()):
            col_name = self.db_model.record().fieldName(i)
            if "id" in col_name.lower():
                continue
                
            friendly_name = nombres_amigables.get(col_name, col_name.capitalize())
            lbl = QLabel(friendly_name)
            lbl.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
            
            inp = QLineEdit()
            inp.setStyleSheet("background-color: #2b2b2b; color: white; padding: 8px; border-radius: 4px; font-size: 14px;")
            
            self.form_layout.addWidget(lbl, row_idx, 0)
            self.form_layout.addWidget(inp, row_idx, 1)
            
            self.form_inputs[col_name] = inp
            row_idx += 1
            
        self.stacked_widget.setCurrentIndex(2)

    def cancel_add_row(self):
        self.stacked_widget.setCurrentIndex(1)

    def save_form_data(self):
        if not self.db_model:
            return
            
        row = self.db_model.rowCount()
        self.db_model.insertRow(row)
        
        for i in range(self.db_model.columnCount()):
            col_name = self.db_model.record().fieldName(i)
            if col_name in self.form_inputs:
                val = self.form_inputs[col_name].text()
                idx = self.db_model.index(row, i)
                self.db_model.setData(idx, val)
                
        if self.db_model.submitAll():
            QMessageBox.information(self, "Éxito", "Registro añadido correctamente.")
            self.stacked_widget.setCurrentIndex(1)
            self.db_model.select() # Recargar datos
        else:
            QMessageBox.critical(self, "Error", f"Error al guardar: {self.db_model.lastError().text()}")
            self.db_model.revertAll()

    def on_table_hover(self, index):
        if not index.isValid():
            self.btn_inline_del.hide()
            return
            
        self._hovered_row = index.row()
        
        rect = self.table_view.visualRect(index)
        viewport_width = self.table_view.viewport().width()
        
        btn_x = viewport_width - self.btn_inline_del.width() - 5
        btn_y = rect.y() + (rect.height() - self.btn_inline_del.height()) // 2
        
        self.btn_inline_del.move(btn_x, btn_y)
        self.btn_inline_del.show()

    def eventFilter(self, obj, event):
        if hasattr(self, 'table_view') and obj == self.table_view.viewport() and event.type() == QEvent.Type.Leave:
            self.btn_inline_del.hide()
            
        if hasattr(self, 'schedule_table') and obj == self.schedule_table.viewport() and event.type() == QEvent.Type.MouseButtonRelease:
            # Usamos QTimer para procesarlo después del evento de selección
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(50, self.process_schedule_selection)
            
        return super().eventFilter(obj, event)

    def inline_delete_row(self):
        if hasattr(self, '_hovered_row') and self.db_model:
            respuesta = QMessageBox.question(
                self, 
                "Confirmar Eliminación", 
                "¿Estás seguro de que deseas eliminar este registro? Esta acción no se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if respuesta == QMessageBox.StandardButton.Yes:
                self.db_model.removeRow(self._hovered_row)
                self.db_model.submitAll() # Asegura que se envíe el borrado a la DB
                self.db_model.select()    # Refresca la vista
                self.btn_inline_del.hide()

    def create_schedule_view(self):
        panel = QFrame()
        panel.setObjectName("CenterPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 30)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        self.lbl_schedule_title = QLabel("HORARIO SEMANAL")
        self.lbl_schedule_title.setObjectName("MainTitle")
        self.lbl_schedule_title.setStyleSheet("color: gray;")
        
        btn_volver = QPushButton("Volver a Profesores")
        btn_volver.setFixedWidth(180)
        btn_volver.setStyleSheet("color: white;")
        btn_volver.clicked.connect(lambda: self.show_db_view("profesor"))
        
        header_layout.addWidget(self.lbl_schedule_title)
        header_layout.addStretch()
        header_layout.addWidget(btn_volver)
        layout.addLayout(header_layout)

        # Header Info
        info_layout = QHBoxLayout()
        info_layout.addStretch()
        lbl_info = QLabel("Arrastra el ratón sobre los bloques vacíos para asignar un horario")
        lbl_info.setStyleSheet("color: gray; margin-bottom: 10px;")
        info_layout.addWidget(lbl_info)
        layout.addLayout(info_layout)

        # Grid
        self.schedule_table = QTableWidget(14, 5) # 14 rows, 5 columns
        self.schedule_table.setHorizontalHeaderLabels(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"])
        
        self.time_slots = [
            "07:00 - 07:45", "07:45 - 08:30", "08:30 - 09:15", "09:15 - 10:00",
            "10:00 - 10:45", "10:45 - 11:30", "11:30 - 12:15", "12:15 - 13:00",
            "13:00 - 13:45", "13:45 - 14:30", "14:30 - 15:15", "15:15 - 16:00",
            "16:00 - 16:45", "16:45 - 17:30"
        ]
        self.schedule_table.setVerticalHeaderLabels(self.time_slots)
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.schedule_table.verticalHeader().setDefaultSectionSize(65)
        
        self.schedule_table.setStyleSheet("""
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
        
        self.schedule_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.schedule_table.setSelectionMode(QTableWidget.SelectionMode.ContiguousSelection)
        self.schedule_table.viewport().installEventFilter(self)
        self.schedule_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        layout.addWidget(self.schedule_table)
        
        self.current_profesor_id = None
        return panel

    def show_schedule_view(self, id_profesor, nb_profesor):
        self.current_profesor_id = id_profesor
        self.lbl_schedule_title.setText(f"HORARIO SEMANAL - {nb_profesor.upper()}")
        
        self.load_schedule_data()
        self.stacked_widget.setCurrentIndex(3)
        self.update_sidebar_active(None)

    def load_schedule_data(self):
        self.schedule_table.clearContents()
        for i in range(14):
            for j in range(5):
                item = QTableWidgetItem("")
                self.schedule_table.setItem(i, j, item)
                
        if not self.current_profesor_id: return
                
        # Cargar asignaciones
        query = QSqlDatabase.database().exec(f"SELECT h.id_horario, h.dia_semana, h.hora_inicio, h.hora_fin, m.nb_materia, h.id_materia, h.num_aula FROM horario h JOIN materia m ON h.id_materia = m.id_materia WHERE h.id_profesor = {self.current_profesor_id}")
        
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        
        while query.next():
            id_h = query.value(0)
            dia = query.value(1)
            h_inicio = query.value(2)
            h_fin = query.value(3)
            nb_mat = query.value(4)
            id_mat = query.value(5)
            n_aula = query.value(6)
            
            if dia not in dias: continue
            col = dias.index(dia)
            
            slot_str = f"{h_inicio} - {h_fin}"
            if slot_str in self.time_slots:
                row = self.time_slots.index(slot_str)
                
                display_text = f"'{nb_mat}'"
                if n_aula:
                    display_text += f"\n {n_aula}"
                    
                item = QTableWidgetItem(display_text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(QColor(218, 232, 252))
                item.setForeground(QColor(10, 40, 100))
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                
                item.setData(Qt.ItemDataRole.UserRole, id_h)
                item.setData(Qt.ItemDataRole.UserRole + 1, id_mat)
                self.schedule_table.setItem(row, col, item)

    def process_schedule_selection(self):
        if self.current_profesor_id is None: return
        
        ranges = self.schedule_table.selectedRanges()
        if not ranges:
            return
            
        sel_range = ranges[0]
        col = sel_range.leftColumn()
        
        if sel_range.leftColumn() != sel_range.rightColumn():
            QMessageBox.warning(self, "Selección Inválida", "Por favor, selecciona horas de un solo día (verticalmente) a la vez.")
            self.schedule_table.clearSelection()
            return
            
        start_row = sel_range.topRow()
        end_row = sel_range.bottomRow()
        
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        dia = dias[col]
        h_inicio = self.time_slots[start_row].split(" - ")[0]
        h_fin = self.time_slots[end_row].split(" - ")[1]
        
        # Guardamos el estado para el formulario
        self.pending_schedule = {
            'col': col,
            'start_row': start_row,
            'end_row': end_row,
            'dia': dia
        }
        
        self.lbl_schedule_form_range.setText(f"Día: {dia} | Horario: {h_inicio} - {h_fin}")
        self.input_schedule_form_aula.clear()
        
        # Cargar materias al combo del formulario
        self.combo_schedule_form_materia.clear()
        query = QSqlDatabase.database().exec("SELECT id_materia, nb_materia FROM materia")
        has_materias = False
        while query.next():
            has_materias = True
            id_m = query.value(0)
            nb_m = query.value(1)
            self.combo_schedule_form_materia.addItem(nb_m, id_m)
            
        if not has_materias:
            QMessageBox.warning(self, "Error", "No tienes ninguna materia guardada en el sistema. Añade una materia primero.")
            self.schedule_table.clearSelection()
            return

        # Mostrar/ocultar botón eliminar según si hay bloques asignados
        tiene_bloques = any(
            self.schedule_table.item(r, col) and self.schedule_table.item(r, col).text()
            for r in range(start_row, end_row + 1)
        )
        self.btn_delete_schedule.setVisible(tiene_bloques)
            
        # Cambiar a la vista del formulario (página 5, índice 4)
        self.stacked_widget.setCurrentIndex(4)

    def create_schedule_form_view(self):
        panel = QFrame()
        panel.setObjectName("CenterPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 40, 40, 30)
        layout.setSpacing(20)

        # Title
        lbl_title = QLabel("Asignar Horario")
        lbl_title.setObjectName("MainTitle")
        lbl_title.setStyleSheet("color: black; font-size: 24px; font-weight: bold;")
        
        self.lbl_schedule_form_range = QLabel("")
        self.lbl_schedule_form_range.setStyleSheet("color: gray; font-size: 16px; margin-bottom: 20px;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(self.lbl_schedule_form_range)

        # Form layout
        form_layout = QGridLayout()
        form_layout.setSpacing(20)
        
        lbl_materia = QLabel("Materia:")
        lbl_materia.setStyleSheet("color: black; font-size: 16px;")
        self.combo_schedule_form_materia = QComboBox()
        self.combo_schedule_form_materia.setFixedHeight(40)
        self.combo_schedule_form_materia.setStyleSheet("""
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
        self.input_schedule_form_aula = QLineEdit()
        self.input_schedule_form_aula.setPlaceholderText("Ej. 123 (máx 3 dígitos numéricos)")
        self.input_schedule_form_aula.setFixedHeight(40)
        self.input_schedule_form_aula.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                color: black;
                background-color: white;
            }
        """)
        
        validator = QIntValidator()
        self.input_schedule_form_aula.setValidator(validator)
        self.input_schedule_form_aula.setMaxLength(3)

        form_layout.addWidget(lbl_materia, 0, 0)
        form_layout.addWidget(self.combo_schedule_form_materia, 0, 1)
        form_layout.addWidget(lbl_aula, 1, 0)
        form_layout.addWidget(self.input_schedule_form_aula, 1, 1)
        
        layout.addLayout(form_layout)
        layout.addStretch()

        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #ddd; max-height: 1px; margin: 5px 0;")
        layout.addWidget(separator)

        # Botón Eliminar
        self.btn_delete_schedule = QPushButton("🗑️  Eliminar bloque(s) de horario")
        self.btn_delete_schedule.setStyleSheet("""
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
        self.btn_delete_schedule.clicked.connect(self.delete_schedule_form)
        layout.addWidget(self.btn_delete_schedule, alignment=Qt.AlignmentFlag.AlignLeft)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setObjectName("MenuButton")
        btn_cancel.setStyleSheet("color: white;")
        btn_cancel.clicked.connect(self.cancel_schedule_form)
        
        btn_save = QPushButton("Guardar")
        btn_save.setObjectName("MenuButtonActive")
        btn_save.setStyleSheet("color: white;")
        btn_save.clicked.connect(self.save_schedule_form)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        
        self.pending_schedule = {}
        return panel

    def cancel_schedule_form(self):
        self.schedule_table.clearSelection()
        self.stacked_widget.setCurrentIndex(3)

    def save_schedule_form(self):
        id_materia_seleccionada = self.combo_schedule_form_materia.currentData()
        nb_materia_seleccionada = self.combo_schedule_form_materia.currentText()
        num_aula = self.input_schedule_form_aula.text().strip()
        
        if not id_materia_seleccionada:
            QMessageBox.warning(self, "Error", "Debes seleccionar una materia.")
            return
            
        msg = f"¿Estás seguro de que deseas aplicar/modificar la materia '{nb_materia_seleccionada}'"
        if num_aula:
            msg += f" en el aula {num_aula}"
        msg += " en el/los bloque(s) seleccionado(s)?"
            
        respuesta = QMessageBox.question(self, "Confirmar Cambio", msg, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        
        if respuesta != QMessageBox.StandardButton.Yes:
            return
            
        col = self.pending_schedule['col']
        start_row = self.pending_schedule['start_row']
        end_row = self.pending_schedule['end_row']
        dia = self.pending_schedule['dia']
        
        for row in range(start_row, end_row + 1):
            item = self.schedule_table.item(row, col)
            slot = self.time_slots[row].split(" - ")
            h_inicio = slot[0]
            h_fin = slot[1]
            
            if item and item.text():
                id_h = item.data(Qt.ItemDataRole.UserRole)
                id_mat = item.data(Qt.ItemDataRole.UserRole + 1)
                
                if id_mat == id_materia_seleccionada:
                    # Toggle: Borramos si es la misma materia 
                    QSqlDatabase.database().exec(f"DELETE FROM horario WHERE id_horario = {id_h}")
                else:
                    # Update materia y aula
                    query = f"UPDATE horario SET id_materia = {id_materia_seleccionada}, num_aula = '{num_aula}' WHERE id_horario = {id_h}"
                    QSqlDatabase.database().exec(query)
            else:
                # Insert
                query_str = f"INSERT INTO horario (id_profesor, id_materia, dia_semana, hora_inicio, hora_fin, num_aula) VALUES ({self.current_profesor_id}, {id_materia_seleccionada}, '{dia}', '{h_inicio}', '{h_fin}', '{num_aula}')"
                query = QSqlDatabase.database().exec(query_str)
                if query.lastError().isValid():
                    QMessageBox.critical(self, "Error", f"No se guardó el horario: {query.lastError().text()}")
                
        self.load_schedule_data()
        self.schedule_table.clearSelection()
        self.stacked_widget.setCurrentIndex(3)

    def delete_schedule_form(self):
        if not self.pending_schedule:
            return

        col = self.pending_schedule['col']
        start_row = self.pending_schedule['start_row']
        end_row = self.pending_schedule['end_row']
        dia = self.pending_schedule['dia']

        dias_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        h_inicio = self.time_slots[start_row].split(" - ")[0]
        h_fin = self.time_slots[end_row].split(" - ")[1]

        respuesta = QMessageBox.question(
            self,
            "Confirmar Eliminación",
            f"¿Estás seguro de que deseas eliminar el horario del {dia} de {h_inicio} a {h_fin}?\n\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if respuesta != QMessageBox.StandardButton.Yes:
            return

        eliminados = 0
        for row in range(start_row, end_row + 1):
            item = self.schedule_table.item(row, col)
            if item and item.text():
                id_h = item.data(Qt.ItemDataRole.UserRole)
                if id_h:
                    QSqlDatabase.database().exec(f"DELETE FROM horario WHERE id_horario = {id_h}")
                    eliminados += 1

        if eliminados > 0:
            QMessageBox.information(self, "Éxito", f"Se eliminaron {eliminados} bloque(s) de horario correctamente.")
        else:
            QMessageBox.warning(self, "Aviso", "No se encontraron bloques con horario asignado para eliminar.")

        self.load_schedule_data()
        self.schedule_table.clearSelection()
        self.stacked_widget.setCurrentIndex(3)
