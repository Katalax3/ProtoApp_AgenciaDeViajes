from dataclasses import dataclass


@dataclass
class Pais:
    idpais: int
    nombre: str

    def __post_init__(self):
        # La columna es NUMERIC(9): psycopg la regresa como Decimal
        self.idpais = int(self.idpais)
