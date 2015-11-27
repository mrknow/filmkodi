# -*- coding: utf-8 -*-

import urllib, urllib2, re, sys, xbmcplugin, xbmcgui
import cookielib, os, string, cookielib, StringIO
import os, time, base64, logging, calendar
import xbmcaddon, string, xbmc


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - iptak"
ptv = xbmcaddon.Addon(scriptID)
plugin_pid = int(sys.argv[1])

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, settings, Parser, libCommon, mrknow_urlparser

log = mrknow_pLog.pLog()

mainUrl = 'http://iptak.pl/'
WszyUrl = 'http://iptak.pl/kategoria/wszystkie/'
#WszyUrl = 'http://iptak.pl/'
sort_asc = '?o=rosnaco&f=tytul'
sort_desc = '?o=malejaco&f=tytul'
playerUrl = 'http://www.youtube.pl/'

HOST = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:19.0) Gecko/20121213 Firefox/19.0'

MENU_TAB = {1: "Nowości",
            2: "Kategorie",
            3: "Szukaj",
            4: "Wszystkie" }


class IPTAK:
    def __init__(self):
        log.info('Starting IPTAK')
        #self.settings = settings.TVSettings()
        #self.parser = Parser.Parser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.cm = libCommon.common()
        self.parser = Parser.Parser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.page = ""


    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('iptak', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self):
        req = urllib2.Request(mainUrl)
        req.add_header('User-Agent', HOST)
        openURL = urllib2.urlopen(req)
        readURL = openURL.read()
        openURL.close()
        #<div id="category" style="border:none !important">
        match = re.compile('<div id="category"(.*?)</ul>', re.DOTALL).findall(readURL)
        match1 = re.compile('<h5>(.*?)</h5>', re.DOTALL).findall(match[0])
        match2 = re.compile('<a(.*?)href="(.*?)">', re.DOTALL).findall(match[0])
       
        if len(match1) > 0:
            log.info('Listuje kategorie: ')
            for i in range(len(match1)):
                self.add('iptak', 'categories-menu', match1[i].strip(), 'None', 'None', match2[i][1], 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        url = mainUrl + '?s=' + urllib.quote_plus(key)
        #print("SearchURL",url)
        return url
        #req = urllib2.Request(url)
        #req.add_header('User-Agent', HOST)
        #openURL = urllib2.urlopen(req)
        #readURL = openURL.read()
       

    def listsItems(self, url,page):
        query_data = { 'url': url+page, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        readURL = self.cm.getURLRequestData(query_data)
        match1 = re.compile('<div id="item" (.*?)><a title="(.*?)" href="(.*?)"><img src="(.*?)" height="193" width="145" alt="(.*?)" /><h6>(.*?)</h6></a>',re.DOTALL).findall(readURL)
        print match1
        if len(match1) > 0:
            for i in range(len(match1)):
                #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                self.add('iptak', 'playSelectedMovie', 'None', self.cm.html_special_chars(match1[i][1]), match1[i][3], match1[i][2], 'aaaa', 'None', False, True)
        match2 = re.compile('<div style="width:640px; font-size: 18px;" id="stronicowanie">(.*?)</div>' ,re.DOTALL).findall(readURL)
        if len(match2)>0:
            match3 = re.compile('<a href="(.*?)">(.*?)</a>',re.UNICODE).findall(match2[0])
            newpage = match3[-1][0].replace('./','')
            if len(match3)>0 and newpage != page:
                log.info('Nastepna strona: '+ match3[-1][0])
                self.add('iptak', 'categories-menu', 'Następna Strona', 'None', 'None', url, 'None', 'None', True, False, newpage)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
       
    def listsItemsW(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        readURL = self.cm.getURLRequestData(query_data)
        match = re.compile('<div id="glownaBox_Polecane">(.*?)<div id="right">',re.DOTALL).findall(readURL)
        #print("Match",match)
        if len(match) > 0:      
                match1 = re.compile('<a title="(.*?)"(.*?)href="(.*?)"(.*?)src="(.*?)"(.*?)<h6>',re.DOTALL).findall(match[0])
                #print("Match1",match1)
                if len(match1) > 0:
                        for i in range(len(match1)):
                                self.add('iptak', 'playSelectedMovie', 'None', self.cm.html_special_chars(match1[i][0]), match1[i][4], match1[i][2], 'aaaa', 'None', False, True)
        match2 = re.compile('class="next page-numbers"(.*?)href="(.*?)"',re.DOTALL).findall(readURL)
        if len(match2) > 0:
                self.add('iptak', 'categories-menu1', 'Nastepna Strona',  'None', 'None', match2[0][1],'aaaa', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItemsN(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        readURL = self.cm.getURLRequestData(query_data)
        match = re.compile('ci</h3>(.*?)<div id="footer">',re.DOTALL).findall(readURL)
        print("Match",match)
        if len(match) > 0:
            match1 = re.compile('<div id="item"><a href="(.*?)" title="(.*?)"><img height="80" width="80" alt="(.*?)" src="(.*?)" /><h6>(.*?)</h6></a></div>',re.DOTALL).findall(match[0])
            print("Match1",match1)
         
            if len(match1) > 0:
                for i in range(len(match1)):
                    okladka = match1[i][3].replace('mala','srednia').replace('../../..','')
                #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                    self.add('iptak', 'playSelectedMovie', 'None', self.cm.html_special_chars(match1[i][1]), mainUrl+okladka, match1[i][0], 'aaaa', 'None', False, True)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))



    def getMovieLinkFromXML(self, url):
        VideoData = {}
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('playMovie\("(.*?)","(.*?)"\)', re.DOTALL).findall(link)
        match1 = re.compile("playMovie\('(.*?)','(.*?)'\)", re.DOTALL).findall(link)
        print("Match",match)
        #VideoData['year'] = str(self.getMovieYear(link))
        # VideoData['year'] = '2090'
        if len(match) > 0:
            if match[0][1] == 'cda':
                linkVideo = 'http://www.cda.pl/video/'+match[0][0]
            elif match[0][1] == 'yt':
                linkVideo = 'http://www.youtube.com/watch?v='+match[0][0]
            else:
                linkVideo = False
        elif len(match1)>0:
            if match1[0][1] == 'cda':
                linkVideo = 'http://www.cda.pl/video/'+match1[0][0]
            elif match1[0][1] == 'yt':
                linkVideo = 'http://www.youtube.com/watch?v='+match1[0][0]
            else:
                linkVideo = False

        else:
            linkVideo = False

        print ("VideoData",linkVideo)
        return linkVideo


    def getMovieYear(self,link):
        match = re.compile('Film z (.*?) roku.', re.DOTALL).findall(link)
        if len(match) > 0:
            return match[0]
        else:
            return False
 

    def searchInputText(self):
        text = None
        k = xbmc.Keyboard()
        k.doModal()
        if (k.isConfirmed()):
            text = k.getText()
        return text
   

    def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True,page = '',year=''):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage)+ "&page=" + urllib.quote_plus(page)+ "&year=" + urllib.quote_plus(year)
        #log.info(str(u))
        if name == 'main-menu' or name == 'categories-menu'or name == 'categories-menu1':
            title = category
        if iconimage == '':
            iconimage = "DefaultVideo.png"
        liz=xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if isPlayable:
            liz.setProperty("IsPlayable", "true")
        liz.setInfo( type="Video", infoLabels={ "Title": title } )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder)
           
    def LOAD_AND_PLAY_VIDEO(self, url, title, icon,year='',plot='', id=''):
        progress = xbmcgui.DialogProgress()
        progress.create('Postęp', '')
        message = "Pracuje...."
        progress.update( 10, "", message, "" )
        xbmc.sleep( 1000 )
        progress.update( 30, "", message, "" )
        progress.update( 50, "", message, "" )
        VideoLink = ''
        subs=''
        VideoLink = self.up.getVideoLink(url)
        if isinstance(VideoLink, basestring):
            videoUrl = VideoLink
        else:
            videoUrl = VideoLink[0]
            subs = VideoLink[1]
        progress.update( 70, "", message, "" )
        if videoUrl == '':
            progress.close()
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu', 'Mo�e to chwilowa awaria.', 'Spr�buj ponownie za jaki� czas')
            return False
        if icon == '' or  icon == 'None':
            icon = "DefaultVideo.png"
        if plot == '' or plot == 'None':
            plot = ''
        liz=xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon, path=videoUrl)
        liz.setInfo( type="video", infoLabels={ "Title": title} )
        xbmcPlayer = xbmc.Player()
        progress.update( 90, "", message, "" )
        progress.close()
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)



    def handleService(self):
        params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        page = self.parser.getParam(params, "page")
        print("Dane", sys.argv[0],sys.argv[1])
        if page ==None:
            page=''
       
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Kategorie':
            log.info('Jest Kategoria: ' + str(url))
            self.listsCategoriesMenu()
        elif name == 'main-menu' and category == 'Nowości':
            log.info('Jest Nowości: ')
            self.listsItemsW(mainUrl)
        elif name == 'main-menu' and category == 'Wszystkie':
            self.listsItemsW(WszyUrl)            
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            #self.listsItems(self.getSearchURL(key),page)
            self.listsItemsW(self.getSearchURL(key))
        elif name == 'categories-menu1' and category != 'None':
            self.listsItemsW(url)
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItemsW(url)
            #self.listsItems(url,page)
        if name == 'playSelectedMovie':
            log.info('playSelectedMovie: ' + str(url))
            data = self.getMovieLinkFromXML(url)
            self.LOAD_AND_PLAY_VIDEO(data, title, icon)
