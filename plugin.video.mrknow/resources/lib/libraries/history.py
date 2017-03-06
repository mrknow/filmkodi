# -*- coding: utf-8 -*-

'''
    plugin.video.mrknow XBMC Addon
    Copyright (C) 2017 mrknow

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

from resources.lib.libraries import control

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

class history:
    def __init__(self):
        self.cache = StorageServer.StorageServer("mrknowfilm")

    def addHistoryItem(self, service, item):
        item = item.decode('UTF-8')
        control.log('HISTORY0: %s' % item)

        if item == "":
            return True
        historyLits = self.cache.get("history_"+service).split(";")
        control.log('HISTORY: %s' % historyLits)
        if historyLits == ['']:
            historyLits = []
        historyLits.insert(0, item)
        historyLits =  ';'.join(historyLits[:10])
        control.log('HISTORY2: %s |%s' % (service, historyLits))

        self.cache.set("history_"+service, historyLits)

    def clearHistoryItems(self, service):
        self.cache.delete("history_%")

    def loadHistoryFile(self, service):
        valTab = []
        historyLits = self.cache.get("history_"+service).split(";")
        control.log('HISTORY: %s |%s' % (service, historyLits))

        for item in historyLits:
            valTab.append(item.encode('UTF-8'))
        return valTab
