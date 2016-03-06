# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import mrknow_urlparser,json


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - alltubefilmy"
ptv = xbmcaddon.Addon(scriptID)
_thisPlugin = int(sys.argv[1])

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_urlparser, mrknow_Pageparser, mrknow_Player
from BeautifulSoup import BeautifulSoup


log = mrknow_pLog.pLog()

mainUrl = 'http://alltube.tv/'
catUrl = 'http://alltube.tv/filmy-online/'


HOST = 'Mozilla/5.0 (Windows NT 6.1; rv:17.0) Gecko/20100101 Firefox/41.0'

MENU_TAB = {#0: "Alfabetycznie",
#            1: "Top dzisiaj",
#            2: "Ostatnie dodane seriale",
            3: "Ostatnio dodane",
            12: "Kategorie",
            15: "Szukaj"
            }

class alltubefilmy:
    def __init__(self):
        log.info('Starting alltubefilmy.pl')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.pp = mrknow_Pageparser.mrknow_Pageparser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.player = mrknow_Player.mrknow_Player()

    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('alltubefilmy', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': mainUrl, 'User-Agent': HOST}
        query_data = { 'url': catUrl, 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost = soup.find('ul', {"id": "filter-category"})
        #print("link",link)
        print("M1",linki_ost)
        if linki_ost:
            linki_all = linki_ost.findAll('li')
            for mylink in linki_all:
                print("m",mylink.text,mylink['data-id'])
                #murl = catUrl + match1[i][0].replace('.html','')
                self.add('alltubefilmy', 'categories-menu', mylink.text,mylink.text,  'None', catUrl + 'kategoria['+mylink['data-id']+']+', 'None', 'None', True, False,str(1),mylink['data-id'])
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
        
    def listsItemsOther(self, key):
        query_data = { 'url': 'http://alltube.tv/szukaj', 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
        post_data = {'search': key}
        link = self.cm.getURLRequestData(query_data,post_data)
        log(link)
        if 'Seriale:' in link:
            link = re.compile('<h4>Filmy:</h4>(.*?)<h4>Seriale:</h4>', re.DOTALL).findall(link)[0]
        log(link)
        soup = BeautifulSoup(link)
        linki_ost = soup.findAll('div', {"class": "item clearfix"})
        log("link %s" % link)
        if linki_ost:
            for mylink in linki_ost:
                self.add('alltubefilmy', 'playSelectedMovie', 'None', mylink.a.text, 'None', mylink.a['href'], 'aaaa', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def GetImage(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match2 = re.compile('<div class="span2">\n                       <img src="(.*?)" alt=""/>\n                       \n                    </div>', re.DOTALL).findall(link)
        if len(match2) > 0: 
            return match2[0]
        else:
            return ""
            
    def listsItems(self, url,strona='', kategoria=''):
        if strona=='':
            strona=1
        nowastrona=int(strona)+1

        if kategoria == 'None':
            myurl = catUrl  + 'strona['+str(nowastrona)+']+'
        else:
            myurl = catUrl  + 'kategoria['+kategoria+']+' +'strona['+str(nowastrona)+']+'

        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': mainUrl, 'User-Agent': HOST}
        query_data = { 'url': url, 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost = soup.findAll('div', {"class": "col-xs-12 col-md-6"})
        #print("link",link)
        if linki_ost:
            #linki_all = soup.findAll('div', {"class": "series"})
            for mylink in linki_ost:
                #print("m",mylink)
                #print("M2",mylink.a['href'])
                #print("M3",mylink.img['src'])
                print("M4",url,strona,mylink.h3.text)
                #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                self.add('alltubefilmy', 'playSelectedMovie', 'None', mylink.h3.text, mylink.img['src'], mylink.a['href'], 'aaaa', 'None', False, True)
        # add(self, service, name,                   category,        title,       iconimage,          url,                           desc, rating, folder = True, isPlayable = True,strona=''):
        self.add('alltubefilmy', 'categories-menu', 'Następna strona','Następna strona',  'None', myurl, 'None', 'None', True, False,str(nowastrona),kategoria)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItemsA(self, url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<li class="letter">(.*?)</li>', re.DOTALL).findall(link)
        print(match)
        if len(match) > 0:
            for i in range(len(match)):
                self.add('alltubefilmy', 'page-menu', 'None',  match[i],  'None', mainUrl, 'aaaa', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItemsS(self, url, strona):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match0 = re.compile('<li data-letter="'+strona+'"><a href="(.*?)">(.*?)</a></li>', re.DOTALL).findall(link)
        print("Match",match0)
        #match1 = re.compile('<li><a href="(.*?)">(.*?)</a></li>\n', re.DOTALL).findall(match[0])
        #print match1
        if len(match0) > 0:
            for i in range(len(match0)):
                title = match0[i][1]

                self.add('alltubefilmy', 'items-menu', 'None', self.cm.html_special_chars(title),  'None', match0[i][0], 'aaaa', 'None', True, False)
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
                print("m",mylink)
                print("M2",mylink.a['href'])

                myimage = mylink.img['src']
                mytitle = mylink.contents[1].text
                myhref = mylink.a['href']
                #myseries = mylink.contents[2].findAll('li')
                #for myitem in myseries:
                self.add('alltubefilmy', 'playSelectedMovie', 'None', mytitle ,  myimage, myhref, 'aaaa', 'None', False, True,'')

        self.add('alltubefilmy', 'playSelectedMovie', 'None', mytitle ,  myimage, myhref, 'aaaa', 'None', False, True,'')

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
                self.add('alltubefilmy', 'playSelectedMovie', 'None', self.cm.html_special_chars(match1[i][1].strip() + ' ' + match1[i][3].strip() + ' ' + match1[i][4].strip()),  'None', mainUrl[:-1]+ match1[i][2], 'aaaa', 'None', False, False,'')
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
                self.add('alltubefilmy', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))        


    def listsSeasons(self, url,img):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<button data-action="scrollTo" data-scroll="(.*?)" class="btn btn-new cf sezonDirect" style="width:85px; font-size:13px;margin: 3px;" href="#" rel="1">(.*?)</button>', re.DOTALL).findall(link)
        #print match
        if img == '' or img ==None:
            img = 'None'
        for i in range(len(match)):
            self.add('alltubefilmy', 'items-menu', 'None', match[i][1],  img, url, 'None', 'None', True, False,match[i][0])
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 
    def searchInputText(self):
        text = None
        k = xbmc.Keyboard()
        k.doModal()
        if (k.isConfirmed()):
            text = k.getText()
        return text
    
    def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True,strona='', kategoria=''):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage)+ "&strona=" + urllib.quote_plus(strona)+ "&kategoria=" + urllib.quote_plus(kategoria)
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
        kategoria = self.parser.getParam(params, "kategoria")
        img = self.parser.getParam(params, "img")
        print ("DANE",kategoria, strona,url,title,name,icon)
        
        
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Ostatnio dodane':
            log.info('Jest Ostatnio dodane: ')
            self.listsItems(catUrl,1,'None')
        elif name == 'main-menu' and category == 'Kategorie':
            log.info('Jest Kategorie: ')
            self.listsCategoriesMenu()



        elif name == 'categories-menu':
            log.info('Jest categories-menu: ')
            self.listsItems(url,strona,kategoria)
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
                self.listsItemsOther(key)
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems(url,strona,filtrowanie)
        if name == 'playSelectedMovie':
            self.player.LOAD_AND_PLAY_VIDEO(url, title,'')


        
  
