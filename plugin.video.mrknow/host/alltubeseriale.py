# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import mrknow_urlparser,json


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - http://zobaczto.tv/ seriale"
ptv = xbmcaddon.Addon(scriptID)
_thisPlugin = int(sys.argv[1])

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_urlparser, mrknow_Pageparser, mrknow_Player
from BeautifulSoup import BeautifulSoup


log = mrknow_pLog.pLog()

mainUrl = 'http://alltube.tv/'
catUrl = 'http://alltube.tv/seriale-online/'


HOST = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/41.0'

MENU_TAB = {0: "Alfabetycznie",
#            1: "Top dzisiaj",
#            2: "Ostatnie dodane seriale",
            3: "Ostatnio dodane odcinki"
#            12: "Kategorie",
#            15: "Szukaj"
            }
LETER_TAB = {
                       1: "0",

                       2: "A",
                       3: "B",
                       4: "C",
                       5: "D",
                       6: "E",
                       7: "F",
                       8: "G",
                       9: "H",
                       10: "I",
                       11: "J",
                       12: "K",
                       13: "L",
                       14: "M",
                       15: "N",
                       16: "O",
                       17: "P",
                       18: "Q",
                       19: "R",
                       20: "S",
                       21: "T",
                       22: "U",
                       23: "V",
                       24: "W",
                       25: "X",
                       26: "Y",
                       27: "Z"
                       }            

