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
        from ui.sidebar import create_left_sidebar
        return create_left_sidebar(self)

    def create_center_panel(self):
        from ui.center import create_center_panel
        return create_center_panel(self)

    def create_profesor_card(self, nombre, materia, aula, avatar_emoji, presente=True):
        from ui.center import create_profesor_card
        return create_profesor_card(self, nombre, materia, aula, avatar_emoji, presente)

    def create_right_sidebar(self):
        from ui.sidebar import create_right_sidebar
        return create_right_sidebar()

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
        from ui.db_view import create_db_view
        return create_db_view(self)

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
        from ui.forms import create_form_view
        return create_form_view(self)

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
        from ui.schedule import create_schedule_view
        return create_schedule_view(self)

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
        from ui.schedule import create_schedule_form_view
        return create_schedule_form_view(self)

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
