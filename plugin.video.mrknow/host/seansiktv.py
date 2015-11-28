# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser, base64

import json



scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - http://seansik.tv/"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, settings, Parser,mrknow_pCommon, mrknow_Player

log = mrknow_pLog.pLog()

mainUrl = 'http://seansik.tv/'
#http://seansik.tv/?act=list&type=film&sort=new&order=asc&view=table

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {5: "Filmy",
            #6: "Seriale",
            #10: "Anime",
            #12: "Junior"
            #13: "Oglądalność",
            #14: "Oceny",
            #15: "Alfabetycznie"
            }
LANG_TAB = {1: "Napisy",
            2: "Lektor",
            8: "Lektor IVO",
            3: "Dubbing",
            4: "PL",
            5: "ENG",
            6: "Japoński",
            7: "Oryginał",
            9: "Napisy eng"
            }


class seansiktv:
    def __init__(self):
        log.info('Starting seansiktv.pl')
        self.settings = settings.TVSettings()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()
        self.cm = mrknow_pCommon.common()
        self.pl = mrknow_Player.mrknow_Player()

    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('seansiktv', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsCategoriesMenu(self):
        query_data = { 'url': 'http://seansiktv.pl/kategorie.html', 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
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
                self.add('seansiktv', 'categories-menu', match1[i][1].strip(), 'None', 'None', url, 'None', 'None', True, False,'0','sort_field=data-dodania&sort_method=asc')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        url = mainUrl + 'search.php?phrase=' + urllib.quote_plus(key) 
        return url
        #req = urllib2.Request(url)
        #req.add_header('User-Agent', HOST)
        #openURL = urllib2.urlopen(req)
        #readURL = openURL.read()
        
    def listsItemsOther(self, url):
        #http://seansiktv.pl/kategorie,0,wszystkie,wszystkie,1900-2013,.html?sort_field=data-dodania&sort_method=asc
        #urllink = url + ',' + str(strona) + ',wszystkie,wszystkie,1900-2013,.html?' + filtrowanie
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<div class="mostPopular movies hotMovies">(.*?)<div class="newMovies movies_r">', re.DOTALL).findall(link)
        match1 = re.compile('<li>\n                        <div class="poster" style="background:url\(\'(.*?)\'\) no-repeat 11px 0px"></div>\n                        <div class="title">\n                            <h2><a href="(.*?)" title="(.*?)">(.*?)</a></h2>', re.DOTALL).findall(match[0])
        print match1
        if len(match1) > 0:
            for i in range(len(match1)):
                data = self.cm.getURLRequestData({ 'url': mainUrl+ match1[i][1], 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True })
                if (data.find('http://seansiktv.pl/static/img/niedostepny.jpg')) == -1:
                    #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                    self.add('seansiktv', 'playSelectedMovie', 'None', match1[i][3],  match1[i][0].replace('_small',''), mainUrl+ match1[i][1], 'aaaa', 'None', True, False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

        
    def listsItems(self, url, strona='1', filtrowanie=''):
        #print strona
        #print filtrowanie
        urllink = url + '?' + filtrowanie + '&page=' + str(strona)
        query_data = { 'url': urllink, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<table >(.*?)</table>', re.DOTALL).findall(link)
        if len(match) > 0:
            for i in range(len(match)):
                match1 = re.compile('<a itemprop="significantLink" href="(.*?)">(.*?)</a>', re.DOTALL).findall(match[i])
                if len(match1) > 0:
                    plik = match1[0][0]
                    tytul = match1[0][1].replace('<br>','').replace('\n','').strip()
                    numer = match1[0][0].replace('/film/','')
                #    #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                    self.add('seansiktv', 'play-menu', 'None', tytul,  'http://srednie.obrazki.seansik.tv/medium_'+numer+'.jpg', mainUrl+ plik[1:], 'aaaa', 'None', True, False)
        self.add('seansiktv', 'categories-menu', 'Następna', 'None', 'None', mainUrl, 'None', 'None', True, False,str(int(strona) + 1), filtrowanie)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsPlayItems(self, url, title, icon):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<div id="translation_(.*?)"(.*?)class="translationList">', re.DOTALL).findall(link)
        sasa = re.compile("_sasa = {(.*?)}",re.DOTALL).findall(link)
        jfilmy = json.loads('{'+sasa[0]+'}')
        if len(match) > 0 and len(sasa)>0:
            for i in range(len(match)):
                match1 = re.compile('<div id="translation_'+match[i][0]+'"(.*?)class="translationList">(.*?)</div>\n                        </div>\n', re.DOTALL).findall(link)
                if len(match1)>0:
                    for j in range(len(match1)):
                        match2 = re.compile('<div data-vid_key="(.*?)" data-id="(.*?)" data-tut="(.*?)" id="(.*?)" style="cursor:pointer;" class="(.*?)">\n                <span class="domain">(.*?)</span>\n                                                                        <span style="float:right;">(.*?)</span>', re.DOTALL).findall(match1[j][1])
                        if len(match2)>0:
                            for k in range(len(match2)):
                                mylink = re.compile('<iframe (.*?)src="(.*?)"(.*?)></iframe>',re.DOTALL).findall(base64.b64decode(jfilmy[match2[k][0]]))
                                #print("kto",mylink)
                                title2 = LANG_TAB[int(match[i][0])] + ' ' + match2[k][5]+ ' ' + match2[k][6]
                                self.add('seansiktv', 'playSelectedMovie', 'None', title2, icon, mylink[0][1], 'None', 'None', False, True)

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
                self.add('seansiktv', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1])) 



    def getSizeAllItems(self, url):
        numItems = 0
        req = urllib2.Request(url)
        req.add_header('User-Agent', HOST)
        openURL = urllib2.urlopen(req)
        readURL = openURL.read()
        openURL.close()
        match = re.compile('<span class="nav_ext">...</span> <a href="http://seansiktv.pl/filmy/page/(.*?)/">(.*?)</a></div>(.*?)</li>', re.DOTALL).findall(readURL)
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
        strona = self.parser.getParam(params, "strona")
        filtrowanie = self.parser.getParam(params, "filtrowanie")
        print("url",url,strona, filtrowanie,icon,title)
        
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Filmy':
            log.info('Jest Filmy: ')
            self.listsItems(mainUrl,1,'act=list&type=film&sort=new&order=desc&view=table')
        elif name == 'play-menu':
            log.info('Jest play-menu: ')
            self.listsPlayItems(url,title,icon)
        elif name == 'main-menu' and category == 'Oglądalność':
            log.info('Jest Wszystkie: ')
            self.listsItems('http://seansiktv.pl/kategorie',0,'sort_field=odslony&sort_method=desc')
        elif name == 'main-menu' and category == 'Oceny':
            log.info('Jest Wszystkie: ')
            self.listsItems('http://seansiktv.pl/kategorie',0,'sort_field=ocena&sort_method=desc')
        elif name == 'main-menu' and category == 'Alfabetycznie':
            log.info('Jest Wszystkie: ')
            self.listsItems('http://seansiktv.pl/kategorie',0,'sort_field=alfabetycznie&sort_method=desc')
        elif name == 'main-menu' and category == 'Gorące':
            log.info('Jest Gorące: ')
            self.listsItemsOther('http://seansiktv.pl/')
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
            self.pl.LOAD_AND_PLAY_VIDEO(url, title, icon)

        
  