class alltubeseriale:
    def __init__(self):
        log.info('Starting alltubeseriale.pl')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.pp = mrknow_Pageparser.mrknow_Pageparser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.player = mrknow_Player.mrknow_Player()

    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('alltubeseriale', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self):
        query_data = { 'url': catUrl, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<ul class="select-movie-type movie-kat-selection">(.*?)</ul>', re.DOTALL).findall(link)
        match1 = re.compile('<a href="#" rel="filter" type="kat" value="(.*?)" >&#9632; (.*?)</a>', re.DOTALL).findall(match[0])
        
        if len(match1) > 0:
            log.info('Listuje kategorie: ')
            for i in range(len(match1)):
                url = mainUrl + match1[i][0].replace('.html','')
                self.add('alltubeseriale', 'categories-menu', match1[i][1].strip(), 'None', 'None', catUrl, 'None', 'None', True, False,'1','kat='+match1[i][0])
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        if key != None:
            url = mainUrl + '/search?search_query='+ urllib.quote_plus(key)+'&x=0&y=0'  
            return url
        else:
            return False
        #req = urllib2.Request(url)
        #req.add_header('User-Agent', HOST)
        #openURL = urllib2.urlopen(req)
        #readURL = openURL.read()
        
    def listsItemsOther(self, url):
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
            link = self.cm.getURLRequestData(query_data)
            match = re.compile('<!-- SERIES -->(.*?)<!-- SERIES INFO -->', re.DOTALL).findall(link)
            match1 = re.compile('<li><a href="(.*?)">(.*?)</a></li>', re.DOTALL).findall(match[0])
            if len(match1) > 0:
                for i in range(len(match1)):
                        #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                        self.add('alltubeseriale', 'playSelectedMovie', 'None', match1[i][1], 'None', match1[i][0], 'aaaa', 'None', False, True)

            xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def GetImage(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match2 = re.compile('<div class="span2">\n                       <img src="(.*?)" alt=""/>\n                       \n                    </div>', re.DOTALL).findall(link)
        if len(match2) > 0: 
            return match2[0]
        else:
            return ""
            
    def listsItems(self, url,strona=''):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<div class="col-xs-12 col-sm-9">(.*?)<h3>(.*?)</h3>', re.DOTALL).findall(link)
        match1 = re.compile('<li class="episode"><a href="(.*?)">(.*?)</a></li>', re.DOTALL).findall(link)
        match2 = re.compile('<div class="row" style="margin-bottom: 15px">\n      <div class="col-sm-3">\n        <img src="(.*?)" alt="(.*?)" class="img-responsive">', re.DOTALL).findall(link)
        #print(match,match1, match2)
        if len(match1) > 0:
            for i in range(len(match1)):
                    #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                    self.add('alltubeseriale', 'playSelectedMovie', 'None', match1[i][1], match2[0][0], match1[i][0], 'aaaa', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItemsA(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<li class="letter">(.*?)</li>', re.DOTALL).findall(link)
        #print(match)
        if len(match) > 0:
            for i in range(len(match)):
                self.add('alltubeseriale', 'page-menu', 'None',  match[i],  'None', mainUrl, 'aaaa', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItemsS(self, url, strona):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match0 = re.compile('<li data-letter="'+strona+'"><a href="(.*?)">(.*?)</a></li>', re.DOTALL).findall(link)
        #print("Match",match0)
        #match1 = re.compile('<li><a href="(.*?)">(.*?)</a></li>\n', re.DOTALL).findall(match[0])
        #print match1
        if len(match0) > 0:
            for i in range(len(match0)):
                title = match0[i][1]

                self.add('alltubeseriale', 'items-menu', 'None', self.cm.html_special_chars(title),  'None', match0[i][0], 'aaaa', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsItemsOst(self, url):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': mainUrl, 'User-Agent': HOST}
        query_data = { 'url': url, 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost = soup.find('div', {"class": "col-sm-9"})
        #print("link",link)
        if linki_ost:
            linki_all = soup.findAll('div', {"class": "series"})
            for mylink in linki_all:
                #print("m",mylink)
                #print("M2",mylink.a['href'])

                myimage = mylink.img['src']
                mytitle = mylink.contents[1].text
                myhref = mylink.a['href']
                #myseries = mylink.contents[2].findAll('li')
                #for myitem in myseries:
                self.add('alltubeseriale', 'playSelectedMovie', 'None', mytitle ,  myimage, myhref, 'aaaa', 'None', False, True,'')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    def listsItemsTop(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<!-- popularne dzisiaj -->\n(.*?)<!-- /popularne dzisiaj -->', re.DOTALL).findall(link)
        #print match
        #                    <td class="title" tyle="width:200px;"><a href="     ">     </a></td>\n                       <td class="episode">\n                          <a href="     "><span class="w">     </span>     </a>\n                       </td>
        match1 = re.compile('<td class="title" tyle="width:200px;"><a href="(.*?)">(.*?)</a></td>\n                       <td class="episode">\n                          <a href="(.*?)"><span class="w">(.*?)</span>(.*?)</a>\n                       </td>', re.DOTALL).findall(match[0])
        if len(match1) > 0:
            for i in range(len(match1)):
                #print ("M",match1[i])
                self.add('alltubeseriale', 'playSelectedMovie', 'None', self.cm.html_special_chars(match1[i][1].strip() + ' ' + match1[i][3].strip() + ' ' + match1[i][4].strip()),  'None', mainUrl[:-1]+ match1[i][2], 'aaaa', 'None', False, False,'')
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
                self.add('alltubeseriale', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))        


    def listsSeasons(self, url,img):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<button data-action="scrollTo" data-scroll="(.*?)" class="btn btn-new cf sezonDirect" style="width:85px; font-size:13px;margin: 3px;" href="#" rel="1">(.*?)</button>', re.DOTALL).findall(link)
        #print match
        if img == '' or img ==None:
            img = 'None'
        for i in range(len(match)):
            self.add('alltubeseriale', 'items-menu', 'None', match[i][1],  img, url, 'None', 'None', True, False,match[i][0])
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 

    
    def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True,strona=''):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage)+ "&strona=" + urllib.quote_plus(strona)
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

    def LOAD_AND_PLAY_VIDEO(self, url, title, icon,year='',plot=''):
        progress = xbmcgui.DialogProgress()
        progress.create('Postęp', '')
        message = ptv.getLocalizedString(30406)
        progress.update( 10, "", message, "" )
        xbmc.sleep( 1000 )
        progress.update( 30, "", message, "" )
        progress.update( 50, "", message, "" )
        VideoLink = ''
        VideoLink = self.pp.getVideoLink(url)

        videoUrl = VideoLink
        progress.update( 70, "", message, "" )
        pluginhandle = int(sys.argv[1])
        if videoUrl == '':
            progress.close()
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu', 'Mo�e to chwilowa awaria.', 'Spr�buj ponownie za jaki� czas')
            return False
        if icon == '' or  icon == 'None':
            icon = "DefaultVideo.png"
        if plot == '' or plot == 'None':
            plot = ''
        liz=xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon, path=videoUrl )
        liz.setInfo( type="video", infoLabels={ "Title": title} )
        xbmcPlayer = xbmc.Player()

        progress.update( 90, "", message, "" )
        progress.close()
        #listitem = xbmcgui.ListItem(path=videoUrl)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

    def handleService(self):
    	params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        strona = self.parser.getParam(params, "strona")
        img = self.parser.getParam(params, "img")
        print ("DANE",url,title,strona,name)
        
        
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Alfabetycznie':
            log.info('Jest Alfabetycznie: ')
            self.listsItemsA(catUrl)
        elif name == 'page-menu' and category == 'None':
            log.info('Jest Alfabetycznie Litera: '+ title)
            self.listsItemsS(catUrl,title)
        elif name == 'serial-menu' and category == 'None':
            log.info('Jest Serial Menu: ')
            self.listsSeasons(url,img)
        elif name == 'items-menu' and category == 'None':
            log.info('Jest Sezon: ')
            self.listsItems(url,strona)
        elif name == 'main-menu' and category == 'Top dzisiaj':
            log.info('Jest Top 30: ')
            self.listsItemsTop(catUrl)
#        elif name == 'main-menu' and category == 'Ostatnie dodane seriale':
#            self.listsItemsTop(catUrl,'Ostatnie dodane seriale', 'Ostatnie dodane odcinki')
        elif name == 'main-menu' and category == 'Ostatnio dodane odcinki':
            log.info('Jest Gorące: ')
            self.listsItemsOst(catUrl)
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            if key != None:
                self.listsItemsOther(self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems(url,strona,filtrowanie)
        if name == 'playSelectedMovie':
            self.player.LOAD_AND_PLAY_VIDEO(url, title,'')


        
  
