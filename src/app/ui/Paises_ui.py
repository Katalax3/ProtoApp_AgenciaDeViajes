# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Paises.ui'
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

class Ui_VentanaPaises(object):
    def setupUi(self, VentanaPaises):
        if not VentanaPaises.objectName():
            VentanaPaises.setObjectName(u"VentanaPaises")
        VentanaPaises.resize(563, 593)
        VentanaPaises.setMaximumSize(QSize(563, 16777215))
        self.gridLayout = QGridLayout(VentanaPaises)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineIDPaises = QLineEdit(VentanaPaises)
        self.lineIDPaises.setObjectName(u"lineIDPaises")

        self.gridLayout.addWidget(self.lineIDPaises, 1, 0, 1, 2)

        self.label_2 = QLabel(VentanaPaises)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 2)

        self.ppaisesBuscar = QPushButton(VentanaPaises)
        self.ppaisesBuscar.setObjectName(u"ppaisesBuscar")

        self.gridLayout.addWidget(self.ppaisesBuscar, 7, 0, 1, 1)

        self.ppaisesNuevo = QPushButton(VentanaPaises)
        self.ppaisesNuevo.setObjectName(u"ppaisesNuevo")

        self.gridLayout.addWidget(self.ppaisesNuevo, 5, 1, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.ppaisesEliminar = QPushButton(VentanaPaises)
        self.ppaisesEliminar.setObjectName(u"ppaisesEliminar")

        self.gridLayout.addWidget(self.ppaisesEliminar, 7, 1, 1, 1)

        self.lineNombrePaises = QLineEdit(VentanaPaises)
        self.lineNombrePaises.setObjectName(u"lineNombrePaises")

        self.gridLayout.addWidget(self.lineNombrePaises, 3, 0, 1, 2)

        self.ppaisesActualizar = QPushButton(VentanaPaises)
        self.ppaisesActualizar.setObjectName(u"ppaisesActualizar")

        self.gridLayout.addWidget(self.ppaisesActualizar, 5, 0, 1, 1)

        self.label = QLabel(VentanaPaises)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.vistaPaises = QTableView(VentanaPaises)
        self.vistaPaises.setObjectName(u"vistaPaises")

        self.gridLayout.addWidget(self.vistaPaises, 6, 0, 1, 2)


        self.retranslateUi(VentanaPaises)

        QMetaObject.connectSlotsByName(VentanaPaises)
    # setupUi

    def retranslateUi(self, VentanaPaises):
        VentanaPaises.setWindowTitle(QCoreApplication.translate("VentanaPaises", u"Países", None))
        self.lineIDPaises.setPlaceholderText(QCoreApplication.translate("VentanaPaises", u"Inserte el ID del país", None))
        self.label_2.setText(QCoreApplication.translate("VentanaPaises", u"Nombre", None))
        self.ppaisesBuscar.setText(QCoreApplication.translate("VentanaPaises", u"Buscar", None))
        self.ppaisesNuevo.setText(QCoreApplication.translate("VentanaPaises", u"Nuevo+", None))
        self.ppaisesEliminar.setText(QCoreApplication.translate("VentanaPaises", u"Eliminar", None))
        self.lineNombrePaises.setPlaceholderText(QCoreApplication.translate("VentanaPaises", u"Inserte el nombre del país", None))
        self.ppaisesActualizar.setText(QCoreApplication.translate("VentanaPaises", u"Actualizar", None))
        self.label.setText(QCoreApplication.translate("VentanaPaises", u"ID del país", None))
    # retranslateUi

