# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import json


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - kinolive"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, settings, Parser,libCommon, Player, mrknow_urlparser

log = mrknow_pLog.pLog()

#mainUrl = 'http://kinolive.pl/'
mainUrl = 'http://alekino.tv'
catUrl = 'http://alekino.tv/filmy/'

HOST = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/30.0'

MENU_TAB = {0: "Filmy",
            1: "Filmy z lektorem",
            2: "Filmy z napisami",
            3: "Filmy z dubbingiem",
            4: "Filmy polskie",
            5: "Filmy HD",
            12: "Kategorie",
            15: "Szukaj"
            }



class kinolive:
    def __init__(self):
        log.info('Starting kinolive.pl')
        self.settings = settings.TVSettings()
        self.parser = Parser.Parser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.cm = libCommon.common()
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "kinoliveserial.cookie"
        query_data = {'url': 'http://alekino.tv/auth/login', 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True}
        data = self.cm.getURLRequestData(query_data)
        self.p = Player.Player()

    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('kinolive', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self):
        query_data = { 'url': catUrl, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<ul class="select-movie-type movie-kat-selection">(.*?)</ul>', re.DOTALL).findall(link)
        #print match
        match1 = re.compile('<li class="filterParent"><a href="#" data-type="filter" data-value="(.*?)" data-filter="genres\[\]">(.*?)</a> <span class="w">(.*?)</span></li>', re.DOTALL).findall(match[0])
        #print match1
        if len(match1) > 0:
            log.info('Listuje kategorie: ')
            for i in range(len(match1)):
                url = mainUrl + match1[i][0].replace('.html','')
                self.add('kinolive', 'categories-menu', match1[i][1].strip() + ' ' + match1[i][2].strip(), 'None', 'None', catUrl, 'None', 'None', True, False,'1','genres[0]='+match1[i][0])
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        if key != None:
            url = mainUrl + '/szukaj?query='+ urllib.quote_plus(key)+'&x=0&y=0#movies'  
            return url
        else:
            return False
        
    def listsItemsOther(self, url):
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
            link = self.cm.getURLRequestData(query_data)
            match = re.compile('<!-- Znalezione filmy -->(.*?)<!-- Znalezione seriale -->', re.DOTALL).findall(link)
            match1 = re.compile('<div class="result box pl-round" style="margin-bottom:10px;">\n(.*?)<a href="(.*?)"><img src="(.*?)" alt="" title="" height="133" width="100"></a>\n(.*?)<a href="(.*?)"(.*?)>(.*?)</a>', re.DOTALL).findall(match[0])
            print ("match",match1)
            if len(match1) > 0:
                for i in range(len(match1)):
                        #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                        self.add('kinolive', 'playSelectedMovie', 'None', match1[i][6],  match1[i][2], mainUrl+ match1[i][1], 'aaaa', 'None', False, False)

            xbmcplugin.endOfDirectory(int(sys.argv[1]))
    def listsItemsTop(self, url):
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
            link = self.cm.getURLRequestData(query_data)
            match = re.compile('<table>(.*?)</table>', re.DOTALL).findall(link)
            if len(match) > 0:
                for i in range(len(match)):
                        match1 = re.compile('<a href="(.*?)"><img src="(.*?)" width="107" height="142" title="(.*?)" alt="(.*?)" /></a>', re.DOTALL).findall(match[i])
                        #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                        self.add('kinolive', 'playSelectedMovie', 'None', match1[0][2],  match1[0][1], mainUrl+ match1[0][0], 'aaaa', 'None', False, False)

            xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
    def listsItems(self, url, strona='0', filtrowanie=''):
        if filtrowanie == None:
            filtrowanie = ''
        urllink = url + '?' + filtrowanie +'&p='+ str(strona)
        query_data = { 'url': urllink, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        #print ("L",link)
        #match = re.compile('<div class="film-main round">(.*?)<div class="tac">', re.DOTALL).findall(link)
        match = re.compile('<div class="row-fluid span12 movie-item">(.*?)<div class="clearfix">', re.DOTALL).findall(link)
        #print ("Match",match)
        
        if len(match) > 0:
            for i in range(len(match)):
                okladka = ''
                match1 = re.compile('<a class="title" href="(.*?)">(.*?)</a>', re.DOTALL).findall(match[i])
                tytul = match1[0][1].replace('<small>','').replace('</small>','')
                match2 = re.compile('<div class="pull-left thumb" style="background-image:url\((.*?)\);">', re.DOTALL).findall(match[i])
                #print match2
                if len(match2) > 0:
                    okladka = match2[0]
                self.add('kinolive', 'playSelectedMovie', 'None', tytul,  okladka, mainUrl+ match1[0][0], 'aaaa', 'None', False, False)
        log.info('Nastepna strona: '+  urllink)
        self.add('kinolive', 'categories-menu', 'Następna', 'None', 'None', url, 'None', 'None', True, False,str(int(strona) + 1), str(filtrowanie))
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
                self.add('kinolive', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
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
                self.add('kinolive', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1])) 


    def getMovieLinkFromXML(self, url):
        VideoData = {}
        query_data = { 'url': url, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        VideoData['year'] = str(self.getMovieYear(link))
        match1 = re.compile('<a href="#" data-type="player" data-version="standard" data-id="(.*?)">', re.DOTALL).findall(link)
        url1 = "http://alekino.tv/players/init/" + match1[0] + "?mobile=false"
        query_data = { 'url': url1, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match15 = re.compile('"data":"(.*?)"', re.DOTALL).findall(link)
        hash = match15[0].replace('\\','')
        post_data = {'hash': hash}
        query_data = {'url': 'http://alekino.tv/players/get', 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True}
        data = self.cm.getURLRequestData(query_data, post_data)
        match16 = re.compile('<iframe src="(.*?)" (.*?)', re.DOTALL).findall(data)
        #<iframe src="http://www.putlocker.com/embed/57870E83A986112B" width="989" height="535" frameborder="0" scrolling="no"></iframe>
        #print ("match16",match16,data)
        linkVideo = ''
        if len(match16) > 0:
            page = urllib.urlopen(match16[0][0].decode('utf8'))
            #print page.geturl()   # This will show the redirected-to URL
            #print ("match16_link",page.geturl())

            linkVideo = self.up.getVideoLink(page.geturl())
            if len(linkVideo) > 0:
                VideoData['link'] = linkVideo + '|Referer=http://alekino.tv/assets/alekino.tv/swf/player.swf'
            else:
                VideoData['link'] = ''
                
        return VideoData
        
    def getMovieYear(self,link):
        match = re.compile('<h1 class="movie-title">(.*?)\((.*?)\)(.*?)</h1>', re.DOTALL).findall(link)
        if len(match) > 0:
            return match[0][1]
        else:
            return False

    def getSizeAllItems(self, url):
        numItems = 0
        req = urllib2.Request(url)
        req.add_header('User-Agent', HOST)
        openURL = urllib2.urlopen(req)
        readURL = openURL.read()
        openURL.close()
        match = re.compile('<span class="nav_ext">...</span> <a href="http://kinolive.pl/filmy/page/(.*?)/">(.*?)</a></div>(.*?)</li>', re.DOTALL).findall(readURL)
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
    

    def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True, strona = '', filtrowanie=''):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage)+ "&strona=" + urllib.quote_plus(strona)+ "&filtrowanie=" + urllib.quote_plus(filtrowanie)
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
        liz.setInfo( type = "Video", infoLabels={ "Title": title, } )
        try:
            xbmcPlayer = xbmc.Player()
            xbmcPlayer.play(videoUrl+'|Referer=http://alekino.tv/assets/alekino.tv/swf/player.swf', liz)
            
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
        strona = self.parser.getParam(params, "strona")
        filtrowanie = self.parser.getParam(params, "filtrowanie")
        print ("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZD",category,url,strona,filtrowanie,name)
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Filmy z lektorem':
            log.info('Jest Filmy z lektorem: ')
            self.listsItems(catUrl,1,'types[0]=1')
        elif name == 'main-menu' and category == 'Filmy z napisami':
            log.info('Jest Wszystkie: ')
            self.listsItems(catUrl,1,'types[0]=3')
        elif name == 'main-menu' and category == 'Filmy z dubbingiem':
            log.info('Jest Wszystkie: ')
            self.listsItems(catUrl,1,'types[0]=2')
        elif name == 'main-menu' and category == 'Filmy polskie':
            log.info('Jest Wszystkie: ')
            self.listsItems(catUrl,1,'types[0]=4')
        elif name == 'main-menu' and category == 'Filmy HD':
            log.info('Jest Wszystkie: ')
            self.listsItems('http://alekino.tv/filmy/hd',1,'')
        elif name == 'main-menu' and category == 'Filmy':
            log.info('Jest F: ')
            self.listsItems(catUrl,1,'')
        elif name == 'main-menu' and category == 'Kategorie':
            log.info('Jest Gorące: ')
            self.listsCategoriesMenu()

        elif name == 'main-menu' and category == 'Top 100 - najczęściej oglądane':
            log.info('Jest Gorące: ')
            self.listsItemsTop('http://kinolive.pl/top100?o=mv')
        elif name == 'main-menu' and category == 'Top 100 - ulubione':
            log.info('Jest Gorące: ')
            self.listsItemsTop('http://kinolive.pl/top100?o=tf')
        elif name == 'main-menu' and category == 'Top 100 - najwyżej ocenione':
            log.info('Jest Gorące: ')
            self.listsItemsTop('http://kinolive.pl/top100?o=tr')

            
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            if key != None:
                self.listsItemsOther(self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems(url,strona,filtrowanie)
        if name == 'playSelectedMovie':
            data = self.getMovieLinkFromXML(url)
            self.p.LOAD_AND_PLAY_VIDEO(data['link'], title, icon, data['year'])
        if name == 'playselectedmovie':
            #print "GGGGGGGGGGGGGGGGGGGGGGGGGGGRRRRRRRRRRRRAAAAAAAAAA"
            data = self.getMovieLinkFromXML(url)
            self.p.LOAD_AND_PLAY_VIDEO(data['link'], title, icon, data['year'])

        
  
