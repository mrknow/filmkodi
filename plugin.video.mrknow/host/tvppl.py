# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser
import json


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - tvppl"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, libCommon, Parser, settings

log = mrknow_pLog.pLog()

startUrl  = 'http://vod.tvp.customers.multiscreen.tv/Navigation'
seriesUrl = 'http://vod.tvp.customers.multiscreen.tv/Movies/SeriesJSON?pageSize=100&pageNo=0&thumbnailSize=640&deviceType=2&parentId='
episodeUrl = 'http://vod.tvp.customers.multiscreen.tv/Movies/EpisodesJSON?pageNo=0&pageSize=100&thumbnailSize=640&deviceType=2&parentId='
seriesDetailUrl = 'http://vod.tvp.customers.multiscreen.tv/movies/SeriesDetailsJSON?thumbnailSize=640&deviceType=2&id='
movieUrl = 'http://vod.tvp.customers.multiscreen.tv/Movies/MovieJSON?thumbnailSize=320&id='
imgUrl = 'http://s.v3.tvp.pl/images/1/f/g/uid_1fghdlydor5l2gcqc8sc1ddjcspavr0_width_160_0_0.jpg'
filmyUrl = 'http://vod.tvp.pl/filmy-fabularne/'





HOST = 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_3 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Mobile/10B329'

MENU_TAB = {1: "Wszystkie",
            3: "Szukaj" }


class tvppl:
    def __init__(self):
        log.info('Starting tvppl.pl')
        self.cm = libCommon.common()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()



    def listsMainMenu(self):
        query_data = { 'url': startUrl, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        objs = json.loads(link)
        for o in objs[0]['SubCategories']:
            nazwa = self.cm.html_special_chars(json.dumps(o["Title"]).replace('"',''))
            id = json.dumps(o["Id"]).replace('"','')
            ListType = json.dumps(o["ListType"]).replace('"','')
            #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
            self.add('tvppl', ListType, 'None', nazwa, 'None', id, 'None', 'None', True, False)
        self.add('tvppl', 'films', 'None', 'Filmy', 'None', '0', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems(self,id):
        query_data = { 'url': episodeUrl+id, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        objs = json.loads(link)
        for o in objs:
            nazwa = self.cm.html_special_chars(json.dumps(o["website_title"]).replace('"','')+ ' '+ json.dumps(o["title"]).replace('"',''))
            id = json.dumps(o["asset_id"]).replace('"','')
            image = json.dumps(o["image"][0]["file_name"]).replace('"','').replace('.jpg','')
            image1 = 'http://s.v3.tvp.pl/images/'+ image[0] + '/' + image[1] +'/' +image[2] + '/uid_'+image +'_width_640_0_0.jpg'            
            self.add('tvppl', 'playSelectedMovie', 'None', nazwa,image1, id, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsSeries(self,id):
        query_data = { 'url': seriesUrl+id, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        objs = json.loads(link)
        for o in objs:
            nazwa = self.cm.html_special_chars(json.dumps(o["title"]).replace('"',''))
            id = json.dumps(o["asset_id"]).replace('"','')
            image = json.dumps(o["image_4x3"][0]["file_name"]).replace('"','').replace('.jpg','')
            image1 = 'http://s.v3.tvp.pl/images/'+ image[0] + '/' + image[1] +'/' +image[2] + '/uid_'+image +'_width_640_0_0.jpg'            
            self.add('tvppl', 'episodes', 'None', nazwa,image1, id, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    def listsFilms(self,url):
        query_data = { 'url': url, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<ul class="headP">(.*?)</ul>', re.DOTALL).findall(link)
        if len(match) > 0:
            for i in range(len(match)):
                match1 = re.compile('<strong class="fullTitle">\r\n                                <a href="(.*?)" title="(.*?)">(.*?)</a>\r\n                            </strong>', re.DOTALL).findall(match[i])
                self.add('tvppl', 'filmy_detale', 'None', self.cm.html_special_chars(match1[0][2]),'None', 'http://vod.tvp.pl'+match1[0][0], 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
    def listsFilmsDetail(self,url,title):
        query_data = { 'url': url, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<strong class="fullTitle">(.*?)</strong>', re.DOTALL).findall(link)
        if len(match) > 0:
            for i in range(len(match)):
                match1 = re.compile('<a href="(.*?)" title="(.*?)">', re.DOTALL).findall(match[i])
                id = match1[0][0]
                id1 = id.split('/');
                self.add('tvppl', 'playSelectedMovie', 'None', self.cm.html_special_chars(title + ' ' + match1[0][1]),'None', id1[-1], 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
    def getMovieLinkFromXML(self, url):
        query_data = { 'url': movieUrl + url, 'use_host': True, 'host': HOST, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        objs = json.loads(link)
        if len(objs['video_format'])>1:
            linkVideo = json.dumps(objs['video_format'][1]["temp_sdt_url"]).replace('"','')
        else: 
            linkVideo = json.dumps(objs['video_format'][0]["temp_sdt_url"]).replace('"','')
        print ('Data',linkVideo)
        return linkVideo
        

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
        print ("MENU",name,category,url,title,icon)
        if name == None:
            self.listsMainMenu()
        elif name == 'episodes':
            log.info('Jest episodes: ')
            self.listsItems(url)
        elif name == 'series':
            log.info('Jest series: ')
            self.listsSeries(url)
        elif name == 'films':
            log.info('Jest films: ')
            self.listsFilms(filmyUrl)
        elif name == 'filmy_detale':
            log.info('Jest filmy_detale: ')
            self.listsFilmsDetail(url,title)
            
            
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems(self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems(url)
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(url), title, icon)

        
  
