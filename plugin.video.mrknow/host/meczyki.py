# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import mrknow_Pageparser
import string


scriptID = 'plugin.video.mrknow'
scriptname = "Wtyczka XBMC www.mrknow.pl - meczyki"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, settings, mrknow_Parser,mrknow_pCommon

log = mrknow_pLog.pLog()

mainUrl = 'http://www.meczyki.pl'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {1: "Dzisiaj",
            2: "Jutro",
            3: "Pojutrze",
            12: "Filmiki" }


class MECZYKI:
    def __init__(self):
        log.info('Starting meczyki.pl')
        self.settings = settings.TVSettings()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.up = mrknow_Pageparser.mrknow_Pageparser()
        self.cm = mrknow_pCommon.common()
        

    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('meczyki', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        readURL = self.cm.getURLRequestData(query_data)
        match = re.compile('<div id="left" class="homepage homepage-index">(.*?)<div id="right">', re.DOTALL).findall(readURL)
        for i in range(len(match)):
            match1 = re.compile('<div class="transmission(.*?)" id="(.*?)">\n    <div class="head">\n        <div class="head2">\n            <div class="icon">\n                <a class="(.*?)" href="(.*?)" title="(.*?)"></a>\n                <div class="time" style="float: left;">\n                    <span>(.*?)</span>\n                </div>\n            </div>\n            <div class="name">(.*?)<a href="(.*?)">\n(.*?)</a>\n                                                    <div class="transdets">\n                    <span class="league">(.*?)</span>\n                </div>\n            </div>\n            <div class="right">\n                                    <div class="buttons">\n', re.DOTALL).findall(match[i])
            print match1
            if len(match1) > 0:
                for j in range(len(match1)):
                    tytul = match1[j][5] +' - '
                    match2 = re.compile('(.*?)<img(.*?) alt="(.*?)" />(.*?)<img(.*?) alt="(.*?)" />', re.DOTALL).findall(match1[j][8])
                    if len(match2) > 0:
                        print ("m",match2)
                        tytul = tytul + match2[0][2] + ' - ' + match2[0][5]
                    else:
                        tytul = tytul + match1[j][8].replace("  ", "")
                    tytul = tytul + '   ' + match1[j][9] + ' - ' + match1[j][4]
                    tytul = tytul.strip()
                    self.add('meczyki', 'categories-menu', tytul, 'None', 'None', mainUrl+ match1[j][7], 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        url = mainUrl + 'search.php?phrase=' + urllib.quote_plus(key) 
        return url

    def listsItems(self, url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', HOST)
        openURL = urllib2.urlopen(req)
        readURL = openURL.read()
        openURL.close()
        match = re.compile('<div class="channels_list active_transmission" id="(.*?)" style="display: block;">(.*?)<div class="tablebottom">', re.DOTALL).findall(readURL)
        valTab = []
        strTab = []
        if len(match) > 0:
            match1 = re.compile('<tr>(.*?)</tr>', re.DOTALL).findall(match[0][1])
            if len(match1) > 0:
                for i in range(len(match1)):
                    match2 = re.compile('<a class="(.*?)" target="_blank" rel="nofollow"\n                           onclick="(.*?)"                            href="(.*?)" data="(.*?)" channel="(.*?)">\n                                                               OGL\xc4\x84DAJ\n                                                    </a>\n                    </td>\n', re.DOTALL).findall(match1[i])
                    if len(match2) > 0:
                        match3 = re.compile('<td class="flag"><img src="(.*?)" /></td>', re.DOTALL).findall(match1[i])
                        match4 = re.compile('<span class="channel_name">(.*?)</span>\n                </td>\n                <td class="desc">(.*?)</td>', re.DOTALL).findall(match1[i])
                        tytul = match4[0][0].replace(" ","").replace('&nbsp;','').replace('\n','') + "-" + match4[0][1].replace(" ","").replace('&nbsp;','').replace('\n','')
                        strTab.append(tytul)
                        strTab.append(mainUrl+match3[0][0])
                        strTab.append(match2[0][2].replace(" ","").replace('&nbsp;','').replace('\n',''))
                        valTab.append(strTab)
                        strTab = []
        valTab.sort(key = lambda x: x[0], reverse=True)
        for i in valTab:
            self.add('meczyki', 'playSelectedMovie', 'None', i[0], i[1], i[2], 'None', 'None', True, False)
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
                self.add('meczyki', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
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
                self.add('meczyki', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1])) 

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
        print("Serwis",name,title,url)
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Dzisiaj':
            log.info('Jest Dzisiaj: ')
            self.listsCategoriesMenu('http://www.meczyki.pl/')
        elif name == 'main-menu' and category == 'Jutro':
            log.info('Jest Dzisiaj: ')
            self.listsCategoriesMenu('http://www.meczyki.pl/jutro,1,dzien.html')
        elif name == 'main-menu' and category == 'Pojutrze':
            log.info('Jest Dzisiaj: ')
            self.listsCategoriesMenu('http://www.meczyki.pl/pojutrze,2,dzien.html')
            
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems(self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems(url)
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.up.getVideoLink(url), title, icon)

        
  
