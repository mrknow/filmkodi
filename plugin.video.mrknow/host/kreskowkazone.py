# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from BeautifulSoup import BeautifulSoup
import  urllib
import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_Player, mrknow_Pageparser, mrknow_urlparser

scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - kreskowkazone"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

mainUrl = 'http://www.kreskowkazone.pl/'
lastUrl = 'http://www.kreskowkazone.pl/wychodzace'
listUrl = 'http://www.kreskowkazone.pl/lista_anime-0'

MENU_TAB = {1: "Ostatnio dodane",
            10: "Spis",
            #4: "Szukaj"
            }


class kreskowkazone:
    def __init__(self):
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.pp1 = mrknow_Pageparser.mrknow_Pageparser()
        self.player = mrknow_Player.mrknow_Player()
        self.log = mrknow_pLog.pLog()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.log.info('Starting kreskowkazone.pl')
        self.COOKIEFILE = self.up.cookieFileName('kreskowkazone.cookie')

    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('kreskowkazone', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def getSearchURL(self, key):
        url = urllib.quote_plus(key)
        return url

    def listsCategoriesMenu(self, url):
        #HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://kreskowkazone.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': url, 'use_host': False, 'use_header': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        result = self.cm.parseDOM(link, 'li', {'class': 'litery'})
        self.log.info('Result %s' % result)
        for mylink in result:
            url = mainUrl + self.cm.parseDOM(mylink, 'a', ret='href')[0]
            title = self.cm.parseDOM(mylink, 'a')[0]
            self.log.info("Result %s %s" % (url,title))
            self.add('kreskowkazone', 'categories-menu', title,'None', 'None', url, 'aaaa', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems(self,url):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://kreskowkazone.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': url, 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost = soup.find('div', {"class": "post_ajax_tm"})
        if linki_ost:
            linki_all = linki_ost.findAll('div', {"class": "item-thumbnail"})
            for mylink in linki_all:
                self.add('kreskowkazone', 'playSelectedMovie', 'None', self.cm.html_special_chars(mylink.img['title'].encode('utf-8')), mylink.img['src'], mylink.a['href'], 'aaaa', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems2(self, url):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://kreskowkazone.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': url, 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        result = self.cm.parseDOM(link, 'div', {'class': 'box-img'})
        for i in result:
            url = mainUrl + self.cm.parseDOM(i, 'a', ret='href')[0]
            img = mainUrl + self.cm.parseDOM(i, 'img', ret='src')[0]
            title = self.cm.parseDOM(i, 'a', ret='title')[0]
            #self.log.info('bbb %s' % title)
            self.add('kreskowkazone', 'sezon-menu', 'None', title, img, url, 'aaaa', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems10(self, url):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://kreskowkazone.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': url, 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER,
                       'use_cookie': True, 'cookiefile': self.COOKIEFILE, 'load_cookie': False,
                       'save_cookie': True, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        result = self.cm.parseDOM(link, 'tr', {'class': 'wiersz'})
        for i in result:
            #self.log.info('bbb url:%s  ' % (i))
            result2 = self.cm.parseDOM(i, 'td', {'class': 'border-c2'})
            #for j in result2:
            #    self.log.info('cc url:%s  ' % (j))
            try:
                url = mainUrl + self.cm.parseDOM(result2[3], 'a', ret='href')[0]
                #result2[4].replace('<span class="sprites ','').replace(' center"></span>','')
                title = '[%s] %s - %s' % (result2[0],result2[1],result2[2].replace('<span class="sprites ','').replace(' center"></span>','').upper())
                self.add('kreskowkazone', 'playSelectedMovie', 'None', title, 'None', url, 'aaaa', 'None', False, True)
            except: pass
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
        elif name == 'main-menu' and category == 'Ostatnio dodane':
            self.listsItems2(lastUrl)
        elif name== 'sezon-menu':
            self.listsItems10(url)
        elif name == 'main-menu' and category == "Spis":
            self.listsCategoriesMenu(listUrl)

        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems2('http://kreskowkazone.tv/szukaj', self.getSearchURL(key))
        elif name == 'categories-menu':
            #self.listsItems(url)
            self.listsItems2(url)
        if name == 'playSelectedMovie':
            self.log.info('url: ' + str(url))
            #mojeurl = self.pp1.getVideoLink(url)
            self.player.LOAD_AND_PLAY_VIDEO(url,'','')

        
  
