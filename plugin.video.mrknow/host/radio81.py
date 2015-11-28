# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser
import json


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - radio81"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, mrknow_pCommon, Parser, settings, Player, mrknow_urlparser, mrknow_Pageparser,mrknow_Player

log = mrknow_pLog.pLog()

mainUrl = 'http://www.radio81.pl/'
chanels = 'http://www.radio81.pl/tv-online/'
playerUrl = 'http://www.youtube.pl/'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {1: "Wszystkie",
            3: "Szukaj" }


class radio81:
    def __init__(self):
        log.info('Starting radio81.pl')
        self.cm = mrknow_pCommon.common()
        self.parser = Parser.Parser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.settings = settings.TVSettings()
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "radio81.cookie"
        self.pp = mrknow_Pageparser.mrknow_Pageparser()
        self.p = mrknow_Player.mrknow_Player()

    def listsMainMenu(self):
        query_data = { 'url': chanels, 'use_host': True, 'host': HOST, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<li id="cid_1">\r\n<a href="(.*?)"(.*?)></div>\r\n<div class="programmeListText">\r\n<span class="programmeListTextLeft"><p class="programmeListTextLeftTitle">(.*?)</p><p class="programmeListTextLeftName">(.*?)</p></span>\r\n</div>\r\n</a>\t</li>', re.DOTALL).findall(link)
        for o in range(len(match)):
            match10 = re.compile('onclick=\"programmeShow\(1, \'(.*?)\'\);">\r\n<div class="programmeListImage" style="background-image:url\(\'(.*?)\'\);\"').findall(match[o][1])
            if len(match10) > 0:
                self.add('radio81', 'items-menu',  'None',match[o][2] +'-'+ match[o][3],match10[0][1], match[o][0], 'None', 'None', True, False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self,url):
        query_data = { 'url': url, 'use_host': True, 'host': HOST, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        print ("LinkChanells",link)
        match1 = re.compile('<li class="group"><div><a href="(.*?)"(.*?)">\r\n<div class="thumb-sm group"><span(.*?)>(.*?)</span><span(.*?)>\r\n<div class="title">(.*?)</div><p class="deck">(.*?)</p></span><span class="img_container">\r\n<img src="(.*?)"(.*?)>\r\n</span></div></a></div></li>', re.DOTALL).findall(link)
        print ("matchchanels",match1)
        for i in range(len(match1)):
            print("i",i,match1[i])
            self.add('radio81', 'playSelectedMovie', 'None', match1[i][5] + ' - '+match1[i][6], 'None', match1[i][0], 'None', 'None', False, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

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
        elif name == 'items-menu':
            log.info('Jest categories-menu: ')
            self.listsCategoriesMenu(url)
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.pp.getVideoLink(url), title, icon)
        
  
