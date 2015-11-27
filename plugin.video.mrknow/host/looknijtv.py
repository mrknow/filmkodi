# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math, time
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser,urlparse
import json


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - cda.pl"
ptv = xbmcaddon.Addon(scriptID)
datapath = xbmc.translatePath(ptv.getAddonInfo('profile'))

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_urlparser, mrknow_Pageparser

log = mrknow_pLog.pLog()

mainUrl = 'http://looknij.tv/'
chanelUrl = 'http://looknij.tv/wp-admin/admin-ajax.php'
COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "looknijtv.cookie"


MENU_TAB = {1: "Kanały" }
            #8: "Video najlepiej ocenione",
            #9: "Krótkie filmy i animacje",
            #10: "Filmy Extremalne",
            #11: "Motoryzacja, wypadki",
            #12: "Muzyka",
            #13: "Prosto z Polski",
            #14: "Rozrywka",
            #15: "Różności",
            #16: "Sport",
            #17: "Śmieszne filmy",
            #27: "[COLOR yellow]Aktualizuj LIBRTMP - aby dzialy kanaly TV - Patche KSV[/COLOR]"            }

max_stron = 0            

class StopDownloading(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

class looknijtv:
    def __init__(self):
        log.info('Starting http://looknij.tv')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.pp = mrknow_Pageparser.mrknow_Pageparser()
        self.up = mrknow_urlparser.mrknow_urlparser()

        
    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('looknijtv', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsCategoriesMenu(self,url):
        query_data = { 'url': url, 'use_host': True, 'use_cookie': True, 'cookiefile': COOKIEFILE, 'load_cookie': False, 'save_cookie': True, 'use_post': False , 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        postdata = {'html_template': 'Grid columns', 'now_open_works':'0','action':'get_portfolio_works','works_per_load':'31','category':'all'}
        query_data = { 'url': chanelUrl, 'use_host': True, 'use_cookie': True, 'cookiefile': COOKIEFILE, 'load_cookie': True, 'save_cookie': False, 'use_post': True , 'return_data': True }
        link = self.cm.getURLRequestData(query_data,postdata)

        match = re.compile('<img alt="(.*?)" src="(.*?)">\r\n                        <div class="portfolio_wrapper"></div>\r\n                        <div class="portfolio_content">\r\n                            <h5>(.*?)</h5>\r\n\t\t\t\t\t\t\t<span class="ico_block">\r\n\t\t\t\t\t\t\t    \r\n\t\t\t\t\t\t\t    <a class="ico_link"  href="(.*?)"><span></span></a>\r\n', re.DOTALL).findall(link)
        print("Match-->",match,link)
        valTab = []
        strTab = []
        if len(match)>0:
            for l in range(len(match)):
                print("Match->L>",match[l])
                #match1 = re.compile('<li><a href="(.*?)">(.*?)<img src="http://wrzucaj.net/images/2014/09/12/flash-player-icon.png" /></a></li>\n').findall(match[l])
                #if len(match1)>0:
                #    for j in range(len(match1)):
                        #print("MAtch1",match1[j])
                strTab.append(match[l][0])
                strTab.append(match[l][1])
                strTab.append(match[l][3])
                valTab.append(strTab)
                strTab = []
            valTab.sort(key = lambda x: x[1])
            for i in valTab:
                print("Match->L>",i)
                self.add('looknijtv', 'playSelectedMovie', 'None', i[0], i[1], i[2], 'None', 'None', False, False)
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


    def getMovieLinkFromXML(self, url):
        #szukamy iframe
        progress = xbmcgui.DialogProgress()
        progress.create('Postęp', '')
        message = "Szukam adresu do wideo"
        progress.update( 10, "", message, "" )
        xbmc.sleep( 1000 )
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match3 = re.compile('<div class="yendifplayer" data-poster="(.*?)" data-vid="(.*?)"><video><source type="(.*?)" src="(.*?)" data-rtmp="(.*?)"></video></div>').findall(link)
        #match = re.compile('<div class="yendifplayer" data-poster="(.*?)"><video><source type="video/mp4" src=""><source type="video/flash" src="(.*?)" data-rtmp="(.*?)"><track src="(.*?)"></video></div>').findall(link)
        print("Match-->",match3)
        progress.update( 30, "", message, "" )
        progress.update( 50, "", message, "" )
        VideoLink = ''
        if len(match3)>0:
            message = "Mam adres wideo, dekoduję..."
            progress.update( 60, "", message, "" )
            VideoLink = match3[0][4]+match3[0][3] + ' live=true timeout=15'
            progress.update( 90, "", message, "" )
        progress.close()
        return VideoLink

    def handleService(self):
    	params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        strona = self.parser.getParam(params, "strona")
        print("Dane",sys.argv[2],url,name,category,title)
        print ("A")

        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == "[COLOR yellow]Aktualizuj LIBRTMP - aby dzialy kanaly TV - Patche KSV[/COLOR]":
            self.LIBRTMP()
        elif name == 'librtmp' and category == "update":
            self.DLLIBRTMP(title,url)
        elif name == 'main-menu' and category == 'Kanały':
            self.listsCategoriesMenu(mainUrl + '?page_id=11')
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(url), title, icon)

        
  
