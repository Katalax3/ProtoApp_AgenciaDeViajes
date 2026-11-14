from psycopg import sql, errors, Connection
from typing import Any

class BaseRepo:
    def __init__(self, conn: Connection, tabla=None) -> None:
        self.tabla = tabla
        self.conn = conn

    def obtener_todos(self):
        try:
            with self.conn.cursor() as cur:
                cur.execute(t"SELECT * FROM {self.tabla:i}")
                return cur.fetchall()
        except errors.Error as e:
            print(f"Ocurrio un error en la base de datos")
            print(f"Codigo de error: {e}")
            self.conn.rollback()
                    

    def insertar_registro(self, datos: dict[str, Any]):
        try:
            with self.conn.cursor() as cur:
                columnas = sql.SQL(", ").join(sql.Identifier(col) for col in datos.keys())
                placeholder = sql.SQL(", ").join("%s" for _ in datos)

                query_insert = sql.SQL("INSERT INTO {tabla:i} ({columnas}) VALUES ({placeholder})").format(
                    tabla = self.tabla,
                    columnas = columnas,
                    placeholder = placeholder
                )

                param = list(datos.values())

                cur.execute(query_insert, param)
                self.conn.commit()

        except errors.Error as e:
            print(f"Ocurrio un error en la base de datos")
            print(f"Codigo de error: {e}")
            self.conn.rollback()

    def actualizar_registro(self, datos: dict[str, Any], id_json: str, id_tabla: str):
        try:
            with self.conn.cursor() as cur:
                id = datos.pop(id_json, None)
                asignaciones = [sql.SQL("{col} = %s").format(col=sql.Identifier(col)) for col in datos.keys()]
                sets = sql.SQL(", ").join(asignaciones)

                query = sql.SQL("UPDATE {tabla:i} SET {sets:q} WHERE {id_tabla:i} = %s").format(tabla=self.tabla, sets=sets, id_tabla=id_tabla)

                params = list(datos.values()) + [id]

                cur.execute(query, params)
                self.conn.commit()

        except errors.Error as e:
                print(f"Ocurrio un error en la base de datos")
                print(f"Codigo de error: {e}")
                self.conn.rollback()

    def eliminar_registro(self, datos: dict[str, Any], id_json: str, id_tabla: str):
        try:
            with self.conn.cursor() as cur:
                id = datos.pop(id_json, None)
                asignaciones = [sql.SQL("{col} = %s").format(col=sql.Identifier(col)) for col in datos.keys()] + [sql.SQL("{id} = %s").format(id=sql.Identifier(id_tabla))]
                wheres = sql.SQL(" AND ").join(asignaciones)

                query = sql.SQL("DELETE FROM {tabla:i} WHERE {wheres:q}").format(tabla = self.tabla, wheres = wheres)

                params = list(datos.values()) + [id]

                cur.execute(query, params)
                self.conn.commit()
                
        except errors.Error as e:
                print(f"Ocurrio un error en la base de datos")
                print(f"Codigo de error: {e}")
                self.conn.rollback()

    def consultar_por_id(self, datos: dict[str, Any], id_json: str, id_tabla: str):
        try:
            with self. conn.cursor() as cur:
                id = datos.get(id_json)

                query = sql.SQL("SELECT * FROM {tabla:i} WHERE {id_tabla:i} = %s").format(tabla = self.tabla, id_tabla=id_tabla)

                cur.execute(query, id)
                self.conn
        except errors.Error as e:
                print(f"Ocurrio un error en la base de datos")
                print(f"Codigo de error: {e}")
                self.conn.rollback()


        