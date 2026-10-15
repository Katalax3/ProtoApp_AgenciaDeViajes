from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from psycopg.rows import dict_row

T = TypeVar('T')

class BaseDAL(Generic[T]):
    
    def __init__(self, table_name: str, model_class: Type[T]):
        self.table_name = table_name
        self.model_class = model_class

    def to_model(self, row: Optional[Dict]) -> Optional[T]:
        if row is None:
            return None
        return self.model_class(**row)

    def _to_model_list(self, rows: List[Dict]) -> List[T]:
        return [self.model_class(**r) for r in rows]

    def get_by_id(self, cur, *, id_value: Any, id_column: str = "id") -> Optional[T]:
        query = f"SELECT * FROM {self.table_name} WHERE {id_column} = %(id)s"
        cur.execute(query, {"id": id_value})
        return self.to_model(cur.fetchone())

    def get_all(self, cur, *, limit: int = 100, offset: int = 0) -> List[T]:
        query = f"SELECT * FROM {self.table_name} LIMIT %(limit)s OFFSET %(offset)s"
        cur.execute(query, {"limit": limit, "offset": offset})
        return self._to_model_list(cur.fetchall())

    def create(self, cur, *, data: Dict[str, Any]) -> Optional[T]:
        columns = ", ".join(data.keys())
        placeholders = ", ".join(f"%({k})s" for k in data.keys())
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING *"
        cur.execute(query, data)
        return self.to_model(cur.fetchone())

    def update(self, cur, *, id_value: Any, data: Dict[str, Any], id_column: str = "id") -> Optional[T]:
        set_clause = ", ".join(f"{k} = %({k})s" for k in data.keys())
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {id_column} = %(id)s RETURNING *"
        params = {**data, "id": id_value}
        data["id"] = id_value
        cur.execute(query, params)
        return self.to_model(cur.fetchone())

    def delete(self, cur, *, id_value: Any, id_column: str = "id") -> bool:
        query = f"DELETE FROM {self.table_name} WHERE {id_column} = %(id)s"
        cur.execute(query, {"id": id_value})
        return cur.rowcount > 0

    def has_children(self, cur, *, id_value: Any, child_table: str, child_column: str,) -> bool:
            query = (
                f"SELECT EXISTS("
                f"  SELECT 1 FROM {child_table} WHERE {child_column} = %(id)s"
                f") AS existe"
            )
            cur.execute(query, {"id": id_value})
            row = cur.fetchone()
            return bool(row["existe"]) if row else False