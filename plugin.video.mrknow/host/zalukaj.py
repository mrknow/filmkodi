# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import  urllib
import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_Player, mrknow_urlparser


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - zalukaj"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )


log = mrknow_pLog.pLog()

mainUrl = 'http://zalukaj.tv'
UrlLastAdded = 'http://zalukaj.tv/cache/lastadded.html'
UrlLastSeen = 'http://zalukaj.tv/cache/lastseen.html'
UrlPopular = 'http://zalukaj.tv/cache/wyswietlenia-miesiac.html'

MENU_TAB = {1: "Ostatnio dodane",
            2: "Ostatnio oglądane",
            3: "Popularne ostatnie 30 dni",
            10: "Kategorie",
            4: "Szukaj" }


class zalukaj:
    def __init__(self):
        log.info('Starting zalukaj.pl')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.player = mrknow_Player.mrknow_Player()




    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('zalukaj', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self):
        query_data = { 'url': mainUrl, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<td class="wef32f"><a href="([^"]+)">(.*?)</a></td>', re.DOTALL).findall(link)
        if len(match) > 0:
            log.info('Listuje kategorie: ')
            for i in range(len(match)):
                #http://zalukaj.tv/gatunek,22/ostatnio-dodane,wszystkie,strona-2
                #mygat = match[i][0].split('/'))
                myurl = 'http://zalukaj.tv/gatunek,'+ match[i][0].split('/')[-1] + '/ostatnio-dodane,wszystkie'
                print("my",myurl)
                #add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True, strona = ''):
                self.add('zalukaj', 'categories-menu', match[i][1], 'None','None', myurl, 'None', 'None', True, False, '1')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        url = urllib.quote_plus(key)
        return url

    def listsItems(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        #log.info('my link || %s' % link)
        match = re.compile('<div style="float:left;"><img style="cursor:pointer;width:120px;height:160px;" src="(.*?)"/></div>(.*?)<div class="rmk23m4">(.*?)<h3><a href="(.*?)" title="(.*?)">(.*?)</a></h3>', re.DOTALL).findall(link)
        log.info('my link 2 || %s' % match)

        if len(match) > 0:
            for i in range(len(match)):
                log.info('my link 2 || %s' % match[i][3])

                self.add('zalukaj', 'playSelectedMovie', 'None', self.cm.html_special_chars(match[i][5]), match[i][0], match[i][3], 'aaaa', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsItems2(self, url, key):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
        postdata = {"searchinput" : key}
        link = self.cm.getURLRequestData(query_data, postdata)
        log(key)
        match = re.compile('<h3><a href="(.*?)" title="(.*?)"><b style="color\:white;">(.*?)</b>(.*?)</a></h3>', re.DOTALL).findall(link)
        log(match)

        if len(match) > 0:
            for i in range(len(match)):
                print("match",match[i])
                tytul = match[i][2] + match[i][4]
                self.add('zalukaj', 'playSelectedMovie', 'None', tytul, match[i][0], match[i][1], 'aaaa', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems3(self, url, strona):
        myurl = url + ',strona-' + strona
        print(myurl)
        query_data = { 'url': myurl, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        #print("link",link)
        match = re.compile('<div class="im23jf" style="background-image:url\((.*?)\);"><p><span>(.*?)</span></p></div>\n\n\t\t\t\t\t\t\t\t\t\t\t\t<div class="rmk23m4">\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t<h3><a href="(.*?)" title="(.*?)">(.*?)</a></h3>', re.DOTALL).findall(link)
        if len(match) > 0:
            for i in range(len(match)):
                print("match",match[i])
                tytul = match[i][4]
                self.add('zalukaj', 'playSelectedMovie', 'None', tytul, match[i][0], match[i][2], 'aaaa', 'None', False, True)

        strona2 = str(int(strona)+1)
        log.info('Nastepna strona: '+  strona2)
        self.add('zalukaj', 'categories-menu', 'Następna', 'None', 'None', url, 'None', 'None', True, False, strona2)
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
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Kategorie':
            log.info('Jest Najnowsze: ')
            self.listsCategoriesMenu()
        elif name == 'main-menu' and category == 'Ostatnio dodane':
            self.listsItems(UrlLastAdded)
        elif name == 'main-menu' and category == "Ostatnio oglądane":
            self.listsItems(UrlLastSeen)
        elif name == 'main-menu' and category == "Popularne ostatnie 30 dni":
            self.listsItems(UrlPopular)


        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems2('http://zalukaj.tv/szukaj', self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems3(url, strona)
        if name == 'playSelectedMovie':
            log.info('url: ' + str(url))
            self.player.LOAD_AND_PLAY_VIDEO(url, title,'')

        
  
