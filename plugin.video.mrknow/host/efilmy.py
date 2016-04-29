# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from BeautifulSoup import BeautifulSoup
import  urllib
import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_Player, mrknow_Pageparser
import json


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - efilmy"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

mainUrl = 'http://efilmy.tv/'

MENU_TAB = {1: "Ostatnio dodane",
            2: "Kategorie",
            3: "Popularne - 7 dni",
            4: "Popularne - 14 dni",
            5: "Popularne - 31 dni",
            6: "Wszystkie",
            10: "Szukaj"
            }


class efilmy:
    def __init__(self):
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.pp1 = mrknow_Pageparser.mrknow_Pageparser()
        self.player = mrknow_Player.mrknow_Player()
        self.log = mrknow_pLog.pLog()
        self.log.info('Starting efilmy.pl')

    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('efilmy', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def getSearchURL(self, key):
        url = urllib.quote_plus(key)
        return url

    def listsCategoriesMenu(self, url):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://efilmy.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': url, 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost1 = soup.find('ul', {"class": "movie-cat"})
        if linki_ost1:
            linki_all1 = linki_ost1.findAll('li')
            for mylink in linki_all1:
                #self.log.info("m %s %s " % (mylink.a.text,mylink.a['href']))
                if mylink.a.text.encode('utf-8') != '':
                    self.add('efilmy', 'categories-menu', self.cm.html_special_chars(mylink.a.text.encode('utf-8')),'None', 'None', mainUrl+ mylink.a['href'].replace('.html',',p0.html'), 'aaaa', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems(self,url):
        #obliczamy stronę
        try:
            mypagenumber = int(url.replace('.html','').split(',')[-1].replace('p',''))
            #self.log.info('[] %s' % mypagenumber)
            mynext = url.replace('p'+str(mypagenumber)+'.html', 'p'+str(mypagenumber+1)+'.html')
        except:
            mynext = ''
        self.log.info('[] %s' % mynext)

        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://efilmy.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': url, 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost = soup.find('div', {"class": "dodane-tresc"})
        if linki_ost:
            self.MyAddItems(linki_ost,'list-item')
        self.add('efilmy', 'categories-menu', 'Następna >>>', "None", "None", mynext, 'aaaa', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems2(self, url):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://efilmy.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': url, 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        objs = json.loads(link)
        for o in objs["suggestions"]:
            #nazwa = json.dumps(o["name"]).replace('"','')
            self.log.info('[] nazwa %s' % o['t'])
            if o['t'] == u'm':
                #<span class="as_tp"> [Napisy PL]</span></a>
                title = o['value']
                try:
                    match = re.compile('<span class="as_tp">(.*?)</span></a>', re.DOTALL).findall(o['value_html'])[0]
                    title = title + match
                except:
                    pass
                self.add('efilmy', 'playSelectedMovie', 'None', title, mainUrl + o['image'], mainUrl + o['data'], 'aaaa', 'None', False, True)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems3(self, url, myclass2):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://efilmy.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': url, 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        linki_ost = BeautifulSoup(link)
        #linki_ost = soup.find('div', {"id": myclass1})
        if linki_ost:
            self.MyAddItems(linki_ost,myclass2)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems4(self, url, myclass1, myclass2):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://efilmy.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': mainUrl, 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost = soup.find('div', {"id": myclass1})
        self.log.info('AAAAAAAAAAAAAAAA %s' % linki_ost)
        if linki_ost:
            self.MyAddItems(linki_ost,myclass2)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def MyAddItems(self, data, myclass):
        linki_ost = data.findAll('div', {"class": myclass})
        if linki_ost:
            for mylink in linki_ost:
                title = mylink.a['title'].replace('online','').replace('Film ','')
                if isinstance(title, unicode):
                    title = title.encode('utf-8')
                self.add('efilmy', 'playSelectedMovie', 'None', title, mainUrl + mylink.a.img['src'], mainUrl + mylink.a['href'], 'aaaa', 'None', False, True)


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
        self.log.info("category: %s " % category)
        print("url", url)
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Ostatnio dodane':
            self.listsItems4(mainUrl, 'main-movie-content', 'main-list-item')
        elif name == 'main-menu' and category == "Popularne - 7 dni":
            self.listsItems3('http://www.efilmy.tv/filmy.php?cmd=popularne&dni=7','similar-item')
        elif name == 'main-menu' and category == "Popularne - 31 dni":
            self.listsItems3('http://www.efilmy.tv/filmy.php?cmd=popularne&dni=31','similar-item')
        elif name == 'main-menu' and category == "Popularne - 14 dni":
            self.listsItems3('http://www.efilmy.tv/filmy.php?cmd=popularne&dni=14','similar-item')
        elif name == 'main-menu' and category == "Kategorie":
            self.listsCategoriesMenu('http://www.efilmy.tv/filmy.html')
        elif name == 'main-menu' and category == "Wszystkie":
            self.listsItems('http://www.efilmy.tv/filmy,p0.html')


        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems2('http://www.efilmy.tv/autocomm.php?query=%s' % self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            self.listsItems(url)
        if name == 'playSelectedMovie':
            self.log.info('url: ' + str(url))
            mojeurl = self.pp1.getVideoLink(url)
            self.player.LOAD_AND_PLAY_VIDEO(mojeurl,'','')

        
  
