# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser
import json

scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - wykop"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, libCommon, Parser
pluginhandle = int(sys.argv[1])

log = mrknow_pLog.pLog()

mainUrl = 'http://www.wykop.pl/m/'
playerUrl = 'http://www.youtube.pl/'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {1: "Wszystkie",
            3: "Szukaj" }


class WYKOP:
    def __init__(self):
        log.info('Starting wykop.pl')
        self.cm = libCommon.common()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()
        


    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('wykop', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self):
        req = urllib2.Request(mainUrl)
        req.add_header('User-Agent', HOST)
        openURL = urllib2.urlopen(req)
        readURL = openURL.read()
        openURL.close()
        match = re.compile('<li data-theme="c">(.*?)<a href="(.*?)" data-transition="slide">(.*?)</a>(.*?)</li>', re.DOTALL).findall(readURL)
        
        if len(match) > 0:
            log.info('Listuje kategorie: ')
            for i in range(len(match)):
                url = mainUrl + match[i][1]
                self.add('wykop', 'categories-menu', match[i][2].strip(), 'None', 'None', url, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        url = mainUrl + 'search.php?phrase=' + urllib.quote_plus(key) 
        return url
        #req = urllib2.Request(url)
        #req.add_header('User-Agent', HOST)
        #openURL = urllib2.urlopen(req)
        #readURL = openURL.read()
        

    def listsItems(self, url, page):
        page2 = str(int(page)+1)
        url = 'http://a.wykop.pl/links/promoted/day/appkey,SI8sP6KDk1/page/'+page 
        url2 = 'http://a.wykop.pl/links/promoted/day/appkey,SI8sP6KDk1/page/'+page2 
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        objs = json.loads(link)
        for o in objs:
            #print ("OO",o)
            if o['type']== 'video':
                image = o['preview'].replace(',w104h74.jpg',',w173h114.jpg')
                #print image
                #add(self, service, name,               category, title,     iconimage, url, desc, rating, folder = True, isPlayable = True):
                self.add('wykop', 'playSelectedMovie', 'None', '[COLOR yellow]'+self.cm.html_special_chars(o['title'].encode('utf-8')) +' [/COLOR] Wykopow:'+str(o['vote_count']),image, o['source_url'], o['description'], 'None', False, False)
            #else:
            #    self.add('wykop', 'SelectedMovie', 'None', o['title'] +' Wykopow:'+str(o['vote_count']),o['preview'], o['source_url'], o['description'], 'None', True, False)
 
        #match1 = re.compile(' <a href="(.*?)" class="inlblk tdnone vtop button" style="right: 0px">następna</a>').findall(link)
        #log.info('Nastepna strona: '+  match1[0])
        self.add('wykop', 'categories-menu', 'Następna', 'None', 'None', url2, 'None', page2, True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        #xbmc.executebuiltin("Container.SetViewMode(515)")
        #xbmcplugin.setContent(int(sys.argv[1]),'tvshows')
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        xbmc.executebuiltin("Container.SetViewMode('tvshows-view')")
        




    def getMovieLinkFromXML(self, url):
        #query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        #link = self.cm.getURLRequestData(query_data)
        #match = re.compile('<blockquote cite="(.*?)"', re.DOTALL).findall(link)
        linkVideo = self.up.getVideoLink(url)
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



    def add(self, service, name, category, title, iconimage, url, desc, page, folder = True, isPlayable = True):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage) + "&page=" + urllib.quote_plus(page)
        #log.info(str(u))
        if name == 'main-menu' or name == 'categories-menu':
            title = category 
        if iconimage == '':
            iconimage = "DefaultVideo.png"
        liz=xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=iconimage )
        liz.setProperty('fanart_image',iconimage)
        if isPlayable:
            liz.setProperty("IsPlayable", "true")
        liz.setInfo( type="Video", infoLabels={ "Title": title, "Plot": desc, "Episode" : "AAA", "Year" : "2000", "Genre" : "bbb" } )
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
        page = self.parser.getParam(params, "page")
        
        print("DANE",url,page)
        if page == None:
            page = '1'
        print("DANE",url,page)
        if name == None:
 #           self.listsMainMenu(MENU_TAB)
 #       elif name == 'main-menu' and category == 'Wszystkie':
 #           log.info('Jest Wszystkie: ')
            self.listsItems(mainUrl,page)
            

        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems(url,page)
        elif name == 'items-audio' and category != 'None':
            log.info('AUDIOAAAAAAAAAAAAAAAAAAurl: ' + str(url))
            self.listsItemsAudio(url)
        if name == 'playSelectedMovie':
            if url != 'None':
                self.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(url), title, icon)
        if name == 'SelectedMovie':
                xbmc.executebuiltin('XBMC.RunAddon(script.web.viewer '+url+')')

        
  
