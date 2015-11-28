# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs



scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - filmsonline"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, settings, Parser,libCommon, Player, mrknow_urlparser

log = mrknow_pLog.pLog()

mainUrl = 'http://www.films-online.pl/'
catUrl = 'filmy--0-0-0-2-0.html'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {5: "Wszystkie",
#            6: "Kategorie",
#            10: "Data dodania",
#            12: "Data premiery",
#            13: "Oglądalność",
#            14: "Oceny",
#            15: "Alfabetycznie"
            }


class filmsonline:
    def __init__(self):
        log.info('Starting filmsonline.pl')
        self.settings = settings.TVSettings()
        self.parser = Parser.Parser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.cm = libCommon.common()
        self.p = Player.Player()



    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('filmsonline', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self):
        query_data = { 'url': 'http://filmsonline.pl/kategorie.html', 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<div class="leftMenu">(.*?)<span>Wersja</span>', re.DOTALL).findall(link)
        match1 = re.compile('<a href="(.*?)">(.*?)</a> ', re.DOTALL).findall(match[0])
        print match
        print match1
        #<a href="filmy,Akcja.html">Akcja</a> 
        
        if len(match1) > 0:
            log.info('Listuje kategorie: ')
            for i in range(len(match1)):
                url = mainUrl + match1[i][0].replace('.html','')
                print url
                self.add('filmsonline', 'categories-menu', match1[i][1].strip(), 'None', 'None', url, 'None', 'None', True, False,'0','sort_field=data-dodania&sort_method=asc')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        url = mainUrl + 'search.php?phrase=' + urllib.quote_plus(key) 
        return url
        #req = urllib2.Request(url)
        #req.add_header('User-Agent', HOST)
        #openURL = urllib2.urlopen(req)
        #readURL = openURL.read()
        
    def listsItemsOther(self, url):
        #http://filmsonline.pl/kategorie,0,wszystkie,wszystkie,1900-2013,.html?sort_field=data-dodania&sort_method=asc
        #urllink = url + ',' + str(strona) + ',wszystkie,wszystkie,1900-2013,.html?' + filtrowanie
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<div class="mostPopular movies hotMovies">(.*?)<div class="newMovies movies_r">', re.DOTALL).findall(link)
        match1 = re.compile('<li>\n                        <div class="poster" style="background:url\(\'(.*?)\'\) no-repeat 11px 0px"></div>\n                        <div class="title">\n                            <h2><a href="(.*?)" title="(.*?)">(.*?)</a></h2>', re.DOTALL).findall(match[0])
        print match1
        if len(match1) > 0:
            for i in range(len(match1)):
                data = self.cm.getURLRequestData({ 'url': mainUrl+ match1[i][1], 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True })
                if (data.find('http://filmsonline.pl/static/img/niedostepny.jpg')) == -1:
                    #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                    self.add('filmsonline', 'playSelectedMovie', 'None', match1[i][3],  match1[i][0].replace('_small',''), mainUrl+ match1[i][1], 'aaaa', 'None', False, False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        
    def listsItems(self, url, strona='0', filtrowanie=''):
        print strona
        filtr = 'filmy-'+str(strona)+'-0-0-0-2-0.html'
        print filtrowanie
        #http://filmsonline.pl/kategorie,0,wszystkie,wszystkie,1900-2013,.html?sort_field=data-dodania&sort_method=asc
        urllink = url + filtr
        print urllink
        query_data = { 'url': urllink, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        print("Link",link)
        #match = re.compile('<div class="moviesWrap">(.*?)<footer>', re.DOTALL).findall(link)
        match1 = re.compile('<div class="moje_box_content">(.*?)<a href="(.*?)">(.*?)<img src="(.*?)" alt="" style="(.*?)"/>\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t</a></div>\n\t\t\t\t\t\t\t<div class="moje_box_tresc">\n\t\t\t\t\t\t\t\t<div class="line_title_moje" style="background:none;">\n\t\t\t\t\t\t\t\t\t<a href="(.*?)"><span class="moje_title">(.*?)</span></a>', re.DOTALL).findall(link)
        print match1
        if len(match1) > 0:
            for i in range(len(match1)):
                #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                self.add('filmsonline', 'playSelectedMovie', 'None', match1[i][6],   mainUrl+match1[i][3].replace('_small',''), mainUrl+ match1[i][1], 'aaaa', 'None', False, False)
        #urllink = url + ',' + str((int(strona)+1)) + ',wszystkie,wszystkie,1900-2013,.html?' + filtrowanie
        log.info('Nastepna strona: '+  urllink)
        self.add('filmsonline', 'categories-menu', 'Następna', 'None', 'None', url, 'None', 'None', True, False,str(int(strona) + 1))
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
                self.add('filmsonline', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
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
                self.add('filmsonline', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1])) 


    def getMovieLinkFromXML(self, url):
        HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'
        query_data = { 'url': url, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile('<div id="e1">(.*?)<iframe src="(.*?)" width="490px" height="338px" frameborder="0" scrolling="no"></iframe>					</div>', re.DOTALL).findall(link)
        print match1
        linkVideo = self.up.getVideoLink(match1[0][1])
        print linkVideo
        return linkVideo



    def getSizeAllItems(self, url):
        numItems = 0
        req = urllib2.Request(url)
        req.add_header('User-Agent', HOST)
        openURL = urllib2.urlopen(req)
        readURL = openURL.read()
        openURL.close()
        match = re.compile('<span class="nav_ext">...</span> <a href="http://filmsonline.pl/filmy/page/(.*?)/">(.*?)</a></div>(.*?)</li>', re.DOTALL).findall(readURL)
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
            


    def handleService(self):
    	params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        strona = self.parser.getParam(params, "strona")
        filtrowanie = self.parser.getParam(params, "filtrowanie")
        print("url",category,url,strona, filtrowanie)
        
        if name == None:
            self.listsItems('http://www.films-online.pl/',1,'')
        elif name == 'main-menu' and category == 'Data premiery':
            log.info('Jest Wszystkie: ')
            self.listsItems('http://filmsonline.pl/kategorie',0,'sort_field=data-premiery&sort_method=desc')
        elif name == 'main-menu' and category == 'Oglądalność':
            log.info('Jest Wszystkie: ')
            self.listsItems('http://filmsonline.pl/kategorie',0,'sort_field=odslony&sort_method=desc')
        elif name == 'main-menu' and category == 'Oceny':
            log.info('Jest Wszystkie: ')
            self.listsItems('http://filmsonline.pl/kategorie',0,'sort_field=ocena&sort_method=desc')
        elif name == 'main-menu' and category == 'Alfabetycznie':
            log.info('Jest Wszystkie: ')
            self.listsItems('http://filmsonline.pl/kategorie',0,'sort_field=alfabetycznie&sort_method=desc')
        elif name == 'main-menu' and category == 'Gorące':
            log.info('Jest Gorące: ')
            self.listsItemsOther('http://filmsonline.pl/')
        elif name == 'main-menu' and category == 'Kategorie':
            log.info('Jest Gorące: ')
            self.listsCategoriesMenu()
 

            
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems(self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems(url,strona,filtrowanie)
        if name == 'playSelectedMovie':
            log.info('Jest playSelectedMovie: ')
            p = self.p.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(url), title, icon)
            log.info('Po playSelectedMovie: ')
            log.info(p)
            
            

        
  
