# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math, time
import xbmcgui, xbmc, xbmcaddon, xbmcplugin


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - tvstrefa"
ptv = xbmcaddon.Addon(scriptID)
datapath = xbmc.translatePath(ptv.getAddonInfo('profile'))

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_urlparser, mrknow_Pageparser, mrknow_Player

log = mrknow_pLog.pLog()

mainUrl = 'http://screen-tv.pl'
imgUrl = 'http://screen-tv.pl/'


class screentv:
    def __init__(self):
        log.info('Starting http://looknij.tv')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.pp = mrknow_Pageparser.mrknow_Pageparser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.player = mrknow_Player.mrknow_Player()

        
    def listsMainMenu(self):
        #<a class="linkstra" href="http://tv-strefa.pl/telewizja-online.php?podstawowe">
        query_data = { 'url': mainUrl, 'use_host': True, 'use_cookie': False, 'use_post': False , 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        print("Link",link)
        match = re.compile('\n<li><a href="(.*?)">(.*?)<img src="(.*?)" /></a></li>', re.DOTALL).findall(link)
        #                     <li><a href="/d   ">     <img src="     " /></a></li>


        print("Link2",match)
        valTab = []
        strTab = []
        if len(match)>0:
            for l in range(len(match)):
                #print("Match->L>", len(match[l]), match[l])
                strTab.append(mainUrl+match[l][0])
                strTab.append(match[l][1])
                strTab.append(imgUrl+match[l][2])
                valTab.append(strTab)
                strTab = []
            valTab.sort(key = lambda x: x[0])
            for i in valTab:
                self.add('screentv', 'playSelectedMovie', 'None', i[1], i[2], i[0], 'None', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


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
        liz=xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon, path=videoUrl)
        liz.setInfo( type="Video", infoLabels={ "Title": title, } )
        print("MAMMAMAMAMAMMAMA")
        try:
            xbmcPlayer = xbmc.Player()
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

            #xbmcPlayer.play(videoUrl, liz)
            
            #if not xbmc.Player().isPlaying():
            #    xbmc.sleep( 10000 )
            #    #xbmcPlayer.play(url, liz)
            
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
        print("Dane",sys.argv[1],url,name,category,title)

        if name == None:
            self.listsMainMenu()
        elif name == 'categories-menu':
            self.listsCategoriesMenu(url)
        elif name == 'chanel-menu':
            self.listsLinks(url)
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.pp.getVideoLink(url), title, icon)


