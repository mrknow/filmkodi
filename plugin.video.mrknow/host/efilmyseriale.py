# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import mrknow_urlparser, urllib
import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_Player


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - efilmyseriale"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )


log = mrknow_pLog.pLog()

mainUrl = 'http://www.efilmy.tv/'
UrlLastAdded = 'http://www.efilmy.tv/seriale.html'
UrlLastSeen = 'http://efilmyseriale.tv/cache/lastseen.html'
UrlPopular = 'http://efilmyseriale.tv/cache/wyswietlenia-miesiac.html'

MENU_TAB = {1: "Ostatnio dodane",
            2: "Wszystkie",
            #3: "Popularne ostatnie 30 dni",
            #10: "Kategorie",
            4: "Szukaj" }


class efilmyseriale:
    def __init__(self):
        log.info('Starting efilmyseriale.pl')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.player = mrknow_Player.mrknow_Player()




    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('efilmyseriale', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self):
        query_data = { 'url': mainUrl, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<td class="wef32f"><a href="([^"]+)">(.*?)</a></td>', re.DOTALL).findall(link)
        if len(match) > 0:
            log.info('Listuje kategorie: ')
            for i in range(len(match)):
                #http://efilmyseriale.tv/gatunek,22/ostatnio-dodane,wszystkie,strona-2
                #mygat = match[i][0].split('/'))
                myurl = 'http://efilmyseriale.tv/gatunek,'+ match[i][0].split('/')[-1] + '/ostatnio-dodane,wszystkie'
                print("my",myurl)
                #add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True, strona = ''):
                self.add('efilmyseriale', 'categories-menu', match[i][1], 'None','None', myurl, 'None', 'None', True, False, '1')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        url = urllib.quote_plus(key)
        return url

    def listsItems(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<a title="(.*?)" href="(.*?)"><img alt="(.*?)" class="sposter" src="(.*?)"/>(.*?)<span>(.*?)<img ', re.DOTALL).findall(link)
        if len(match) > 0:
            for i in range(1, len(match)):
                print("Match",match[i])
                self.add('efilmyseriale', 'playSelectedMovie', 'None', match[i][0].replace('Serial','') + '-' +match[i][5], mainUrl+ match[i][3], mainUrl+match[i][1], 'aaaa', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems4(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<li><a title="Serial  (.*?)" href="(.*?)">(.*?)<span class="bold">(.*?)</span> <!--<img src="theme/filmz/gfx/pl.png" />--></a></li>', re.DOTALL).findall(link)
        print("Match",match)
        if len(match) > 0:
            for i in range(1, len(match)):
                print("Match",match[i])
                self.add('efilmyseriale', 'playSelectedMovie', 'None', match[i][2].replace('Serial','') + '-'+match[i][3], 'None', mainUrl + match[i][1], 'aaaa', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsItems2(self, url, key):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
        postdata = {'searchinput' : key}
        link = self.cm.getURLRequestData(query_data, postdata)
        match = re.compile('<div class="tivief4">\n<div style="float:left;"><img style="width:120px;height:160px;" src="(.*?)"/></div>\n<div class="rmk23m4">\n<h3><a href="(.*?)" title="(.*?)">(.*?)</a></h3>\n<div style="min-height:110px;font-size:10px;">(.*?)<a href="(.*?)">(.*?)</a>', re.DOTALL).findall(link)
        if len(match) > 0:
            for i in range(len(match)):
                print("match",match[i])
                tytul = match[i][3].replace('<b style="color:white;">','').replace('</b>','')
                self.add('efilmyseriale', 'playSelectedMovie', 'None', match[i][2] + ' - ' + match[i][3], 'None', mainUrl + match[i][1] , 'aaaa', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems3(self, url):
        myurl='http://www.efilmy.tv/js/menu.js'
        query_data = { 'url': myurl, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        print("link",link)
        match = eval(re.compile('var serials_pl =(.*?);', re.DOTALL).findall(link)[0])
        match1 = eval(re.compile('var serials_seo =(.*?);', re.DOTALL).findall(link)[0])
        valTab = []
        strTab = []
        for e in range(len(match)):
            strTab.append(match[e])
            strTab.append(match1[e])
            valTab.append(strTab)
            strTab = []
        valTab.sort(key = lambda x: x[0])
        for i in valTab:
            self.add('efilmyseriale', 'sesons-menu', 'None', i[0], 'None', mainUrl + 'serial,'+ i[1] + '.html', 'aaaa', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def searchInputText(self):
        text = None
        k = xbmc.Keyboard()
        k.doModal()
        if (k.isConfirmed()):
            text = k.getText()
        return text
    

    def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True, strona = ''):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage) + "&strona=" + urllib.quote_plus(strona)
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
            


    def handleService(self):
    	params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        strona = self.parser.getParam(params, "strona")
        if strona == None:
            strona = '1'
        print("Strona", strona)
        print("name", name)
        print("category", category)
        print("url", url)
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Kategorie':
            log.info('Jest Najnowsze: ')
            self.listsCategoriesMenu()
        elif name == 'main-menu' and category == 'Ostatnio dodane':
            self.listsItems(UrlLastAdded)
        elif name == 'main-menu' and category == "Wszystkie":
            self.listsItems3(mainUrl)
        elif name == 'main-menu' and category == "Popularne ostatnie 30 dni":
            self.listsItems(UrlPopular)
        elif name == 'sesons-menu':
            self.listsItems4(url)


        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems2('http://efilmyseriale.tv/szukaj', self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems3(url, strona)
        if name == 'playSelectedMovie':
            log.info('url: ' + str(url))
            self.player.LOAD_AND_PLAY_VIDEO(url, title,'')

        
  
