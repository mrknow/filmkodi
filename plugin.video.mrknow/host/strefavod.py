# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser
import urlparse,httplib
try:
    import simplejson as json
except ImportError:
    import json

scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - strefavod"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, libCommon, Parser, Player

log = mrknow_pLog.pLog()

catUrl = 'http://www.strefavod.pl/api/GetCategories?type=Genre&sort=Name'
#http://www.strefavod.pl/api/GetMovies?categoryIds=433&limit=500

imgurl = 'http://m.ocdn.eu/_m/'
mainUrl = 'http://www.strefavod.pl/api/GetMovie?Id=2034'
playerUrl = 'http://www.youtube.pl/'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'
null = 0
true = 1
false =0

MENU_TAB = {2: "Kategorie",
            3: "Polecane",
            4: "Szukaj",
}


class strefavod:
    def __init__(self):
        log.info('Starting strefavod.pl')
        self.cm = libCommon.common()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()
        self.p = Player.Player()

    def getpage(self,url,data=None):
        print ("URL",url)
        header = {"User-Agent": "StrefaVOD/1.0 CFNetwork/609.1.4 Darwin/13.0.0","AppVersion": "1.0","DeviceVendor": "api-mobile-ios"}
        req = urllib2.Request(url, data, header)
        f = urllib2.urlopen(req)
        response = f.read()
        f.close() 
        print ("GetPage Response",response)
        return response


    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('strefavod', 'main-menu', val, val, 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
 


    def listsCategoriesMenu(self,url):
        valTab = [] 
        strTab = [] 
        vod_filmy = eval(self.getpage(url,None))
        print ("VOD FILMY", vod_filmy)
        for e in vod_filmy["Result"]:
            print ("E",e)
            strTab.append(self.cm.html_special_chars(e["Name"]))
            strTab.append(e["Count"])
            strTab.append(e["Id"])
            strTab.append(e["Codename"])
            
            valTab.append(strTab)
            strTab = []
            valTab.sort(key = lambda x: x[0])
        for i in valTab:
            self.add('strefavod', 'categories-menu', i[3], i[0] + ' (' + str(i[1])+')', 'None', 'None', 'None', 'None', True, False,str(i[2]))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
    def listsItems(self, id1,url=''):
        valTab = [] 
        strTab = [] 
        if url == '':
            url = 'http://www.strefavod.pl/api/GetMovies?categoryIds='+id1+'&limit=500'
            
        vod_items = eval(self.getpage(url,None))
        print ("vod_items",vod_items)
        for e in vod_items["Result"]["Movies"]:
            strTab.append(e["Title"])
            strTab.append(e["ImageUrl"]) #Poster
            strTab.append(e["Id"])
            valTab.append(strTab)
            strTab = []
            valTab.sort(key = lambda x: x[0])
        for i in valTab:
            self.add('strefavod', 'playSelectedMovie', 'None', i[0], i[1], 'None', 'None', 'None', False, False,str(i[2]))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))



    def getMovieLinkFromXML(self, id1):
        url = 'http://www.strefavod.pl/api/GetMovie?Id='+id1
        vod_items = eval(self.getpage(url,None))
#       print ("vod_items",vod_items)
        for e in vod_items["Result"]["Movie"]["MediaFiles"]:
            if e["MediaFileRole"] == "Main":
                print "mamy to"
                if len(e["MediaFileFormats"])>0:
                    url = e["MediaFileFormats"][0]["Url"]
                    print ("u",url)
        if len(url) > 0:
            return url
        else:
            return ''
    def getMovieYear(self, id1):
        url = 'http://www.strefavod.pl/api/GetMovie?Id='+id1
        vod_items = eval(self.getpage(url,None))
        print ("vod_items",vod_items["Result"]["Movie"]["Year"])
        if len(str(vod_items["Result"]["Movie"]["Year"])) > 0:
            return str(vod_items["Result"]["Movie"]["Year"])


    def getSearchURL(self):
        text = self.searchInputText()
        url = 'http://www.strefavod.pl/api/GetMoviesByKeyword?keyword='+urllib.quote_plus(text) 
        self.listsItems('',url)


    def searchInputText(self):
        text = None
        k = xbmc.Keyboard()
        k.doModal()
        if (k.isConfirmed()):
            text = k.getText()
        return text
    

    def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True,id1='0',id2='0',year=''):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage) + "&id1=" + urllib.quote_plus(id1) + "&id2=" + urllib.quote_plus(id2) + "&year=" + urllib.quote_plus(year)
        #log.info(str(u))
#        if name == 'main-menu' or name == 'categories-menu':
#            title = category 
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
        id1 = self.parser.getParam(params, "id1")
        id2 = self.parser.getParam(params, "id2")
        year = self.parser.getParam(params, "year")
        print ("ID",category,id1,id2, icon,year)
        
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Kategorie':
            log.info('Jest Kategorie: ')
            self.listsCategoriesMenu('http://www.strefavod.pl/api/GetCategories?type=Genre&sort=Name')
        elif name == 'main-menu' and category == 'Polecane':
            log.info('Jest Polecane: ')
            self.listsItems('','http://www.strefavod.pl/api/getpromomovies')
        elif name == 'main-menu' and category == 'Szukaj':
            log.info('Jest Szukaj: ')
            self.getSearchURL()
        elif name == 'categories-menu' and id1 !='':
            log.info('Jest Kategorie: ')
            self.listsItems(id1)

        if name == 'playSelectedMovie':
            self.p.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(id1), title, icon,self.getMovieYear(id1))
        if name == 'playselectedmovie':
            self.p.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(id1), title, icon,self.getMovieYear(id1))

        
  
