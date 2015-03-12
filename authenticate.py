"""
*   This module is part of the data_server.py application
*   $Rev: 27 $
*   $Date: 2011-08-06 18:10:58 +0200 (Sat, 06 Aug 2011) $
*   $Author: stefan $
*
*   Copyright notice:
* 
*   (c) 2011 Stefan Besler (stefan.besler@gmail.com)
*       2013 Albert Frisch (albert.frisch@gmail.com)
*
*   All rights reserved
*
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt4 import QtCore
from PyQt4 import QtGui
from authenticate_ui import Ui_Dialog
import csv
import numpy as np


class AuthenticateDialog(QtGui.QMainWindow, Ui_Dialog):
  accepted = QtCore.pyqtSignal()
  rejected = QtCore.pyqtSignal()
   
  def __init__(self, parent = None):
    super(AuthenticateDialog, self).__init__(parent)
    # setup the GUI --> function generated by pyuic4
    self.parent = parent
    self.setupUi(self)
    self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool);
   
    frect = QtCore.QRect(self.frameGeometry());
    frect.moveCenter(QtGui.QDesktopWidget().availableGeometry().center());
    self.move(frect.topLeft())
    
    self.quit=False
    settings = QtCore.QSettings("LevT","Authentication")
    self.hostEdit.setText(settings.value("Host").toString())
    self.userEdit.setText(settings.value("User").toString())
    self.passwordEdit.setText(settings.value("Pwd").toString())
  #__init__(self, parent = None)
    
  def reject(self):
    self.quit=True
    self.host=""
    self.user=""
    self.pwd=""
    self.rejected.emit()
    self.hide()
  #reject(self)
    
  def accept(self):
    self.host=self.hostEdit.text()
    self.user=self.userEdit.text()
    self.pwd=self.passwordEdit.text()
    self.parent.setEnabled(True)
    self.accepted.emit()
    self.hide()
    self.close()
  #accept(self)
    
  def closeEvent(self, event):
    settings = QtCore.QSettings("LevT","Authentication")
    settings.setValue("Host", self.hostEdit.text())
    settings.setValue("User", self.userEdit.text())
    settings.setValue("Pwd", self.passwordEdit.text())
    settings.sync()
  #closeEvent(self, event)
