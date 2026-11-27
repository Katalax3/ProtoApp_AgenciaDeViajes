from typing import Any
from agencia_viajes_web import BaseRepo
from psycopg import errors, sql
from psycopg.rows import dict_row


class ViajeRepo(BaseRepo):
    def __init__(self, conn, tabla: str = "viaje") -> None:
        super().__init__(conn, tabla)

    def obtener_viaje(self) -> list[dict[str, Any]]:
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                query = sql.SQL("""
                    SELECT
                        v.id_viaje,
                        v.id_nombre_viaje,
                        COALESCE(nv.nombre, 'Sin nombre') AS nombre_viaje,
                        v.id_transporte,
                        COALESCE(t.nombre, 'N/A') AS nombre_transporte,
                        v.id_ciudad_origen,
                        COALESCE(co.nombre, 'N/A') AS nombre_ciudad_origen,
                        v.id_ciudad_destino,
                        COALESCE(cd.nombre, 'N/A') AS nombre_ciudad_destino,
                        v.fecha_salida,
                        v.fecha_llegada,
                        COALESCE(v.costo, 0) AS costo
                    FROM viaje v
                    LEFT JOIN nombre_viaje nv ON nv.id_nombre_viaje = v.id_nombre_viaje
                    LEFT JOIN ciudad co ON co.id_ciudad = v.id_ciudad_origen
                    LEFT JOIN ciudad cd ON cd.id_ciudad = v.id_ciudad_destino
                    LEFT JOIN medio_transporte t ON t.id_transporte = v.id_transporte
                    ORDER BY v.id_viaje
                """)
                cur.execute(query)
                return cur.fetchall()
        except errors.Error as e:
            print(f"Error al obtener viajes: {e}")
            self.conn.rollback()
            return []

    def obtener_viaje_por_id(self, id_viaje: int) -> dict[str, Any] | None:
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                query = sql.SQL("""
                    SELECT
                        v.id_viaje, 
                        v.id_nombre_viaje,
                        COALESCE(nv.nombre, 'Sin nombre') AS nombre_viaje,
                        v.id_transporte, COALESCE(t.nombre, 'N/A') AS nombre_transporte,
                        v.id_ciudad_origen, COALESCE(co.nombre, 'N/A') AS nombre_ciudad_origen,
                        v.id_ciudad_destino, COALESCE(cd.nombre, 'N/A') AS nombre_ciudad_destino,
                        v.fecha_salida, v.fecha_llegada, COALESCE(v.costo, 0) AS costo
                    FROM viaje v
                    LEFT JOIN nombre_viaje nv ON nv.id_nombre_viaje = v.id_nombre_viaje
                    LEFT JOIN ciudad co ON co.id_ciudad = v.id_ciudad_origen
                    LEFT JOIN ciudad cd ON cd.id_ciudad = v.id_ciudad_destino
                    LEFT JOIN medio_transporte t ON t.id_transporte = v.id_transporte
                    WHERE v.id_viaje = %s
                """)
                cur.execute(query, (id_viaje,))
                return cur.fetchone()
        except errors.Error as e:
            print(f"Error al obtener viaje por ID: {e}")
            self.conn.rollback()
            return None

    def obtener_ciudades(self) -> list[dict[str, Any]]:
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT id_ciudad, nombre FROM ciudad ORDER BY nombre")
                return cur.fetchall()
        except errors.Error as e:
            print(f"Error al obtener ciudades: {e}")
            return []

    def obtener_transportes(self) -> list[dict[str, Any]]:
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT id_transporte, nombre FROM medio_transporte ORDER BY nombre")
                return cur.fetchall()
        except errors.Error as e:
            print(f"Error al obtener transportes: {e}")
            return []

    def obtener_nombre_viaje(self) -> list[dict[str, Any]]:
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT id_nombre_viaje, nombre FROM nombre_viaje ORDER BY nombre")
                return cur.fetchall()
        except errors.Error as e:
            print(f"Error al obtener el nombre de los viajes: {e}")
            return []