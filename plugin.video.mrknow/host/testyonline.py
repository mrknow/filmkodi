# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from BeautifulSoup import BeautifulSoup
import  urllib
import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_Player, mrknow_Pageparser

scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - testyonline"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

mainUrl = 'http://testyonline.com'

MENU_TAB = {1: "Ostatnio dodane",
            10: "Spis",
            #4: "Szukaj"
            }


class testyonline:
    def __init__(self):
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.pp1 = mrknow_Pageparser.mrknow_Pageparser()
        self.player = mrknow_Player.mrknow_Player()
        self.log = mrknow_pLog.pLog()
        self.log.info('Starting testyonline.pl')
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "cdapl.cookie"


    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('testyonline', 'main-menu', val, 'None', 'None', 'None', 'None', 'None', True, False)
        HEADER1 = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                  'Referer': 'http://yoy.tv/',
                  'User-Agent': self.cm.randomagent(),
                  }
        query_data = { 'url': 'http://yoy.tv/signin', 'use_host': False, 'use_header': False, 'use_cookie': True, 'save_cookie': True, 'load_cookie': False, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match = re.compile('<input name="_token" type="hidden" value="(.*?)">', re.DOTALL).findall(link)
        #if len(match) > 0:
        if 1==2:
            self.log('Mam token %s' % match[0])
            HEADER2 = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
                      'Referer': 'http://yoy.tv/signin',
                      'User-Agent': self.cm.randomagent(),
                      'Content-Type':"application/x-www-form-urlencoded"}
            query_data = { 'url': 'http://yoy.tv/signin', 'use_host': False, 'use_header': True, 'header': HEADER2, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True, 'cookiefile': self.COOKIEFILE,  'use_post': True, 'return_data': True }
            post_data = {'_token': match[0],
                         'email': 'mrknow@interia.pl',
                         'password':'westwest',
                         'remember_me': '1'}
            link = self.cm.getURLRequestData(query_data,post_data)
            #self.log(link)

        query_data = { 'url': 'http://yoy.tv/channels/272', 'use_host': False,  'use_header': True, 'header': HEADER1, 'use_cookie': True, 'save_cookie': True, 'load_cookie': True, 'cookiefile': self.COOKIEFILE, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile('<param name=FlashVars value="cid=(.*?)&fms=rtmp://(.*?)/yoy&email=(.*?)&secret=(.*?)&hash=(.*?)&bn=(.*?)&sb=(.*?)"/>', re.DOTALL).findall(link)
        #self.log('my %s' % match1)
        #<link>rtmp://94.242.228.188/yoy/_definst_/ playpath=272?hash=$doregex[hash] conn=S:OK swfUrl=http://yoy.tv/playerv3.swf flashVer=WIN\2020,0,0,228 swfVfy=1 live=1 timeout=13 pageUrl=http://yoy.tv/channels/272</link>
        #<page>http://yoy.tv/channels/272</page>
        #<referer>http://yoy.tv/</referer>
        #<agent>Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36</agent>
        #myurl = 'rtmp://'+match1[0][1]+'/yoy/_definst_/ playpath='+match1[0][0]+'?hash='+match1[0][4]+'& conn=S:OK swfUrl=http://yoy.tv/playerv3.swf flashVer=WIN\2020,0,0,228 swfVfy=1 live=1 timeout=13 pageUrl=http://yoy.tv/channels/272|Referer=http://yoy.tv/channels/272'
        #myurl = 'rtmp://'+match1[0][1]+'/yoy/_definst_/ playpath='+match1[0][0]+'?hash='+match1[0][4]+'&email=mrknow@interia.pl&secret='+match1[0][3]+' conn=S:OK swfUrl=http://yoy.tv/playerv3.swf flashVer=WIN\2020,0,0,228 swfVfy=1 live=1 timeout=13 pageUrl=http://yoy.tv/channels/272|Referer=http://yoy.tv/playerv3.swf'
        #myurl = 'rtmp://'+match1[0][1]+'/yoy/_definst_/'+match1[0][0]+'?hash='+match1[0][4]+' conn=S:OK swfUrl=http://yoy.tv/playerv3.swf flashVer=WIN\2020,0,0,228 swfVfy=1 live=1 timeout=13 pageUrl=http://yoy.tv/channels/272|Referer=http://yoy.tv/channels/272'
        #myurl = 'rtmp://'+match1[0][1]+'/yoy/_definst_/'+match1[0][0]+'?hash='+match1[0][4]+'&email=mrknow@interia.pl&secret='+match1[0][3]+' conn=B:0 swfUrl=http://yoy.tv/playerv3.swf swfVfy=1 live=1 timeout=13 pageUrl=http://yoy.tv/channels/272'
        #myurl = 'rtmp://'+match1[0][1]+'/yoy/_definst_ playpath='+match1[0][0]+'?hash='+match1[0][4]+'&email=mrknow%40interia.pl&secret='+match1[0][3]+' flashVer="LNX\ 20,0,0,306" swfUrl="http://yoy.tv/playerv3.swf" pageUrl="http://yoy.tv/channels/272" swfVfy=1 live=1 timeout=13 conn=B:0'
        #hash='+match1[0][4]+'&email=mrknow@interia.pl&secret='+match1[0][3]+' conn=B:0 swfUrl=http://yoy.tv/playerv3.swf swfVfy=1 live=1 timeout=13 pageUrl=http://yoy.tv/channels/272
        #myurl = 'rtmp://'+match1[0][1]+'/yoy/_definst_/ playpath='+match1[0][0]+'?hash='+match1[0][4]+'&email=mrknow%40interia.pl&secret='+match1[0][3]+'&bn=Rozpocznij&sb=Zatrzymaj flashVer=LNX\20,0,0,306 conn=S:OK swfUrl=http://yoy.tv/playerv3.swf swfVfy=1 live=1 timeout=13 pageUrl=http://yoy.tv/channels/272|Referer=http://yoy.tv/playerv3.swf'
        #<param name=FlashVars value="cid=272&fms=rtmp://94.242.228.182/yoy&email=mrknow@interia.pl&secret=VxBa4DX3giANAOtp089K0mwdjd4xUE&hash=ZsUozyMq85sSIDsTSx7WKl89eewo9rWE2xX31Taj&bn=Rozpocznij transmisję!&sb=Zatrzymaj transmisję"/>
        #myurl = 'rtmp://'+match1[0][1]+'/yoy/_definst_/ playpath='+match1[0][0]+'?hash='+match1[0][4]+'&email=mrknow%40interia.pl&secret='+match1[0][3]+'&bn=Rozpocznij&sb=Zatrzymaj flashVer=LNX\20,0,0,306 conn=S:OK swfUrl=http://yoy.tv/playerv3.swf swfVfy=1 live=1 timeout=13 pageUrl=http://yoy.tv/channels/272|Referer=http://yoy.tv/playerv3.swf'
        #myurl = 'rtmp://'+match1[0][1]+'/yoy/_definst_/'+match1[0][0]+' conn=S:authenticate conn=S:email:mrknow%40interia.pl conn=S:hash:'+match1[0][4]+' conn=S:cid conn=S:272 conn=S:secret conn=S:'+match1[0][3]+' flashVer=LNX\20,0,0,306 swfUrl=http://yoy.tv/playerv3.swf swfVfy=1 live=1 timeout=13 pageUrl=http://yoy.tv/channels/272'
        #str1 = "0xfb00009d1402000c6175746865".decode("hex")
        #yurl = 'rtmp://'+match1[0][1]+'/yoy/_definst_/'+match1[0][0]+' ccommand='+str1+'.............email...mrknow@interia.pl..hash..'+match1[0][4]+'..cid...272..secret...'+match1[0][3]+'... flashVer=LNX\20,0,0,306 swfUrl=http://yoy.tv/playerv3.swf swfVfy=1 live=1 timeout=13 pageUrl=http://yoy.tv/channels/272'
        """
        var func1 = ["\x6A\x20\x6E\x28\x61\x29\x7B\x74\x28\x61\x29\x7B\x33\x22\x63\x22\x3A\x32\x22\x67\x22\x3B\x33\x22\x64\x22\x3A\x32\x22\x61\x22\x3B\x33\x22\x61\x22\x3A\x32\x22\x64\x22\x3B\x33\x22\x67\x22\x3A\x32\x22\x63\x22\x3B\x33\x22\x73\x22\x3A\x32\x22\x39\x22\x3B\x33\x22\x68\x22\x3A\x32\x22\x62\x22\x3B\x33\x22\x62\x22\x3A\x32\x22\x68\x22\x3B\x33\x22\x39\x22\x3A\x32\x22\x73\x22\x3B\x33\x22\x65\x22\x3A\x32\x22\x36\x22\x3B\x33\x22\x35\x22\x3A\x32\x22\x38\x22\x3B\x33\x22\x38\x22\x3A\x32\x22\x35\x22\x3B\x33\x22\x36\x22\x3A\x32\x22\x65\x22\x3B\x33\x22\x66\x22\x3A\x32\x22\x6D\x22\x3B\x33\x22\x6D\x22\x3A\x32\x22\x66\x22\x3B\x33\x22\x69\x22\x3A\x32\x22\x37\x22\x3B\x33\x22\x37\x22\x3A\x32\x22\x69\x22\x3B\x33\x22\x6B\x22\x3A\x32\x22\x34\x22\x3B\x33\x22\x34\x22\x3A\x32\x22\x6B\x22\x3B\x33\x22\x2E\x22\x3A\x32\x22\x6C\x22\x3B\x33\x22\x6C\x22\x3A\x32\x22\x2E\x22\x3B\x75\x3A\x32\x20\x61\x7D\x7D\x6A\x20\x70\x28\x61\x29\x7B\x62\x3D\x22\x22\x3B\x6F\x28\x69\x3D\x30\x3B\x69\x3C\x61\x2E\x71\x3B\x69\x2B\x2B\x29\x7B\x63\x3D\x6E\x28\x61\x2E\x72\x28\x69\x2C\x31\x29\x29\x3B\x62\x2B\x3D\x63\x7D\x32\x20\x62\x7D", "\x7C", "\x73\x70\x6C\x69\x74", "\x7C\x7C\x72\x65\x74\x75\x72\x6E\x7C\x63\x61\x73\x65\x7C\x7C\x45\x7C\x5A\x7C\x78\x7C\x7A\x7C\x42\x7C\x7C\x7C\x7C\x43\x7C\x7C\x7C\x41\x7C\x53\x7C\x7C\x66\x75\x6E\x63\x74\x69\x6F\x6E\x7C\x76\x7C\x7C\x7C\x70\x61\x72\x73\x65\x53\x74\x72\x7C\x66\x6F\x72\x7C\x63\x68\x65\x63\x6B\x53\x74\x72\x7C\x6C\x65\x6E\x67\x74\x68\x7C\x73\x75\x62\x73\x74\x72\x7C\x7C\x73\x77\x69\x74\x63\x68\x7C\x64\x65\x66\x61\x75\x6C\x74", "\x72\x65\x70\x6C\x61\x63\x65", "", "\x5C\x77\x2B", "\x5C\x62", "\x67"];
		eval(function(funcp1, funca1, funcc1, funck1, funce1, funcd1) {
		    funce1 = function(funcc1) {
		        return funcc1.toString(36)
		    };
		    if (!func1[5][func1[4]](/^/, String)) {
		        while (funcc1--) {
		            funcd1[funcc1.toString(funca1)] = funck1[funcc1] || funcc1.toString(funca1)
		        };
		        funck1 = [function(funce1) {
		            return funcd1[funce1]
		        }];
		        funce1 = function() {
		            return func1[6]
		        };
		        funcc1 = 1
		    };
		    while (funcc1--) {
		        if (funck1[funcc1]) {
		            funcp1 = funcp1[func1[4]](new RegExp(func1[7] + funce1(funcc1) + func1[7], func1[8]), funck1[funcc1])
		        }
		    };
		    return funcp1
		}(func1[0], 31, 31, func1[3][func1[2]](func1[1]), 0, {}));
        """
        #self.add('testyonline', 'playSelectedMovie', 'None', 'Yoy play', 'None', myurl, 'aaaa', 'None', False, True)

        myurl2 = 'rtmp://144.76.154.14/live/ swfUrl=http://cyberms.pl/onlinetv/jwplayer.flash.swf swfVfy=1 live=1 timeout=13 pageUrl=http://cyberms.pl/onlinetv/tvn-24.html playpath=tvn24'
        self.add('testyonline', 'playSelectedMovie', 'None', 'Cyberms', 'None', myurl2, 'aaaa', 'None', False, True)
        myurl3 = 'rtmp://144.76.154.14/live/ swfUrl=http://cyberms.pl/onlinetv/jwplayer.flash.swf swfVfy=1 live=1 timeout=13 pageUrl=http://cyberms.pl/onlinetv/tvn-24.html playpath=tvp1'
        self.add('testyonline', 'playSelectedMovie', 'None', 'Cyberms', 'None', myurl3, 'aaaa', 'None', False, True)
        myurl4 = 'http://n-1-30.dcs.redcdn.pl/dcs/o2/tvnplayer/vod/04_350_05812_0000/WIDEVINE_TV_HD/84dfd235-5528-4099-9816-420919f01725/hd.wvm'
        self.add('testyonline', 'playSelectedMovie2', 'None', 'Widevine', 'None', myurl4, 'aaaa', 'None', False, True)

        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def getSearchURL(self, key):
        url = urllib.quote_plus(key)
        return url

    def listsCategoriesMenu(self, url):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://testyonline.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': 'http://testyonline.com/', 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost1 = soup.find('div', {"id": "sidebar"})
        linki_all1 = linki_ost1.findAll('li')
        for mylink in linki_all1:
            print("m",mylink.a.text,mylink.a['href'])
            self.add('testyonline', 'categories-menu', self.cm.html_special_chars(mylink.a.text.encode('utf-8')),'None', 'None', mylink.a['href'], 'aaaa', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems(self,url):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://testyonline.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': url, 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost = soup.find('div', {"class": "post_ajax_tm"})
        if linki_ost:
            linki_all = linki_ost.findAll('div', {"class": "item-thumbnail"})
            for mylink in linki_all:
                self.add('testyonline', 'playSelectedMovie', 'None', self.cm.html_special_chars(mylink.img['title'].encode('utf-8')), mylink.img['src'], mylink.a['href'], 'aaaa', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems2(self, url):
        HEADER = {'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3', 'Referer': 'http://testyonline.com/', 'User-Agent': self.cm.randomagent()}
        query_data = { 'url': 'http://testyonline.com/', 'use_host': False, 'use_host': False, 'use_header': True, 'header': HEADER, 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        soup = BeautifulSoup(link)
        linki_ost = soup.find('div', {"class": "carousel-content"})
        if linki_ost:
            linki_all = linki_ost.findAll('div', {"class": "item-thumbnail"})
            for mylink in linki_all:
                self.add('testyonline', 'playSelectedMovie', 'None', self.cm.html_special_chars(mylink.text.encode('utf-8')), mylink.img['src'], mylink.a['href'], 'aaaa', 'None', False, True)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

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
            
    def LOAD_AND_PLAY_VIDEO(self, videoUrl, title='', icon=''):
        ok=True
        if videoUrl == '':
                d = xbmcgui.Dialog()
                d.ok('Nie znaleziono streamingu.', 'Może to chwilowa awaria.', 'Spróbuj ponownie za jakiś czas')
                return False
        liz=xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon, path=videoUrl)
        liz.setInfo( type="Video", infoLabels={ "Title": title, } )
        try:
            xbmcPlayer = xbmc.Player()
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

        except:
            d = xbmcgui.Dialog()
            d.ok('Błąd przy przetwarzaniu.', 'Problem')
        return ok

    #eval(unescape((unescape('%72%74%66%70%3a%2f%2f%31%38%35%6c%31%30%30%6c%38%36%6c%31%30%76%2f%2e%78%34%5a%2f%68%53%6f')));
    ##varQpxMFIrptItrBhlOdHyIuFGOtpwUtrefNbNWXjAYRDa=unescape(checkStr(unescape('%66%6b%4d%53%61%6d%34%6f%79%51%46%39%32%70%62%39%62%61%42%5a%76%37%2e%59%6d%6b%2b%38%4c%37%52%2e%46%47%67%43%7a%5a%36%6f%35%72%38%3d')));'));
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
        print("category", category)
        print("url", url)
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Ostatnio dodane':
            self.listsItems2(mainUrl)
        elif name == 'main-menu' and category == "Spis":
            self.listsCategoriesMenu(mainUrl)

        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems2('http://testyonline.tv/szukaj', self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            self.listsItems(url)
        if name == 'playSelectedMovie':
            self.log.info('url: ' + str(url))
            #mojeurl = self.pp1.getVideoLink(url)
            self.player.LOAD_AND_PLAY_VIDEO(url,'','')
        if name == 'playSelectedMovie2':
            self.log.info('url: ' + str(url))
            #mojeurl = self.pp1.getVideoLink(url)
            self.LOAD_AND_PLAY_VIDEO(url)

        
  
