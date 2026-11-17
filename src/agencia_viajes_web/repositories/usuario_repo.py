from typing import Any
from agencia_viajes_web import BaseRepo
from agencia_viajes_web import Security

class UsuarioRepo(BaseRepo):
    def __init__(self, conn, tabla="usuario") -> None:
        super().__init__(conn, tabla)
        self.__hash = Security()

    def insertar_usuario(self, datos:dict[str, Any]):
        if "contrasena" in datos and datos["contrasena"]:
            datos["contrasena"] = self.__hash.hash_password(datos["contrasena"])

        return super().insertar_registro(datos=datos)