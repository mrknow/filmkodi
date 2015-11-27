# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser
import json


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - filmbox"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, libCommon, Parser, Player

log = mrknow_pLog.pLog()

mainUrl = 'http://www.filmboxliveapp.com/mobile/ios/pl/images/'
chanels = 'http://www.filmboxliveapp.com/channel/channels_pl.json'
playerUrl = 'http://www.youtube.pl/'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {1: "Wszystkie",
            3: "Szukaj" }


class filmbox:
    def __init__(self):
        log.info('Starting filmbox.pl')
        self.cm = libCommon.common()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()
        self.p = Player.Player()        


    def listsMainMenu(self, table):
        query_data = { 'url': chanels, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        
        objs = json.loads(link)
        print objs 
        for o in objs["channels"]:
            nazwa = json.dumps(o["name"]).replace('"','')
            print nazwa
            stream = json.dumps(o["stream"]).replace('"','')
            print stream
            image = o["images"][0]["image"]
            image = ptv.getAddonInfo('path') + os.path.sep + "images" + os.path.sep  + nazwa +".png"
            
            #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
            #self.add('filmbox', 'playSelectedMovie', 'None', nazwa, mainUrl+image, stream, 'None', 'None', True, False)
            self.add('filmbox', 'playSelectedMovie', 'None', nazwa, image, stream, 'None', 'None', False, False)
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self):
        req = urllib2.Request(mainUrl)
        req.add_header('User-Agent', HOST)
        openURL = urllib2.urlopen(req)
        readURL = openURL.read()
        openURL.close()
        match = re.compile('<li data-theme="c">(.*?)<a href="(.*?)" data-transition="slide">(.*?)</a>(.*?)</li>', re.DOTALL).findall(readURL)
        
        if len(match) > 0:
            log.info('Listuje kategorie: ')
            for i in range(len(match)):
                url = mainUrl + match[i][1]
                self.add('filmbox', 'categories-menu', match[i][2].strip(), 'None', 'None', url, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        url = mainUrl + 'search.php?phrase=' + urllib.quote_plus(key) 
        return url
        #req = urllib2.Request(url)
        #req.add_header('User-Agent', HOST)
        #openURL = urllib2.urlopen(req)
        #readURL = openURL.read()
        

    def listsItems(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        #match = re.compile('<strong>\s(.*?)<a href="(.*?)">(.*?)</a>\s(.*?)[video](.*?)</strong>', re.DOTALL).findall(readURL)
        match = re.compile('<strong>\s(.*?)<a href="(.*?)">(.*?)</a>(.*?)</strong>', re.DOTALL).findall(link)
        prin
        if len(match) > 0:
            for i in range(len(match)):
             if match[i][3].find('video') > -1:# 0
            
                #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                self.add('filmbox', 'playSelectedMovie', 'None', match[i][2], 'None', match[i][1], 'aaaa', 'None', True, False)
 
        match1 = re.compile(' <a href="(.*?)" class="inlblk tdnone vtop button" style="right: 0px">następna</a>').findall(link)
        log.info('Nastepna strona: '+  match1[0])
        self.add('filmbox', 'categories-menu', 'Następna', 'None', 'None', match1[0], 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsItemsPage(self, url):
        if not url.startswith("http://"):
            url = mainUrl + url
        if self.getSizeAllItems(url) > 0  and self.getSizeItemsPerPage(url) > 0:
            a = math.ceil(float(self.getSizeAllItems(url)) / float(self.getSizeItemsPerPage(url)))
            for i in range(int(a)):
                num = i + 1
                title = 'Lista ' + str(num)
                destUrl = url + sort_asc + '&page=' + str(num)
                self.add('filmbox', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))        


    def listsItemsSerialPage(self, url, sizeOfSerialParts):
        if not url.startswith("http://"):
            url = mainUrl + url
        if sizeOfSerialParts > 0  and self.getSizeItemsPerPage(url) > 0:
            a = math.ceil(float(sizeOfSerialParts) / float(self.getSizeItemsPerPage(url)))
            for i in range(int(a)):
                num = i + 1
                title = 'Lista ' + str(num)
                destUrl = url + sort_asc + '&page=' + str(num)
                self.add('filmbox', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1])) 


    def getMovieLinkFromXML(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<blockquote cite="(.*?)"', re.DOTALL).findall(link)
        linkVideo = self.up.getVideoLink(match[0])
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
            self.p.LOAD_AND_PLAY_VIDEO(url+'|User-Agent=Mozilla%2f5.0+(iPad%3b+CPU+OS+6_0+like+Mac+OS+X)+AppleWebKit%2f536.26+(KHTML%2c+​like+Gecko)+Version%2f6.0+Mobile%2f10A5355d+Safari%2f8536.25', title, icon)

        
  
