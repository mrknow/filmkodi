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

import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_urlparser, mrknow_Pageparser, mrknow_Player, mrknow_utils
from BeautifulSoup import BeautifulSoup

log = mrknow_pLog.pLog()

mainUrl = 'http://www.tvseriesonline.pl/'
catUrl = 'http://www.tvseriesonline.pl/'

HOST = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/30.0'

MENU_TAB = {0: "Alfabetycznie",
#            1: "Top dzisiaj",
#            2: "Ostatnie dodane seriale",
            3: "Ostatnio dodane odcinki"
#            12: "Kategorie",
#            15: "Szukaj"
            }
LETER_TAB = {
                       1: "0-9",
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

class tvseriesonlinepl:
    def __init__(self):
        log.info('Starting tvseriesonlinepl.pl')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.pp = mrknow_Pageparser.mrknow_Pageparser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.player = mrknow_Player.mrknow_Player()

    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('tvseriesonlinepl', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
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
                self.add('tvseriesonlinepl', 'categories-menu', match1[i][1].strip(), 'None', 'None', catUrl, 'None', 'None', True, False,'1','kat='+match1[i][0])
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
                        self.add('tvseriesonlinepl', 'playSelectedMovie', 'None', match1[i][1], 'None', match1[i][0], 'aaaa', 'None', False, True)

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
        soup = BeautifulSoup(link)
        tytul = ''
        #
        match2 = re.compile('<div class="dlugi"><h2>(.*?)\((.*?)\)</h2></div>', re.DOTALL).findall(link)
        print("Match2",match2)
        if len(match2) > 0:
            tytul = match2[0][0]
        mytab = []
        linki_all = soup.findAll('h3', {"class": "title"})
        print("Moje",linki_all)
        if linki_all:
            for mylink in linki_all:
                tag_a = mylink.find('a')
                print("tag_a",tag_a)
                self.add('tvseriesonlinepl', 'playSelectedMovie', 'None', tytul + ' - ' + self.cm.html_special_chars(tag_a.text.encode('utf8')), 'None', tag_a['href'], 'aaaa', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItemsA(self, url):
       #for num, val in LETER_TAB.items():
       #     self.add('tvseriesonlinepl', 'page-menu', 'None',  val,  'None', mainUrl, 'aaaa', 'None', True, False)
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        linki_seriale = mrknow_utils.soup_get_links(link, "ul", {"id": "categories"})
        if len(linki_seriale)>0:
            for i in range(len(linki_seriale)):
                self.add('tvseriesonlinepl', 'items-menu', 'None', linki_seriale[i]['text'],  'None', linki_seriale[i]['link'], 'None', 'None', True, False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItemsS(self, url, strona):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<li class="first" id="letter-'+strona+'">'+strona+':</li>(.*?)<li class="first"', re.DOTALL).findall(link)
        print("Match",match)
        match1 = re.compile('<li><a href="(.*?)">(.*?)</a></li>\n', re.DOTALL).findall(match[0])
        print match1
        if len(match1) > 0:
            for i in range(len(match1)):
                title = match1[i][1]
                if title.find('NOWE') >-1:
                    #print ("Mam nowe", title)
                    title = title.replace('<span class="subtitle none">',' - NOWE [/COLOR]')
                    title = title.replace('/ NOWE</span> ','[COLOR yellow]')
                    title = title.strip() 
                    
                
                self.add('tvseriesonlinepl', 'items-menu', 'None', self.cm.html_special_chars(title),  'None', match1[i][0], 'aaaa', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        

    def listsItemsOst(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('		<div id="morecontent">(.*?)<div class="x"></div>', re.DOTALL).findall(link)
        match1 = re.compile('<div class="over">\r\n\t\t\t\t\t<a href="(.*?)"  class="catTitle" title="(.*?)">(.*?)</a>\t\t\t\t\t</div>\r\n\t\t\t\t\t\t<a href="(.*?)"><img width="180" height="180" src="(.*?)" class="attachment-thumbnail" alt="(.*?)" /></a>\t\t\t\t</div>\r\n\t\t\t\t\t<a href="(.*?)" class="epi">(.*?)<img src="(.*?)" class="catlang" />\t\t\t\t\t</a>\r\n\t\t\t\t<div class="data">(.*?)</div>\r\n\t\t\t</header>', re.DOTALL).findall(match[0])
        if len(match1) > 0:
            for i in range(len(match1)):
                #print("dane",match1[i])
                self.add('tvseriesonlinepl', 'playSelectedMovie', 'None', self.cm.html_special_chars(match1[i][1].strip() + ' - ' + match1[i][7].strip()),  match1[i][4], match1[i][6], 'aaaa', 'None', False, True,'')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    def listsItemsTop(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<!-- popularne dzisiaj -->\n(.*?)<!-- /popularne dzisiaj -->', re.DOTALL).findall(link)
        print match
        #                    <td class="title" tyle="width:200px;"><a href="     ">     </a></td>\n                       <td class="episode">\n                          <a href="     "><span class="w">     </span>     </a>\n                       </td>
        match1 = re.compile('<td class="title" tyle="width:200px;"><a href="(.*?)">(.*?)</a></td>\n                       <td class="episode">\n                          <a href="(.*?)"><span class="w">(.*?)</span>(.*?)</a>\n                       </td>', re.DOTALL).findall(match[0])
        if len(match1) > 0:
            for i in range(len(match1)):
                #print ("M",match1[i])
                self.add('tvseriesonlinepl', 'playSelectedMovie', 'None', self.cm.html_special_chars(match1[i][1].strip() + ' ' + match1[i][3].strip() + ' ' + match1[i][4].strip()),  'None', mainUrl[:-1]+ match1[i][2], 'aaaa', 'None', False, False,'')
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
                self.add('tvseriesonlinepl', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))        


    def listsSeasons(self, url,img):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<button data-action="scrollTo" data-scroll="(.*?)" class="btn btn-new cf sezonDirect" style="width:85px; font-size:13px;margin: 3px;" href="#" rel="1">(.*?)</button>', re.DOTALL).findall(link)
        #print match
        if img == '' or img ==None:
            img = 'None'
        for i in range(len(match)):
            self.add('tvseriesonlinepl', 'items-menu', 'None', match[i][1],  img, url, 'None', 'None', True, False,match[i][0])
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
    def getMovieLinkFromXML(self, url):
        VideoData = {}
        query_data = { 'url': url, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        #VideoData['year'] = str(self.getMovieYear(link))
        #                   #<a href="#" data-type="player" data-version="standard" data-id="54368">
        match1 = re.compile('<a href="#" data-type="player" data-version="standard" data-id="(.*?)">', re.DOTALL).findall(link)
        url1 = "http://alekino.tv/players/init/" + match1[0] + "?mobile=false"
        query_data = { 'url': url1, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match15 = re.compile('"data":"(.*?)"', re.DOTALL).findall(link)
        hash = match15[0].replace('\\','')
        post_data = {'hash': hash}
        query_data = {'url': 'http://alekino.tv/players/get', 'use_host': False, 'use_cookie': True, 'save_cookie': False, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True}
        data = self.cm.getURLRequestData(query_data, post_data)
        #print("Data",data)
        match16 = re.compile('<iframe src="(.*?)" (.*?)', re.DOTALL).findall(data)
        match17 = re.compile('<iframe src="(.*?)" style="border:0px; width: 630px; height: 430px;" scrolling="no"></iframe>', re.DOTALL).findall(data)
        print("Match",match16,match17)
        if len(match16) > 0:
            page = urllib.urlopen(match16[0][0].decode('utf8'))
            #print page.geturl()   # This will show the redirected-to URL
            #print ("match16_link",page.geturl())

            linkVideo = self.up.getVideoLink(page.geturl())

            #linkVideo = self.up.getVideoLink(match16[0].decode('utf8'))
            return linkVideo + '|Referer=http://alekino.tv/assets/alekino.tv/swf/player.swf'
        if len(match17) > 0:
            page = urllib.urlopen(match17[0].decode('utf8'))
            #print page.geturl()   # This will show the redirected-to URL
            #print ("match16_link",page.geturl())

            linkVideo = self.up.getVideoLink(page.geturl())
            #linkVideo = self.up.getVideoLink(match17[0].decode('utf8'))
            return linkVideo + '|Referer=http://alekino.tv/assets/alekino.tv/swf/player.swf'
        

    def searchInputText(self):
        text = None
        k = xbmc.Keyboard()
        k.doModal()
        if (k.isConfirmed()):
            text = k.getText()
        return text
    

    """def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True, strona = '', img = ''):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage)+ "&strona=" + urllib.quote_plus(strona)+ "&img=" + urllib.quote_plus(img)
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
    """
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
            self.listsItemsOst('http://www.tvseriesonline.pl/tab/1/')
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            if key != None:
                self.listsItemsOther(self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems(url,strona,filtrowanie)
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(url, title,'')


        
  
