#-*- coding: iso-8859-2 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - joemonster"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, settings, Parser

log = mrknow_pLog.pLog()

mainUrl = 'http://www.joemonster.org/'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {1: "Najnowsze",
            2: "Najpopularniejsze",
            9: "Szukaj" }


class joemonster:
    def __init__(self):
        log.info('Starting joemonster.pl')
        self.settings = settings.TVSettings()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()



    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('joemonster', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self):
        req = urllib2.Request(mainUrl)
        req.add_header('User-Agent', HOST)
        openURL = urllib2.urlopen(req)
        readURL = openURL.read()
        openURL.close()
        match = re.compile('<li data-theme="c">(.*?)<a href="(.*?)" data-transition="slide">(.*?)</a>(.*?)</li>', re.DOTALL).findall(readURL)
        print len(match)
        
        if len(match) > 0:
            log.info('Listuje kategorie: ')
            for i in range(len(match)):
                url = mainUrl + match[i][1]
                self.add('joemonster', 'categories-menu', match[i][2].strip(), 'None', 'None', url, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        url = mainUrl + 'search.php?phrase=' + urllib.quote_plus(key) 
        return url
        #req = urllib2.Request(url)
        #req.add_header('User-Agent', HOST)
        #openURL = urllib2.urlopen(req)
        #readURL = openURL.read()
        

    def listsItems(self, url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', HOST)
        openURL = urllib2.urlopen(req)
        readURL = openURL.read()
        openURL.close()
        #match = re.compile('<strong>\s(.*?)<a href="(.*?)">(.*?)</a>\s(.*?)[video](.*?)</strong>', re.DOTALL).findall(readURL)
        match = re.compile('<div class="mtv-thumb"><a href="(.*?)" target=_top><center><img src="(.*?)" border="0" hspace="10" title="(.*?)" class="mtvBigThumb"></center></a><br class=odstep></div><div class="mtv-desc"><a href="(.*?)" class=title target=_top><b>(.*?)</b></a><div class=\'tiny\'><DIV>(.*?)</DIV><br><br>', re.DOTALL).findall(readURL)

        print match
        if len(match) > 0:
            for i in range(len(match)):
            
                #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                self.add('joemonster', 'playSelectedMovie', 'None', match[i][2].decode('iso-8859-2').encode('utf8'), match[i][1], mainUrl+match[i][0], match[i][5], 'None', True, False)
       
       #     
       #         req1 = urllib2.Request(mainUrl + match[i][1])
       #         req1.add_header('User-Agent', HOST)
       #         openURL1 = urllib2.urlopen(req)
       #         readURL1 = openURL1.read()
       #         openURL1.close()
       #         match1 = re.compile('<a data-role="button" data-transition="fade" data-theme="b" href=\'(.*?)\' target="_blank" data-icon="arrow-r" data-iconpos="top">(.*?)</a>', re.DOTALL).findall(readURL)
       #         print match1
       #         if len(match1) > 0:
       #             self.add('joemonster', 'playSelectedMovie', 'None', match[i][3], match[a][1], match[a][0], match[a][4], 'None', True, False)
       
        
        match1 = re.compile('<a href="(.*?)" class="pagerNav" title="(.*?)">(.*?)</a>').findall(readURL)
        print match1

        
        log.info('Nastepna strona: '+  match1[10][0])
        self.add('joemonster', 'categories-menu', 'Nastepna', 'None', 'None', mainUrl+match1[-2][0], 'None', 'None', True, False)
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
                self.add('joemonster', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
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
                self.add('joemonster', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1])) 


    def getMovieLinkFromXML(self, url):
        urlLink = 'None'
        print url
        req = urllib2.Request(url)
        req.add_header('User-Agent', HOST)
        openURL = urllib2.urlopen(req)
        readURL = openURL.read()
        openURL.close()
        match = re.compile('<iframe id="ytplayer" type="text/html"   src="(.*?)"  allowfullscreen webkitallowfullscreen mozallowfullscreen  frameborder="0" WIDTH="800" HEIGHT="450"></iframe>', re.DOTALL).findall(readURL)
        print match
        if len(match) > 0:
            linkVideo = self.up.getVideoLink(match[0])
            return linkVideo
        match = re.compile('<div id="flashcontent101"><embed src="(.*?)" allowfullscreen="true"  type="application/x-shockwave-flash" WIDTH="800" HEIGHT="450" wmode="opaque"></embed>', re.DOTALL).findall(readURL)
        print match
        if len(match) > 0:
            o = parse_qs(urlparse(match[0]).query)
            print o
            linkVideo =  urllib.unquote(o['file'][0])
            return linkVideo
        match = re.compile('<param name="movie" value="(.*?)">', re.DOTALL).findall(readURL)
        print match
        if len(match) > 0:       
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
        elif name == 'main-menu' and category == 'Najnowsze':
            log.info('Jest Wszystkie: ')
            self.listsItems('http://www.joemonster.org/filmy/najnowsze')
        elif name == 'main-menu' and category == 'Najpopularniejsze':
            log.info('Jest Wszystkie: ')
            self.listsItems('http://www.joemonster.org/filmy/najpopularniejsze')
            
            
            
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems(self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems(url)
        if name == 'playSelectedMovie':
            log.info('play: ' + str(url))
            self.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(url), title, icon)

        
  
