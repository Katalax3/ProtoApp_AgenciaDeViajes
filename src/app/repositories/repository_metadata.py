# src/app/repositories/metadata_repository.py
from  database.connection import get_db_connection  # tu helper de conexión existente

def obtener_limites_columnas(tabla: str, schema: str = "public") -> dict[str, dict]:
    """
    Lee los límites de las columnas de una tabla en PostgreSQL.

    Devuelve:
    {
      "idparcia":   {"max_digits": 9, "max_value": 999_999_999},
      "tipoparcia": {"max_length": 50},
      ...
    }
    """
    sql = """
        SELECT column_name,
               data_type,
               numeric_precision,
               numeric_scale,
               character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name   = %s
    """

    limites: dict[str, dict] = {}
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (schema, tabla))
            for column_name, data_type, precision, scale, max_len in cur.fetchall():
                if data_type == "numeric" and precision is not None and scale == 0:
                    limites[column_name] = {
                        "max_digits": precision,
                        "max_value": 10 ** precision - 1,
                    }
                elif data_type in ("character varying", "character") and max_len:
                    limites[column_name] = {"max_length": max_len}
                elif data_type == "text":
                    pass
    return limites