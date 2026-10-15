# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Bancos.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHeaderView, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTableView,
    QWidget)

class Ui_VentanaBancos(object):
    def setupUi(self, VentanaBancos):
        if not VentanaBancos.objectName():
            VentanaBancos.setObjectName(u"VentanaBancos")
        VentanaBancos.resize(563, 593)
        VentanaBancos.setMaximumSize(QSize(563, 16777215))
        self.gridLayout = QGridLayout(VentanaBancos)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineIDBancos = QLineEdit(VentanaBancos)
        self.lineIDBancos.setObjectName(u"lineIDBancos")

        self.gridLayout.addWidget(self.lineIDBancos, 1, 0, 1, 2)

        self.label_2 = QLabel(VentanaBancos)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 2)

        self.pbancosBuscar = QPushButton(VentanaBancos)
        self.pbancosBuscar.setObjectName(u"pbancosBuscar")

        self.gridLayout.addWidget(self.pbancosBuscar, 7, 0, 1, 1)

        self.pbancosNuevo = QPushButton(VentanaBancos)
        self.pbancosNuevo.setObjectName(u"pbancosNuevo")

        self.gridLayout.addWidget(self.pbancosNuevo, 5, 1, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.pbancosEliminar = QPushButton(VentanaBancos)
        self.pbancosEliminar.setObjectName(u"pbancosEliminar")

        self.gridLayout.addWidget(self.pbancosEliminar, 7, 1, 1, 1)

        self.lineNombreBancos = QLineEdit(VentanaBancos)
        self.lineNombreBancos.setObjectName(u"lineNombreBancos")

        self.gridLayout.addWidget(self.lineNombreBancos, 3, 0, 1, 2)

        self.pbancosActualizar = QPushButton(VentanaBancos)
        self.pbancosActualizar.setObjectName(u"pbancosActualizar")

        self.gridLayout.addWidget(self.pbancosActualizar, 5, 0, 1, 1)

        self.label = QLabel(VentanaBancos)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.vistaBancos = QTableView(VentanaBancos)
        self.vistaBancos.setObjectName(u"vistaBancos")

        self.gridLayout.addWidget(self.vistaBancos, 6, 0, 1, 2)


        self.retranslateUi(VentanaBancos)

        QMetaObject.connectSlotsByName(VentanaBancos)
    # setupUi

    def retranslateUi(self, VentanaBancos):
        VentanaBancos.setWindowTitle(QCoreApplication.translate("VentanaBancos", u"Bancos", None))
        self.lineIDBancos.setPlaceholderText(QCoreApplication.translate("VentanaBancos", u"Inserte el ID del banco", None))
        self.label_2.setText(QCoreApplication.translate("VentanaBancos", u"Nombre del Banco", None))
        self.pbancosBuscar.setText(QCoreApplication.translate("VentanaBancos", u"Buscar", None))
        self.pbancosNuevo.setText(QCoreApplication.translate("VentanaBancos", u"Nuevo+", None))
        self.pbancosEliminar.setText(QCoreApplication.translate("VentanaBancos", u"Eliminar", None))
        self.lineNombreBancos.setPlaceholderText(QCoreApplication.translate("VentanaBancos", u"Inserte el nombre del banco", None))
        self.pbancosActualizar.setText(QCoreApplication.translate("VentanaBancos", u"Actualizar", None))
        self.label.setText(QCoreApplication.translate("VentanaBancos", u"ID del banco", None))
    # retranslateUi