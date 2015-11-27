# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser
import json,hashlib
import urlparse


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - wrzuta"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, libCommon, Parser, settings

log = mrknow_pLog.pLog()

mainUrl = 'http://www.wrzuta.pl/'
catUrl = mainUrl + 'ajax/pliki/edytuj'
loginUrl = 'https://ssl.wrzuta.pl/zaloguj'


HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {1: ["Audio - Najnowsze","http://www.wrzuta.pl/audio/najnowsze"],
            2: ["Audio - Popularne","http://www.wrzuta.pl/audio/popularne"],
            #3: ["Audio - Kategorie","http://www.wrzuta.pl/audio/popularne"],
            3: ["Audio - Szukaj","./"],
            4: ["Filmy - Najnowsze","http://www.wrzuta.pl/filmy/najnowsze"],
            5: ["Filmy - Szukaj","./"],
            #6: ["Moje konto",""],
            #5: ["Kanały",""],
            #6: ["Zestawienia Audio","http://www.wrzuta.pl/zestawienia/audio/"],
            #7: ["Zestawienia Filmy","http://www.wrzuta.pl/zestawienia/filmy"],
            #8: ["Zestawienia Obrazy","http://www.wrzuta.pl/zestawienia/obrazy"],
            #30: ["Szukaj",""]
 }

AUDIO_TAB = {
 }



