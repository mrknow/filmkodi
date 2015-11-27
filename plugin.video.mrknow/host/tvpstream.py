# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser
import json



scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - tvpstream"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, libCommon, Parser

log = mrknow_pLog.pLog()

mainUrl = 'http://tvpstream.tvp.pl/'
chanel1 = 'http://www.tvp.pl/shared/cdn/tokenizer_v2.php?object_id='
playerUrl = 'http://www.youtube.pl/'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {1: "Wszystkie",
            3: "Szukaj" }


class tvpstream:
    def __init__(self):
        log.info('Starting tvpstream.pl')
        self.cm = libCommon.common()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()



    def listsMainMenu(self, table):
        query_data = { 'url': mainUrl, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile("<div id='portrait'>(.*?)</body>", re.DOTALL).findall(link)
        match = re.compile('<div style="background-image:url\(\'(.*?)\'\);(.*?)" id="(.*?)" data-channel="(.*?)" data-name=\'(.*?)\' class="button"></div>', re.DOTALL).findall(match1[0])
        if len(match) > 0:
            for i in range(len(match)):    
                self.add('tvpstream', 'playSelectedMovie', 'None', match[i][4], match[i][0], match[i][3], 'aaaa', 'None', False, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getMovieLinkFromXML(self, url):
        newurl = 'http://tvpstream.tvp.pl/sess/vplayer.php?object_id='+url.replace('l','')+'&platform=sdt-v3-mobile&template=vplayer/tvpstream.html'
        req = urllib2.Request(newurl)
        req.add_header('Referer', 'http://tvpstream.tvp.pl/')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link22=response.read()
        response.close()        
        match = re.compile('<video id="myVideo" width="100%" height="100%" src="(.*?)" autoplay="true" controls="false" ></video>', re.DOTALL).findall(link22)
        linkVideo = match[0]
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
            
            if not xbmc.Player().isPlaying():
                xbmc.sleep( 10000 )
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
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Wszystkie':
            log.info('Jest Wszystkie: ')
            self.listsItems(mainUrl)
            
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems(self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems(url)
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(url), title, icon)
#            self.LOAD_AND_PLAY_VIDEO(url, title, icon)
        if name == 'playSelectedMovie1':
            self.LOAD_AND_PLAY_VIDEO(url, title, icon)

        
  
