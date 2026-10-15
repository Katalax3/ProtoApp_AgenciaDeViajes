import re
from typing import List, Optional
from psycopg import Cursor, Connection
from app.services.base_service import BaseService, with_db
from app.dal import BaseDAL
from app.models.Pais import Pais

# solo letras, acentos y espacios
PATRON_NOMBRE = re.compile(r"^[A-Za-zÁÉÍÓÚÜáéíóúüÑñ ]+$")
ID_MAX = 999999999   # NUMERIC(9)
NOMBRE_MAX = 30


class PaisDuplicadoError(ValueError):
    """Se intentó guardar un país con un ID que ya existe en la tabla."""


class PaisesService(BaseService):
    def __init__(self) -> None:
        self.dal = BaseDAL(table_name="pais", model_class=Pais)

    @staticmethod
    def _validar_id(idpais) -> int:
        try:
            idpais = int(idpais)
        except (TypeError, ValueError):
            raise ValueError("El ID del país debe ser un número entero.")
        if not 1 <= idpais <= ID_MAX:
            raise ValueError(f"El ID del país debe estar entre 1 y {ID_MAX}.")
        return idpais

    @staticmethod
    def _validar_nombre(nombre: str) -> str:
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValueError("El nombre del país no puede estar vacío.")
        if len(nombre) > NOMBRE_MAX:
            raise ValueError(f"El nombre es demasiado largo (máximo {NOMBRE_MAX} caracteres).")
        if not PATRON_NOMBRE.match(nombre):
            raise ValueError("El nombre solo puede tener letras y espacios.")
        return nombre

    @with_db
    def listar(self, limit: int = 100, offset: int = 0, *, cur: Cursor, conn: Connection) -> List[Pais]:
        paises = self.dal.get_all(cur, limit=limit, offset=offset)
        return sorted(paises, key=lambda p: p.idpais)

    @with_db
    def buscar_por_id(self, idpais: int, *, cur: Cursor, conn: Connection) -> Optional[Pais]:
        return self.dal.get_by_id(cur, id_value=idpais, id_column="idpais")

    @with_db
    def buscar_con_hijos(self, idpais: int, *, cur: Cursor, conn: Connection) -> tuple[Optional[Pais], int]:
        """Regresa (país, # de ciudades hijas). Si no existe: (None, 0)."""
        pais = self.dal.get_by_id(cur, id_value=idpais, id_column="idpais")
        if pais is None:
            return None, 0
        return pais, self._contar_ciudades(cur, idpais)

    @staticmethod
    def _contar_ciudades(cur: Cursor, idpais: int) -> int:
        cur.execute("SELECT COUNT(*) AS total FROM ciudad WHERE idpais = %(id)s", {"id": idpais})
        return int(cur.fetchone()["total"])

    @with_db
    def crear(self, idpais: str, nombre: str, *, cur: Cursor, conn: Connection) -> Pais | None:
        idpais = self._validar_id(idpais)
        nombre = self._validar_nombre(nombre)

        if self.dal.get_by_id(cur, id_value=idpais, id_column="idpais"):
            conn.rollback()
            raise PaisDuplicadoError(f"Ya existe un país con el ID {idpais}.")

        row = self.dal.create(cur, data={"idpais": idpais, "nombre": nombre})
        if not row:
            conn.rollback()
            raise ValueError("No se pudo crear el país")
        conn.commit()
        return row

    @with_db
    def actualizar(self, idpais: int, nombre: str, *, cur: Cursor, conn: Connection) -> Pais:
        idpais = self._validar_id(idpais)
        nombre = self._validar_nombre(nombre)
        row = self.dal.update(cur, id_value=idpais, data={"nombre": nombre}, id_column="idpais")
        if row is None:
            conn.rollback()
            raise ValueError(f"No existe el país con id {idpais}.")
        conn.commit()
        return row

    @with_db
    def eliminar(self, idpais: int, *, cur: Cursor, conn: Connection) -> None:
        idpais = self._validar_id(idpais)
        pais = self.dal.get_by_id(cur, id_value=idpais, id_column="idpais")
        if pais is None:
            conn.rollback()
            raise ValueError(f"No existe el país con id {idpais}.")

        # no eliminar si tiene hijos (ciudades)
        ciudades = self._contar_ciudades(cur, idpais)
        if ciudades > 0:
            conn.rollback()
            raise ValueError(
                f"{pais.nombre} tiene {ciudades} ciudad(es) registrada(s). Primero elimine sus ciudades."
            )

        if not self.dal.delete(cur, id_value=idpais, id_column="idpais"):
            conn.rollback()
            raise ValueError(f"No se pudo eliminar el país con id {idpais}.")
        conn.commit()