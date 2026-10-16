from database.connection import get_db_connection
from psycopg.rows import dict_row
from PySide6.QtWidgets import QMessageBox
from src.app.dal import AuthDAL

class AuthService:
    def autenticar_usuario(self, identificador: str, rol: str, contrasena: str) -> dict | None:

        try:
            with get_db_connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    auth_dal = AuthDAL(cur)
                    usuario = auth_dal.obtener_usuario_por_identificador(identificador, rol)

                    if usuario and usuario["contrasena"] == contrasena:
                        return usuario
                    
        except Exception as e:
             QMessageBox.critical(None, "Mensaje de error", f"Error al conectar o consultar la BD: {e}")          
