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
scriptname = "Filmy online www.mrknow.pl - vodpl"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, libCommon, Parser, Player

log = mrknow_pLog.pLog()

jsonurl = 'http://video.external.cms.onetapi.pl/'
imgurl = 'http://m.ocdn.eu/_m/'
mainUrl = 'http://www.vodpl.pl/m/'
playerUrl = 'http://www.youtube.pl/'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'
null = 0
true = 1

MENU_TAB = {2: "filmy",
            3: "polecamy",
            4: "dokumenty",
            5: "bajki",
            6: "seriale",
            7: "tv"}


class vodpl:
    def __init__(self):
        log.info('Starting vodpl.pl')
        self.cm = libCommon.common()
        self.parser = Parser.Parser()
        self.up = urlparser.urlparser()
        self.p = Player.Player()

    def getpage(self,data,url=jsonurl):
        header = {"Content-Type": "application/json-rpc","Accept": "application/json","X-Onet-App": "vod.ios.mobile-apps.onetapi.pl","User-Agent": "pl.vod.onet.pl/1.1 (unknown, iPhone OS 6.1.2, iPhone, Scale/2.000000)"}
        req = urllib2.Request(url, data, header)
        f = urllib2.urlopen(req)
        response = f.read()
        f.close() 
        #print ("GetPage Response",response)
        return response


    def listsMainMenu(self, table):
        for num, val in table.items():
            self.add('vodpl', 'main-menu', val, val, 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsSerialeMenu(self,category):
        valTab = [] 
        strTab = [] 
        if category == "seriale":
            #data = '{"method":"cmsQuery","id":"F165C38A-C2B7-4800-9D2D-4E5B30489639","jsonrpc":"2.0","params":{"sort":"DATE_DESC","method":"search","args":{"withoutDRM":"True","device":"mobile","payment":["-svod","-ppv"],"channel":"seriale"},"context":"onet/vod","range":[0,10000]}}'
            data = '{"method":"cmsQuery","id":"F165C38A-C2B7-4800-9D2D-4E5B30489639","jsonrpc":"2.0","params":{"sort":"DATE_DESC","method":"search","args":{"withoutDRM":"False","device":"mobile","payment":["svod","ppv"],"channel":"seriale"},"context":"onet/vod","range":[0,10000]}}'
            vod_filmy = eval(self.getpage(data))
            vod_filmy = eval(self.getpage(data))
        elif category == "tv":
            #data = '{"method":"cmsQuery","id":"F165C38A-C2B7-4800-9D2D-4E5B30489639","jsonrpc":"2.0","params":{"sort":"DATE_DESC","method":"search","args":{"withoutDRM":"True","device":"mobile","payment":["-svod","-ppv"],"channel":"tv"},"context":"onet/vod","range":[0,10000]}}'
            data = '{"method":"cmsQuery","id":"F165C38A-C2B7-4800-9D2D-4E5B30489639","jsonrpc":"2.0","params":{"sort":"DATE_DESC","method":"search","args":{"withoutDRM":"False","device":"mobile","payment":["svod","ppv"],"channel":"tv"},"context":"onet/vod","range":[0,10000]}}'
            vod_filmy = eval(self.getpage(data))


#        print vod_filmy
        for e in vod_filmy["result"]["data"]:
            strTab.append(self.cm.html_special_chars(e["seriesTitle"]))
            if 'poster' in e:
                image = imgurl + e['poster']["imageId"] + ',10,1.jpg'
            else:
                image = ''
            strTab.append(image)
            strTab.append(e["seriesId"])
            valTab.append(strTab)
            strTab = []
            valTab.sort(key = lambda x: x[0])
        for i in valTab:
            self.add('vodpl', 'seriale-menu', category, i[0], i[1], 'None', 'None', 'None', True, False,str(i[2]),i[2])
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self,category):
        valTab = [] 
        strTab = [] 
        if category == 'filmy':
            #data = '{"method":"cmsQuery","id":"A564F3E3-9074-4847-9C2A-8902B2B43B76","jsonrpc":"2.0","params":{"sort":"TITLE_ASC","method":"aggregates","args":{"withoutDRM":"True","device":"mobile","names":"genres","payment":["-svod","-ppv"],"channel":"filmy"},"context":"onet/vod"}}'
            data = '{"method":"cmsQuery","id":"A564F3E3-9074-4847-9C2A-8902B2B43B76","jsonrpc":"2.0","params":{"sort":"TITLE_ASC","method":"aggregates","args":{"withoutDRM":"False","device":"mobile","names":"genres","payment":["svod","ppv"],"channel":"filmy"},"context":"onet/vod"}}'
            vod_filmy = eval(self.getpage(data))
        elif category == "dokumenty":
            #data = '{"method":"cmsQuery","id":"CD01FEB2-201B-42F2-AB21-E380491F2AA6","jsonrpc":"2.0","params":{"sort":"TITLE_ASC","method":"aggregates","args":{"withoutDRM":"True","device":"mobile","names":"genres","payment":["-svod","-ppv"],"channel":"dokumenty"},"context":"onet/vod"}}'
            data = '{"method":"cmsQuery","id":"CD01FEB2-201B-42F2-AB21-E380491F2AA6","jsonrpc":"2.0","params":{"sort":"TITLE_ASC","method":"aggregates","args":{"withoutDRM":"False","device":"mobile","names":"genres","payment":["svod","ppv"],"channel":"dokumenty"},"context":"onet/vod"}}'
            vod_filmy = eval(self.getpage(data))
        elif category == "seriale":
            data = '{"method":"cmsQuery","id":"F165C38A-C2B7-4800-9D2D-4E5B30489639","jsonrpc":"2.0","params":{"sort":"DATE_DESC","method":"search","args":{"withoutDRM":"False","device":"mobile","payment":["svod","ppv"],"channel":"seriale"},"context":"onet/vod","range":[0,10000]}}'
            vod_filmy = eval(self.getpage(data))
        vod_filmy = eval(self.getpage(data))
        print ("VOD FILMY", vod_filmy["result"]["data"])
        for e in vod_filmy["result"]["data"][0]["items"]:
            strTab.append(self.cm.html_special_chars(e["name"]))
            strTab.append(e["value"])
            strTab.append(vod_filmy["id"])
            valTab.append(strTab)
            strTab = []
            valTab.sort(key = lambda x: x[0])
        for i in valTab:
            self.add('vodpl', 'categories-menu', category, i[0], 'None', 'None', 'None', 'None', True, False,str(i[1]),i[2])
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
    def getSearchURL(self, key):
        url = mainUrl + 'search.php?phrase=' + urllib.quote_plus(key) 
        return url
        #req = urllib2.Request(url)
        #req.add_header('User-Agent', HOST)
        #openURL = urllib2.urlopen(req)
        #readURL = openURL.read()
        

    def listsItems(self, category, title,id1='',id2=''):
        valTab = [] 
        strTab = [] 
        vod_getitems = '[{"method":"cmsQuery","id":"'+id2+'","jsonrpc":"2.0","params":{"sort":"DATE_DESC","method":"search","args":{"withoutDRM":"False","device":"mobile","payment":["svod","ppv"],"genre":"'+title+'","channel":"'+category+'"},"context":"onet/vod","range":[0,10000]}}]'
        if category == 'seriale':
            vod_getitems = ''
        vod_items = eval(self.getpage(vod_getitems))
        print ("vod_items",vod_items)
        for e in vod_items[0]["result"]["data"]:
            title = self.cm.html_special_chars(e["title"])
            if 'poster' in e:
                image = imgurl + e['poster']["imageId"] + ',10,1.jpg'
            else:
                image = ''
            strTab.append(self.cm.html_special_chars(e["title"]))
            strTab.append(image)
            strTab.append(e["videoId"])
            strTab.append(e["ckmId"])
            if 'year' in e.keys():
                strTab.append(str(e["year"]))
            else:
                strTab.append("1900")
            valTab.append(strTab)
            strTab = []
            valTab.sort(key = lambda x: x[0])
        for i in valTab:
            self.add('vodpl', 'playSelectedMovie', 'None', i[0], i[1], 'None', 'None', 'None', False, False,str(i[2]),i[3],i[4] )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems1(self, category,id1='',id2=''):
        valTab = [] 
        strTab = [] 
        if category == 'bajki':
            vod_getitems = '{"method":"cmsQuery","id":"8123F341-04FF-45D2-B16F-2DF5CB6801EA","jsonrpc":"2.0","params":{"sort":"DATE_DESC","method":"search","args":{"withoutDRM":"True","device":"mobile","noSeriesGroup":"True","payment":["-svod","-ppv"]},"context":"onet/bajki","range":[0,10000]}}'
            vod_items = eval(self.getpage(vod_getitems))
            for e in vod_items["result"]["data"]:
                title = self.cm.html_special_chars(e["title"])
                if 'poster' in e:
                    image = imgurl + e['poster']["imageId"] + ',10,1.jpg'
                else:
                    image = ''
                strTab.append(self.cm.html_special_chars(e["title"]))
                strTab.append(image)
                strTab.append(e["videoId"])
                strTab.append(e["ckmId"])
                
                valTab.append(strTab)
                strTab = []
                valTab.sort(key = lambda x: x[0])

        if category == 'polecamy':
            vod_getitems = '{"method":"cmsQuery","id":"70DC3E4B-3E1F-4FF5-AFDE-B5970A6FCF60","jsonrpc":"2.0","params":{"sort":"DEFAULT","method":"guideListsByType","args":{"type":"mobile-sg-polecane","guidelistView":"listitem"},"context":"onet/vod"}}'
            vod_items = eval(self.getpage(vod_getitems,'http://content.external.cms.onetapi.pl/')) 
