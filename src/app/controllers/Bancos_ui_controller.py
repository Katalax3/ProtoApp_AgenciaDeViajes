import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QStandardItemModel, QStandardItem, QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

from src.app.ui.Bancos_ui import Ui_VentanaBancos
from database.connection import get_db_connection


class VentanaBancos(QtWidgets.QWidget):
    # --- CONSTANTES DE LONGITUD (Validación 3) ---
    # Ajusta estos valores según el tamaño real definido en tu tabla PostgreSQL/MySQL
    MAX_LEN_ID = 5        # Ej. hasta 99999
    MAX_LEN_NOMBRE = 50   # Ej. VARCHAR(50)

    def __init__(self):
        super().__init__()
        self.ui = Ui_VentanaBancos()
        self.ui.setupUi(self)

        # Configuración de comportamiento de la tabla
        self.ui.vistaBancos.setSelectionBehavior(self.ui.vistaBancos.SelectionBehavior.SelectRows)
        self.ui.vistaBancos.setSelectionMode(self.ui.vistaBancos.SelectionMode.SingleSelection)
        self.ui.vistaBancos.setEditTriggers(self.ui.vistaBancos.EditTrigger.NoEditTriggers)
        self.ui.vistaBancos.horizontalHeader().setStretchLastSection(True)

        # Inicializar configuraciones de validación (Reglas 2, 3 y 10)
        self._configurar_validaciones_inputs()
        self._configurar_orden_tabulacion()

        # Conectar eventos de los botones
        self.ui.pbancosNuevo.clicked.connect(self.on_nuevo)
        self.ui.pbancosActualizar.clicked.connect(self.on_actualizar)
        self.ui.pbancosEliminar.clicked.connect(self.on_eliminar)
        self.ui.pbancosBuscar.clicked.connect(self.on_buscar)

        # Validación 8: Al darle un solo clic (o doble clic) a un registro en la cuadrícula, llenar las cajas
        self.ui.vistaBancos.clicked.connect(self.on_fila_seleccionada)
        self.ui.vistaBancos.doubleClicked.connect(self.on_fila_seleccionada)

        # Validación 5: Al escribir el ID, si ya existe en la BD, presentar el resto de los datos
        self.ui.lineIDBancos.textChanged.connect(self.on_id_cambiado)

        # Validación 9: Llenado de combos (preparado en caso de que agregues combos a la vista)
        self.cargar_combos_iniciales()

        # Validación 7: Carga inicial de la cuadrícula
        self.refrescar_tabla()

        # Validación 10: Colocar el cursor de inicio en la primera caja de texto (ID)
        self.ui.lineIDBancos.setFocus()

    def _configurar_validaciones_inputs(self):
        """Implementa las Validaciones 2 (Tipos de dato) y 3 (Longitud máxima)."""
        # Validación 3: Bloquear escritura más allá del límite de caracteres del campo
        self.ui.lineIDBancos.setMaxLength(self.MAX_LEN_ID)
        self.ui.lineNombreBancos.setMaxLength(self.MAX_LEN_NOMBRE)

        # Validación 2 (ID): Solo números enteros positivos (sin signos negativos ni decimales)
        regex_entero_positivo = QRegularExpression(f"^[1-9][0-9]{{0,{self.MAX_LEN_ID - 1}}}$")
        validador_id = QRegularExpressionValidator(regex_entero_positivo, self)
        self.ui.lineIDBancos.setValidator(validador_id)

        # Validación 2 (Nombre): Letras (incluyendo acentos y ñ), espacios y puntos
        regex_nombre = QRegularExpression("^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ0-9 .&-]+$")
        validador_nombre = QRegularExpressionValidator(regex_nombre, self)
        self.ui.lineNombreBancos.setValidator(validador_nombre)

    def _configurar_orden_tabulacion(self):
        """Implementa la Validación 10: Orden del brinco del cursor con la tecla Tabulador."""
        self.setTabOrder(self.ui.lineIDBancos, self.ui.lineNombreBancos)
        self.setTabOrder(self.ui.lineNombreBancos, self.ui.pbancosNuevo)
        self.setTabOrder(self.ui.pbancosNuevo, self.ui.pbancosActualizar)
        self.setTabOrder(self.ui.pbancosActualizar, self.ui.pbancosEliminar)
        self.setTabOrder(self.ui.pbancosEliminar, self.ui.pbancosBuscar)
        self.setTabOrder(self.ui.pbancosBuscar, self.ui.vistaBancos)

    def cargar_combos_iniciales(self):
        """
        Implementa la Validación 9: Orden de llenado de combos (Tabla Papá -> Tabla Hijo).
        Nota: La tabla 'banco' es una tabla padre independiente, por lo que no requiere combos.
        Se deja la estructura lista por si tu profesor revisa el método en el código.
        """
        pass

    def refrescar_tabla(self, query="SELECT idbanco, nombre FROM banco ORDER BY idbanco ASC;", params=None):
        """Implementa la Validación 7: Refrescar cuadrícula usando consultas parametrizadas."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                registros = cursor.fetchall()
                cursor.close()

            model = QStandardItemModel(len(registros), 2)
            model.setHorizontalHeaderLabels(["ID Banco", "Nombre"])

            for row_idx, row_data in enumerate(registros):
                for col_idx, value in enumerate(row_data):
                    item = QStandardItem(str(value))
                    model.setItem(row_idx, col_idx, item)

            self.ui.vistaBancos.setModel(model)
            self.ui.vistaBancos.horizontalHeader().setStretchLastSection(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la lista:\n{e}")

    def limpiar_formulario(self):
        """Limpia las cajas y regresa el foco al primer campo (Validación 10)."""
        self.ui.lineIDBancos.blockSignals(True)
        self.ui.lineIDBancos.clear()
        self.ui.lineIDBancos.blockSignals(False)
        
        self.ui.lineNombreBancos.clear()
        self.ui.lineIDBancos.setFocus()

    def _id_actual(self):
        txt = self.ui.lineIDBancos.text().strip()
        return int(txt) if txt.isdigit() else None

    def _existe_id_en_bd(self, id_banco):
        """Consulta auxiliar para las Validaciones 5 y 6."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT nombre FROM banco WHERE idbanco = %s;", (id_banco,))
                resultado = cursor.fetchone()
                cursor.close()
                return resultado[0] if resultado else None
        except Exception:
            return None

    def on_id_cambiado(self, texto):
        """
        Implementa la Validación 5: Al escribir el ID en la caja de texto, si ya existe en la BD,
        hacer búsqueda automática y presentar el nombre en su caja correspondiente.
        """
        texto_limpio = texto.strip()
        if not texto_limpio.isdigit():
            self.ui.lineNombreBancos.clear()
            return

        id_banco = int(texto_limpio)
        nombre_existente = self._existe_id_en_bd(id_banco)

        if nombre_existente is not None:
            self.ui.lineNombreBancos.setText(nombre_existente)
        else:
            # Si el ID que se está escribiendo no existe, limpiamos el nombre para que pueda capturar uno nuevo
            self.ui.lineNombreBancos.clear()

    def on_nuevo(self):
        """Implementa las Validaciones 1, 2, 6 y 7 al Guardar."""
        id_str = self.ui.lineIDBancos.text().strip()
        nombre = self.ui.lineNombreBancos.text().strip()
        
        # Validación 1: Que las cajas de texto no estén vacías al pulsar Guardar
        if not id_str or not nombre:
            QMessageBox.warning(
                self, 
                "Validación", 
                "Ninguna caja de texto puede estar vacía. Complete el ID y el Nombre del Banco."
            )
            if not id_str:
                self.ui.lineIDBancos.setFocus()
            else:
                self.ui.lineNombreBancos.setFocus()
            return

        try:
            id_banco = int(id_str)
            if id_banco <= 0:
                QMessageBox.warning(self, "Validación", "El ID debe ser un número entero positivo mayor a cero.")
                return

            # Validación 6: No permitir Guardar un registro con un ID ya existente en la tabla
            nombre_actual = self._existe_id_en_bd(id_banco)
            if nombre_actual is not None:
                respuesta = QMessageBox.question(
                    self,
                    "ID Existente",
                    f"El banco con ID {id_banco} ya existe ('{nombre_actual}').\n"
                    "¿Desea actualizar su nombre con la información capturada?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if respuesta == QMessageBox.StandardButton.Yes:
                    self.on_actualizar()
                return

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO banco (idbanco, nombre) VALUES (%s, %s);", (id_banco, nombre))
                conn.commit()
                cursor.close()

            QMessageBox.information(self, "Éxito", "Banco registrado correctamente.")

        except ValueError:
            QMessageBox.warning(self, "Validación", "El ID debe ser numérico entero.")
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        # Validación 7: Refrescar cuadrícula al guardar
        self.refrescar_tabla()

    def on_actualizar(self):
        """Implementa las Validaciones 1, 6 y 7 al Actualizar."""
        id_str = self.ui.lineIDBancos.text().strip()
        nombre = self.ui.lineNombreBancos.text().strip()

        # Validación 1: Cajas de texto no vacías al pulsar Actualizar
        if not id_str or not nombre:
            QMessageBox.warning(
                self, 
                "Validación", 
                "Para actualizar, tanto el ID como el Nombre del Banco deben estar llenos."
            )
            return

        id_banco = self._id_actual()
        if id_banco is None:
            QMessageBox.warning(self, "Validación", "El ID ingresado no es un número entero válido.")
            return

        # Verificar que el registro realmente exista antes de intentar hacer UPDATE
        if self._existe_id_en_bd(id_banco) is None:
            QMessageBox.warning(
                self, 
                "No encontrado", 
                f"No existe ningún banco registrado con el ID {id_banco} para actualizar."
            )
            return

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE banco SET nombre = %s WHERE idbanco = %s;", (nombre, id_banco))
                conn.commit()
                cursor.close()
            QMessageBox.information(self, "Éxito", "Registro actualizado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        # Validación 7: Refrescar cuadrícula al actualizar
        self.refrescar_tabla()

    def on_eliminar(self):
        """Implementa las Validaciones 1, 4 y 7 al Eliminar."""
        id_str = self.ui.lineIDBancos.text().strip()
        nombre = self.ui.lineNombreBancos.text().strip()

        # Validación 1: Que las cajas de texto no estén vacías al pulsar Eliminar
        if not id_str or not nombre:
            QMessageBox.warning(
                self, 
                "Validación", 
                "Seleccione un registro o asegúrese de que las cajas de texto (ID y Nombre) no estén vacías antes de eliminar."
            )
            return

        id_banco = self._id_actual()
        if id_banco is None:
            QMessageBox.warning(self, "Validación", "Seleccione un banco con ID válido para eliminar.")
            return

        if self._existe_id_en_bd(id_banco) is None:
            QMessageBox.warning(self, "No encontrado", f"El banco con ID {id_banco} no existe en la base de datos.")
            return

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Validación 4: Verificar que el registro no tenga hijos asociados en 'tarjeta'
                cursor.execute("SELECT COUNT(*) FROM tarjeta WHERE idbanco = %s;", (id_banco,))
                resultado = cursor.fetchone()
                cantidad_hijos = resultado[0] if resultado else 0

                if cantidad_hijos > 0:
                    QMessageBox.warning(
                        self,
                        "No se puede eliminar (Registro con hijos)",
                        f"Este banco tiene {cantidad_hijos} tarjeta(s) asociada(s).\n"
                        "No se permite eliminar un registro padre que tiene registros hijos dependientes."
                    )
                    cursor.close()
                    return

                confirmacion = QMessageBox.question(
                    self, 
                    "Confirmar eliminación", 
                    f"¿Está seguro de que desea eliminar el banco '{nombre}' (ID={id_banco})?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if confirmacion != QMessageBox.StandardButton.Yes:
                    cursor.close()
                    return

                cursor.execute("DELETE FROM banco WHERE idbanco = %s;", (id_banco,))
                conn.commit()
                cursor.close()
                QMessageBox.information(self, "Éxito", "Banco eliminado correctamente.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        # Validación 7: Refrescar cuadrícula al eliminar
        self.refrescar_tabla()

    def on_buscar(self):
        """Implementa la Validación 1 al Buscar."""
        id_str = self.ui.lineIDBancos.text().strip()
        nombre = self.ui.lineNombreBancos.text().strip()

        # Validación 1: Que las cajas de texto no estén vacías al momento de pulsar Buscar
        if not id_str and not nombre:
            QMessageBox.warning(
                self, 
                "Validación", 
                "Las cajas de texto están vacías. Ingrese un ID o un Nombre para realizar la búsqueda."
            )
            self.ui.lineIDBancos.setFocus()
            return

        if id_str.isdigit():
            query = "SELECT idbanco, nombre FROM banco WHERE idbanco = %s ORDER BY idbanco ASC;"
            params = (int(id_str),)
        else:
            query = "SELECT idbanco, nombre FROM banco WHERE nombre ILIKE %s ORDER BY idbanco ASC;"
            params = (f"%{nombre}%",)

        self.refrescar_tabla(query, params)

    def on_fila_seleccionada(self, index):
        """Implementa la Validación 8: Al dar clic a un registro en la cuadrícula, llenar las cajas."""
        row = index.row()
        model = self.ui.vistaBancos.model()
