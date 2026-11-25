import secrets
from datetime import date
from typing import Any

from psycopg import errors
from agencia_viajes_web import BaseRepo


class VentaRepo(BaseRepo):
    def __init__(self, conn, tabla: str = "boleto") -> None:
        super().__init__(conn, tabla)

    # ---------- Agencia del empleado logueado (la sesión solo guarda nombre y paterno) ----------
    def obtener_agencia_empleado(self, nombre: str, paterno: str) -> int:
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """SELECT DISTINCT id_agencia FROM usuario
                       WHERE tipo_usuario = 'Empleado' AND nombre = %s AND paterno = %s""",
                    (nombre, paterno),
                )
                filas = cur.fetchall()
        except errors.Error as e:
            print(f"Error al obtener la agencia del empleado: {e}")
            self.conn.rollback()
            raise ValueError("No se pudo determinar la agencia del empleado.")
        if not filas:
            raise ValueError("No se encontró al empleado en la base de datos.")
        if len(filas) > 1:
            raise ValueError("Hay empleados con el mismo nombre en agencias distintas; no se puede saber la agencia.")
        return filas[0]["id_agencia"]

    # ---------- Catálogos para los combos ----------
    def buscar_clientes(self, texto: str, limite: int = 10) -> list[dict[str, Any]]:
        """Busca clientes por nombre, paterno o materno. Cada palabra escrita debe aparecer en el nombre completo."""
        terminos = [t for t in texto.split() if t]
        if not terminos:
            return []
        condiciones = " AND ".join(
            ["(nombre || ' ' || paterno || ' ' || COALESCE(materno, '')) ILIKE %s"] * len(terminos)
        )
        params: list[Any] = [
            "%" + t.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%" for t in terminos
        ]
        params.append(limite)
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"""
                    SELECT id_usuario,
                           TRIM(nombre || ' ' || paterno || ' ' || COALESCE(materno, '')) AS nombre_completo
                    FROM usuario
                    WHERE tipo_usuario = 'Cliente' AND {condiciones}
                    ORDER BY nombre, paterno, materno
                    LIMIT %s
                """, params)
                return cur.fetchall()
        except errors.Error as e:
            print(f"Error al buscar clientes: {e}")
            self.conn.rollback()
            return []

    def obtener_paises(self) -> list[dict[str, Any]]:
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT id_pais, nombre FROM pais ORDER BY nombre")
                return cur.fetchall()
        except errors.Error as e:
            print(f"Error al obtener países: {e}")
            self.conn.rollback()
            return []

    # ---------- Lista de viajes por ruta y fecha ----------
    def buscar_viajes(self, id_origen: int, id_destino: int, fecha: date) -> list[dict[str, Any]]:
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT v.id_viaje,
                           v.nombre,
                           v.fecha_salida,
                           v.fecha_llegada,
                           v.costo,
                           t.nombre AS transporte,
                           (SELECT COUNT(*) FROM asiento a WHERE a.id_transporte = v.id_transporte)
                         - (SELECT COUNT(*) FROM detalles_reserva d WHERE d.id_viaje = v.id_viaje)
                           AS asientos_libres
                    FROM viaje v
                    JOIN medio_transporte t ON t.id_transporte = v.id_transporte
                    WHERE v.id_ciudad_origen = %s
                      AND v.id_ciudad_destino = %s
                      AND v.fecha_salida::date = %s
                    ORDER BY v.fecha_salida
                """, (id_origen, id_destino, fecha))
                return cur.fetchall()
        except errors.Error as e:
            print(f"Error al buscar viajes: {e}")
            self.conn.rollback()
            return []

    def obtener_asientos(self, id_viaje: int) -> list[dict[str, Any]]:
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT a.id_asiento,
                           a.num_asiento,
                           (d.id_detalles_reserva IS NOT NULL) AS ocupado
                    FROM viaje v
                    JOIN asiento a ON a.id_transporte = v.id_transporte
                    LEFT JOIN detalles_reserva d
                           ON d.id_asiento = a.id_asiento AND d.id_viaje = v.id_viaje
                    WHERE v.id_viaje = %s
                    ORDER BY LENGTH(a.num_asiento), a.num_asiento
                """, (id_viaje,))
                return cur.fetchall()
        except errors.Error as e:
            print(f"Error al obtener asientos: {e}")
            self.conn.rollback()
            return []

    # ---------- Venta (todo en una sola transacción) ----------
    def vender_boleto(self, datos: dict[str, Any], id_agencia: int) -> int:
        """Crea pasajero/documento (si no existen), reserva, detalle y boleto.
        Devuelve id_boleto. Lanza ValueError con mensaje legible si algo no cuadra."""
        try:
            with self.conn.cursor() as cur:
                # 1. Viaje
                cur.execute(
                    "SELECT id_viaje, id_transporte, costo, fecha_salida FROM viaje WHERE id_viaje = %s",
                    (datos["id_viaje"],),
                )
                viaje = cur.fetchone()
                if not viaje:
                    raise ValueError("El viaje no existe.")
                if viaje["fecha_salida"].date() < date.today():
                    raise ValueError("No se pueden vender boletos de viajes que ya salieron.")

                # 2. Cliente (quien compra)
                cur.execute(
                    "SELECT nombre, paterno, materno FROM usuario WHERE id_usuario = %s AND tipo_usuario = 'Cliente'",
                    (datos["id_cliente"],),
                )
                cliente = cur.fetchone()
                if not cliente:
                    raise ValueError("El cliente no existe.")

                # 3. Asiento del autobús de ese viaje
                cur.execute(
                    "SELECT id_asiento FROM asiento WHERE id_transporte = %s AND num_asiento = %s",
                    (viaje["id_transporte"], datos["num_asiento"]),
                )
                asiento = cur.fetchone()
                if not asiento:
                    raise ValueError(f"El asiento {datos['num_asiento']} no existe en este autobús.")

                cur.execute(
                    "SELECT 1 FROM detalles_reserva WHERE id_viaje = %s AND id_asiento = %s",
                    (datos["id_viaje"], asiento["id_asiento"]),
                )
                if cur.fetchone():
                    raise ValueError(f"El asiento {datos['num_asiento']} ya está ocupado.")

                # 4. Pasajero + documento de identidad (se reutilizan si ya existen)
                cur.execute(
                    """SELECT id_documento_identidad, id_pasajero FROM documento_identidad
                       WHERE numero_documento = %s AND tipo_documento = %s AND id_pais_emision = %s""",
                    (datos["numero_documento"], datos["tipo_documento"], datos["id_pais_emision"]),
                )
                doc = cur.fetchone()
                if doc:
                    id_pasajero = doc["id_pasajero"]
                    id_doc = doc["id_documento_identidad"]
                else:
                    cur.execute(
                        "INSERT INTO pasajero (nombre, paterno, materno) VALUES (%s, %s, %s) RETURNING id_pasajero",
                        (cliente["nombre"], cliente["paterno"], cliente["materno"]),
                    )
                    id_pasajero = cur.fetchone()["id_pasajero"]
                    cur.execute(
                        """INSERT INTO documento_identidad (id_pasajero, id_pais_emision, tipo_documento, numero_documento)
                           VALUES (%s, %s, %s, %s) RETURNING id_documento_identidad""",
                        (id_pasajero, datos["id_pais_emision"], datos["tipo_documento"], datos["numero_documento"]),
                    )
                    id_doc = cur.fetchone()["id_documento_identidad"]

                cur.execute(
                    "SELECT 1 FROM detalles_reserva WHERE id_pasajero = %s AND id_viaje = %s",
                    (id_pasajero, datos["id_viaje"]),
                )
                if cur.fetchone():
                    raise ValueError("Ese pasajero ya tiene un boleto para este viaje.")

                # 5. La agencia debe estar ligada al viaje (FK de reserva)
                cur.execute(
                    "INSERT INTO agencia_viaje (id_agencia, id_viaje) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (id_agencia, datos["id_viaje"]),
                )

                # 6. Reserva -> detalle -> boleto
                cur.execute(
                    """INSERT INTO reserva (id_viaje, id_agencia, id_cliente, fecha_reserva)
                       VALUES (%s, %s, %s, NOW()) RETURNING id_reserva""",
                    (datos["id_viaje"], id_agencia, datos["id_cliente"]),
                )
                id_reserva = cur.fetchone()["id_reserva"]

                cur.execute(
                    """INSERT INTO detalles_reserva (id_reserva, id_viaje, id_pasajero, id_documento_identidad, id_asiento)
                       VALUES (%s, %s, %s, %s, %s) RETURNING id_detalles_reserva""",
                    (id_reserva, datos["id_viaje"], id_pasajero, id_doc, asiento["id_asiento"]),
                )
                id_detalles = cur.fetchone()["id_detalles_reserva"]

                num_boleto = secrets.token_hex(8).upper()  # 16 caracteres
                cur.execute(
                    """INSERT INTO boleto (id_detalles_reserva, num_boleto, fecha_emision, precio)
                       VALUES (%s, %s, NOW(), %s) RETURNING id_boleto""",
                    (id_detalles, num_boleto, viaje["costo"]),
                )
                id_boleto = cur.fetchone()["id_boleto"]

            self.conn.commit()
            return id_boleto

        except ValueError:
            self.conn.rollback()
            raise
        except errors.UniqueViolation:
            # Alguien más tomó el asiento justo en medio de la operación
            self.conn.rollback()
            raise ValueError("El asiento o el pasajero ya tienen un boleto en este viaje.")
        except errors.Error as e:
            print(f"Error al registrar la venta: {e}")
            self.conn.rollback()
            raise

    # ---------- Boleto "en borrador": se arma con lo elegido en pantalla, sin guardar nada ----------
    def preparar_boleto(self, id_viaje: int, id_cliente: int, num_asiento: str) -> dict[str, Any]:
        """Valida viaje, fecha, cliente y asiento (que exista y esté libre) y devuelve los datos del boleto.
        No escribe nada en la BD. Lanza ValueError con mensaje legible si algo no cuadra."""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT v.id_transporte, v.fecha_salida,
                           t.nombre AS transporte, co.nombre AS origen, cd.nombre AS destino
                    FROM viaje v
                    JOIN medio_transporte t ON t.id_transporte = v.id_transporte
                    JOIN ciudad co ON co.id_ciudad = v.id_ciudad_origen
                    JOIN ciudad cd ON cd.id_ciudad = v.id_ciudad_destino
                    WHERE v.id_viaje = %s
                """, (id_viaje,))
                viaje = cur.fetchone()
                if not viaje:
                    raise ValueError("El viaje no existe.")
                if viaje["fecha_salida"].date() < date.today():
                    raise ValueError("La fecha de salida no puede ser menor a la de hoy.")

                cur.execute("""
                    SELECT TRIM(nombre || ' ' || paterno || ' ' || COALESCE(materno, '')) AS nombre_completo
                    FROM usuario WHERE id_usuario = %s AND tipo_usuario = 'Cliente'
                """, (id_cliente,))
                cliente = cur.fetchone()
                if not cliente:
                    raise ValueError("El cliente no existe.")

                cur.execute(
                    "SELECT id_asiento FROM asiento WHERE id_transporte = %s AND num_asiento = %s",
                    (viaje["id_transporte"], num_asiento),
                )
                asiento = cur.fetchone()
                if not asiento:
                    raise ValueError(f"El asiento {num_asiento} no existe en este autobús.")

                cur.execute(
                    "SELECT 1 FROM detalles_reserva WHERE id_viaje = %s AND id_asiento = %s",
                    (id_viaje, asiento["id_asiento"]),
                )
                if cur.fetchone():
                    raise ValueError(f"El asiento {num_asiento} ya está ocupado.")

            return {
                "cliente": cliente["nombre_completo"],
                "fecha_salida": viaje["fecha_salida"],
                "origen": viaje["origen"],
                "destino": viaje["destino"],
                "num_asiento": num_asiento,
                "transporte": viaje["transporte"],
            }
        except ValueError:
            self.conn.rollback()
            raise
        except errors.Error as e:
            print(f"Error al preparar el boleto: {e}")
            self.conn.rollback()
            raise

    # ---------- Datos para el comprobante PDF ----------
    def obtener_boleto(self, id_boleto: int) -> dict[str, Any] | None:
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT b.id_boleto, b.num_boleto, b.fecha_emision, b.precio,
                           a.num_asiento,
                           t.nombre AS transporte,
                           v.nombre AS nombre_viaje, v.fecha_salida, v.fecha_llegada,
                           co.nombre AS origen, cd.nombre AS destino,
                           TRIM(u.nombre || ' ' || u.paterno || ' ' || COALESCE(u.materno, '')) AS cliente,
                           TRIM(p.nombre || ' ' || p.paterno || ' ' || COALESCE(p.materno, '')) AS pasajero
                    FROM boleto b
                    JOIN detalles_reserva d ON d.id_detalles_reserva = b.id_detalles_reserva
                    JOIN reserva r ON r.id_reserva = d.id_reserva
                    JOIN usuario u ON u.id_usuario = r.id_cliente
                    JOIN pasajero p ON p.id_pasajero = d.id_pasajero
                    JOIN asiento a ON a.id_asiento = d.id_asiento
                    JOIN viaje v ON v.id_viaje = d.id_viaje
                    JOIN medio_transporte t ON t.id_transporte = v.id_transporte
                    JOIN ciudad co ON co.id_ciudad = v.id_ciudad_origen
                    JOIN ciudad cd ON cd.id_ciudad = v.id_ciudad_destino
                    WHERE b.id_boleto = %s
                """, (id_boleto,))
                return cur.fetchone()
        except errors.Error as e:
            print(f"Error al obtener boleto: {e}")
            self.conn.rollback()
            return None
