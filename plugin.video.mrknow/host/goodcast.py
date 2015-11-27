# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser
import json


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - goodcast"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, libCommon, Parser, settings, pageparser, Player

log = mrknow_pLog.pLog()

mainUrl = 'http://goodcast.tv/'
chanels = 'http://goodcast.tv/lista.html'
playerUrl = 'http://www.youtube.pl/'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {1: "Wszystkie",
            3: "Szukaj" }


class goodcast:
    def __init__(self):
        log.info('Starting goodcast.pl')
        self.cm = libCommon.common()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()
        self.cm = libCommon.common()
        self.settings = settings.TVSettings()
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "goodcast.cookie"
        self.pp = pageparser.pageparser()
        self.p = Player.Player()

    def listsMainMenu(self):
        query_data = { 'url': chanels, 'use_host': True, 'host': HOST, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        #match = re.compile('<li id=\'(.*?)\'><a href=\'(.*?)\'>(.*?)</a></li>', re.DOTALL).findall(link)
        #<a href="tvp1.html" TARGET="_blank"><font color="white">TVP1</font></a> 
        #<a href="tvp2.html" TARGET="_blank"><font color="white">TVP2</font></a>
        match = re.compile('<a href="(.*?)" TARGET="_blank"><font color="(.*?)">(.*?)</font></a>', re.DOTALL).findall(link)
        print ("match",match)
        print match
        for o in range(len(match)):
            if match[o][1] == "white":
                self.add('goodcast', 'playSelectedMovie', 'None', match[o][2], 'None', mainUrl+ match[o][0], 'None', 'None', False, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

       
    def getMovieLinkFromXML(self, url):
        #print ("URL",url)
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
        liz=xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
        liz.setInfo( type="Video", infoLabels={ "Title": title, } )
        try:
            xbmcPlayer = xbmc.Player()
            xbmcPlayer.play(videoUrl, liz)
            
           # if not xbmc.Player().isPlaying():
           #     xbmc.sleep( 10000 )
                #xbmcPlayer.play(url, liz)
            
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
        print(name,category,url,title)
        if name == None:
            self.listsMainMenu()
        elif name == 'main-menu' and category == 'Wszystkie':
            log.info('Jest Wszystkie: ')
            self.listsCategoriesMenu(chanels)
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(url), title, icon)
        
  
