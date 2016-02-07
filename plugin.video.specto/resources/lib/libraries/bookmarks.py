# -*- coding: utf-8 -*-

'''
    Specto Add-on
    Copyright (C) 2015 lambda

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import hashlib

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

from resources.lib.libraries import control


def getBookmark(name, imdb='0'):
    try:
        offset = '0'
        idFile = hashlib.md5()
        for i in name: idFile.update(str(i))
        for i in imdb: idFile.update(str(i))
        idFile = str(idFile.hexdigest())
        dbcon = database.connect(control.databaseFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM bookmark WHERE idFile = '%s'" % idFile)
        match = dbcur.fetchone()
        offset = str(match[1])
        dbcon.commit()
        return offset
    except:
        return '0'


def addBookmark(currentTime, name, imdb='0'):
    try:
        idFile = hashlib.md5()
        for i in name: idFile.update(str(i))
        for i in imdb: idFile.update(str(i))
        idFile = str(idFile.hexdigest())
        timeInSeconds = str(currentTime)
        control.makeFile(control.dataPath)
        dbcon = database.connect(control.databaseFile)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS bookmark (""idFile TEXT, ""timeInSeconds TEXT, ""UNIQUE(idFile)"");")
        dbcur.execute("DELETE FROM bookmark WHERE idFile = '%s'" % idFile)
        dbcur.execute("INSERT INTO bookmark Values (?, ?)", (idFile, timeInSeconds))
        dbcon.commit()
    except:
        pass


def deleteBookmark(name, imdb='0'):
    try:
        idFile = hashlib.md5()
        for i in name: idFile.update(str(i))
        for i in imdb: idFile.update(str(i))
        idFile = str(idFile.hexdigest())
        control.makeFile(control.dataPath)
        dbcon = database.connect(control.databaseFile)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS bookmark (""idFile TEXT, ""timeInSeconds TEXT, ""UNIQUE(idFile)"");")
        dbcur.execute("DELETE FROM bookmark WHERE idFile = '%s'" % idFile)
        dbcon.commit()
    except:
        pass

