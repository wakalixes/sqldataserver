"""
*   This module is part of the data_server.py application
*   $Rev: 24 $
*   $Date: 2011-08-06 02:10:37 +0200 (Sat, 06 Aug 2011) $
*   $Author: stefan $
*
*   Copyright notice:
* 
*   (c) 2011 Stefan Besler (stefan.besler@gmail.com)
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


import csv as csv
import sys,os
from sqlite3 import dbapi2 as sqlite
import datetime
import re
import platform
import math

class DatabaseFiller(object):
  entries = 0 
  loaded = False
  db = ""
  tbl= ""
  rows = []
  def __init__(self,db,dataObject=""): 
    type(self).entries = 0
    type(self).loaded = 0
    self.db = db
    self.newData = False
    
  def load(self,dataObject):
    """implement loading a table here"""
    pass

  def uniqueColumn(self):
    """return the unique name of the tables unique column"""
    pass
  
  def fill(self, rowIds=None):
    """database gets filled here if loaded correctly"""
    if not self.loaded or len(self.rows) <= 0:
      print("nothing got loaded yet")
      return

    # TODO: check if one line has more columns and deal with it
    columnNamesStr=""
    keysStr=""

    cur = self.db.cursor()
    #cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dataTable'");
    #dt = cur.fetchall()
    
    # init a table, this will only happen the first time, when the database is created  
    #if len(dt) == 0:
      
    for k,v in self.rows[0]:
      if k==self.uniqueColumn():
        columnNamesStr += k.replace(" ","_")+" VARCHAR(255) PRIMARY KEY UNIQUE,"
      else:
        columnNamesStr += k.replace(" ","_")+" VARCHAR(50),"
	  
      keysStr += k.replace(" ","_")+"," 

    columnNamesStr = columnNamesStr[0:len(columnNamesStr)-1]
    # print "CREATE TABLE IF NOT EXISTS dataTable ("+ columnNamesStr+")"
    cur.execute("CREATE TABLE IF NOT EXISTS dataTable ("+ columnNamesStr+")")
    self.db.commit()
    # end if create dataTable if it does not exists

    # sadly columns could have been added, the following code is nesacarry to add them
    keys = set([])
    for r in self.rows:
      for k,v in r:
        keys.add(k.replace(" ", "_"))
        
    #print "keys found:"+str(keys)

    cur.execute ("SELECT * FROM dataTable LIMIT 1")
    keysExisting = set([])
    for k in cur.description:
      keysExisting.add(str(k[0]).lower())

    #print "keys already in db: "+str(keysExisting)

    #add columns if it is needed
    for ck in keys:
      if not ck.lower() in keysExisting:
        print("adding a column: %s" % str(ck))
        cur.execute("ALTER TABLE dataTable ADD COLUMN %s VARCHAR(50)" % str(ck))

    
    #insert all values or update some
    for i,r in enumerate(self.rows):
      ck=''
      cv=''
      updatekv=''
      for k,v in r:
        ck="%s %s," % (ck,k.replace(" ","_"))
        cv="%s '%s'," % (cv,str(v))
        updatekv="%s %s='%s'," %(updatekv, k.replace(" ","_"), str(v))

      if not ck =='' and not cv == '':      
        if not rowIds or self.newData:
          ck=ck[0:len(ck)-1]
          cv=cv[0:len(cv)-1]
          if platform.system() == "Windows":
            cur.execute("INSERT IGNORE INTO dataTable (%s) VALUES(%s)" % (ck,cv))
          else:
            cur.execute("INSERT OR IGNORE INTO dataTable (%s) VALUES(%s)" % (ck,cv))
        else:
          updatekv=updatekv[0:len(updatekv)-1]
          cur.execute("UPDATE dataTable SET %s WHERE %s='%s'" % (updatekv, self.uniqueColumn(), rowIds[i]))

    self.db.commit()
 
class LogBilderDatabaseFiller(DatabaseFiller):
  def __init__(self,db, dataObject): 
    DatabaseFiller.__init__(self,db,dataObject)

    #print "filler created"
    self.load(dataObject)
    self.fill()


  def load(self,dataObject):
    self.data = csv.reader(open(dataObject, 'rb'), delimiter='\t', quotechar='|')
    self.rows = []
    failsafe = False
    id = ""

    for i,row in enumerate(self.data):
      self.rows.append([])
      for column,val in enumerate(row):
        val= val.replace(',','.')
        try:
          cv = float(val)
          if math.isnan(cv):
            cv = 0
        except ValueError:
          cv=''
          if column==0:
            ckey= "Dataset"
            id = val
            cv=self.getDatasetName(val)
            keyAt = -1
          elif column==1:
            ckey= "Date"
            cv=val+" "
            keyAt = 0
          elif column==2:
            ckey='Time'
            cv=val
            keyAt = 1
          else:
            ckey = val;
            keyAt = column

        if column==3:
            ckey='Tag'

        if cv != '' and ckey != '' and column-1 == keyAt:
          self.rows[i].append ([ckey,cv])
          ckey = ''
          #print "key: %s val: %s" %(ckey,cv)

        #add a picture id in the end
        if column == len(row)-1:
          self.rows[i].append(["id", id])

    self.loaded=True

  def uniqueColumn(self):
    return "id"
  
  def getDatasetName(self,name):
    matchObj = re.match( r'([0-9]*)_(.*)_(.*)', name, re.M|re.I)

    if not matchObj:
      raise Exception("no valid datasetname '%s'" % name)
   
    return matchObj.group(2)



class BackupDatabaseFiller(DatabaseFiller):
  def __init__(self,db, dataObject): 
    DatabaseFiller.__init__(self,db,dataObject)

    #print "filler created"
    self.load(dataObject)
    self.fill()


  def load(self,dataObject):
    self.data = csv.reader(open(dataObject, 'rb'), delimiter='\t', quotechar='|')
    self.rows = []
    failsafe = False
    id = ""

    for i,row in enumerate(self.data):
      self.rows.append([])
      for j in xrange(0,len(row)-1,2):
        ckey = row[j]
        cv = row[j+1]
        keyAt = j
        cv= cv.replace(',','.')
        if cv != '' and ckey != '':
          self.rows[i].append ([ckey,cv])
          ckey = ''

    self.loaded=True

  def uniqueColumn(self):
    return "id"
  
  def getDatasetName(self,name):
    matchObj = re.match( r'([0-9]*)_(.*)_(.*)', name, re.M|re.I)

    if not matchObj:
      raise Exception("no valid datasetname '%s'" % name)
   
    return matchObj.group(2)
    
    

class AndorDatabaseFiller(DatabaseFiller):
  def __init__(self,db, dataObject=[], valueList=[], pictureIdList="", newData=False): 
    DatabaseFiller.__init__(self,db,dataObject)
    self.rows = [ zip(dataObject[i], valueList[i]) for i in xrange(len(dataObject)) ]
    self.loaded = True
    self.newData = newData
    self.fill(pictureIdList)

  def uniqueColumn(self):
    return "id"

  def fill(self, rowIds):
    newRowIds = [ os.path.splitext(str(cid))[0] for cid in rowIds ]
    DatabaseFiller.fill(self,newRowIds)


class CsvDatabaseFiller(DatabaseFiller):
    def __init__(self,database, dataObject=""): 
        DatabaseFiller.__init__(self, dataObject) 
        self.load(dataObject)
  
    def load(self,object):
      pass
