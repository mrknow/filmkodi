# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin

try:
    import simplejson as json
except ImportError:
    import json

scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - vodpl"
ptv = xbmcaddon.Addon(scriptID)

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_Player, mrknow_urlparser

log = mrknow_pLog.pLog()

jsonurl = 'http://video.external.cms.onetapi.pl/'
imgurl = 'http://m.ocdn.eu/_m/'
mainUrl = 'http://www.vodpl.pl/m/'
playerUrl = 'http://www.youtube.pl/'

HOST = 'Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543 Safari/419.3'
null = 0
true = 1

MENU_TAB = {2: "Filmy",
            3: "Polecamy",
            4: "Dokumenty",
            5: "Bajki",
            6: "Seriale",
            7: "TV"
}


class vodpl:
    def __init__(self):
        log.info('Starting vodpl.pl')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.p = mrknow_Player.mrknow_Player()

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
        if category == "Seriale":
            #data = '{"method":"cmsQuery","id":"F165C38A-C2B7-4800-9D2D-4E5B30489639","jsonrpc":"2.0","params":{"sort":"DATE_DESC","method":"search","args":{"withoutDRM":"True","device":"mobile","payment":["-svod","-ppv"],"channel":"seriale"},"context":"onet/vod","range":[0,10000]}}'
            data = '{"method":"cmsQuery","id":"F165C38A-C2B7-4800-9D2D-4E5B30489639","jsonrpc":"2.0","params":{"sort":"DATE_DESC","method":"search","args":{"withoutDRM":"False","device":"mobile","payment":["svod","ppv"],"channel":"seriale"},"context":"onet/vod","range":[0,10000]}}'
            vod_filmy = eval(self.getpage(data))
            vod_filmy = eval(self.getpage(data))
        elif category == "TV":
            #data = '{"method":"cmsQuery","id":"F165C38A-C2B7-4800-9D2D-4E5B30489639","jsonrpc":"2.0","params":{"sort":"DATE_DESC","method":"search","args":{"withoutDRM":"True","device":"mobile","payment":["-svod","-ppv"],"channel":"tv"},"context":"onet/vod","range":[0,10000]}}'
            data = '{"method":"cmsQuery","id":"F165C38A-C2B7-4800-9D2D-4E5B30489639","jsonrpc":"2.0","params":{"sort":"DATE_DESC","method":"search","args":{"withoutDRM":"False","device":"mobile","payment":["svod","ppv"],"channel":"tv"},"context":"onet/vod","range":[0,10000]}}'
            vod_filmy = eval(self.getpage(data))



        for e in vod_filmy["result"]["data"]:
            #log.info('vod: %s' % e)
            try:
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
            except:
                pass
        for i in valTab:
            self.add('vodpl', 'seriale-menu', category, i[0], i[1], 'None', 'None', 'None', True, False,str(i[2]),i[2])
        xbmcplugin.endOfDirectory(int(sys.argv[1]))


    def listsCategoriesMenu(self,category):
        valTab = [] 
        strTab = [] 
        if category == 'Filmy':
            #data = '{"method":"cmsQuery","id":"A564F3E3-9074-4847-9C2A-8902B2B43B76","jsonrpc":"2.0","params":{"sort":"TITLE_ASC","method":"aggregates","args":{"withoutDRM":"True","device":"mobile","names":"genres","payment":["-svod","-ppv"],"channel":"filmy"},"context":"onet/vod"}}'
            data = '{"method":"cmsQuery","id":"A564F3E3-9074-4847-9C2A-8902B2B43B76","jsonrpc":"2.0","params":{"sort":"TITLE_ASC","method":"aggregates","args":{"withoutDRM":"False","device":"mobile","names":"genres","payment":["svod","ppv"],"channel":"filmy"},"context":"onet/vod"}}'
            vod_filmy = eval(self.getpage(data))
        elif category == "Dokumenty":
            #data = '{"method":"cmsQuery","id":"CD01FEB2-201B-42F2-AB21-E380491F2AA6","jsonrpc":"2.0","params":{"sort":"TITLE_ASC","method":"aggregates","args":{"withoutDRM":"True","device":"mobile","names":"genres","payment":["-svod","-ppv"],"channel":"dokumenty"},"context":"onet/vod"}}'
            data = '{"method":"cmsQuery","id":"CD01FEB2-201B-42F2-AB21-E380491F2AA6","jsonrpc":"2.0","params":{"sort":"TITLE_ASC","method":"aggregates","args":{"withoutDRM":"False","device":"mobile","names":"genres","payment":["svod","ppv"],"channel":"dokumenty"},"context":"onet/vod"}}'
            vod_filmy = eval(self.getpage(data))
        elif category == "Seriale":
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
        if category == 'Seriale':
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
            self.add('vodpl', 'playSelectedMovie', 'None', i[0], i[1], 'None', 'None', 'None', False, True,str(i[2]),i[3],i[4] )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems1(self, category,id1='',id2=''):
        valTab = [] 
        strTab = [] 
        if category == 'Bajki':
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

        if category == 'Polecamy':
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
        if category == 'Seriale':
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
        if category == 'TV':
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
            self.add('vodpl', 'playSelectedMovie', 'None', i[0], i[1], 'None', 'None', 'None', False, True,i[2],i[3],i[4] )
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
        url = 'http://qi.ckm.onetapi.pl/?callback=jQuery18301641132461372763_1362164907154&body[id]=EBBAE1E4326E4CE9343FFEEF56A9198D&body[jsonrpc]=2.0&body[method]=get_asset_detail&body[params][ID_Publikacji]='+id2+'&body[params][Service]=vod.onet.pl&content-type=application%2Fjsonp&x-onet-app=player.front.onetapi.pl&_=1362164913145'
        query_data = { 'url': url, 'use_host': True, 'host':'Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_2 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Mobile/10B146', 'use_cookie': False, 'use_post': False, 'return_data': True }
        link = self.cm.getURLRequestData(query_data)
        match1 = re.compile('\((.*?)\)', re.DOTALL).findall(link)
        #log.info("Mydata %s" % match1)
        tab = []
        tab2 = []
        if len(match1)>0:
            d = json.loads(match1[0])
            log.info("Mydata d: %s" % d['result'])
            try:
                for i in d['result']['0']['formats']['wideo']['mp4']:
                    tab2.append(i['url'])
                    log.info("1: %s " % i['url'])
                    tab.append('Wideo bitrate - ' + i['video_bitrate'])
                    log.info("2: %s:" % i['video_bitrate'])
            except:
                pass

            log.info("Mydata d: %s" % d['result']['0']['formats']['wideo']['mp4'])

            
        d = xbmcgui.Dialog()        
        video_menu = d.select("Wybór jakości video", tab)

        if video_menu != "":
            #print match2[video_menu][0]
            url = tab2[video_menu]
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
            
    def LOAD_AND_PLAY_VIDEO(self, videoUrl, title, icon):
        ok=True
        log.info("VideoUrl: %s" % videoUrl)
        if videoUrl == 'NONE':
            return False

        if videoUrl == '':
                d = xbmcgui.Dialog()
                d.ok('Nie znaleziono streamingu.', 'Może to chwilowa awaria.', 'Spróbuj ponownie za jakiś czas')
                return False
        liz=xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon, path=videoUrl )
        liz.setInfo( type="video", infoLabels={ "Title": title} )
        xbmcPlayer = xbmc.Player()

        try:
            xbmcPlayer = xbmc.Player()
            #xbmcPlayer.play(videoUrl, liz)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

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
        id1 = self.parser.getParam(params, "id1")
        id2 = self.parser.getParam(params, "id2")
        year = self.parser.getParam(params, "year")
        log.info ("URL: %s name %s: category: %s" % (url,name,category))
        
        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Filmy':
            log.info('Jest Filmy: ')
            self.listsCategoriesMenu(category)
        elif name == 'main-menu' and category == 'Seriale':
            log.info('Jest Seriale: ')
            self.listsSerialeMenu(category)
        elif name == 'main-menu' and category == 'Dokumenty':
            log.info('Jest dokumenty: ')
            self.listsCategoriesMenu(category)
        elif name == 'main-menu' and category == 'Bajki':
            log.info('Jest bajki: ')
            self.listsItems1('Bajki')
        elif name == 'main-menu' and category == 'Polecamy':
            log.info('Jest polecamy: ')
            self.listsItems1('Polecamy')
        elif name == 'main-menu' and category == 'TV':
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
            self.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(id1,id2), title, icon)
        if name == 'playselectedmovie':
            self.LOAD_AND_PLAY_VIDEO(self.getMovieLinkFromXML(id1,id2), title, icon)

        
  
