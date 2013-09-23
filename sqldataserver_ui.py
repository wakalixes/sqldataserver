# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'puredataserver.ui'
#
# Created: Thu Oct 20 15:13:03 2011
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PureServerMainWindow(object):
    def setupUi(self, PureServerMainWindow):
        PureServerMainWindow.setObjectName(_fromUtf8("PureServerMainWindow"))
        PureServerMainWindow.setWindowModality(QtCore.Qt.WindowModal)
        PureServerMainWindow.resize(250, 91)
        PureServerMainWindow.setMinimumSize(QtCore.QSize(300, 200))
        PureServerMainWindow.setMaximumSize(QtCore.QSize(600, 300))
        PureServerMainWindow.setWindowTitle(QtGui.QApplication.translate("PureServerMainWindow", "Pure-Data-Server", None, QtGui.QApplication.UnicodeUTF8))
        PureServerMainWindow.setIconSize(QtCore.QSize(16, 16))
        PureServerMainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        PureServerMainWindow.setUnifiedTitleAndToolBarOnMac(False)
        self.centralwidget = QtGui.QWidget(PureServerMainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.listWidget = QtGui.QListWidget(self.centralwidget)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.verticalLayout.addWidget(self.listWidget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.resetButton = QtGui.QPushButton(self.centralwidget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        self.resetButton.setPalette(palette)
        self.resetButton.setText(QtGui.QApplication.translate("PureServerMainWindow", "reset db", None, QtGui.QApplication.UnicodeUTF8))
        self.resetButton.setObjectName(_fromUtf8("resetButton"))
        self.verticalLayout.addWidget(self.resetButton)
        self.mergeButton = QtGui.QPushButton(self.centralwidget)
        self.mergeButton.setText(QtGui.QApplication.translate("PureServerMainWindow", "merge db files", None, QtGui.QApplication.UnicodeUTF8))
        self.mergeButton.setObjectName(_fromUtf8("mergeButton"))
        self.verticalLayout.addWidget(self.mergeButton)
        self.mergedailyButton = QtGui.QPushButton(self.centralwidget)
        self.mergedailyButton.setText(QtGui.QApplication.translate("PureServerMainWindow", "merge daily files", None, QtGui.QApplication.UnicodeUTF8))
        self.mergedailyButton.setObjectName(_fromUtf8("mergedailyButton"))
        self.verticalLayout.addWidget(self.mergedailyButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        PureServerMainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(PureServerMainWindow)
        QtCore.QMetaObject.connectSlotsByName(PureServerMainWindow)

    def retranslateUi(self, PureServerMainWindow):
        pass

