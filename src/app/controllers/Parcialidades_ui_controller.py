from PySide6.QtWidgets import QWidget, QMessageBox
from PySide6.QtCore import Qt
from src.app.services import ParcialidadesService
from src.app.ui import Ui_VentanaParcialidades
from src.app.presenters.parcialidades_table_model import ParcialidadesTableModel


class VentanaParcialidades(QWidget):
    def __init__(self, Parcialidades_service):
        super().__init__()
        self.ui = Ui_VentanaParcialidades()
        self.ui.setupUi(self)

        self.service: ParcialidadesService = Parcialidades_service

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

        self.ui.vistaParcialidades.doubleClicked.connect(self.on_fila_seleccionada)

        self.ui.pparcialidadesEliminar.setEnabled(False)

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


    def on_nuevo(self):
        idParcialidades = self.ui.lineIDParcialidades.text()
        nombre = self.ui.lineTipoParcialidades.text()
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
        Parcialidades = self.service.buscar_por_id(idParcialidades)  # type: ignore[call-arg]
        if Parcialidades is None:
            QMessageBox.information(self, "Buscar", "No se encontró la parcialidad.")
            self.ui.pparcialidadesEliminar.setEnabled(False)
            self.ui.pparcialidadesEliminar.setToolTip("")
            return
        self.ui.lineTipoParcialidades.setText(Parcialidades.tipoparcia)
        self._actualizar_estado_boton_eliminar(Parcialidades.idparcia)

    def on_fila_seleccionada(self, index):
        Parcialidades = self.table_model.get_Parcialidades_at(index.row())
        if not Parcialidades:
            self.ui.pparcialidadesEliminar.setEnabled(False)
            self.ui.pparcialidadesEliminar.setToolTip("")
            return

        self.ui.lineIDParcialidades.setText(str(Parcialidades.idparcia))
        self.ui.lineTipoParcialidades.setText(Parcialidades.tipoparcia)

        self._actualizar_estado_boton_eliminar(Parcialidades.idparcia)    