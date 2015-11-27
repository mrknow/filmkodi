# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs
import urlparser
import json,hashlib
import urlparse


scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - interia"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, libCommon, Parser, settings

log = mrknow_pLog.pLog()

mainUrl = 'http://www.interia.tv'
catUrl = mainUrl + 'ajax/pliki/edytuj'
loginUrl = 'https://ssl.interia.pl/zaloguj'


HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'

MENU_TAB = {1: ["Rozrywka"],
            2: ["Wiadomości"],
            3: ["Całkiem kobiece"],
            3: ["Typowo męskie"],
            4: ["Dla dzieci"],
            5: ["Hity internetu"]
 }

FUN_TAB = { 1: ["/rozrywka/teledyski", "Teledyski"],
            2: ["/rozrywka/imprezy", "Imprezy"],
            3: ["/rozrywka/zwiastuny","Zwiastuny"],
            4: ["/rozrywka/wywiady", "Wywiady"],
            5: ["/rozrywka/film","Film"],
            6: ["/rozrywka/zycie-gwiazd","Życie gwiazd"],
            7: ["/rozrywka/teatr","Teatr"],
            8: ["/rozrywka/literatura","Literatura"],
            9: ["/rozrywka/etiudy-filmowe","Etiudy filmowe"]
 }
NEWS_TAB = {    2: ["/wiadomosci/polska","Polska"],
                3: ["/wiadomosci/europa","Europa"],
                4: ["/wiadomosci/swiat","Świat"],
                5: ["/wosp","Wośp"]
 }

WMEN_TAB = {    2: ["/calkiem-kobiece/gotowanie","Gotowanie"],
                3: ["/calkiem-kobiece/zycie-gwiazd","Życie gwiazd"],
                4: ["/calkiem-kobiece/lifestyle","Lifestyle"],
                5: ["/calkiem-kobiece/moda","Moda"],
                6: ["/calkiem-kobiece/uroda","Uroda"]
                }
                
MEN_TAB = {    2: ["/typowo-meskie/motoryzacja","Motoryzacja"],
                3: ["/typowo-meskie/technologie","Technologie"],
                4: ["/typowo-meskie/biznes","Biznes"],
                5: ["/typowo-meskie/polityka","Polityka"],
                6: ["/typowo-meskie/sport","Sport"]
                }
KIDS_TAB = {    2: ["/dla-dzieci/teledyski","Teledyski"],
                3: ["/dla-dzieci/bajki","Bajki"]
                }
HIT_TAB = {    2: ["/hity-internetu","Hity internetu"],
                3: ["/top-tygodnia","Top tygodnia"],
                4: ["/top-miesiaca","Top miesiąca"]
                }
           

