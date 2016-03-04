# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
import urllib
import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_Player, mrknow_urlparser


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - filmydokumentalne"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )


log = mrknow_pLog.pLog()

mainUrl = 'http://www.filmydokumentalne.eu/'
popularneUrl = 'http://www.filmydokumentalne.eu/polecane/'
newUrl = 'http://www.filmydokumentalne.eu/najnowsze-filmy/'

MENU_TAB = {1: "Najnowsze",
            2: "Polecane",
            3: "Kategorie",
            4: "Szukaj" }


class filmydokumentalne:
    def __init__(self):
        log.info('Starting filmydokumentalne.pl')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.player = mrknow_Player.mrknow_Player()




    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('filmydokumentalne', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<li class="cat-item (.*?)"><a href="(.*?)" >(.*?)</a>', re.DOTALL).findall(link)
        if len(match) > 0:
            log.info('Listuje kategorie: ')
            match2 = sorted(match, key=lambda x: x[2])
            print ("match2", match2)
            for i in range(len(match2)):
                #add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True, strona = ''):
                self.add('filmydokumentalne', 'categories-menu', match2[i][2], 'None','None', match2[i][1], 'None', 'None', True, False, '1')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        url = mainUrl + '?s=' + urllib.quote_plus(key)
        return url

    def listsItems(self, url, strona='1'):
        mylink = url + 'page/' + strona
        print("myli",mylink)
        query_data = { 'url': mylink, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        print("1")
        match = re.compile('<h1><a href="(.*?)" title="czytaj wiecej">(.*?)</a></h1>', re.DOTALL).findall(link)
        print("2")

        if len(match) > 0:
            for i in range(len(match)):
                self.add('filmydokumentalne', 'playSelectedMovie', 'None', self.cm.html_special_chars(match[i][1]), 'None', match[i][0], 'aaaa', 'None', False, True)
        strona2 = str(int(strona)+1)
        if "Ostatnia" in link:
            log.info('Nastepna strona: '+  strona2)
            self.add('filmydokumentalne', 'categories-menu', 'Następna', 'None', 'None', url, 'None', 'None', True, False, strona2)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsItems2(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<h1><a href="(.*?)" title="czytaj wiecej">(.*?)</a></h1>', re.DOTALL).findall(link)
        if len(match) > 0:
            for i in range(len(match)):
                self.add('filmydokumentalne', 'playSelectedMovie', 'None', self.cm.html_special_chars(match[i][1]), 'None', match[i][0], 'aaaa', 'None', False, True)
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
            self.listsCategoriesMenu(mainUrl)
        elif name == 'main-menu' and category == 'Najnowsze':
            log.info('Jest Najnowsze: ')
            self.listsItems(newUrl, strona)
        elif name == 'main-menu' and category == "Polecane":
            self.listsItems2(popularneUrl)
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems2(self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems(url, strona)
        if name == 'playSelectedMovie':
            log.info('url: ' + str(url))
            self.player.LOAD_AND_PLAY_VIDEO(url, title,'')

        
  
