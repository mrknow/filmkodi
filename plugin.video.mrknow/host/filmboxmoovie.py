# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import httplib
import xml.etree.ElementTree as ET
import json

scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - filmboxmoovie"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, libCommon, Parser,Player, mrknow_urlparser

log = mrknow_pLog.pLog()

mainUrl = 'http://pl.filmboxlive.com/'
catUrl = 'http://api.invideous.com/plugin/get_package_videos?package_id=12&publisher_id=5842&records_per_page=50&filter_by_live=0&custom_order_by_order_priority=asc&custom_filter_by_genre='
#chanels = 'http://www.filmboxliveapp.com/channel/channels_pl.json'
#playerUrl = 'http://www.youtube.pl/'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {1: "Wszystkie",
            3: "Szukaj" }


class filmboxmoovie:
    def __init__(self):
        log.info('Starting filmboxmoovie.pl')
        self.cm = libCommon.common()
        self.parser = Parser.Parser()
        #self.up = urlparser.urlparser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.p = Player.Player()


    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('filmboxmoovie', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self):
        req = urllib2.Request('http://www.filmboxliveapp.net/mobilev2/ios/AppConfig_pl.xml')
        req.add_header('User-Agent', HOST)
        openURL = urllib2.urlopen(req)
        readURL = openURL.read()
        openURL.close()
        match = re.compile('<el name="Kategorie">(.*?)</el>', re.DOTALL).findall(readURL)
        match1 = re.compile('<el name="(.*?)" type="movie" action="custom_filter_by_genre" value="(.*?)" package="(.*?)"/>', re.DOTALL).findall(match[0])

        #Niestandardowe Kategorie
        self.add('filmboxmoovie', 'categories-menu', 'Wszystkie Filmy', 'None', 'None', 'http://api.invideous.com/plugin/get_package_videos?package_id=12&publisher_id=5842&records_per_page=50&filter_by_live=0&custom_order_by_order_priority=asc&custom_filter_by_genre=Action%7CDrama%7CComedy%7CRomance%7CHorror%7CThriller%7CFamily', 'None', 'None', True, False)
        self.add('filmboxmoovie', 'categories-menu', 'Polecane', 'None', 'None', 'http://api.invideous.com/plugin/get_package_videos?package_id=12&publisher_id=5842&records_per_page=30&filter_by_live=0&custom_order_by_order_priority=asc&custom_filter_by_genre=recommended', 'None', 'None', True, False)
        query_data = { 'url': 'http://admin.filmboxliveapp.com/GetList?ctr=poland', 'use_host': False, 'use_cookie': False,  'use_post': False,'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match11 = re.compile('"latestvideos":\[(.*?)\]', re.DOTALL).findall(link)
        match12 = re.compile('"mostwatched":\[(.*?)\]', re.DOTALL).findall(link)
        self.add('filmboxmoovie', 'categories-menu', 'Nowości', 'None', 'None', 'http://api.invideous.com/plugin/get_videos_details?videos='+match11[0]+'&publisher_id=5842', 'None', 'None', True, False)
        self.add('filmboxmoovie', 'categories-menu', 'Wybór redakcji', 'None', 'None', 'http://api.invideous.com/plugin/get_videos_details?videos='+match12[0]+'&publisher_id=5842', 'None', 'None', True, False)
        
        #Szukaj
        self.add('filmboxmoovie', 'main-menu', 'Szukaj', 'None', 'None', 'http://api.invideous.com/plugin/get_package_videos?package_id=12&publisher_id=5842&filter_by_live=0&records_per_page=50&filter_by_title=', 'None', 'None', True, False)
        
        if len(match1) > 0:
            log.info('Listuje kategorie: ')
            match2 = re.compile('<option label="(.*?)" value="(.*?)">(.*?)</option>', re.DOTALL).findall(match[0])
            for i in range(len(match1)):
            #http://api.invideous.com/plugin/get_package_videos?package_id=12&publisher_id=5842&records_per_page=30&page=1&filter_by_live=0&custom_order_by_order_priority=asc&custom_filter_by_genre=Comedy

                self.add('filmboxmoovie', 'categories-menu', match1[i][0].strip(), 'None', 'None', catUrl+match1[i][1], 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def getSearchURL(self, key):
        url = mainUrl + 'search.php?phrase=' + urllib.quote_plus(key) 
        return url
        #req = urllib2.Request(url)
        #req.add_header('User-Agent', HOST)
        #openURL = urllib2.urlopen(req)
        #readURL = openURL.read()
        

    def listsItems(self, url,strona='1'):
        
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "filmboxmoovie.cookie"
        url1 = url + '&page=' + strona
        query_data = { 'url': url1, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        objs = json.loads(link)
        turl = '|User-Agent=XBMC%2F12.1%20Git%3A20130317-0d373cc%20(Windows%20NT%206.1%3B%20http%3A%2F%2Fwww.xbmc.org)'

        for o in objs['response']['result']['videos']:
            print ("AAAAAAAA",o)
            #self.add('filmboxmoovie', 'playSelectedMovie', 'None', o['title'], o['custom_attributes']['largeImage'], o['source_url'], 'aaaa', 'None', True, False,'0',o['custom_attributes']['year_of_production'])
            self.add('filmboxmoovie', 'playSelectedMovie', 'None', o['title'], o['custom_attributes']['largeImage'], o['custom_attributes']['sony_source_url'], 'aaaa', 'None', False, False,'0',o['custom_attributes']['year_of_production'])
        self.add('filmboxmoovie', 'categories-menu', 'Następna', 'None', 'None', url, 'None', 'None', True, False,str(int(strona)+1))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def searchInputText(self):
        text = None
        k = xbmc.Keyboard()
        k.doModal()
        if (k.isConfirmed()):
            text = k.getText()
        return text

    def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True,strona='1',year=''):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage)+ "&strona=" + urllib.quote_plus(strona)+ "&year=" + urllib.quote_plus(year)
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
        year = self.parser.getParam(params, "year")
      
        if name == None:
            self.listsCategoriesMenu()
        elif name == 'main-menu' and category == 'Wszystkie':
            log.info('Jest Wszystkie: ')
            self.listsItems('http://www.filmboxliveapp.net/mobilev2/ios/AppConfig_pl.xml')         
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems(url +key)
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItems(url,strona)
        if name == 'playSelectedMovie':
            self.p.LOAD_AND_PLAY_VIDEO(url+'|User-Agent=Mozilla%2f5.0+(iPad%3b+CPU+OS+6_0+like+Mac+OS+X)+AppleWebKit%2f536.26+(KHTML%2c+​like+Gecko)+Version%2f6.0+Mobile%2f10A5355d+Safari%2f8536.25',title,icon,year,'')
        if name == 'playselectedmovie':
            self.p.LOAD_AND_PLAY_VIDEO(url+'|User-Agent=Mozilla%2f5.0+(iPad%3b+CPU+OS+6_0+like+Mac+OS+X)+AppleWebKit%2f536.26+(KHTML%2c+​like+Gecko)+Version%2f6.0+Mobile%2f10A5355d+Safari%2f8536.25',title,icon,year,'')

        
  