class interia:
    def __init__(self):
        log.info('Starting interia.pl')
        self.cm = libCommon.common()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()
        self.cm = libCommon.common()
        self.settings = settings.TVSettings()
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "interia.cookie"

    #  def add(self, service, name,    category, title, iconimage, url, desc, rating, folder = True, isPlayable = True):
    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('interia', 'main-menu', val[0], val[0], 'None','None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    def listsMain2Menu(self, table):
        for num, val in table.items():
            self.add('interia', 'category-menu', val[1], val[1] + ' - Najnowsze', 'None',val[0], 'None', 'None', True, False)
            self.add('interia', 'category-menu', val[1], val[1] + ' - Najczęściej oglądane', 'None',val[0] + '/top', 'None', 'None', True, False)
            
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

     
        
    def listsitems(self,url):
        id = url.split(",")
        query_data = {'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<section class="album-navigator">(.*?)</section>', re.DOTALL).findall(link)
        if len(match) > 0:
            match1 = re.compile('<a href="(.*?)" class="brief-thumbnail" title="(.*?)">\r\n                            <span class="item-wrap">\r\n                                <img src="(.*?)" alt="(.*?)" />', re.DOTALL).findall(match[0])
            if len(match1) > 0:
                for i in range(len(match1)):
                    print ("Match1",match1[i])
                    turl = match1[i][0].split(",")
                    tempurl = turl[0] + ',' + turl[1] + ',' + turl[2] 
                    self.add('interia', 'playSelectedMovie','None',  self.cm.html_special_chars(match1[i][1]),match1[i][2], mainUrl+tempurl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1])) 
        
    def listsCategoriesMy(self,url):
        print ("url",url)
        query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }        
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<li  \r\n                            class="brief-list-item(.*?)">(.*?)</li>\r\n', re.DOTALL).findall(link)
        #print ("Link",link)
        print ("match",match)
        #<li class="brief-list-item i1 iodd ifirstinrow">\r\n                            <section>\r\n    <div class="brief-video img-C426 brief-list-video" id="brief_11">\r\n        <header><div class="brief-header">\r\n                                    <div class="brief-details">\r\n                <strong class="brief-title">                    <a class="brief-title-link" href="/wideo-weekend-ona-tanczy-dla-mnie,vId,875811" title="Weekend - Ona Ta\xc5\x84czy Dla Mnie ">\r\n                        Weekend - Ona Ta\xc5\x84czy Dla Mnie <span class="video-age-rank-16"></span>                    </a>                    \r\n                </strong>                                    <div class="brief-description">\r\n                        <p class="description"><span></span></p>\r\n                        <p class="stat shows">Wy\xc5\x9bwietle\xc5\x84: \r\n                            <b>\r\n                                                                    154903                                                            \r\n                            </b>\r\n                        </p>\r\n                                            </div>\r\n                            </div>\r\n                                        <div class="brief-datetime">\r\n                    \xc5\x9aroda, 14 listopada 2012 (12:49)                </div>\r\n                    </div></header>\r\n                                                            <a href="/wideo-weekend-ona-tanczy-dla-mnie,vId,875811" class="brief-thumbnail">\r\n                    <img src="http://i3.ytimg.com/vi/JvxG3zl_WhU/hqdefault.jpg" alt="Weekend - Ona Ta\xc5\x84czy Dla Mnie " class="external youtube" />\r\n                    <span class="brief-play">Zobacz film</span>\r\n                </a>\r\n                        </div>\r\n</section>                        </li>
        match20 = re.compile('<li class="brief-list-item (.*?)">(.*?)</li>\r\n', re.DOTALL).findall(link)
        print ("match20",match20)
        
        if len(match) > 0:
            for i in range(len(match)):
                match1 = re.compile('<a href="(.*?)"(.*?)>\r\n                    <img src="(.*?)" alt="(.*?)"(.*?)/>', re.DOTALL).findall(match[i][1])
                match2 = re.compile('<a class="brief-thumbnail" href="(.*?)">\r\n                            <img class="brief-image" src="(.*?)" alt="(.*?)" />', re.DOTALL).findall(match[i][1])
                if len(match1) > 0:
                    self.add('interia', 'playSelectedMovie','None',  self.cm.html_special_chars(match1[0][3]),match1[0][2], mainUrl+match1[0][0], 'None', 'None', True, False)
                elif len(match2) > 0:
                    #print ("match2",match2)
                    self.add('interia', 'items-menu','None',  self.cm.html_special_chars(match2[0][2]),match2[0][1], mainUrl+match2[0][0], 'None', 'None', True, False)
        #<li class="next"><a href="/rozrywka/teledyski,nPack,2"><span>następne</span></a></li>
        if len(match20) > 0:
            for i in range(len(match20)):
                print match20[i][1]
                #<a href="/wideo-weekend-ona-tanczy-dla-mnie,vId,875811" class="brief-thumbnail">\r\n                    <img src="http://i3.ytimg.com/vi/JvxG3zl_WhU/hqdefault.jpg" alt="Weekend - Ona Ta\xc5\x84czy Dla Mnie " class="external youtube" />
                match1 = re.compile('<a href="(.*?)"(.*?)>\r\n                    <img src="(.*?)" alt="(.*?)"(.*?)/>', re.DOTALL).findall(match20[i][1])
                match2 = re.compile('<a class="brief-thumbnail" href="(.*?)">\r\n                            <img class="brief-image" src="(.*?)" alt="(.*?)" />', re.DOTALL).findall(match20[i][1])
                if len(match1) > 0:
                    self.add('interia', 'playSelectedMovie','None',  self.cm.html_special_chars(match1[0][3]),match1[0][2], mainUrl+match1[0][0], 'None', 'None', True, False)
                elif len(match2) > 0:
                    #print ("match2",match2)
                    self.add('interia', 'items-menu','None',  self.cm.html_special_chars(match2[0][2]),match2[0][1], mainUrl+match2[0][0], 'None', 'None', True, False)
        
        match10 = re.compile('<li class="next"><a href="(.*?)"><span>następne</span></a></li>').findall(link)
        if len(match10) > 0:
            log.info('Nastepna strona: '+  match10[0])
            self.add('interia', 'category-menu', 'Następna','Następna', 'None', match10[0], 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1])) 
        
    def getMovieLinkFromXML(self, url):
        id = url.split(",")
        #print ("IKLE",str(len(id)))
        if len(id)== 3:
            turl = 'http://www.interia.tv/getVideoInfo?id='+ id[-1]
            query_data = { 'url': turl, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }        
            link = self.cm.getURLRequestData(query_data)
            query_data = { 'url': url, 'use_host': False, 'use_cookie': False, 'use_post': False, 'return_data': True }        
            link1 = self.cm.getURLRequestData(query_data)
            #print ("Link1",link1)
            match1 = re.compile('<url_hi>(.*?)</url_hi>', re.DOTALL).findall(link)
            match2 = re.compile('<url_lo>(.*?)</url_lo>', re.DOTALL).findall(link)
            #<iframe width=\\\\"625\\\\" height=\\\\"377\\\\" src=\\\\"http:\\\\/\\\\/www.youtube.com\\\\/embed\\\\/OLQRPdWr098?hl=pl&fs=1&rel=0&wmode=opaque&autoplay=1\\\\" frameborder=\\\\"0\\\\" allowfullscreen wmode=\\\\"opaque\\\\"><\\\\/iframe>
            match3 = re.compile('iframe width=\\\\"625\\\\" height=\\\\"377\\\\" src=\\\\"(.*?)\\\\" frameborder=\\\\"0\\\\" allowfullscreen wmode=\\\\"opaque\\\\"><\\\\/iframe>', re.DOTALL).findall(link1)
            match4 = re.compile('var oembedData = {"html":"<iframe src=\\\\"(.*?)\\\\" width=\\\\"625\\\\" height=\\\\"377\\\\" frameborder=\\\\"0\\\\" allowfullscreen>', re.DOTALL).findall(link1)
            
            #print ("ILE3",str(len(match3)))
            #print ("match",match4,match3,match1,match2)
            if len(match1) > 0:
                linkVideo = match1[0]
            elif len(match2) > 0:
                linkVideo = match2[0]
            if len(match3) > 0:
                linkVideo = self.up.getVideoLink(match3[0].replace('\\',''))
                print ("LINK YOUTUBE",linkVideo) 
            if len(match4) > 0:
                req = urllib2.Request(match4[0].replace('\\',''))
                req.add_header('Referer', url)
                #req.add_header('User-Agent', HOST)
                response = urllib2.urlopen(req)
                link=response.read()
                response.close()
                #url_mp4: \'http://redir.atmcdn.pl/http/o2/TVN-Xnews/xlink/4f58cf5cb60fd0b7b6c3690d613c5dd9/2fdd5e52-3d6b-11e3-9414-0025b511226e.mp4?salt=5E2DF8AE0EB77CFD4B15B6BDEE42C7A7&token=DC71F411845370ACE8853D78D7E88434D8016B933A62C102357EDDB79C43861E6DB68825F0D2E102FA06FD7A364BC66CB4C29A361EBFA67326873DBE25DAF4D341798AFF758B647E493B10F1CBA5CBE46E52C7687B2DF0C74983D9706E84C53BAE341E0D94C84F12FF920FBEE278A9C6DF761A613FF8FB0928E45D7F96B00682\',
                tlinkVideo = re.compile("url_mp4: \'(.*?)\',", re.DOTALL).findall(link)
                linkVideo = tlinkVideo[0]
                #print ("LINK x-link",linkVideo) 
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
        elif name == 'main-menu' and category == 'Rozrywka':
            log.info('Rozrywka:')
            self.listsMain2Menu(FUN_TAB)
        elif name == 'main-menu' and category == 'Wiadomości':
            log.info('Rozrywka:')
            self.listsMain2Menu(NEWS_TAB)
        elif name == 'main-menu' and category == 'Całkiem kobiece':
            log.info('Rozrywka:')
            self.listsMain2Menu(WMEN_TAB)
        elif name == 'main-menu' and category == 'Typowo męskie':
            log.info('Rozrywka:')
            self.listsMain2Menu(MEN_TAB)
        elif name == 'main-menu' and category == 'Dla dzieci':
            log.info('Rozrywka:')
            self.listsMain2Menu(KIDS_TAB)
        elif name == 'main-menu' and category == 'Hity internetu':
            log.info('Rozrywka:')
            self.listsMain2Menu(HIT_TAB)
 
 
        elif name == 'category-menu':
            log.info('Jest KATEGORIA: ')
            #self.login()
            self.listsCategoriesMy(mainUrl+url)            
        elif name == 'items-menu' and category == 'None':
            log.info('Jest listsitems: url')
            self.listsitems(url)            
        if name == 'playSelectedMovie':
            self.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(url), title, icon)
        
  
