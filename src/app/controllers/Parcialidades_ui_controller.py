from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Qt
from src.app.services import ParcialidadesService
from src.app.ui import Ui_VentanaParcialidades
from src.app.presenters.parcialidades_table_model import ParcialidadesTableModel
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIntValidator

# Fallback si la BD no responde o no hay permisos
_FALLBACK_ID_DIGITS = 9
_FALLBACK_TIPO_LEN = 20


class VentanaParcialidades(QWidget):
    def __init__(self, Parcialidades_service):
        super().__init__()
        self.ui = Ui_VentanaParcialidades()
        self.ui.setupUi(self)
        self.service: ParcialidadesService = Parcialidades_service

        try:
            self._limites = self.service.limites_columnas()
        except Exception:
            self._limites = {}
        self._aplicar_limites_a_widgets()

        self.table_model = ParcialidadesTableModel(self)
        self.ui.vistaParcialidades.setModel(self.table_model)

        self.ui.vistaParcialidades.setSelectionBehavior(
            self.ui.vistaParcialidades.SelectionBehavior.SelectRows
        )
        self.ui.vistaParcialidades.setSelectionMode(
            self.ui.vistaParcialidades.SelectionMode.SingleSelection
        )
        self.ui.vistaParcialidades.setEditTriggers(
            self.ui.vistaParcialidades.EditTrigger.NoEditTriggers
        )
        self.ui.vistaParcialidades.horizontalHeader().setStretchLastSection(True)

        self.ui.pparcialidadesNuevo.clicked.connect(self.on_nuevo)
        self.ui.pparcialidadesActualizar.clicked.connect(self.on_actualizar)
        self.ui.pparcialidadesEliminar.clicked.connect(self.on_eliminar)
        self.ui.pparcialidadesBuscar.clicked.connect(self.on_buscar)

        self.ui.vistaParcialidades.clicked.connect(self.on_fila_seleccionada)

        # Recuerda el Tipo que se llenó desde la BD, para saber si se debe limpiar
        self._tipo_cargado: str | None = None

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)  # ms
        self._search_timer.timeout.connect(self._busqueda_automatica)
        self.ui.lineIDParcialidades.textChanged.connect(self._on_id_text_changed)

        self.ui.pparcialidadesEliminar.setEnabled(False)

        # Orden del tabulador ID -> Tipo -> botones -> tabla
        # y foco inicial en el ID
        self.setTabOrder(self.ui.lineIDParcialidades, self.ui.lineTipoParcialidades)
        self.setTabOrder(self.ui.lineTipoParcialidades, self.ui.pparcialidadesNuevo)
        self.setTabOrder(self.ui.pparcialidadesNuevo, self.ui.pparcialidadesActualizar)
        self.setTabOrder(self.ui.pparcialidadesActualizar, self.ui.pparcialidadesBuscar)
        self.setTabOrder(self.ui.pparcialidadesBuscar, self.ui.pparcialidadesEliminar)
        self.setTabOrder(self.ui.pparcialidadesEliminar, self.ui.vistaParcialidades)
        self.ui.lineIDParcialidades.setFocus()

        self.refrescar_tabla()

    def refrescar_tabla(self):

        try:
            Parcialidadeses = self.service.listar() # type: ignore[call-arg]
            self.table_model.set_data(Parcialidadeses)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la lista:\n{e}")


    def _actualizar_estado_boton_eliminar(self, idparcia: int | None):
        if idparcia is None:
            self.ui.pparcialidadesEliminar.setEnabled(False)
            self.ui.pparcialidadesEliminar.setToolTip("")
            return

        try:
            tiene_hijos = self.service.tiene_hijos(idparcia)  # type: ignore[call-arg]
        except Exception:
            # Si falla la consulta, por seguridad permitimos que el backend decida
            tiene_hijos = False

        self.ui.pparcialidadesEliminar.setEnabled(not tiene_hijos)
        self.ui.pparcialidadesEliminar.setToolTip(
            f"No se puede eliminar: la parcialidad {idparcia} tiene registros relacionados."
            if tiene_hijos else ""
        )

    def limpiar_formulario(self):
        self.ui.lineIDParcialidades.clear()
        self.ui.lineTipoParcialidades.clear()

    def _id_actual(self):
        txt = self.ui.lineIDParcialidades.text().strip()
        return int(txt) if txt.isdigit() else None

    def _on_id_text_changed(self, _text: str):
        self._search_timer.start()  # reinicia el debounce

    def _busqueda_automatica(self):
        txt = self.ui.lineIDParcialidades.text().strip()
        if not txt.isdigit():
            self._actualizar_estado_boton_eliminar(None)
            return

        id_parcia = int(txt)
        try:
            parcialidad = self.service.buscar_por_id(id_parcia)  # type: ignore[call-arg]
        except Exception:
            return

        if parcialidad is None:
            # No existe: no llenamos el tipo (el usuario puede estar creando uno nuevo)
            # Si el Tipo venía de un registro cargado antes, se limpia para no
            # guardarlo por error con el ID nuevo
            if self._tipo_cargado is not None and self.ui.lineTipoParcialidades.text() == self._tipo_cargado:
                self.ui.lineTipoParcialidades.clear()
            self._tipo_cargado = None
            self._actualizar_estado_boton_eliminar(None)
            return

        # Existe: rellenamos automáticamente el campo "tipo"
        self.ui.lineTipoParcialidades.blockSignals(True)
        self.ui.lineTipoParcialidades.setText(parcialidad.tipoparcia)
        self.ui.lineTipoParcialidades.blockSignals(False)
        self._tipo_cargado = parcialidad.tipoparcia  # Registra el Tipo cargado
        self._actualizar_estado_boton_eliminar(parcialidad.idparcia)


    def on_nuevo(self):
        idParcialidades = self.ui.lineIDParcialidades.text()
        nombre = self.ui.lineTipoParcialidades.text()

        id_num = self._id_actual()
        if id_num is None:
            QMessageBox.warning(self, "Validación", "Ingrese el ID de la parcialidad.")
            self.ui.lineIDParcialidades.setFocus()
            return

        try:
            if self.service.buscar_por_id(id_num) is not None:  # type: ignore[call-arg]
                QMessageBox.warning(
                    self, "Registro existente",
                    f"Ya existe una parcialidad con el ID {id_num}. "
                    f"Use Actualizar para modificarla."
                )
                return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        try:
            self.service.crear(idParcialidades, nombre) # type: ignore[call-arg]
        except ValueError as e:
            QMessageBox.warning(self, "Validación", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        self.refrescar_tabla()          # <- aquí se actualiza la tabla

    def on_actualizar(self):
        idParcialidades = self._id_actual()
        if idParcialidades is None:
            QMessageBox.warning(self, "Validación", "Seleccione una parcialidad válido.")
            return
        try:
            self.service.actualizar(idParcialidades, self.ui.lineTipoParcialidades.text()) # type: ignore[call-arg]
        except ValueError as e:
            QMessageBox.warning(self, "Validación", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        self.refrescar_tabla()

    def on_eliminar(self):
        idParcialidades = self._id_actual()
        if idParcialidades is None:
            QMessageBox.warning(self, "Validación", "Seleccione una parcialidad válida.")
            return
        try:
            if self.service.tiene_hijos(idParcialidades):  # type: ignore[call-arg]
                QMessageBox.warning(
                    self, "Bloqueado",
                    f"La parcialidad {idParcialidades} tiene registros relacionados "
                    f"y no puede eliminarse."
                )
                self._actualizar_estado_boton_eliminar(idParcialidades)
                return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        if QMessageBox.question(
            self, "Confirmar",
            f"¿Eliminar parcialidad id={idParcialidades}?"
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            self.service.eliminar(idParcialidades)  # type: ignore[call-arg]
        except ValueError as e:
            QMessageBox.warning(self, "Bloqueado", str(e))
            self._actualizar_estado_boton_eliminar(idParcialidades)
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        self.refrescar_tabla()

    def on_buscar(self):
        idParcialidades = self._id_actual()
        if idParcialidades is None:
            QMessageBox.warning(self, "Validación", "Ingrese un ID numérico.")
            return
        try:
            Parcialidades = self.service.buscar_por_id(idParcialidades)  # type: ignore[call-arg]
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        if Parcialidades is None:
            QMessageBox.information(self, "Buscar", "No se encontró la parcialidad.")
            self.ui.pparcialidadesEliminar.setEnabled(False)
            self.ui.pparcialidadesEliminar.setToolTip("")
            return
        self.ui.lineTipoParcialidades.setText(Parcialidades.tipoparcia)
        self._tipo_cargado = Parcialidades.tipoparcia  # Registra el Tipo cargado
        self._actualizar_estado_boton_eliminar(Parcialidades.idparcia)

    def on_fila_seleccionada(self, index):
        parcialidad = self.table_model.get_Parcialidades_at(index.row())
        if not parcialidad:
            self.ui.pparcialidadesEliminar.setEnabled(False)
            self.ui.pparcialidadesEliminar.setToolTip("")
            return

        self.ui.lineIDParcialidades.blockSignals(True)
        self.ui.lineIDParcialidades.setText(str(parcialidad.idparcia))
        self.ui.lineIDParcialidades.blockSignals(False)

        self.ui.lineTipoParcialidades.setText(parcialidad.tipoparcia)
        self._tipo_cargado = parcialidad.tipoparcia  # Registra el Tipo cargado

        self._actualizar_estado_boton_eliminar(parcialidad.idparcia)

    def _aplicar_limites_a_widgets(self):
        # --- ID (numeric(9,0)) ---
        meta = self._limites.get("idparcia", {})
        max_digits = meta.get("max_digits", _FALLBACK_ID_DIGITS)
        max_value = meta.get("max_value", 10 ** max_digits - 1)
        self.ui.lineIDParcialidades.setMaxLength(max_digits)
        self.ui.lineIDParcialidades.setValidator(
            QIntValidator(0, max_value, self)
        )

        # --- Tipo (varchar) ---
        meta = self._limites.get("tipoparcia", {})
        max_len = meta.get("max_length", _FALLBACK_TIPO_LEN)
        self.ui.lineTipoParcialidades.setMaxLength(max_len)  