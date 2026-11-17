from typing import Any

from psycopg import Connection
from agencia_viajes_web import BaseRepo
from agencia_viajes_web import Security

class ViajeRepo(BaseRepo):
    def __init__(self, conn, tabla = "viaje") -> None:
        super().__init__(conn, tabla)