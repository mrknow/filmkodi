# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser
import json


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - mmtv"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, libCommon, Parser, settings

log = mrknow_pLog.pLog()

mainUrl = 'http://www.mmtvliveapp.com/mobile/ios/pl/images/'
chanels = 'https://www.mmtv.pl/FrontOffice/ApiliveProductsList.go?platform='+ptv.getSetting('mmtv_platform')+'&terminal='+ptv.getSetting('mmtv_terminal')
playerUrl = 'https://www.mmtv.pl/FrontOffice/LiveAvailability.go'
loginUrl = 'https://www.mmtv.pl/FrontOffice/ApisubscriberLogin.go'

HOST = 'User-Agent: mm-ott/0.1 CFNetwork/609.1.4 Darwin/13.0.0'

MENU_TAB = {1: "Wszystkie",
            3: "Szukaj" }


class mmtv:
    def __init__(self):
        log.info('Starting mmtv.pl')
        self.cm = libCommon.common()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "mmtv.cookie"
        self.settings = settings.TVSettings()
        
    def login(self):    
        if ptv.getSetting('mmtv_login') == 'true':
            #username=mrknow&password=WestWest2009&deviceId=e7701cb8d47305ebdcd538f1bf890a0a8005a9e7&platform=IOS&terminal=PHONE&captcha=(null)
            post_data = {'username': ptv.getSetting('mmtv_user'), 'password': ptv.getSetting('mmtv_pass'),'deviceId': ptv.getSetting('mmtv_deviceid'),'platform': ptv.getSetting('mmtv_platform'),'terminal': ptv.getSetting('mmtv_terminal'), 'captcha':''}
            query_data = {'url': loginUrl, 'use_host': True, 'host': HOST, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True}
            data = self.cm.getURLRequestData(query_data, post_data)
            print ("Data1",data)
            #post_data = {'login': ptv.getSetting('mmtv_user'), 'pass': ptv.getSetting('mmtv_pass'), 'log_in2':'Zaloguj'}
            #query_data = {'url': mainUrl+'index.php?p=login', 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True}
            #data = self.cm.getURLRequestData(query_data, post_data)
            #print ("Data2",data)
            if self.isLoggedIn(data) == True:
                xbmc.executebuiltin("(" + ptv.getSetting('mmtv_user') + ", Zostales poprawnie zalogowany,4000)")
            else:
                xbmc.executebuiltin("XBMC.Notification(Blad logowania, sprawdź login i hasło. Używam Player z limitami,4000)")  
        else:
            query_data = { 'url': playerUrl, 'use_host': True, 'host': HOST, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
            link = self.cm.getURLRequestData(query_data)
            xbmc.executebuiltin("XBMC.Notification(Skonfiguruj konto w ustawieniach, obecnie uzywam Player z limitami,4000)")  
        
    def isLoggedIn(self, data):
        objs = json.loads(data)
        print objs['errorCode']
        if objs['errorCode'] == 0:
          return True
        else:
          return False


    def listsMainMenu(self, table):
        query_data = { 'url': chanels, 'use_host': True, 'host': HOST, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        print ("L",link)
        objs = json.loads(link)
        print objs['result']
        for o in objs['result']:
            print o
            nazwa = json.dumps(o["name"]).replace('"','')
        #    print nazwa
            stream = json.dumps(o["live"]).replace('"','')
            image = json.dumps(o["cover"]).replace('"','')
        #    image = ptv.getAddonInfo('path') + os.path.sep + "images" + os.path.sep  + nazwa +".png"
            print ("Live",stream)
            #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
            #self.add('mmtv', 'playSelectedMovie', 'None', nazwa, mainUrl+image, stream, 'None', 'None', True, False)
            self.add('mmtv', 'playSelectedMovie', 'None', nazwa,image, stream, 'None', 'None', False, False)
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]))




    def getMovieLinkFromXML(self, url):
        print url
        #url = "https://www.mmtv.pl/FrontOffice/ApiliveProductPlaylist.go?productId=39&platform=IOS&terminal=PHONE"
        query_data = { 'url': url, 'use_host': True, 'host': HOST, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        print ("ALLLLLLL",link)
        objs = json.loads(link)
        print objs
        session = self.cm.getCookieItem(self.COOKIEFILE, 'JSESSIONID')
        linkVideo = json.dumps(objs['result']['livx']).replace('"','')
#        linkVideo = match[0].replace('sss','hls').replace('manifest?type=.ism','playlist.m3u8').replace('https','http')
        print ('Data',session,linkVideo)
        print ("CEEEEDAA",link)
        if (ptv.getSetting('mmtv_platform') == 'IOS'):
            return linkVideo
        if (ptv.getSetting('mmtv_platform') == 'ANDROID'):
            linkVideo = linkVideo + '/playlist.m3u8?sessionId='+session
            return linkVideo.replace('rtsp','hls')
        return linkVideo


    def getSizeAllItems(self, url):
        numItems = 0
        req = urllib2.Request(url)
        req.add_header('User-Agent', HOST)
        openURL = urllib2.urlopen(req)
        readURL = openURL.read()
        openURL.close()
        match = re.compile('<li data-theme="c" action="watch">(.*?)<a href="(.*?)" data-transition="slide">(.*?)<img src="(.*?)" height="90px" width="90px" title="(.*?)" />(.*?)</a>(.*?)</li>', re.DOTALL).findall(readURL)
        if len(match) == 1:
            numItems = match[0]
        return numItems
    
    
    def getSizeItemsPerPage(self, url):
        numItemsPerPage = 0
        openURL = urllib.urlopen(url)
        readURL = openURL.read()
        openURL.close()
        match = re.compile('<div class="movie-(.+?)>').findall(readURL)
        if len(match) > 0:
            numItemsPerPage = len(match)
        return numItemsPerPage        

    def getMovieID(self, url):
        id = 0
        tabID = url.split(',')
        if len(tabID) > 0:
            id = tabID[1]
        return id


    def getItemTitles(self, table):
        out = []
        for i in range(len(table)):
            value = table[i]
            out.append(value[1])
        return out

    def getItemURL(self, table, key):
        link = ''
        for i in range(len(table)):
            value = table[i]
            if key in value[0]:
                link = value[2]
                break
        return link


    def searchInputText(self):
        text = None
        k = xbmc.Keyboard()
        k.doModal()
        if (k.isConfirmed()):
            text = k.getText()
        return text
    

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
            self.login()
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

        
  
