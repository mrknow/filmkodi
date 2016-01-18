# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import pageparser
import string


scriptID = 'plugin.video.mrknow'
scriptname = "Wtyczka XBMC www.mrknow.pl - drhtvcompl"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, settings, mrknow_Parser, BeautifulSoup

log = mrknow_pLog.pLog()

mainUrl = 'http://www.drhtv.com.pl/'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {1: "Kanały",
            6: "Poniedziałek",
            7: "Wtorek",
            8: "Środa",
            9: "Czwartek",
            10: "Piątek",
            11: "Sobota",
            12: "Niedziela" }


class drhtvcompl:
    def __init__(self):
        log.info('Starting drhtvcompl.pl')
        self.settings = settings.TVSettings()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.up = pageparser.pageparser()

    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('drhtvcompl', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self,url):
        self.add('drhtvcompl', 'playSelectedMovie', 'None','DrHTV-1' , 'None', 'http://www.drhtv.com.pl/drhtv1.html', 'aaaa', 'None', True, False)
        self.add('drhtvcompl', 'playSelectedMovie', 'None','DrHTV-2' , 'None', 'http://www.drhtv.com.pl/drhtv2.html', 'aaaa', 'None', True, False)
        self.add('drhtvcompl', 'playSelectedMovie', 'None','DrHTV-3' , 'None', 'http://www.drhtv.com.pl/drhtv3.html', 'aaaa', 'None', True, False)
        self.add('drhtvcompl', 'playSelectedMovie', 'None','DrHTV-4' , 'None', 'http://www.drhtv.com.pl/drhtv4.html', 'aaaa', 'None', True, False)
        self.add('drhtvcompl', 'playSelectedMovie', 'None','DrHTV-5' , 'None', 'http://www.drhtv.com.pl/drhtv5.html', 'aaaa', 'None', True, False)
        self.add('drhtvcompl', 'playSelectedMovie', 'None','DrHTV-6' , 'None', 'http://www.drhtv.com.pl/drhtv6.html', 'aaaa', 'None', True, False)
        self.add('drhtvcompl', 'playSelectedMovie', 'None','DrHTV-7' , 'None', 'http://www.drhtv.com.pl/drhtv7.html', 'aaaa', 'None', True, False)
        self.add('drhtvcompl', 'playSelectedMovie', 'None','DrHTV-8' , 'None', 'http://www.drhtv.com.pl/drhtv8.html', 'aaaa', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        url = mainUrl + 'search.php?phrase=' + urllib.quote_plus(key) 
        return url
        #req = urllib2.Request(url)
        #req.add_header('User-Agent', HOST)
        #openURL = urllib2.urlopen(req)
        #readURL = openURL.read()
        

    def listsItems(self, url,day):
        req = urllib2.Request(url)
        req.add_header('User-Agent', HOST)
        openURL = urllib2.urlopen(req)
        readURL = openURL.read()
        openURL.close()
        if day == 'Poniedziałek':
            match = re.compile('<div class="mecze" id="d1_t" style="(.*?)">(.*?)<div class="mecze" id="d2_t" style="(.*?)">', re.DOTALL).findall(readURL)
        elif day == 'Wtorek':
            match = re.compile('<div class="mecze" id="d2_t" style="(.*?)">(.*?)<div class="mecze" id="d3_t" style="(.*?)">', re.DOTALL).findall(readURL)
        elif day == 'Środa':
            match = re.compile('<div class="mecze" id="d3_t" style="(.*?)">(.*?)<div class="mecze" id="d4_t" style="(.*?)">', re.DOTALL).findall(readURL)
        elif day == 'Czwartek':
            match = re.compile('<div class="mecze" id="d4_t" style="(.*?)">(.*?)<div class="mecze" id="d5_t" style="(.*?)">', re.DOTALL).findall(readURL)
        elif day == 'Piątek':
            match = re.compile('<div class="mecze" id="d5_t" style="(.*?)">(.*?)<div class="mecze" id="d6_t" style="(.*?)">', re.DOTALL).findall(readURL)
        elif day == 'Sobota':
            match = re.compile('<div class="mecze" id="d6_t" style="(.*?)">(.*?)<div class="mecze" id="d7_t" style="(.*?)">', re.DOTALL).findall(readURL)
        elif day == 'Niedziela':
            match = re.compile('<div class="mecze" id="d7_t" style="(.*?)">(.*?)<div id="srodekd">', re.DOTALL).findall(readURL)

        match1 = re.compile('<div class="mecz_h">(.*?)</div>(.*?)<div class="mecz_t">(.*?)<b>(.*?)</b><br />(.*?)<img src="(.*?)" alt="" style="width:16px; height:16px;" />(.*?)</div>(.*?)<div class="mecz_p"><a href="(.*?)" target="_blank" class="play">play</a></div>', re.DOTALL).findall(match[0][1])
        
        for i in range(len(match1)):
            print ("Ile",i)
#            print ("match1", match1[i])
            if len(match1) > 0:
                   #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                self.add('drhtvcompl', 'playSelectedMovie', 'None',match1[i][0] +' -- '+ match1[i][3], mainUrl+match1[i][5], mainUrl+match1[i][8], 'aaaa', 'None', True, False)
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
                self.add('drhtvcompl', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
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
                self.add('drhtvcompl', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1])) 


    def getMovieLinkFromXML(self, url):
        #http://www.drhtv.com.pl/drhtv1.html
        if url.lower() in ['http://www.drhtv.com.pl/drhtv1.html', 'http://www.drhtv.com.pl/drhtv2.html', 'http://www.drhtv.com.pl/drhtv3.html', 'http://www.drhtv.com.pl/drhtv4.html', 'http://www.drhtv.com.pl/drhtv5.html', 'http://www.drhtv.com.pl/drhtv6.html', 'http://www.drhtv.com.pl/drhtv7.html', 'http://www.drhtv.com.pl/drhtv8.html']: 
            linkVideo = self.up.getVideoLink(url)
            return linkVideo
        else: 
            req = urllib2.Request(url)
            req.add_header('User-Agent', HOST)
            openURL = urllib2.urlopen(req)
            readURL = openURL.read()
            openURL.close()
            match = re.compile('<p style="text-align: center;"><a(.*?)href="(.*?)" target="_blank">', re.DOTALL).findall(readURL)
            linkVideo = self.up.getVideoLink(match[0][1])
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
        elif name == 'main-menu' and category == 'Kanały':
            log.info('Jest kanały: ')
            self.listsCategoriesMenu('http://www.drhtv.com.pl/',)
        elif name == 'main-menu' and category == 'Poniedziałek':
            log.info('Jest Poniedziałek: ')
            self.listsItems('http://www.drhtv.com.pl/meczenazywo.html','Poniedziałek')
        elif name == 'main-menu' and category == 'Wtorek':
            log.info('Jest Wtorek: ')
            self.listsItems('http://www.drhtv.com.pl/meczenazywo.html','Wtorek')
        elif name == 'main-menu' and category == 'Środa':
            log.info('Jest Środa: ')
            self.listsItems('http://www.drhtv.com.pl/meczenazywo.html','Środa')
        elif name == 'main-menu' and category == 'Czwartek':
            log.info('Jest Czwartek: ')
            self.listsItems('http://www.drhtv.com.pl/meczenazywo.html','Czwartek')
        elif name == 'main-menu' and category == 'Piątek':
            log.info('Jest Piątek: ')
            self.listsItems('http://www.drhtv.com.pl/meczenazywo.html','Piątek')
        elif name == 'main-menu' and category == 'Sobota':
            log.info('Jest Sobota: ')
            self.listsItems('http://www.drhtv.com.pl/meczenazywo.html','Sobota')
        elif name == 'main-menu' and category == 'Niedziela':
            log.info('Jest Niedziela: ')
            self.listsItems('http://www.drhtv.com.pl/meczenazywo.html','Niedziela')

            
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems(self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems(url)
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(url), title, icon)

        
  
