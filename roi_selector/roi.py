# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'roi.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ROI(object):
    def setupUi(self, ROI):
        ROI.setObjectName("ROI")
        ROI.resize(879, 709)
        self.centralWidget = QtWidgets.QWidget(ROI)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.crop_btn = QtWidgets.QToolButton(self.centralWidget)
        self.crop_btn.setToolTip("")
        self.crop_btn.setObjectName("crop_btn")
        self.buttonGroup = QtWidgets.QButtonGroup(ROI)
        self.buttonGroup.setObjectName("buttonGroup")
        self.buttonGroup.addButton(self.crop_btn)
        self.verticalLayout.addWidget(self.crop_btn)
        self.lines_btn = QtWidgets.QToolButton(self.centralWidget)
        self.lines_btn.setToolTip("")
        self.lines_btn.setObjectName("lines_btn")
        self.buttonGroup.addButton(self.lines_btn)
        self.verticalLayout.addWidget(self.lines_btn)
        self.save_btn = QtWidgets.QToolButton(self.centralWidget)
        self.save_btn.setToolTip("")
        self.save_btn.setObjectName("save_btn")
        self.buttonGroup.addButton(self.save_btn)
        self.verticalLayout.addWidget(self.save_btn)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.url_bar = QtWidgets.QLineEdit(self.centralWidget)
        self.url_bar.setObjectName("url_bar")
        self.horizontalLayout.addWidget(self.url_bar)
        self.browse_btn = QtWidgets.QPushButton(self.centralWidget)
        self.browse_btn.setObjectName("browse_btn")
        self.horizontalLayout.addWidget(self.browse_btn)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.image_display = QtWidgets.QGraphicsView(self.centralWidget)
        self.image_display.setObjectName("image_display")
        self.verticalLayout_2.addWidget(self.image_display)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 1, 1, 1)
        ROI.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(ROI)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 879, 25))
        self.menuBar.setObjectName("menuBar")
        ROI.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(ROI)
        self.mainToolBar.setObjectName("mainToolBar")
        ROI.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(ROI)
        self.statusBar.setObjectName("statusBar")
        ROI.setStatusBar(self.statusBar)

        self.retranslateUi(ROI)
        QtCore.QMetaObject.connectSlotsByName(ROI)

    def retranslateUi(self, ROI):
        _translate = QtCore.QCoreApplication.translate
        ROI.setWindowTitle(_translate("ROI", "ROI"))
        self.crop_btn.setText(_translate("ROI", "..."))
        self.lines_btn.setText(_translate("ROI", "..."))
        self.save_btn.setText(_translate("ROI", "..."))
        self.browse_btn.setText(_translate("ROI", "Browse"))
