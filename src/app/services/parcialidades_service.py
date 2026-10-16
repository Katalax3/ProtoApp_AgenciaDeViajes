from typing import List, Optional
from psycopg import Cursor, Connection
from src.app.services.base_service import BaseService, with_db 
from src.app.dal import BaseDAL
from src.app.models.Parcialidades import Parcialidades


class ParcialidadesService(BaseService):


    TABLAS_HIJAS: list[tuple[str, str]] = [
        ("registroparcia", "idparcia"),
    ]


    def __init__(self) -> None:
        self.dal = BaseDAL(table_name="Parcialidades", model_class=Parcialidades)

    @with_db
    def listar(self, limit: int = 100, offset: int = 0, *, cur: Cursor, conn: Connection) -> List[Parcialidades]:
        return self.dal.get_all(cur, limit=limit, offset=offset)

    @with_db
    def buscar_por_id(self, idparcia: int, *, cur: Cursor, conn: Connection) -> Optional[Parcialidades]:
        return self.dal.get_by_id(cur, id_value=idparcia, id_column="idparcia")

    @with_db
    def crear(self, idparcia: str, tipoparcia: str, *, cur: Cursor, conn: Connection) -> Parcialidades | None:
        tipoparcia = (tipoparcia or "").strip()
        if not tipoparcia:
            conn.rollback()
            raise ValueError("El tipoparcia de la parcialidad no puede estar vacío.")
        if len(tipoparcia) > 100:
            conn.rollback()
            raise ValueError("El tipoparcia es demasiado largo.")
        
        row = self.dal.create(cur, data={"idparcia": idparcia, "tipoparcia": tipoparcia})
        if not row:
            conn.rollback()
            raise ValueError("No se pudo crear la parcialidad")
        conn.commit()
        return row

    @with_db
    def actualizar(self, idparcia: int, tipoparcia: str, *, cur: Cursor, conn: Connection) -> Parcialidades:
        tipoparcia = (tipoparcia or "").strip()
        if not tipoparcia:
            conn.rollback()
            raise ValueError("El tipoparcia del país no puede estar vacío.")
        row = self.dal.update(cur, id_value=idparcia, data={"tipoparcia": tipoparcia}, id_column="idparcia")
        if row is None:
            conn.rollback()
            raise ValueError(f"No existe la parcialidad con id {idparcia}.")
        conn.commit()
        return row

    @with_db
    def tiene_hijos(self, idparcia: int, *, cur: Cursor, conn: Connection) -> bool:
        for tabla, col in self.TABLAS_HIJAS:
            if self.dal.has_children(
                cur, id_value=idparcia,
                child_table=tabla, child_column=col,
            ):
                return True
        return False

    @with_db
    def eliminar(self, idparcia: int, *, cur: Cursor, conn: Connection) -> None:
        for tabla, col in self.TABLAS_HIJAS:
            if self.dal.has_children(
                cur, id_value=idparcia,
                child_table=tabla, child_column=col,
            ):
                conn.rollback()
                raise ValueError(
                    f"No se puede eliminar la parcialidad {idparcia}: "
                    f"tiene registros relacionados en {tabla}."
                )
            
        row = self.dal.delete(cur, id_value=idparcia, id_column="idparcia")
        if not row:
            conn.rollback()
            raise ValueError(f"No se pudo eliminar la parcialidad con id {idparcia}.")
        conn.commit()