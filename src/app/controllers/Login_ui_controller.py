import sys
from PySide6.QtWidgets import QDialog, QMessageBox
from src.app.ui import Ui_Login
from .MenuOpciones_ui_controller import MenuOpciones
from src.app.services import AuthService

class VentanaLogin(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Login()
        self.ui.setupUi(self)
        self.auth_service = AuthService()

        self.ui.BCliente.setCheckable(True)
        self.ui.BEmpleado.setCheckable(True)
        self.ui.buttonGroup.setExclusive(True)
        self.ui.BCliente.setChecked(True)
        self.ui.EContrasena.setEchoMode(self.ui.EContrasena.EchoMode.Password)

        
        self.ui.Ingresar.clicked.connect(self.procesar_login)

    def obtener_rol(self) -> str:
            if self.ui.BCliente.isChecked():
                 return "clientes"
            return "empleados"

    def siguiente_ventana(self, rol: str):
              self.ventana_principal = MenuOpciones(rol=rol)
              self.ventana_principal.show()
              self.close()
                        
    def procesar_login(self):
     identificador = self.ui.EUsuarioCorreo.text().strip()
     contrasena = self.ui.EContrasena.text().strip()
     rol = self.obtener_rol()

     if not identificador or not contrasena:
          QMessageBox.warning(self, "Campos Vacios", "Por favor ingrese su usuario/correo y contraseña")
          return

     try:
          usuario = self.auth_service.autenticar_usuario(identificador, rol, contrasena)

          if usuario:
               self.siguiente_ventana(rol)
          else:
               QMessageBox.critical(self, "Mensaje de error", "Credenciales incorrectas o el usuario no existe")
     except Exception as e:
                  QMessageBox.critical(None, "Mensaje de error", f"Error al conectar o consultar la BD: {e}")