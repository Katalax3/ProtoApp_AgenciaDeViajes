import sys
from PySide6 import QtWidgets
from PySide6.QtWidgets import QMessageBox, QHeaderView
from PySide6.QtGui import QStandardItemModel, QStandardItem

from app.ui.Bancos_ui import Ui_VentanaBancos
from database.connection import get_db_connection


class VentanaBancos(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_VentanaBancos()
        self.ui.setupUi(self)

        # Configuración de comportamiento de la tabla (Idéntico a Parcialidades)
        self.ui.vistaBancos.setSelectionBehavior(self.ui.vistaBancos.SelectionBehavior.SelectRows)
        self.ui.vistaBancos.setSelectionMode(self.ui.vistaBancos.SelectionMode.SingleSelection)
        self.ui.vistaBancos.setEditTriggers(self.ui.vistaBancos.EditTrigger.NoEditTriggers)
        self.ui.vistaBancos.horizontalHeader().setStretchLastSection(True)

        # Conectar eventos de los botones y tabla
        self.ui.pbancosNuevo.clicked.connect(self.on_nuevo)
        self.ui.pbancosActualizar.clicked.connect(self.on_actualizar)
        self.ui.pbancosEliminar.clicked.connect(self.on_eliminar)
        self.ui.pbancosBuscar.clicked.connect(self.on_buscar)

        self.ui.vistaBancos.doubleClicked.connect(self.on_fila_seleccionada)

        self.refrescar_tabla()

    def refrescar_tabla(self, query="SELECT idbanco, nombre FROM banco ORDER BY idbanco ASC;"):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                registros = cursor.fetchall()
                cursor.close()

            # Usamos QStandardItemModel compatible con QTableView
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
        self.ui.lineIDBancos.clear()
        self.ui.lineNombreBancos.clear()

    def _id_actual(self):
        txt = self.ui.lineIDBancos.text().strip()
        return int(txt) if txt.isdigit() else None

    def on_nuevo(self):
        id_str = self.ui.lineIDBancos.text().strip()
        nombre = self.ui.lineNombreBancos.text().strip()
        
        if not id_str or not nombre:
            QMessageBox.warning(self, "Validación", "Complete el ID y el Nombre del Banco.")
            return

        try:
            id_banco = int(id_str)
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO banco (idbanco, nombre) VALUES (%s, %s);", (id_banco, nombre))
                conn.commit()
                cursor.close()
        except ValueError:
            QMessageBox.warning(self, "Validación", "El ID debe ser numérico.")
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        self.refrescar_tabla()

    def on_actualizar(self):
        id_banco = self._id_actual()
        nombre = self.ui.lineNombreBancos.text().strip()

        if id_banco is None or not nombre:
            QMessageBox.warning(self, "Validación", "Seleccione un banco válido e ingrese el nuevo nombre.")
            return

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE banco SET nombre = %s WHERE idbanco = %s;", (nombre, id_banco))
                conn.commit()
                cursor.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        self.refrescar_tabla()

    def on_eliminar(self):
        id_banco = self._id_actual()
        if id_banco is None:
            QMessageBox.warning(self, "Validación", "Seleccione un banco válido para eliminar.")
            return

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar si existen registros hijos asociados en la tabla 'tarjeta'
                cursor.execute("SELECT COUNT(*) FROM tarjeta WHERE idbanco = %s;", (id_banco,))
                resultado = cursor.fetchone()
                cantidad_hijos = resultado[0] if resultado else 0

                if cantidad_hijos > 0:
                    QMessageBox.warning(
                        self,
                        "No se puede eliminar",
                        f"Este banco tiene {cantidad_hijos} tarjeta(s) asociada(s).\n"
                        "Debe eliminar o reasignar las tarjetas dependientes antes de borrar el banco."
                    )
                    cursor.close()
                    return

                if QMessageBox.question(self, "Confirmar", f"¿Eliminar banco id={id_banco}?") != QMessageBox.StandardButton.Yes:
                    cursor.close()
                    return

                cursor.execute("DELETE FROM banco WHERE idbanco = %s;", (id_banco,))
                conn.commit()
                cursor.close()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        self.limpiar_formulario()
        self.refrescar_tabla()

    def on_buscar(self):
        id_str = self.ui.lineIDBancos.text().strip()
        nombre = self.ui.lineNombreBancos.text().strip()

        if id_str.isdigit():
            query = f"SELECT idbanco, nombre FROM banco WHERE idbanco = {id_str};"
        elif nombre:
            query = f"SELECT idbanco, nombre FROM banco WHERE nombre ILIKE '%{nombre}%';"
        else:
            query = "SELECT idbanco, nombre FROM banco ORDER BY idbanco ASC;"

        self.refrescar_tabla(query)

    def on_fila_seleccionada(self, index):
        row = index.row()
        model = self.ui.vistaBancos.model()
        if model:
            id_banco = model.item(row, 0).text()
            nombre = model.item(row, 1).text()
            
            self.ui.lineIDBancos.setText(id_banco)
            self.ui.lineNombreBancos.setText(nombre)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana = VentanaBancos()
    ventana.show()
    sys.exit(app.exec())