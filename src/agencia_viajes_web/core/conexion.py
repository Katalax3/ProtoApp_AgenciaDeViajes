from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from psycopg import errors
from .database import database
from fastapi import HTTPException


class Conexion():
    def __init__(self) -> None:
        self.__pool = ConnectionPool(database.database_url, kwargs={"row_factory":dict_row}, max_size=10, min_size=2)

    def obtener_conexion(self):
        try:
            conn = self.__pool.getconn()
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                return conn
        except errors:
            print("No se pudo conectar con la base de datos")
            return None

    def liberar_conexion(self, conn):
        if conn is not None:
            self.__pool.putconn(conn)

    def get_db(self):
        conn = self.obtener_conexion()
        if conn is None:
            raise HTTPException(
                status_code=503, detail="Base de datos no disponible"
            )
        try:
            yield conn
        finally:
            self.liberar_conexion(conn)