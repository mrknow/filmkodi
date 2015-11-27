# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math, time
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser,urlparse
import json


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - cda.pl"
ptv = xbmcaddon.Addon(scriptID)
datapath = xbmc.translatePath(ptv.getAddonInfo('profile'))

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_urlparser, mrknow_Pageparser, mrknow_Player

log = mrknow_pLog.pLog()

mainUrl = 'http://zobacztv.beep.pl/'
mainUrl = 'http://zobacztv.beep.pl/'



class zobaczjcompl:
    def __init__(self):
        log.info('Starting zobaczjcompl.pl')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.pp = mrknow_Pageparser.mrknow_Pageparser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.player = mrknow_Player.mrknow_Player()
        
    def listsMainMenu(self):
        query_data = {'url': mainUrl, 'use_host': False, 'use_post': False,'return_data': True}
        data = self.cm.getURLRequestData(query_data)
        match = re.compile('<td><a href="(.*?)"><img width="(.*?)" height="(.*?)"(.*?)src="(.*?)"(.*?)/></a></td>\n', re.DOTALL).findall(data)
        #print("Match-->",match)
        valTab = []
        strTab = []
        if len(match)>0:
            for l in range(len(match)):
                if len(match[l][0]) > 0:
                        strTab.append(mainUrl+match[l][0])
                        strTab.append(mainUrl+match[l][4])
                        strTab.append(match[l][0])
                        valTab.append(strTab)
                        strTab = []
            valTab.sort(key = lambda x: x[0])
            for i in valTab:
                self.add('zobaczjcompl', 'playSelectedMovie', 'None', i[2], i[1], i[0], 'None', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))



    def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True,strona=''):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage)+ "&strona=" + urllib.quote_plus(strona)
        #log.info(str(u))
        if name == 'main-menu' or name == 'categories-menu':
            title = category 
        if iconimage == '':
            iconimage = "DefaultVideo.png"
        liz=xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if isPlayable:
            liz.setProperty("IsPlayable", "true")
        liz.setInfo( type="Video", infoLabels={ "Title": title } )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder)
            

    def LOAD_AND_PLAY_VIDEO(self, videoUrl, title, icon):
        ok=True
        if videoUrl == '':
                d = xbmcgui.Dialog()
                d.ok('Nie znaleziono streamingu.', 'Może to chwilowa awaria.', 'Spróbuj ponownie za jakiś czas')
                return False
        liz=xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon, path=videoUrl)
        liz.setInfo( type="Video", infoLabels={ "Title": title, } )
        try:
            xbmcPlayer = xbmc.Player()
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

        except:
            d = xbmcgui.Dialog()
            d.ok('Błąd przy przetwarzaniu.', 'Problem')        
        return ok


    def handleService(self):
    	params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        strona = self.parser.getParam(params, "strona")
        #print("Dane",url,name,category,title)

        if name == None:
            self.listsMainMenu()
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.pp.getVideoLink(url), title, icon)

        
  
