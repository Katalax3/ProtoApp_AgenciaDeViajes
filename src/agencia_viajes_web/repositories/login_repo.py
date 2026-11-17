from .base_repo import BaseRepo
from psycopg import sql, errors, Connection
from typing import Any, cast
from agencia_viajes_web import Security

class LoginRepo(BaseRepo):
    def __init__(self, conn, tabla="usuario") -> None:
        super().__init__(conn, tabla)
        self.__hash = Security()

    def validar_credenciales(self, datos: dict[str, Any]):
        try:
            with self.conn.cursor() as cur:
                query=sql.SQL("SELECT nombre, paterno, tipo_usuario, contrasena FROM {tabla} WHERE correo=%s").format(tabla=sql.Identifier(cast(str, self.tabla)))
                correo = datos.get("correo")
                cur.execute(query, (correo, ))
                registro = cur.fetchone()

                if not registro:
                    raise ValueError(f"No existe dicho usuario en la base de datos")

                registro_dict = cast(dict[str, Any], registro)

                contrasena_plana = registro_dict.get("contrasena")
                
                if not contrasena_plana or not self.__hash.verify_password(datos["contrasena"], contrasena_plana):
                    raise ValueError(f"La contraseña es incorrecta")

                return registro_dict

        except ValueError:
            self.conn.rollback()
            raise
        except errors.Error:
            self.conn.rollback()
            raise

                