"""
*   This module is part of the data_server.py application
*   $Rev: 27 $
*   $Date: 2011-08-06 18:10:58 +0200 (Sat, 06 Aug 2011) $
*   $Author: stefan $
*
*   Copyright notice:
* 
*   (c) 2011 Stefan Besler (stefan.besler@gmail.com)
*       2013 Albert Frisch (alebrt.frisch@gmail.com)
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



"""This module is needed for pushing data generated from the LabView picture program
into the database that we are using (local.db)
There's a lot of stuff in here that is not acually needed, for instance we are setting up
a Qt-Window for this (why?!?) anyhow on each start of this module we will add all the content
from log_bilder.txt into local database and from then we will watch the file letztezeile.txt
add push the data we find there into the database. letztezeile.txt is essentially current
last line from log_bilder.txt and it is much fast to just add the data we find there than
loading log_bilder.txt everytime"""
import numpy as np
import csv as csv
import sys
from PyQt4 import QtCore
from PyQt4 import QtGui
from sqldataserver_ui import Ui_PureServerMainWindow
from authenticate import AuthenticateDialog
from data_filler import LogBilderDatabaseFiller,BackupDatabaseFiller
from scipy import linspace, polyval, polyfit, sqrt, stats, randn
import sys,os
import MySQLdb as mysql
import datetime
import re
import time

REMOTEUSER = True # use 'True' if this app should be run remotely
ROOTUSER = ''
ROOTPWD = ''
ROOTHOST = ''

output=None
seriousState=False
def message(s, serious=False):
  """helper function for message handling, add a date and time to each
  message we want to show
  s: str
    message to show"""
  global seriousState
  if seriousState and not serious:
    return
  if output.count() > 10 and not seriousState:
    output.clear()
  output.addItem(datetime.datetime.now().strftime("%b %d %H:%M:%S: ")+str(s))
  print datetime.datetime.now().strftime("%b %d %H:%M:%S: ")+str(s)
  seriousState = serious
#message(s, serious=False)

class PureDataServerWindow(QtGui.QMainWindow, Ui_PureServerMainWindow):
  """This class is the main window for doing data pushing. Actually this window contains
  no GUI elements at all but it provides a nice endless loop for watching for changes in
  letztezeile.txt. The actual watching out for file changes is done by a file-watcher, a
  Qt class which is exactly designed for this propose and the endless loop (Qt internal)
  is of course needed for keeping this programm alive all the time"""
  
  db=''
  dbcur=''
  path=''
  warned=False
  
  # file to check during runtime (should be small to be fast)
  lastLineFile="E:\Experiment Data\letztezeile.txt"
  
  # file to merge into database when the app is started (can be a large file)
  startMergeFile="E:\Experiment Data\dailylog.txt"
  
  def __init__(self, parent = None):
    """setup a filewatcher and connect to local.db where we store all the data we get in"""    
    # initialization of the superclass
    super(PureDataServerWindow, self).__init__(parent)
    self.setupUi(self)
    #self.setWindowFlags(QtCore.Qt.Tool);

    # remote access ?
    global REMOTEUSER,ROOTUSER,ROOTPWD,ROOTHOST
    self.authenticateDialog = AuthenticateDialog(self)
    if REMOTEUSER:
      QtCore.QObject.connect(self.authenticateDialog, QtCore.SIGNAL('accepted()'),self.__initGUI)
      QtCore.QObject.connect(self.authenticateDialog, QtCore.SIGNAL('rejected()'),self.close)
      self.authenticateDialog.show()
    else:
      self.authenticateDialog.close()
      self.authenticateDialog.host = ROOTHOST
      self.authenticateDialog.user = ROOTUSER
      self.authenticateDialog.pwd = ROOTPWD
      self. __initGUI()
  #__init__(self, parent = None)
      
  def __initGUI(self):
    global output, seriousState
    output = self.listWidget
    print self.listWidget
    message("running")    
    QtCore.QObject.connect(self.listWidget, QtCore.SIGNAL('itemSelectionChanged()'),self.connectToDatabase)
    QtCore.QObject.connect(self.mergeButton, QtCore.SIGNAL('clicked()'),self.merge)
    QtCore.QObject.connect(self.resetButton, QtCore.SIGNAL('clicked()'),self.reset)
    QtCore.QObject.connect(self.mergedailyButton, QtCore.SIGNAL('clicked()'),self.mergedaily)
     
    self.pathname = os.path.realpath(os.path.dirname(sys.argv[0]))

    #setup a file watcher
    self.fileMonitor=QtCore.QFileSystemWatcher(self)
    try:
      self.fileMonitor.addPath(self.lastLineFile)
    except:
      print "'%s' file doesn't exist" % self.lastLineFile
      

    #connect to mysql database
    self.connectToDatabase()
    self.prepareConditionWriting()

    QtCore.QObject.connect(self.fileMonitor, QtCore.SIGNAL('fileChanged(const QString&)'),self.fileChanged) 

    # intial pushing to database
    t1 = time.clock()
    message("Initial merge ('%s')" % self.startMergeFile)
    # add everything when starting the application
    if os.path.exists(self.startMergeFile):
      LogBilderDatabaseFiller(self.db, self.startMergeFile)
    else:
      message("'%s' does not exist" % self.startMergeFile)

    t2 = time.clock()
    message("merge done (%i ms)" % int(round((1000.0 * (t2 - t1)))) )
    f = open('mysqldb.log', 'w')
    f.write("changed something, please perform an update")

    # timer to make a stupid mysql call in order to keep the connection alive
    self.timer=QtCore.QTimer()
    QtCore.QObject.connect(self.timer,QtCore.SIGNAL('timeout()'), self.dontLooseConnection)
    self.timer.start(1000*60*60)
  #__initGUI(self)
    
  def dontLooseConnection(self):
    try:        
      self.dbcur.execute("SELECT * FROM dataTable LIMIT 1")
      self.db.commit()
    except mysql.Error,e:
      print "Error in keeping connetion alive, reconnecting..."
      self.connectToDatabase()
  #dontLooseConnection(self)
   
  def merge(self):
    message ("Merging a file to the database")
    
    lineEdit=QtGui.QFileDialog.getOpenFileName(self, "Import data", self.pathname+"../", "*.txt")
    # do we want to import a backup or a log_bilder file?
    rex = r'(.*)(_log_bilder)(.*)'
    matchObj = re.match(rex, lineEdit, re.M|re.I)
    if matchObj:
      message ("you try to add a  log_bilder file (LevT only!!)")
      LogBilderDatabaseFiller(self.db, lineEdit)
    else:
      message ("you try to add a backup file")
      BackupDatabaseFiller(self.db, lineEdit)
  #merge(self)
      
  def mergedaily(self):
    t1 = time.clock()
    message ("Merging a daily-log file to the database")
    lineEdit=QtGui.QFileDialog.getOpenFileName(self, "Import daily log data", self.pathname+"../", "*.txt")
    LogBilderDatabaseFiller(self.db, lineEdit)
    t2 = time.clock()
    message("merge done (%i ms)" % int(round((1000.0 * (t2 - t1)))) )
    message("Restart Data Analysing software!")
  #mergedaily(self)
    
  def reset(self):
    message ("Resetting database request")

    reply = QtGui.QMessageBox.question(self, 'Message',
            "Do you want to back the database first? (recommended) ", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)

    if reply == QtGui.QMessageBox.Yes:
      message("backup database")
      lineEdit=QtGui.QFileDialog.getSaveFileName(self, "Import data", self.pathname+"../", "*.txt")
      f = open(lineEdit,"w")
      
      self.dbcur.execute (str("SELECT * FROM dataTable LIMIT 1"))
      keys = self.dbcur.description
      self.dbcur.execute("SELECT * FROM dataTable ORDER BY id")
      dt = self.dbcur.fetchall()
      
      for row in dt:
        line=""
        for i,column in enumerate(row):
          line += keys[i][0]+"\t"+str(column)+"\t"
        f.write(line+"\n")
	
      message("... done")
      
    really = QtGui.QMessageBox.question(self, 'Message',
            "Are you absolutely sure that you want to do this? ", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)

    if really == QtGui.QMessageBox.Yes:
      message("Resetting database")
      self.dbcur.execute ("DELETE FROM dataTable")
      message("... done")      
  #reset(self)

  def connectToDatabase(self):
    try:
      ssl_settings = {
      'key': self.pathname+"/certificate/client-key.pem", \
      'ca': self.pathname+'/certificate/ca-cert.pem', \
      'cert': self.pathname+'/certificate/client-cert.pem'
      }
      
      self.db = mysql.connect(str(self.authenticateDialog.host), str(self.authenticateDialog.user), str(self.authenticateDialog.pwd), 'localdb', ssl=ssl_settings); 
      
      self.dbcur = self.db.cursor()
      self.dbcur.execute("SET AUTOCOMMIT=1")

      seriousState = False
      message("Connected to database")
    except mysql.Error,e:
      message("Couldn't connect to MySQL server!"+str(e), serious=True)
      message("click here to reconnect", serious=True)
  #connectToDatabase(self)
      
  def prepareConditionWriting(self):
    """ this works only when running as root, generates a table that is used in sql_data_plot.py """
    if self.db == None:
      message("No database connection")
      return

    try:
      self.dbcur.execute("SELECT * FROM conditionTable LIMIT 1")
    except mysql.Error,e: 
      message("(warning) conditionTable does not exist "+str(e))   
      self.dbcur.execute("CREATE TABLE IF NOT EXISTS conditionTable (id VARCHAR(255), Dataset VARCHAR(100), Date VARCHAR(50), Conditions TEXT, axes VARCHAR(255), fitplugin VARCHAR(255), transformplugin VARCHAR(255), fitparameters VARCHAR(255), transformparameters VARCHAR(255), Temperature VARCHAR(100), Holding VARCHAR(100), Trap VARCHAR(50), Ramping VARCHAR(50), Compressed VARCHAR(50), Calibration VARCHAR(50), Text TEXT);")
      self.dbcur.execute("ALTER TABLE conditionTable ADD PRIMARY KEY (id), ADD UNIQUE (id);")
      self.dbcur.execute("ALTER TABLE conditionTable ADD INDEX(Dataset), ADD INDEX(Date);")
      self.db.commit()
  #prepareConditionWriting(self)
      
  def closeEvent(self,e):
    self.authenticateDialog.close()
  #closeEvent(self,e)
    
  def directoryChanged(self,path):
    """ if letztezeile.txt gets removed by a user for some reason we just watch the directory that
    it is usually in"""
    
    if not self.lastLineFile in self.fileMonitor.files() and os.path.exists(lastLineFile):
      self.fileMonitor.addPath(self.lastLineFile)
  #directoryChanged(self,path)
      
  def fileChanged(self,fname):
    """ add something to local.db, this is called whenever the filewatcher of the class sees a 
    change in letztezeile.txt (indirectly via"""
    try:
      self.db.cursor()
    except (AttributeError, mysql.OperationalError):
      self.connectToDatabase()
          
    t1 = time.clock()
    if os.path.exists(self.lastLineFile):
      LogBilderDatabaseFiller(self.db, self.lastLineFile)

      # write a log that other apps might watch for changes
      f = open('../db/mysqldb.log', 'w')
      f.write("changed something, please perform an update")
      
    message("update (%i ms)" % int(round((1000.0 * (time.clock() - t1)))) )
  #fileChanged(self,fname)
    
app = QtGui.QApplication(sys.argv)
dmw = PureDataServerWindow()
dmw.show()
sys.exit(app.exec_())
 