#            print vod_items 
            for e in vod_items["result"]["data"][0]["contentLeads"]:
#                print e["title"]
#                print e['poster']["imageId"]
#                print e["videoId"]
#                print e["ckmId"]
                title = self.cm.html_special_chars(e["title"])
                if 'poster' in e:
                    image = imgurl + e['poster']["imageId"] + ',10,1.jpg'
                else:
                    image = ''
#                print e
                strTab.append(self.cm.html_special_chars(e["title"]))
                strTab.append(image)
                strTab.append(str(e["videoId"]))
                strTab.append(e["ckmId"])
                strTab.append(str(e["year"]))
                valTab.append(strTab)
                strTab = []
                valTab.sort(key = lambda x: x[0])
        if category == 'seriale':
            vod_getitems = '{"method":"cmsQuery","id":"9EA24AB8-4896-4F2E-87BC-1F5C6D1EC4C7","jsonrpc":"2.0","params":{"sort":"DATE_DESC","method":"episodes","args":{"withoutDRM":"True","device":"mobile","seriesId":"'+id1+'","payment":["-svod","-ppv"]},"context":"onet/vod","range":[0,10000]}}'
            vod_items = eval(self.getpage(vod_getitems))
            for e in vod_items["result"]["data"]:
                title = 'odc. '+ str(e["episode"]) + " - " + self.cm.html_special_chars(e["title"])
                if 'poster' in e:
                    image = imgurl + e['poster']["imageId"] + ',10,1.jpg'
                else:
                    image = ''
                strTab.append(title)
                strTab.append(image)
                strTab.append(e["videoId"])
                strTab.append(e["ckmId"])
                valTab.append(strTab)
                strTab = []
                valTab.sort(key = lambda x: x[0])
        if category == 'tv':
            vod_getitems = '{"method":"cmsQuery","id":"9EA24AB8-4896-4F2E-87BC-1F5C6D1EC4C7","jsonrpc":"2.0","params":{"sort":"DATE_DESC","method":"episodes","args":{"withoutDRM":"True","device":"mobile","seriesId":"'+id1+'","payment":["-svod","-ppv"]},"context":"onet/vod","range":[0,10000]}}'
            vod_items = eval(self.getpage(vod_getitems))
            for e in vod_items["result"]["data"]:
                title = 'odc. '+ str(e["episode"]) + " - " + self.cm.html_special_chars(e["title"])
                if 'poster' in e:
                    image = imgurl + e['poster']["imageId"] + ',10,1.jpg'
                else:
                    image = ''
                strTab.append(title)
                strTab.append(image)
                strTab.append(e["videoId"])
                strTab.append(e["ckmId"])
                valTab.append(strTab)
                strTab = []
                valTab.sort(key = lambda x: x[0])
        for i in valTab:
            if str(len(i)) > 4:
                i.append('0')
            self.add('vodpl', 'playSelectedMovie', 'None', i[0], i[1], 'None', 'None', 'None', False, False,i[2],i[3],i[4] )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
    def listsItemsPage(self, url):
        if not url.startswith("http://"):
            url = mainUrl + url
        if self.getSizeAllItems(url) > 0  and self.getSizeItemsPerPage(url) > 0:
            a = math.ceil(float(self.getSizeAllItems(url)) / float(self.getSizeItemsPerPage(url)))
            for i in range(int(a)):
                num = i + 1
                title = 'Lista ' + str(num)
                destUrl = url + sort_asc + '&page=' + str(num)
                self.add('vodpl', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))        


    def listsItemsSerialPage(self, url, sizeOfSerialParts):
        if not url.startswith("http://"):
            url = mainUrl + url
        if sizeOfSerialParts > 0  and self.getSizeItemsPerPage(url) > 0:
            a = math.ceil(float(sizeOfSerialParts) / float(self.getSizeItemsPerPage(url)))
            for i in range(int(a)):
                num = i + 1
                title = 'Lista ' + str(num)
                destUrl = url + sort_asc + '&page=' + str(num)
                self.add('vodpl', 'items-menu', 'None', title, 'None', destUrl, 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1])) 


    def getMovieLinkFromXML(self, id1,id2):
        #match = re.compile('<blockquote cite="(.*?)"', re.DOTALL).findall(link)
        #vod_item = '{"method":"cmsGet","id":"BAEAC0C3-1FC5-48D2-BC01-671AFC429C11","jsonrpc":"2.0","params":{"context":"onet/vod","id":"112363","object":"Video"}}'
        #response = self.getpage(vod_item)
        #url = 'http://vod.pl/'+id2+',d2dd64302895d26784c706717a1996b0.html?dv=aplikacja_iosVOD/filmy'
        url = 'http://qi.ckm.onetapi.pl/?callback=jQuery18301641132461372763_1362164907154&body[id]=EBBAE1E4326E4CE9343FFEEF56A9198D&body[jsonrpc]=2.0&body[method]=get_asset_detail&body[params][ID_Publikacji]='+id2+'&body[params][Service]=vod.onet.pl&content-type=application%2Fjsonp&x-onet-app=player.front.onetapi.pl&_=1362164913145'
        query_data = { 'url': url, 'use_host': True, 'host':'Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_2 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Mobile/10B146', 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        #link = 'jQuery18301641132461372763_1362164907154({"jsonrpc": "2.0", "result": {"0": {"playlist": [{"type": "movie", "format": "wideo"}], "meta": {"description": "<STRONG>&quot;Disco Robaczki&quot; to animowana komedia przygodowa dla ca\u0142ej rodziny w rytmie najwi\u0119kszych przeboj\u00f3w tanecznych! Tomasz Karolak, Zbigniew Wodecki, Agnieszka Chyli\u0144ska i Anna Mucha w polskiej wersji j\u0119zykowej filmu. </STRONG><br><br>\nD\u017cd\u017cownica Bogdan nie mo\u017ce pogodzi\u0107 si\u0119 z szar\u0105 egzystencj\u0105 pracownika fabryki kompostu. Pewnego dnia odkrywa w rzeczach taty zakurzon\u0105 p\u0142yt\u0119, odpala gramofon i doznaje ol\u015bnienia... Jego serce zawsze bi\u0142o w rytmie disco. Zak\u0142ada zesp\u00f3\u0142 i wraz z grup\u0105 przyjaci\u00f3\u0142, kt\u00f3rzy braki talentu nadrabiaj\u0105 ambicj\u0105, zg\u0142asza si\u0119 do udzia\u0142u w konkursie wokalnym.<br><br>\nBogdan i jego rozbujane Disco Robaczki - Gocha, Tytus, Nerwal i Kadrowa Danuta - zrobi\u0105 wszystko, \u017ceby udowodni\u0107 jurorom i ca\u0142emu \u015bwiatu, \u017ce... d\u017cd\u017cownice s\u0105 gor\u0105ce i nie ma haka na robaka! Zanim spe\u0142ni\u0105 si\u0119 ich marzenia - czeka je ca\u0142e mn\u00f3stwo szalonych przyg\u00f3d, w tym spotkanie oko w haczyk z gro\u017anym w\u0119dkarzem, uwi\u0119zienie przez zbieracza \u017cywej przyn\u0119ty i konfrontacja z robalami-gorylami dyrektora Pastewnego.<br><br>\nObok komicznych i trzymaj\u0105cych w napi\u0119ciu perypetii sympatycznych bohater\u00f3w, nieocenionym walorem tego filmu jest muzyka. Widzowie us\u0142ysz\u0105 najwi\u0119ksze hity lat 70., mi\u0119dzy innymi <STRONG>&quot;Disco Inferno&quot;</STRONG>, <STRONG>&quot;YMCA&quot;</STRONG>, <STRONG>&quot;I Will Survive&quot;</STRONG> w ca\u0142kowicie nowych, wsp\u00f3\u0142czesnych wykonaniach.", "reference": "OnetDB-7854:856:403", "tags": ["film", "disco", "muzyka", "konkurs", "rywalizacja", "animacja"], "lenght": 4510, "OID_CKM_Media": 35150, "UUID": "fff4ab1f-cb26-4dcc-8a56-5ebc031119de", "service": "vod", "title": "Disco Robaczki", "addDate": "2012-10-01 09:09:00", "OID": "351763026", "ID_Publikacji": "351763026", "drm": "{\"PlayReady\": \"NFvdzPg5G0S0UwiWMn+ipw==\"}", "licenseurl": "/351763026,2013030213151362226514,drmlicense.xml", "nobanner": 0, "image": "5a494526d403f1ad5e3756cb12f572c1.jpg"}, "license": {"service": 1, "geoIP": 1, "allowedEmmisionDevices": {"mobile": 1, "PC": 1, "TV": 1, "Lajt": 1}, "period": 1, "source": {"name": "Kino \u015awiat", "copyright": "", "url": "", "text": "", "imageUrl": "", "providerLogo": {"position": "", "imageUrl": ""}}, "adult": 0}, "formats": {"wideo": {"ismc": [{"url": "http://media.onet.pl/vod/7072407_11_350_14088_0000.ism/Manifest", "video_bitrate": null, "audio_bitrate": null}], "mp4": [{"url": "http://media.onet.pl/_mv/aIvtLxlfoQ.d.mp4", "video_bitrate": "200.00", "audio_bitrate": "128.00"}, {"url": "http://media.onet.pl/_mv/aIvtLxlfoQ.c.mp4", "video_bitrate": "450.00", "audio_bitrate": "128.00"}, {"url": "http://media.onet.pl/_mv/aIvtLxlfoQ.b.mp4", "video_bitrate": "900.00", "audio_bitrate": "128.00"}, {"url": "http://media.onet.pl/_mv/aIvtLxlfoQ.a.mp4", "video_bitrate": "1800.00", "audio_bitrate": "128.00"}]}}}}, "id": "EBBAE1E4326E4CE9343FFEEF56A9198D"});'
        #{"url": "http://media.onet.pl/_mv/YcnPH7o2pO.d.mp4", "video_bitrate": "200.00", "audio_bitrate": "128.00"}
        match1 = re.compile('"mp4": \[\{(.*?)\}\]', re.DOTALL).findall(link)
        match2 = re.compile('"url": "(.*?)", "video_bitrate": "(.*?)", "audio_bitrate": "(.*?)"', re.DOTALL).findall(match1[0])
        
        tab = []
        for i in range(len(match2)):
            tab.append('Wideo bitrate - ' + match2[i][1])
            
        d = xbmcgui.Dialog()        
        video_menu = d.select("Wybór jakości video", tab)

        if video_menu != "":
            #print match2[video_menu][0]
            url = match2[video_menu][0]
            return url
            
          



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
    
    
    def getSizeItemsPerPage(self, url):
        numItemsPerPage = 0
        openURL = urllib.urlopen(url)
        readURL = openURL.read()
        openURL.close()
        match = re.compile('<div class="movie-(.+?)>').findall(readURL)
        if len(match) > 0:
            numItemsPerPage = len(match)
        return numItemsPerPage        

    def getMovieID(self, url):
        id = 0
        tabID = url.split(',')
        if len(tabID) > 0:
            id = tabID[1]
        return id


    def getItemTitles(self, table):
        out = []
        for i in range(len(table)):
            value = table[i]
            out.append(value[1])
        return out

    def getItemURL(self, table, key):
        link = ''
        for i in range(len(table)):
            value = table[i]
            if key in value[0]:
                link = value[2]
                break
        return link


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
#        print ("ID",category,id1,id2, params,year)
        
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'filmy':
            log.info('Jest Filmy: ')
            self.listsCategoriesMenu(category)
        elif name == 'main-menu' and category == 'seriale':
            log.info('Jest Seriale: ')
            self.listsSerialeMenu(category)
        elif name == 'main-menu' and category == 'dokumenty':
            log.info('Jest dokumenty: ')
            self.listsCategoriesMenu(category)
        elif name == 'main-menu' and category == 'bajki':
            log.info('Jest bajki: ')
            self.listsItems1('bajki')
        elif name == 'main-menu' and category == 'polecamy':
            log.info('Jest polecamy: ')
            self.listsItems1('polecamy')
        elif name == 'main-menu' and category == 'tv':
            log.info('Jest polecamy: ')
            self.listsSerialeMenu('tv')
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            self.listsItems(self.getSearchURL(key))
        elif name == 'categories-menu' and category != 'None':
            print ("Dane",category,title,id1,id2)
            self.listsItems(category,title,id1,id2)
        elif name == 'seriale-menu' and category != 'None':
            print ("Seriale items",category,title,id1,id2)
            self.listsItems1(category,id1,id2)

        if name == 'playSelectedMovie':
            self.p.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(id1,id2), title, icon, year)
        if name == 'playselectedmovie':
            self.p.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(id1,id2), title, icon, year)

        
  
