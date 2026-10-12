from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QIntValidator, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QMessageBox

from app.services import PaisesService
from app.ui import Ui_VentanaPaises
from app.presenters.paises_table_model import PaisesTableModel

# solo letras, acentos y espacios
PATRON_NOMBRE = r"[A-Za-zÁÉÍÓÚÜáéíóúüÑñ ]*"
ID_MAX = 999999999   # NUMERIC(9)


class VentanaPaises(QWidget):
    def __init__(self, paises_service: PaisesService | None = None):
        super().__init__()
        self.ui = Ui_VentanaPaises()
        self.ui.setupUi(self)

        self.service: PaisesService = paises_service or PaisesService()

        # Validaciones en las cajas: longitud máxima y tipo de dato
        self.ui.lineIDPaises.setMaxLength(9)
        self.ui.lineNombrePaises.setMaxLength(30)
        self.ui.lineIDPaises.setValidator(QIntValidator(1, ID_MAX, self))
        self.ui.lineNombrePaises.setValidator(
            QRegularExpressionValidator(QRegularExpression(PATRON_NOMBRE), self)
        )

        self.table_model = PaisesTableModel(self)
        self.ui.vistaPaises.setModel(self.table_model)

        self.ui.vistaPaises.setSelectionBehavior(
            self.ui.vistaPaises.SelectionBehavior.SelectRows
        )
        self.ui.vistaPaises.setSelectionMode(
            self.ui.vistaPaises.SelectionMode.SingleSelection
        )
        self.ui.vistaPaises.setEditTriggers(
            self.ui.vistaPaises.EditTrigger.NoEditTriggers
        )
        self.ui.vistaPaises.horizontalHeader().setStretchLastSection(True)

        self.ui.ppaisesNuevo.clicked.connect(self.on_nuevo)
        self.ui.ppaisesActualizar.clicked.connect(self.on_actualizar)
        self.ui.ppaisesEliminar.clicked.connect(self.on_eliminar)
        self.ui.ppaisesBuscar.clicked.connect(self.on_buscar)

        self.ui.vistaPaises.doubleClicked.connect(self.on_fila_seleccionada)

        # Orden del cursor con Tab
        self.setTabOrder(self.ui.lineIDPaises, self.ui.lineNombrePaises)
        self.setTabOrder(self.ui.lineNombrePaises, self.ui.ppaisesNuevo)
        self.setTabOrder(self.ui.ppaisesNuevo, self.ui.ppaisesActualizar)
        self.setTabOrder(self.ui.ppaisesActualizar, self.ui.ppaisesBuscar)
        self.setTabOrder(self.ui.ppaisesBuscar, self.ui.ppaisesEliminar)
        self.ui.lineIDPaises.setFocus()

        self.refrescar_tabla()

    def refrescar_tabla(self):
        try:
            paises = self.service.listar()  # type: ignore[call-arg]
            self.table_model.set_data(paises)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la lista:\n{e}")

    def limpiar_formulario(self):
        self.ui.lineIDPaises.clear()
        self.ui.lineNombrePaises.clear()
        self.ui.vistaPaises.clearSelection()
        self.ui.lineIDPaises.setFocus()

    def _id_actual(self):
        txt = self.ui.lineIDPaises.text().strip()
        return int(txt) if txt.isdigit() else None

    def on_nuevo(self):
        idpais = self.ui.lineIDPaises.text()
        nombre = self.ui.lineNombrePaises.text()
        try:
            self.service.crear(idpais, nombre)  # type: ignore[call-arg]
        except ValueError as e:
            QMessageBox.warning(self, "Validación", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        self.refrescar_tabla()

    def on_actualizar(self):
        idpais = self._id_actual()
        if idpais is None:
            QMessageBox.warning(self, "Validación", "Seleccione un país válido.")
            return
        try:
            self.service.actualizar(idpais, self.ui.lineNombrePaises.text())  # type: ignore[call-arg]
        except ValueError as e:
            QMessageBox.warning(self, "Validación", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        self.refrescar_tabla()

    def on_eliminar(self):
        idpais = self._id_actual()
        if idpais is None:
            QMessageBox.warning(self, "Validación", "Seleccione un país válido.")
            return
        if QMessageBox.question(self, "Confirmar",
                                f"¿Eliminar país id={idpais}?") != QMessageBox.StandardButton.Yes:
            return
        try:
            self.service.eliminar(idpais)  # type: ignore[call-arg]
        except ValueError as e:
            QMessageBox.warning(self, "No se puede eliminar", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        self.refrescar_tabla()

    def on_buscar(self):
        idpais = self._id_actual()
        if idpais is None:
            QMessageBox.warning(self, "Validación", "Ingrese un ID numérico.")
            return
        try:
            pais = self.service.buscar_por_id(idpais)  # type: ignore[call-arg]
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar:\n{e}")
            return
        if pais is None:
            QMessageBox.information(self, "Buscar", "No se encontró el país.")
            return
        self.ui.lineNombrePaises.setText(pais.nombre)

    def on_fila_seleccionada(self, index):
        pais = self.table_model.get_pais_at(index.row())
        if pais:
            self.ui.lineIDPaises.setText(str(pais.idpais))
            self.ui.lineNombrePaises.setText(pais.nombre)