class wrzuta:
    def __init__(self):
        log.info('Starting wrzuta.pl')
        self.cm = libCommon.common()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()
        self.cm = libCommon.common()
        self.settings = settings.TVSettings()
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "wrzuta.cookie"

    def login(self):    
        if ptv.getSetting('wrzuta_login') == 'true':
            
            tmplogin = hashlib.sha1(ptv.getSetting('wrzuta_pass')).hexdigest()
            tmplogin1 = hashlib.sha1(tmplogin+ptv.getSetting('wrzuta_user')).hexdigest()
            query_data = { 'url': loginUrl, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }        
            link = self.cm.getURLRequestData(query_data)
            #print ("L",link)
            post_data = {'login': ptv.getSetting('wrzuta_user'), 'password': tmplogin1, 'user_remember':'','fbid': ''}
            #login=mrknow&password=ffcee7d644dab355cb9111ceb96c348786fe9a82&user_remember=&fbid=
            
            query_data = {'url': loginUrl, 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True}
            data = self.cm.getURLRequestData(query_data, post_data)
            #print ("Data1",data)
            #post_data = {'login': ptv.getSetting('wrzuta_user'), 'pass': ptv.getSetting('wrzuta_pass'), 'log_in2':'Zaloguj'}
            #query_data = {'url': mainUrl+'index.php?p=login', 'use_host': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': True, 'return_data': True}
            #data = self.cm.getURLRequestData(query_data, post_data)
            #print ("Data2",data)
            if self.isLoggedIn(data) == True:
                xbmc.executebuiltin("XBMC.Notification(" + ptv.getSetting('wrzuta_user') + ", Zostales poprawnie zalogowany,4000)")
            else:
                xbmc.executebuiltin("XBMC.Notification(Blad logowania,4000)")  
        else:
            log.info('Wyświetlam ustawienia')
            self.settings.showSettings()
            xbmc.executebuiltin("XBMC.Notification(Skonfiguruj konto w ustawieniach, obecnie uzywam Player z limitami,4000)")  

    #  def add(self, service, name,    category, title, iconimage, url, desc, rating, folder = True, isPlayable = True):
    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('wrzuta', 'main-menu', val[0], val[0], 'None', val[1], 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

     
    def listsCategoriesMenu(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        print ("LINK",link)
        match = re.compile('<div class="box-entry-file-thumb">\n\t\t\t\t\t\t<a href="(.*?)" class="box-file-link">\n\t\t\t\t\t\t\t<img src="(.*?)" height="(.*?)" width="(.*?)" alt="(.*?)" />', re.DOTALL).findall(link)
        #print ("match",match)
        if len(match) > 0:
            for i in range(len(match)):
                #print match[i]
                url = match[i][0]
                #add(self, service, name,      category, title, iconimage, url, desc, rating, folder = True, isPlayable = True):
                self.add('wrzuta', 'playSelectedMovie', 'None', self.cm.html_special_chars(match[i][4]),   match[i][1], url, 'None', 'None', True, False)
        match2 = re.compile('<a class="paging-next" rel="(.*?)"\n\t\t\thref="(.*?)">', re.DOTALL).findall(link)
        if len(match2) > 0:  
            self.add('wrzuta', 'main-menu', 'Audio - Najnowsze', 'Następna strona', os.path.join(ptv.getAddonInfo('path'), "images/") +'nastepna_strona.png', match2[0][1], 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))        

    def listsCategoriesSearch(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        #print ("LINK",link)
        match = re.compile('<li  class="(.*?)"  data-cat="(.*?)">\n\t\t\n\t\t\t\n\t\t\t\t<a href="(.*?)" target="_blank" class="image">\n\t\t\t\n\t\t\t\t\n\t\t\t\t\t<img src="(.*?)" height="(.*?)" width="(.*?)" alt="(.*?)" />', re.DOTALL).findall(link)
        #print ("match",match)
        if len(match) > 0:
            for i in range(len(match)):
                print match[i]
                url = match[i][2]
                #add(self, service, name,      category, title, iconimage, url, desc, rating, folder = True, isPlayable = True):
                self.add('wrzuta', 'playSelectedMovie', 'None', self.cm.html_special_chars(match[i][6]),   match[i][3], url, 'None', 'None', True, False)
        match2 = re.compile('<a class="paging-next" rel="(.*?)"\n\t\t\thref="(.*?)">', re.DOTALL).findall(link)
        if len(match2) > 0:  
            self.add('wrzuta', 'main-menu', 'Audio - Szukaj', 'Następna strona', os.path.join(ptv.getAddonInfo('path'), "images/") +'nastepna_strona.png', match2[0][1], 'None', 'None', True, False,'Następna')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))        

    def listsFilms(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        print ("LINK",link)
        match = re.compile('<div class="left-area">\n\t\t\t\t\t\t\t<a href="(.*?)" class="position-img">\n\t\t\t\t\t\t\t\t\n\t\t\t\t\t\t\t\t\t<img src="(.*?)" alt="(.*?)" height="(.*?)" width="(.*?)"/>', re.DOTALL).findall(link)
        print ("match",match)
        if len(match) > 0:
            for i in range(len(match)):
                #print match[i]
                url = match[i][0]
                #add(self, service, name,      category, title, iconimage, url, desc, rating, folder = True, isPlayable = True):
                self.add('wrzuta', 'playSelectedMovie', 'None', self.cm.html_special_chars(match[i][2]),   match[i][1], url, 'None', 'None', True, False)
        match2 = re.compile('<a class="paging-next" rel="(.*?)"\n\t\t\thref="(.*?)">', re.DOTALL).findall(link)
        if len(match2) > 0:  
            self.add('wrzuta', 'main-menu', 'Filmy - Najnowsze', 'Następna strona', os.path.join(ptv.getAddonInfo('path'), "images/") +'nastepna_strona.png', match2[0][1], 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))        

    def listsFilmsSearch(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': True, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        print ("LINK",link)
        match = re.compile('<li  data-cat="(.*?)">\n\t\t\n\t\t\t\n\t\t\t\t<a href="(.*?)" target="_blank" class="image">\n\t\t\t\n\t\t\t\t\n\t\t\t\t\t\n\t\t\t\t\t\t<img src="(.*?)" alt="(.*?)" width="(.*?)" height="(.*?)" class="image" />', re.DOTALL).findall(link)
        print ("match",match)
        if len(match) > 0:
            for i in range(len(match)):
                #print match[i]
                url = match[i][1]
                #add(self, service, name,      category, title, iconimage, url, desc, rating, folder = True, isPlayable = True):
                self.add('wrzuta', 'playSelectedMovie', 'None', self.cm.html_special_chars(match[i][3]),   match[i][2], url, 'None', 'None', True, False)
        match2 = re.compile('<a class="paging-next" rel="(.*?)"\n\t\t\thref="(.*?)">', re.DOTALL).findall(link)
        if len(match2) > 0:  
            self.add('wrzuta', 'main-menu', 'Filmy - Szukaj', 'Następna strona', os.path.join(ptv.getAddonInfo('path'), "images/") +'nastepna_strona.png', match2[0][1], 'None', 'None', True, False,'Nastepna')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))        
        
        
    def listsitemsAudio(self,url):
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        #print ("LINK",link)
    #<a href="http://raptuss.wrzuta.pl/audio/9ICwJ2ec2ze/ewelina_lisowska_-_jutra_nie_bedzie" class="file-music-title">Ewelina Lisowska - Jutra nie będzie</a>
        match = re.compile('<div class="file-info">\n\t\t\t\t<a href="(.*?)" class="file-music-title">(.*?)</a>', re.DOTALL).findall(link)
        pl=xbmc.PlayList(1)
        pl.clear()
        if len(match) > 0:
            log.info('Listuje pliki: ')
            for i in range(len(match)):
                #print match[i]
                listitem = xbmcgui.ListItem( match[i][1].strip(), thumbnailImage='None')
                url = self.up.getVideoLink(match[i][0])
                listitem.setInfo( type="Audio", infoLabels={ "Title": match[i][1].strip() } )
                xbmc.PlayList(1).add(url, listitem)
	

	xbmc.Player().play(pl)
	return True

    def listsCategoriesMy(self,url):
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<div id="right" class="music">\n\n\t\n\t\t<div class="music-menu">(.*?)</div>', re.DOTALL).findall(link)
        if len(match) > 0:
            match1 = re.compile('<a href="(.*?)" class="music-position(.*?)">\n\t\t\t\t\t<i></i>\n\t\t\t\t\t<p>(.*?)</p>\n\t\t\t\t</a>', re.DOTALL).findall(match[0])
            #print ("match1",match1)
            for i in range(len(match1)):
                    url = match1[i][0]
                    self.add('wrzuta', 'items-audio','None',  self.cm.html_special_chars(match1[i][2]),'None', url, 'None', 'None', True, False)
            xbmcplugin.endOfDirectory(int(sys.argv[1])) 
        
    def getMovieLinkFromXML(self, url):
        linkVideo = self.up.getVideoLink(url)
        #print linkVideo 
        
        return linkVideo
        

    

    def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True,strona='None'):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage)+ "&strona=" + urllib.quote_plus(strona)
        log.info(str(u))
        if name == 'main-menu' or name == 'categories-menu':
            if title == 'None':
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
            
           # if not xbmc.Player().isPlaying():
           #     xbmc.sleep( 10000 )
                #xbmcPlayer.play(url, liz)
            
        except:
            d = xbmcgui.Dialog()
            d.ok('Błąd przy przetwarzaniu.', 'Problem')        
        return ok
        
    def searchInputText(self):
        text = None
        k = xbmc.Keyboard()
        k.doModal()
        if (k.isConfirmed()):
            text = k.getText()
        return text

    def handleService(self):
    	params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        strona = self.parser.getParam(params, "strona")
        print("MENU --------------- ",name,category,url,title,strona)
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Audio - Najnowsze':
            log.info('Jest Audio Najnowsze: '+url)
            self.listsCategoriesMenu(url)
        elif name == 'main-menu' and category == 'Filmy - Najnowsze':
            log.info('Jest Filmy Najnowsze: '+url)
            self.listsFilms(url)
        elif name == 'main-menu' and category == "Audio - Szukaj":
            if strona == 'None':
                key = self.searchInputText()
                url = 'http://www.wrzuta.pl/szukaj/audio/'+urllib.quote_plus(key)
            self.listsCategoriesSearch(url)
        elif name == 'main-menu' and category == "Filmy - Szukaj":
            if strona == 'None':
                key = self.searchInputText()
                url = 'http://www.wrzuta.pl/szukaj/filmow/'+urllib.quote_plus(key)
            self.listsFilmsSearch(url)
            
        elif name == 'main-menu' and category == 'Audio - Popularne':
            log.info('Jest Audio - Popularne: '+url)
            self.listsCategoriesMy(url)
        elif name == 'main-menu' and category == 'Moje konto':
            log.info('Jest Moje konto: ')
            self.login()
            self.listsCategoriesMy()            
        elif name == 'items-audio' and category == 'None':
            log.info('Jest Audio: url')
            self.listsitemsAudio(url)            
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.up.getVideoLink(url), title, icon)
        
  
