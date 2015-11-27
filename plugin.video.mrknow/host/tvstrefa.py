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

mainUrl = 'http://tv-strefa.pl/'
chanelUrl = 'http://tv-strefa.pl/telewizja-online.php'


class tvstrefa:
    def __init__(self):
        log.info('Starting http://looknij.tv')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.pp = mrknow_Pageparser.mrknow_Pageparser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.player = mrknow_Player.mrknow_Player()

        
    def listsMainMenu(self):
        #<a class="linkstra" href="http://tv-strefa.pl/telewizja-online.php?podstawowe">
        query_data = { 'url': chanelUrl, 'use_host': True, 'use_cookie': False, 'use_post': False , 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        #print("Link",link)
        match = re.compile('<div class="telonlinelist"><div style="padding: 10px;"><b style="font-size: 20px;">(.*?)</b><br/>(.*?)</div><br/>\n<a class="linkstra" href="(.*?)">(.*?)<span style="font-size: 12px;">(.*?): (.*?)</span></a></div>\n\n', re.DOTALL).findall(link)
        #print("Link2",match)
        if len(match)>0:
            for l in range(len(match)):
                #print("Match->L>",match[l])
                mytitle = match[l][0] + "  (" +match[l][5]+")"
                self.add('tvstrefa', 'categories-menu', mytitle, 'None', 'None' , match[l][2], 'None', 'None', True, False)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsCategoriesMenu(self,url):
        query_data = { 'url': url, 'use_host': True,  'use_post': False , 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<div class="telonlinelista1"><img src="(.*?)" alt="(.*?)"/><b>(.*?)</b></div>(.*?)</div>\n<a class="linkstra" href="(.*?)">(.*?)</a></div>\n<div class="telonlinelist">', re.DOTALL).findall(link)
        valTab = []
        strTab = []
        if len(match)>0:
            for l in range(len(match)):
                #print("Match->L>", len(match[l]), match[l])
                strTab.append(match[l][1])
                strTab.append(mainUrl+match[l][0])
                strTab.append(match[l][4])
                valTab.append(strTab)
                strTab = []
            valTab.sort(key = lambda x: x[0])
            for i in valTab:
                self.add('tvstrefa', 'chanel-menu', 'None', i[0], i[1], i[2], 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsLinks(self,url):
        query_data = { 'url': url, 'use_host': True,  'use_post': False , 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<div class="linkstr">\n(.*?)\n</div>', re.DOTALL).findall(link)
        if len(match)>0:
            for l in range(len(match)):
                match1 = re.compile('<img src="(.*?)" alt="(.*?)"/>\n(.*?)\n<b>(.*?)</b><br/>(.*?)<div>\n<a class="linkstram" href="(.*?)"(.*?)>(.*?)</a>\n<a class="linkstram" href="(.*?)">(.*?)</a></div>', re.DOTALL).findall(match[l])
                if len(match1)>0:
                    for j in range(len(match1)):
                        print("A1",match1[j][1],match1[j][2],match1[j][3],match1[j][5])

                        if "Looknij" in match1[j][3] or "Stat" in match1[j][3] or "Ustream" in match1[j][3]:
                            print ("Mam kolor!!!!!!!")
                            tytul = "[COLOR white]" + match1[j][1] + " " + match1[j][2] + " " + match1[j][3] + " [/COLOR]"
                        else:
                            tytul = "[COLOR black]" + match1[j][1] +" " + match1[j][2] + " " + match1[j][3]+ " [/COLOR]"
                        #[COLOR white] [/COLOR]
                        self.add('tvstrefa', 'playSelectedMovie', 'None', tytul, 'None', match1[j][5], 'None', 'None', False, True)
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
        #print("Dane",sys.argv[1],url,name,category,title)

        if name == None:
            self.listsMainMenu()
        elif name == 'categories-menu':
            self.listsCategoriesMenu(url)
        elif name == 'chanel-menu':
            self.listsLinks(url)
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.pp.getVideoLink(url), title, icon)


