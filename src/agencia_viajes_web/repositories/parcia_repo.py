from typing import Any

from psycopg import Connection
from agencia_viajes_web import BaseRepo
from agencia_viajes_web import Security

class ParciaRepo(BaseRepo):
    def __init__(self, conn, tabla="parcialidad") -> None:
        super().__init__(conn, tabla)