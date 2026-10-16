from PySide6.QtCore import QRegularExpression, QTimer
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QMessageBox

from src.app.services.paises_service import PaisesService, PaisDuplicadoError
from src.app.ui import Ui_VentanaPaises
from src.app.presenters.paises_table_model import PaisesTableModel

# ---- Definición de los campos (según la tabla Pais) -------------------------
# idPais  NUMERIC(9)  -> solo dígitos, entero positivo, máx. 9 caracteres
# nombre  VARCHAR(30) -> solo letras/acentos/espacios, máx. 30 caracteres
ID_LONGITUD = 9
NOMBRE_LONGITUD = 30
PATRON_ID = r"[1-9][0-9]{0,8}"                      # sin ceros a la izquierda, sin signo, sin decimales
PATRON_NOMBRE = r"[A-Za-zÁÉÍÓÚÜáéíóúüÑñ ]*"        # solo letras, acentos y espacios

TOOLTIP_ELIMINAR = "Elimina el país capturado"


class VentanaPaises(QWidget):
    def __init__(self, paises_service: PaisesService | None = None):
        super().__init__()
        self.ui = Ui_VentanaPaises()
        self.ui.setupUi(self)

        self.service: PaisesService = paises_service or PaisesService()

        # True cuando el nombre de la caja fue llenado automáticamente por una búsqueda
        self._nombre_autocompletado = False

        # --- Validaciones 2 y 3: tipo de dato y longitud máxima ---------------
        self.ui.lineIDPaises.setMaxLength(ID_LONGITUD)
        self.ui.lineNombrePaises.setMaxLength(NOMBRE_LONGITUD)
        self.ui.lineIDPaises.setValidator(
            QRegularExpressionValidator(QRegularExpression(PATRON_ID), self)
        )
        self.ui.lineNombrePaises.setValidator(
            QRegularExpressionValidator(QRegularExpression(PATRON_NOMBRE), self)
        )

        # --- Cuadrícula --------------------------------------------------------
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

        # --- Botones -----------------------------------------------------------
        self.ui.ppaisesNuevo.clicked.connect(self.on_nuevo)
        self.ui.ppaisesActualizar.clicked.connect(self.on_actualizar)
        self.ui.ppaisesEliminar.clicked.connect(self.on_eliminar)
        self.ui.ppaisesBuscar.clicked.connect(self.on_buscar)
        self.ui.ppaisesEliminar.setToolTip(TOOLTIP_ELIMINAR)

        # --- Validación 8: un clic en la cuadrícula llena las cajas ------------
        self.ui.vistaPaises.clicked.connect(self.on_fila_seleccionada)

        # --- Validación 5: al escribir un ID existente se cargan sus datos -----
        self._timer_busqueda = QTimer(self)
        self._timer_busqueda.setSingleShot(True)
        self._timer_busqueda.setInterval(250)   # espera a que el usuario termine de teclear
        self._timer_busqueda.timeout.connect(self._buscar_automatico)
        self.ui.lineIDPaises.textChanged.connect(self._on_id_cambiado)
        self.ui.lineNombrePaises.textEdited.connect(self._on_nombre_editado)

        # --- Validación 10: orden del cursor -----------------------------------
        self.ui.lineIDPaises.returnPressed.connect(self.ui.lineNombrePaises.setFocus)
        self.ui.lineNombrePaises.returnPressed.connect(self.ui.ppaisesNuevo.setFocus)
        self.setTabOrder(self.ui.lineIDPaises, self.ui.lineNombrePaises)
        self.setTabOrder(self.ui.lineNombrePaises, self.ui.ppaisesNuevo)
        self.setTabOrder(self.ui.ppaisesNuevo, self.ui.ppaisesActualizar)
        self.setTabOrder(self.ui.ppaisesActualizar, self.ui.ppaisesBuscar)
        self.setTabOrder(self.ui.ppaisesBuscar, self.ui.ppaisesEliminar)
        self.setTabOrder(self.ui.ppaisesEliminar, self.ui.vistaPaises)
        self.ui.lineIDPaises.setFocus()

        self.refrescar_tabla()

    def showEvent(self, event):
        super().showEvent(event)
        # el cursor inicia siempre en la caja del ID al abrir la ventana
        QTimer.singleShot(0, self.ui.lineIDPaises.setFocus)

    # ------------------------------------------------------------------ utilidades
    def refrescar_tabla(self):
        """Validación 7: recarga la cuadrícula."""
        try:
            self.table_model.set_data(self.service.listar())  # type: ignore[call-arg]
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la lista:\n{e}")

    def limpiar_formulario(self):
        self._timer_busqueda.stop()
        self._nombre_autocompletado = False
        self.ui.lineIDPaises.clear()
        self.ui.lineNombrePaises.clear()
        self.ui.vistaPaises.clearSelection()
        self._set_eliminar_habilitado(True)
        self.ui.lineIDPaises.setFocus()

    def _id_actual(self):
        txt = self.ui.lineIDPaises.text().strip()
        return int(txt) if txt.isdigit() else None

    def _nombre_actual(self) -> str:
        return self.ui.lineNombrePaises.text().strip()

    def _aviso(self, titulo: str, mensaje: str, campo=None):
        QMessageBox.warning(self, titulo, mensaje)
        if campo is not None:
            campo.setFocus()

    # --- Validación 1: cajas no vacías -----------------------------------------
    def _validar_id_capturado(self) -> int | None:
        """Para Buscar y Eliminar solo se necesita el ID."""
        idpais = self._id_actual()
        if idpais is None:
            self._aviso("Validación", "Capture el ID del país.", self.ui.lineIDPaises)
        return idpais

    def _validar_formulario_completo(self) -> tuple[int, str] | None:
        """Para Guardar (insert/update) se necesitan ID y nombre."""
        idpais = self._validar_id_capturado()
        if idpais is None:
            return None
        nombre = self._nombre_actual()
        if not nombre:
            self._aviso("Validación", "Capture el nombre del país.", self.ui.lineNombrePaises)
            return None
        return idpais, nombre

    # --- Validación 4: botón Eliminar deshabilitado si hay hijos ---------------
    def _set_eliminar_habilitado(self, habilitado: bool, motivo: str = ""):
        btn = self.ui.ppaisesEliminar
        btn.setEnabled(habilitado)
        btn.setToolTip(TOOLTIP_ELIMINAR if habilitado else motivo)

    def _actualizar_estado_eliminar(self, pais, ciudades: int):
        if pais is not None and ciudades > 0:
            self._set_eliminar_habilitado(
                False,
                f"No se puede eliminar {pais.nombre}: tiene {ciudades} ciudad(es) registrada(s). "
                "Elimine primero sus ciudades.",
            )
        else:
            self._set_eliminar_habilitado(True)

    # --- Validación 5: búsqueda automática por ID -------------------------------
    def _on_id_cambiado(self, _texto):
        self._timer_busqueda.start()

    def _on_nombre_editado(self, _texto):
        self._nombre_autocompletado = False

    def _consultar(self, idpais: int):
        """Busca el país y sus hijos. Regresa (pais, ciudades) o None si falló."""
        try:
            return self.service.buscar_con_hijos(idpais)  # type: ignore[call-arg]
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar:\n{e}")
            return None

    def _mostrar_pais(self, pais, ciudades: int):
        self.ui.lineNombrePaises.setText(pais.nombre)
        self._nombre_autocompletado = True
        self._actualizar_estado_eliminar(pais, ciudades)

    def _buscar_automatico(self):
        idpais = self._id_actual()
        if idpais is None:
            if self._nombre_autocompletado:
                self.ui.lineNombrePaises.clear()
                self._nombre_autocompletado = False
            self._set_eliminar_habilitado(True)
            return
        resultado = self._consultar(idpais)
        if resultado is None:
            return
        pais, ciudades = resultado
        if pais is not None:
            self._mostrar_pais(pais, ciudades)
        else:
            # ID nuevo: se quita lo que se había autocompletado de otro registro
            if self._nombre_autocompletado:
                self.ui.lineNombrePaises.clear()
                self._nombre_autocompletado = False
            self._set_eliminar_habilitado(True)

    # ----------------------------------------------------------------- botones
    def on_nuevo(self):
        datos = self._validar_formulario_completo()
        if datos is None:
            return
        idpais, nombre = datos
        try:
            self.service.crear(str(idpais), nombre)  # type: ignore[call-arg]
        except PaisDuplicadoError:
            # Validación 6: el ID ya existe -> avisar y ofrecer actualizar
            resp = QMessageBox.question(
                self, "Registro existente",
                f"Ya existe un país con el ID {idpais}.\n¿Desea actualizar su nombre?",
            )
            if resp == QMessageBox.StandardButton.Yes:
                self.on_actualizar()
            else:
                self.ui.lineIDPaises.setFocus()
                self.ui.lineIDPaises.selectAll()
            return
        except ValueError as e:
            QMessageBox.warning(self, "Validación", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        self.refrescar_tabla()

    def on_actualizar(self):
        datos = self._validar_formulario_completo()
        if datos is None:
            return
        idpais, nombre = datos
        try:
            self.service.actualizar(idpais, nombre)  # type: ignore[call-arg]
        except ValueError as e:
            QMessageBox.warning(self, "Validación", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        self.refrescar_tabla()

    def on_eliminar(self):
        idpais = self._validar_id_capturado()
        if idpais is None:
            return
        if QMessageBox.question(self, "Confirmar",
                                f"¿Eliminar país id={idpais}?") != QMessageBox.StandardButton.Yes:
            return
        try:
            self.service.eliminar(idpais)  # type: ignore[call-arg]
        except ValueError as e:
            QMessageBox.warning(self, "No se puede eliminar", str(e))
            self._buscar_automatico()   # refresca el estado del botón
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        self.refrescar_tabla()

    def on_buscar(self):
        idpais = self._validar_id_capturado()
        if idpais is None:
            return
        resultado = self._consultar(idpais)
        if resultado is None:
            return
        pais, ciudades = resultado
        if pais is None:
            QMessageBox.information(self, "Buscar", "No se encontró el país.")
            self.ui.lineIDPaises.setFocus()
            return
        self._mostrar_pais(pais, ciudades)

    def on_fila_seleccionada(self, index):
        """Validación 8: clic en la cuadrícula -> datos a las cajas de texto."""
        pais = self.table_model.get_pais_at(index.row())
        if not pais:
            return
        self._timer_busqueda.stop()
        self.ui.lineIDPaises.blockSignals(True)
        self.ui.lineIDPaises.setText(str(pais.idpais))
        self.ui.lineIDPaises.blockSignals(False)
        resultado = self._consultar(pais.idpais)
        if resultado is None:
            return
        encontrado, ciudades = resultado
        self._mostrar_pais(encontrado or pais, ciudades)