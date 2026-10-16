from typing import List
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from src.app.models.Pais import Pais


class PaisesTableModel(QAbstractTableModel):
    HEADERS = ["ID", "Nombre"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: List[Pais] = []

    def set_data(self, paises: List[Pais]):
        self.beginResetModel()
        self._data = list(paises)
        self.endResetModel()

    def get_pais_at(self, row: int) -> Pais | None:
        if 0 <= row < len(self._data):
            return self._data[row]
        return None

    def rowCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._data)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.HEADERS)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        Pais = self._data[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return str(Pais.idpais)
            if index.column() == 1:
                return Pais.nombre
        if role == Qt.ItemDataRole.TextAlignmentRole and index.column() == 0:
            return int(Qt.AlignmentFlag.AlignCenter)
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return None