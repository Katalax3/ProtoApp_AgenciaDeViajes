# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Parcialidades.ui'
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

class Ui_VentanaParcialidades(object):
    def setupUi(self, VentanaParcialidades):
        if not VentanaParcialidades.objectName():
            VentanaParcialidades.setObjectName(u"VentanaParcialidades")
        VentanaParcialidades.resize(563, 593)
        VentanaParcialidades.setMaximumSize(QSize(563, 16777215))
        self.gridLayout = QGridLayout(VentanaParcialidades)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(VentanaParcialidades)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 2)

        self.pparcialidadesActualizar = QPushButton(VentanaParcialidades)
        self.pparcialidadesActualizar.setObjectName(u"pparcialidadesActualizar")

        self.gridLayout.addWidget(self.pparcialidadesActualizar, 6, 0, 1, 1)

        self.lineTipoParcialidades = QLineEdit(VentanaParcialidades)
        self.lineTipoParcialidades.setObjectName(u"lineTipoParcialidades")

        self.gridLayout.addWidget(self.lineTipoParcialidades, 4, 0, 1, 2)

        self.vistaParcialidades = QTableView(VentanaParcialidades)
        self.vistaParcialidades.setObjectName(u"vistaParcialidades")

        self.gridLayout.addWidget(self.vistaParcialidades, 7, 0, 1, 2)

        self.pparcialidadesNuevo = QPushButton(VentanaParcialidades)
        self.pparcialidadesNuevo.setObjectName(u"pparcialidadesNuevo")

        self.gridLayout.addWidget(self.pparcialidadesNuevo, 6, 1, 1, 1, Qt.AlignmentFlag.AlignRight)

        self.label = QLabel(VentanaParcialidades)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.lineIDParcialidades = QLineEdit(VentanaParcialidades)
        self.lineIDParcialidades.setObjectName(u"lineIDParcialidades")

        self.gridLayout.addWidget(self.lineIDParcialidades, 1, 0, 1, 2)

        self.pparcialidadesBuscar = QPushButton(VentanaParcialidades)
        self.pparcialidadesBuscar.setObjectName(u"pparcialidadesBuscar")

        self.gridLayout.addWidget(self.pparcialidadesBuscar, 2, 0, 1, 1, Qt.AlignmentFlag.AlignLeft)

        self.pparcialidadesEliminar = QPushButton(VentanaParcialidades)
        self.pparcialidadesEliminar.setObjectName(u"pparcialidadesEliminar")

        self.gridLayout.addWidget(self.pparcialidadesEliminar, 8, 0, 1, 2)


        self.retranslateUi(VentanaParcialidades)

        QMetaObject.connectSlotsByName(VentanaParcialidades)
    # setupUi

    def retranslateUi(self, VentanaParcialidades):
        VentanaParcialidades.setWindowTitle(QCoreApplication.translate("VentanaParcialidades", u"Parcialidades", None))
        self.label_2.setText(QCoreApplication.translate("VentanaParcialidades", u"Tipo", None))
        self.pparcialidadesActualizar.setText(QCoreApplication.translate("VentanaParcialidades", u"Actualizar", None))
        self.lineTipoParcialidades.setPlaceholderText(QCoreApplication.translate("VentanaParcialidades", u"Inserte el tipo de la parcialidad", None))
        self.pparcialidadesNuevo.setText(QCoreApplication.translate("VentanaParcialidades", u"Nuevo+", None))
        self.label.setText(QCoreApplication.translate("VentanaParcialidades", u"ID de la parcialidad", None))
        self.lineIDParcialidades.setPlaceholderText(QCoreApplication.translate("VentanaParcialidades", u"Inserte el ID de la parcialidad", None))
        self.pparcialidadesBuscar.setText(QCoreApplication.translate("VentanaParcialidades", u"Buscar", None))
        self.pparcialidadesEliminar.setText(QCoreApplication.translate("VentanaParcialidades", u"Eliminar", None))
    # retranslateUi

