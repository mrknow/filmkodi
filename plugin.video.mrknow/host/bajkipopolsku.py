# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from BeautifulSoup import BeautifulSoup
import  urllib
import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_Player, mrknow_Pageparser

scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - bajkipopolsku"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

mainUrl = 'http://bajkipopolsku.com'

MENU_TAB = {1: "Ostatnio dodane",
            10: "Spis",
            #4: "Szukaj"
            }


class bajkipopolsku:
    def __init__(self):
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.pp1 = mrknow_Pageparser.mrknow_Pageparser()
        self.player = mrknow_Player.mrknow_Player()
        self.log = mrknow_pLog.pLog()
        self.log.info('Starting bajkipopolsku.pl')

    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('bajkipopolsku', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def getSearchURL(self, key):
        url = urllib.quote_plus(key)
        return url

    def listsCategoriesMenu(self, url):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://bajkipopolsku.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': 'http://bajkipopolsku.com/', 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost1 = soup.find('div', {"id": "sidebar"})
        linki_all1 = linki_ost1.findAll('li')
        for mylink in linki_all1:
            self.log("m %s | %s " %(mylink.a.text,mylink.a['href']))
            self.add('bajkipopolsku', 'categories-menu', self.cm.html_special_chars(mylink.a.text.encode('utf-8')),'None', 'None', mylink.a['href'], 'aaaa', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems(self,url):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://bajkipopolsku.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': url, 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost = soup.find('div', {"class": "post_ajax_tm"})
        if linki_ost:
            linki_all = linki_ost.findAll('div', {"class": "item-thumbnail"})
            for mylink in linki_all:
                self.add('bajkipopolsku', 'playSelectedMovie', 'None', self.cm.html_special_chars(mylink.img['alt'].encode('utf-8')), mylink.img['src'], mylink.a['href'], 'aaaa', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems2(self, url):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://bajkipopolsku.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': 'http://bajkipopolsku.com/', 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost = soup.find('div', {"class": "carousel-content"})
        if linki_ost:
            linki_all = linki_ost.findAll('div', {"class": "item-thumbnail"})
            for mylink in linki_all:
                self.add('bajkipopolsku', 'playSelectedMovie', 'None', self.cm.html_special_chars(mylink.text.encode('utf-8')), mylink.img['src'], mylink.a['href'], 'aaaa', 'None', False, True)
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
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Ostatnio dodane':
            self.listsItems2(mainUrl)
        elif name == 'main-menu' and category == "Spis":
            self.listsCategoriesMenu(mainUrl)

        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems2('http://bajkipopolsku.tv/szukaj', self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            self.listsItems(url)
        if name == 'playSelectedMovie':
            self.log.info('url: ' + str(url))
            mojeurl = self.pp1.getVideoLink(url)
            self.player.LOAD_AND_PLAY_VIDEO(mojeurl,'','')

        
  
