from psycopg import sql, errors, Connection
from typing import Any

class BaseRepo:
    def __init__(self, conn: Connection, tabla: str) -> None:
        self.tabla = tabla
        self.conn = conn

    def obtener_todos(self):
        try:
            with self.conn.cursor() as cur:
               query=sql.SQL("SELECT * FROM {tabla}").format(tabla=sql.Identifier(self.tabla))
               cur.execute(query)
               return cur.fetchall()
        except errors.Error as e:
            print(f"Ocurrio un error en la base de datos")
            print(f"Codigo de error: {e}")
            self.conn.rollback()
            return []
                    

    def insertar_registro(self, datos: dict[str, Any]):
        try:
            with self.conn.cursor() as cur:
                cols = sql.SQL(", ").join(sql.Identifier(col) for col in datos.keys())
                placeholders = sql.SQL(", ").join(sql.SQL("%s") for _ in datos)

                query_insert = sql.SQL("INSERT INTO {tabla} ({cols}) VALUES ({placeholders}) RETURNING *").format(
                    tabla = sql.Identifier(self.tabla),
                    cols = cols,
                    placeholders = placeholders
                )

                param = list(datos.values())

                cur.execute(query_insert, param)
                self.conn.commit()
                return cur.fetchone()

        except errors.Error as e:
            print(f"Ocurrio un error en la base de datos")
            print(f"Codigo de error: {e}")
            self.conn.rollback()

    def actualizar_registro(self, datos: dict[str, Any], id_val: int, id_tabla: str):
        try:
            with self.conn.cursor() as cur:
                
                asignaciones = [sql.SQL("{col} = %s").format(col=sql.Identifier(col)) for col in datos.keys()]
                sets = sql.SQL(", ").join(asignaciones)

                query = sql.SQL("UPDATE {tabla} SET {sets} WHERE {id_tabla} = %s RETURNING *").format(tabla=sql.Identifier(self.tabla), sets=sets, id_tabla=sql.Identifier(id_tabla))

                params = list(datos.values()) + [id_val]

                cur.execute(query, params)
                self.conn.commit()
                return cur.fetchone()

        except errors.Error as e:
                print(f"Ocurrio un error en la base de datos")
                print(f"Codigo de error: {e}")
                self.conn.rollback()

    def eliminar_registro(self, id_val: int, id_tabla: str):
        try:
            with self.conn.cursor() as cur:
                query = sql.SQL("DELETE FROM {tabla} WHERE {id_tabla} = %s").format(tabla = sql.Identifier(self.tabla), id_tabla=sql.Identifier(id_tabla))

                cur.execute(query, (id_val, ))
                self.conn.commit()
                return cur.rowcount > 0
                
        except errors.Error as e:
                print(f"Ocurrio un error en la base de datos")
                print(f"Codigo de error: {e}")
                self.conn.rollback()

    def consultar_por_id(self, id_val: int, id_tabla: str):
        try:
            with self. conn.cursor() as cur:
                id = id_val

                query = sql.SQL("SELECT * FROM {tabla} WHERE {id_tabla} = %s").format(tabla = sql.Identifier(self.tabla), id_tabla=sql.Identifier(id_tabla))

                cur.execute(query, (id, ))
                return cur.fetchone()
            
        except errors.Error as e:
                print(f"Ocurrio un error en la base de datos")
                print(f"Codigo de error: {e}")
                self.conn.rollback()

    def tiene_registros_hijos(self, id_val: int, id_tabla: str, tabla_hija: str, fk_columna: str) -> bool:
        try:
            with self.conn.cursor() as cur:
                query = sql.SQL("SELECT COUNT(*) FROM {tabla_hija} WHERE {fk_columna} = %s").format(
                    tabla_hija=sql.Identifier(tabla_hija),
                    fk_columna=sql.Identifier(fk_columna)
                )
                cur.execute(query, (id_val,))
                resultado = cur.fetchone()
                
                if not resultado:
                    return False
                
                conteo = list(resultado.values())[0] if isinstance(resultado, dict) else resultado[0]
                return conteo > 0
        except errors.Error as e:
            self.conn.rollback()
            return False