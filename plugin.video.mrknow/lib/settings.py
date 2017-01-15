# -*- coding: utf-8 -*-
import xbmcplugin, xbmcaddon, xbmcgui, xbmc
import sys, os, stat, re
import urllib
import mrknow_pLog

scriptID = sys.modules[ "__main__" ].scriptID
log = mrknow_pLog.pLog()


class TVSettings:
    def __init__(self):
        addon = xbmcaddon.Addon(scriptID)

    def showSettings(self):
        xbmcaddon.Addon(scriptID).openSettings(sys.argv[0])
        
    #def recStart(self):
    def getSettings(self, service):
        valDict = {}
        settingsTab = self.getSettingsTab()
        for i in range(len(settingsTab)):
            if settingsTab[i][0] == service:
                valDict[settingsTab[i][1]] = addon.getSetting(settingsTab[i][1])
        return valDict


    def getSettingsTab(self):
        valTab = []
        strTab = []      
        xmlfile = addon.getAddonInfo('path') + os.path.sep + 'resources' + os.path.sep + 'settings.xml'       
        xmldoc = minidom.parse(xmlfile)
        setlist = xmldoc.getElementsByTagName('setting')  
        for i in range(len(setlist)):
            try: s = setlist[i].attributes["id"]
            except: pass
            else:
                s = s.value
                tab = s.split('_')
                strTab.append(tab[0])
                strTab.append(s)
                valTab.append(strTab)
                strTab = []
        return valTab    