from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QAction
from src.app.ui import Ui_MenuOpciones
from .Parcialidades_ui_controller import VentanaParcialidades
from .Paises_ui_controller import VentanaPaises
from .Bancos_ui_controller import VentanaBancos
from app.services.parcialidades_service import ParcialidadesService

class MenuOpciones(QMainWindow):
    def __init__(self, rol: str):
        super().__init__()
        self.ui = Ui_MenuOpciones()
        self.ui.setupUi(self)
        self.service = ParcialidadesService()
        self.rol = rol
        self.ui.menuBarMO.triggered.connect(self.SeleccionarVentanaTabla)

    def SeleccionarVentanaTabla(self, action):
        text = action.text()
        if text == 'Parcialidades':
            self.siguiente_ventana = VentanaParcialidades(self.service)
            self.siguiente_ventana.show()
        if text == 'Paises':
            self.siguiente_ventana = VentanaPaises()
            self.siguiente_ventana.show()
        if text == 'Bancos':
            self.siguiente_ventana = VentanaBancos()
            self.siguiente_ventana.show()
