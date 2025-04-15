# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'acoustic_vis.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QApplication, QHeaderView, QMainWindow, QPushButton,
    QSizePolicy, QTableView, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.start_capture_button = QPushButton(self.centralwidget)
        self.start_capture_button.setObjectName(u"start_capture_button")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.start_capture_button.sizePolicy().hasHeightForWidth())
        self.start_capture_button.setSizePolicy(sizePolicy)
        self.start_capture_button.setMinimumSize(QSize(125, 0))

        self.verticalLayout.addWidget(self.start_capture_button)

        self.sample_data_table = QTableView(self.centralwidget)
        self.sample_data_table.setObjectName(u"sample_data_table")
        self.sample_data_table.horizontalHeader().setMinimumSectionSize(30)
        self.sample_data_table.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout.addWidget(self.sample_data_table)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.start_capture_button.setText(QCoreApplication.translate("MainWindow", u"Start Capturing", None))
    # retranslateUi

