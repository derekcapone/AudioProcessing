# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ScrollAreaRawAcoustic.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QHeaderView,
    QLabel, QLayout, QMainWindow, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 780, 580))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.row0 = QHBoxLayout()
        self.row0.setObjectName(u"row0")
        self.row0.setSizeConstraint(QLayout.SetFixedSize)
        self.line_number_label = QLabel(self.scrollAreaWidgetContents)
        self.line_number_label.setObjectName(u"line_number_label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.line_number_label.sizePolicy().hasHeightForWidth())
        self.line_number_label.setSizePolicy(sizePolicy1)
        self.line_number_label.setMinimumSize(QSize(120, 0))

        self.row0.addWidget(self.line_number_label)

        self.line_number_combobox = QComboBox(self.scrollAreaWidgetContents)
        self.line_number_combobox.setObjectName(u"line_number_combobox")

        self.row0.addWidget(self.line_number_combobox)

        self.row0_spacer = QSpacerItem(40, 14, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.row0.addItem(self.row0_spacer)


        self.verticalLayout_2.addLayout(self.row0)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.sensor_number_label = QLabel(self.scrollAreaWidgetContents)
        self.sensor_number_label.setObjectName(u"sensor_number_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.sensor_number_label.sizePolicy().hasHeightForWidth())
        self.sensor_number_label.setSizePolicy(sizePolicy2)
        self.sensor_number_label.setMinimumSize(QSize(120, 0))

        self.horizontalLayout.addWidget(self.sensor_number_label)

        self.sensor_number_combobox = QComboBox(self.scrollAreaWidgetContents)
        self.sensor_number_combobox.setObjectName(u"sensor_number_combobox")

        self.horizontalLayout.addWidget(self.sensor_number_combobox)

        self.row1_spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.row1_spacer)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.submit_refresh_layout = QHBoxLayout()
        self.submit_refresh_layout.setObjectName(u"submit_refresh_layout")
        self.submit_refresh_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.show_sample_button = QPushButton(self.scrollAreaWidgetContents)
        self.show_sample_button.setObjectName(u"show_sample_button")
        sizePolicy1.setHeightForWidth(self.show_sample_button.sizePolicy().hasHeightForWidth())
        self.show_sample_button.setSizePolicy(sizePolicy1)
        self.show_sample_button.setMinimumSize(QSize(183, 0))

        self.submit_refresh_layout.addWidget(self.show_sample_button)

        self.refresh_data_button = QPushButton(self.scrollAreaWidgetContents)
        self.refresh_data_button.setObjectName(u"refresh_data_button")
        sizePolicy1.setHeightForWidth(self.refresh_data_button.sizePolicy().hasHeightForWidth())
        self.refresh_data_button.setSizePolicy(sizePolicy1)
        self.refresh_data_button.setMinimumSize(QSize(183, 0))

        self.submit_refresh_layout.addWidget(self.refresh_data_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.submit_refresh_layout.addItem(self.horizontalSpacer)


        self.verticalLayout_2.addLayout(self.submit_refresh_layout)

        self.sensor_data_list = QTableWidget(self.scrollAreaWidgetContents)
        if (self.sensor_data_list.columnCount() < 2):
            self.sensor_data_list.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.sensor_data_list.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.sensor_data_list.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.sensor_data_list.setObjectName(u"sensor_data_list")
        self.sensor_data_list.setAlternatingRowColors(True)
        self.sensor_data_list.horizontalHeader().setMinimumSectionSize(180)
        self.sensor_data_list.horizontalHeader().setDefaultSectionSize(180)
        self.sensor_data_list.horizontalHeader().setStretchLastSection(True)

        self.verticalLayout_2.addWidget(self.sensor_data_list)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.line_number_label.setText(QCoreApplication.translate("MainWindow", u"Line Number:", None))
        self.sensor_number_label.setText(QCoreApplication.translate("MainWindow", u"Sensor Number: ", None))
        self.show_sample_button.setText(QCoreApplication.translate("MainWindow", u"Show Sensor Data", None))
        self.refresh_data_button.setText(QCoreApplication.translate("MainWindow", u"Refresh Table", None))
        ___qtablewidgetitem = self.sensor_data_list.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Sample Number", None));
        ___qtablewidgetitem1 = self.sensor_data_list.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Sample Value", None));
    # retranslateUi

