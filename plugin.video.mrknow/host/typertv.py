# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser
import json


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - typertv"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, mrknow_pCommon, mrknow_Parser, settings,mrknow_urlparser, mrknow_Pageparser

log = mrknow_pLog.pLog()

mainUrl = 'http://www.typertv.com.pl/'



class typertv:
    def __init__(self):
        log.info('Starting typertv.com.pl')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.settings = settings.TVSettings()
        self.pp = mrknow_Pageparser.mrknow_Pageparser()

        
    def listsMainMenu(self):
        query_data = { 'url': mainUrl, 'use_host': True, 'use_cookie': False, 'use_post': False , 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<li><a href="(.*?)"  class=" ">(.*?)</a></li>', re.DOTALL).findall(link)
        valTab = []
        strTab = []
        if len(match)>0:
            for l in range(len(match)):
                strTab.append(match[l][0])
                strTab.append(match[l][1])
                valTab.append(strTab)
                strTab = []
            valTab.sort(key = lambda x: x[1])
            for i in valTab:
                self.add('typertv', 'playSelectedMovie', 'None', i[1], 'None', i[0], 'None', 'None', False, True)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def getMovieLinkFromXML(self, url):
        linkVideo = self.pp.getVideoLink(url)
        return linkVideo


    

    def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage)
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
        print("Dane",sys.argv[1],url,name,category,title)

        if name == None:
            self.listsMainMenu()
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.pp.getVideoLink(url), title, icon)
            
  
