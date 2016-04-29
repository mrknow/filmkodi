# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs

#nie chciało mi się więc, ściągnołem
# @autor - https://gitlab.com/u/samsamsam
#https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2/blob/master/IPTVPlayer/hosts/hosttvnvod.py

if sys.version_info >=  (2, 7):
    import json as json
else:
    import simplejson as json

scriptID = 'plugin.video.mrknow'
scriptname = "Filmy online www.mrknow.pl - tvnplayer"
ptv = xbmcaddon.Addon(scriptID)
_thisPlugin = int(sys.argv[1])

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "../resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_urlparser, mrknow_Pageparser, mrknow_Player
from BeautifulSoup import BeautifulSoup


log = mrknow_pLog.pLog()


mainUrl = 'https://api.tvnplayer.pl/api/?platform=ConnectedTV&terminal=Samsung2&format=json&v=3.6&authKey=453198a80ccc99e8485794789292f061'
mainUrl2 = 'http://api.tvnplayer.pl/api2/?v=3.7&platform=Mobile&terminal=Android&format=json&authKey=4dc7b4f711fb9f3d53919ef94c23890c'
scaleUrl = 'http://redir.atmcdn.pl/scale/o2/tvn/web-content/m/'

class tvnplayer:

    HOST         = 'Mozilla/5.0 (SmartHub; SMART-TV; U; Linux/SmartTV; Maple2012) AppleWebKit/534.7 (KHTML, like Gecko) SmartTV Safari/534.7'
    HOST_ANDROID = 'Apache-HttpClient/UNAVAILABLE (java 1.4)'
    ICON_URL     = 'http://redir.atmcdn.pl/scale/o2/tvn/web-content/m/%s?quality=50&dstw=290&dsth=287&type=1'

    QUALITIES_TABLE = {
        'HD'            : 7,
        'Bardzo wysoka' : 6,
        'Wysoka'        : 5,
        'Standard'      : 4,
        'Średnia'       : 3,
        'Niska'         : 2,
        'Bardzo niska'  : 1,
    }

    SERVICE_MENU_TABLE = [
        "Kategorie",
        "Wyszukaj",
        "Historia wyszukiwania"
    ]

    def __init__(self):
        log.info('Starting tvnplayer.pl')
        self.cm = mrknow_pCommon.common()
        self.parser = mrknow_Parser.mrknow_Parser()
        self.pp = mrknow_Pageparser.mrknow_Pageparser()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.p = mrknow_Player.mrknow_Player()
        self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "tvnplayer.cookie"

        userAgent = HOST_ANDROID
        self.cm.HEADER = {'User-Agent': userAgent, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        self.itemsPerPage = 30 # config.plugins.iptvplayer.tvp_itemsperpage.value
        self.loggedIn = None
        self.ACCOUNT  = False



    def get_jsonparsed_data(self, url):
        log.info('[tvnplayer] url:%s'% url)
        response = urllib2.urlopen(url)
        data = str(response.read())
        response.close()
        return json.loads(data)

    def listsMainMenu(self):
        GeoIP = self.get_jsonparsed_data(mainUrl + '&m=checkClientip')
        ptv.setSetting(id='checkClientip', value=str(GeoIP['result']))
        njson = self.get_jsonparsed_data(mainUrl + '&m=mainInfo')
        categories = njson['categories']
        for item in categories:
            name = item.get('name','')
            type = item.get('type','')
            id = item['id']
            if type != 'titles_of_day' and type != 'favorites' and type != 'pauses':
                self.add('tvnplayer', 'items-menu', type, name,  'None', 'getItems', 'None', 'None', True, False,id)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsItems(self, url, typ, id,sezon):
        urlQuery = '&m=%s&type=%s&id=%s&limit=500&page=1&sort=newest' % (url, typ, id)
        if sezon  > 0:
            urlQuery = urlQuery + '&season=' + str(sezon)
        data = self.get_jsonparsed_data(mainUrl+ urlQuery)
        if (not 'seasons' in data) or (len(data['seasons']) == 0): #bez sezonow albo odcinki w sezonie
            for item in  data['items']:
                title = item['title']
                typ = item.get('type','')
                id = item['id']
                thumbnail = item['thumbnail'][0]['url']
                gets = {'type': 1,'quality': 95,'srcmode': 0,'srcx': item['thumbnail'][0]['srcx'],'srcy': item['thumbnail'][0]['srcy'],
                        'srcw': item['thumbnail'][0]['srcw'],'srch': item['thumbnail'][0]['srch'],'dstw': 256,'dsth': 292}
                thumbnailimage='%s%s?%s' % (scaleUrl, thumbnail, urllib.urlencode(gets))
                if item['type'] == 'episode':
                    sort = False
                    if item['season'] != 0 and item['season'] != None:
                        title = title + ', sezon ' + str(item['season'])
                    if item['episode'] != 0 and item['episode'] != None:
                        title = title + ', odcinek ' + str(item['episode'])
                    if ('preview_' in item['type_episode']):
                        title = title + ' [COLOR FFFF0000](' + item['start_date'] + ')[/COLOR]'

                if item['type'] == 'series':
                    if item['season'] != 0 and item['season'] != None:
                        title = title + ', sezon ' + str(item['season'])

                subtitle = item.get('sub_title', None)
                if subtitle != None and len(subtitle) > 0:
                    title = title + ' - ' + subtitle
                if item['type'] == 'episode':
                    self.add('tvnplayer', 'playSelectedMovie', typ, title,  thumbnailimage, 'getItem', 'None', 'None', False, True,id,sezon)

                else:
                    self.add('tvnplayer', 'items-menu', typ, title,  thumbnailimage, 'getItems', 'None', 'None', True, False,id,sezon)

        else: #listuj sezony
            for item in data['seasons']:
                if item['thumbnail'] != None:
                    thumbnail = item['thumbnail'][0]['url']
                    gets = {'type': 1,'quality': 95,'srcmode': 0,'srcx': item['thumbnail'][0]['srcx'],'srcy': item['thumbnail'][0]['srcy'],
                        'srcw': item['thumbnail'][0]['srcw'],'srch': item['thumbnail'][0]['srch'],'dstw': 256,'dsth': 292}
                    icon='%s%s?%s' % (scaleUrl, thumbnail, urllib.urlencode(gets))
                else:
                    icon = ''
                t = data['items'][0]['title']
                self.add('tvnplayer', 'sezon-menu', 'series',  t + ' - ' + item['name'],  'None', 'getItems', 'None', 'None', True, False,item['vdp_id'],item['id'])
        self.endDir(True)

    def listsItems2(self, url, typ, id,sezon):
        urlQuery = '&m=%s&type=%s&id=%s&limit=500&page=1&sort=newest' % (url, typ, id)
        if sezon  > 0:
            urlQuery = urlQuery + '&season=' + str(sezon)
        data = self.get_jsonparsed_data(mainUrl+ urlQuery)
        for item in  data['items']:
            title = item['title']
            typ = item.get('type','')
            id = item['id']
            thumbnail = item['thumbnail'][0]['url']
            gets = {'type': 1,'quality': 95,'srcmode': 0,'srcx': item['thumbnail'][0]['srcx'],'srcy': item['thumbnail'][0]['srcy'],
                    'srcw': item['thumbnail'][0]['srcw'],'srch': item['thumbnail'][0]['srch'],'dstw': 256,'dsth': 292}
            thumbnailimage='%s%s?%s' % (scaleUrl, thumbnail, urllib.urlencode(gets))
            if item['type'] == 'episode':
                sort = False
                if item['season'] != 0 and item['season'] != None:
                    title = title + ', sezon ' + str(item['season'])
                if item['episode'] != 0 and item['episode'] != None:
                    title = title + ', odcinek ' + str(item['episode'])
                if ('preview_' in item['type_episode']):
                    title = title + ' [COLOR FFFF0000](' + item['start_date'] + ')[/COLOR]'

            if item['type'] == 'series':
                if item['season'] != 0 and item['season'] != None:
                    title = title + ', sezon ' + str(item['season'])

            subtitle = item.get('sub_title', None)
            if subtitle != None and len(subtitle) > 0:
                title = title + ' - ' + subtitle
            if item['type'] == 'episode':
                self.add('tvnplayer', 'playSelectedMovie', typ, title,  thumbnailimage, 'getItem', 'None', 'None', False, True,id,sezon)
            else:
                self.add('tvnplayer', 'items-menu', typ, title,  thumbnailimage, 'getItems', 'None', 'None', True, False,id,sezon)
        self.endDir(True)


    def getMovieLinkFromXML(self, typ,id):
        #TODO:Proxy
        if ptv.getSetting('checkClientip') == 'False':
            pl_proxy = 'http://' + ptv.getSetting('pl_proxy') + ':' + ptv.getSetting('pl_proxy_port')
            proxy_handler = urllib2.ProxyHandler({'http':pl_proxy})
            if ptv.getSetting('pl_proxy_pass') <> '' and ptv.getSetting('pl_proxy_user') <> '':
                password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
                password_mgr.add_password(None, pl_proxy, ptv.getSetting('pl_proxy_user'), ptv.getSetting('pl_proxy_pass'))
                proxy_auth_handler = urllib2.ProxyBasicAuthHandler(password_mgr)
                opener = urllib2.build_opener(proxy_handler, proxy_auth_handler)
            else:
                opener = urllib2.build_opener(proxy_handler)
        urlQuery = '&type=%s&id=%s&sort=newest&m=getItem&deviceScreenHeight=1080&deviceScreenWidth=1920' % (typ, id)
        #urlQuery2 = '&m=getItem&id=%s&deviceType=Tablet&os=4.4.2' % (id)
        urlQuery2 = '&m=getItem&id=%s' % (id)

        if ptv.getSetting('checkClientip') == 'False':
            try:
                getItem = opener.open(mainUrl + urlQuery)
            except Exception, ex:
                ok = xbmcgui.Dialog().ok('TVNPlayer', 'Coś nie tak z Twoim proxy', 'error message', str(ex))
                return ok
        else:
            getItem = urllib2.urlopen(mainUrl + urlQuery)
        link=''
        data = json.loads(getItem.read())
        getItem.close()
        log.info('[tvn] data:%s' % data)
        #czy jest video
        if data['item']['videos']['main']['video_content'] == None or len(data['item']['videos']['main']['video_content']) == 0:
            if ptv.getSetting('checkClientip') == 'False':
                try:
                    getItem = opener.open(mainUrl2 + urlQuery)
                except Exception, ex:
                    ok = xbmcgui.Dialog().ok('TVNPlayer', 'Coś nie tak z Twoim proxy', 'error message', str(ex))
                    return ok
            else:
                getItem = urllib2.urlopen(mainUrl2 + urlQuery)
                print("main2",mainUrl2 + urlQuery)
            data = json.loads(getItem.read())
            getItem.close()

        if data['item']['videos']['main']['video_content'] != None and len(data['item']['videos']['main']['video_content']) != 0:

            #znajdz jakosc z settings wtyczki
            video_content = data['item']['videos']['main']['video_content']
            profile_name_list = []
            for item in video_content:
                profile_name = item['profile_name']
                profile_name_list.append(profile_name)
            if ptv.getSetting('auto_quality') == 'true' :
                if 'HD' in profile_name_list:
                    select = profile_name_list.index('HD')
                elif 'Bardzo Wysoka' in profile_name_list:
                    select = profile_name_list.index('Bardzo Wysoka')
                elif 'Wysoka' in profile_name_list:
                    select = profile_name_list.index('Wysoka')
                else:
                    select = xbmcgui.Dialog().select('Wybierz jakość', profile_name_list)
            else:
                select = xbmcgui.Dialog().select('Wybierz jakość', profile_name_list)

            if 'url' in data['item']['videos']['main']['video_content'][select]:
                stream_url = data['item']['videos']['main']['video_content'][select]['url']
                if ptv.getSetting('checkClientip') == 'False':
                    new_stream_url = opener.open(stream_url)
                else:
                    new_stream_url = urllib2.urlopen(stream_url)
                link = new_stream_url.read()
                new_stream_url.close()
            else:
                print("UUUUUUUUUUUUUUUUUUUUUU>>>>>>>>>>>>>>>>>>>>>NIE")
                d = xbmcgui.Dialog()
                d.ok('Plik zaszyfrowany!', 'Na Kodi nie ma mozliwości odtwarzania plików Widevine', 'Spróbuj bezpośrednio na tablecie')
                link ='NONE'
        return link

    def LOAD_AND_PLAY_VIDEO(self, videoUrl, title, icon):
        ok=True
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


    def endDir(self, sort=False, content=None, viewMode=None, ps=None):
        if ps==None:
            ps=int(sys.argv[1])
        if sort==True:
            xbmcplugin.addSortMethod(ps, xbmcplugin.SORT_METHOD_LABEL)
        canBeContent = ["files", "songs", "artists", "albums", "movies", "tvshows", "episodes", "musicvideos"]
        if content in canBeContent:
            xbmcplugin.setContent(ps,content)
        if viewMode!=None:
            viewList = {}
            if 'confluence' in xbmc.getSkinDir():
                viewList = {
                    'List':                                         '50',
                    'Big List':                                     '51',
                    'ThumbnailView':                        '500',
                    'PosterWrapView':                       '501',
                    'PosterWrapView2_Fanart':       '508',
                    'MediaInfo':                            '504',
                    'MediaInfo2':                           '503',
                    'MediaInfo3':                           '515',
                    'WideIconView':                         '505',
                    'MusicVideoInfoListView':       '511',
                    'AddonInfoListView1':           '550',
                    'AddonInfoThumbView1':          '551',
                    'LiveTVView1':                          '560'
                }
            if viewMode in viewList:
                view = viewList[viewMode]
            else:
                view='None'
            xbmc.executebuiltin("Container.SetViewMode(%s)" % (view))
        xbmcplugin.endOfDirectory(ps)


    def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True,id=0, sezon=0):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage)+ "&id=" + urllib.quote_plus(str(id))+ "&sezon=" + urllib.quote_plus(str(sezon))
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


    def handleService(self):
    	params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        sezon = self.parser.getParam(params, "sezon")
        id = self.parser.getParam(params, "id")
        #print ("DANE",name,category,  title,sezon,id)
        if name == None:
            self.listsMainMenu()
        elif name == 'items-menu':
            log.info('Jest items-menu: ')
            self.listsItems(url,category,id,sezon)
        elif name == 'sezon-menu':
            log.info('Jest sezon-menu: ')
            self.listsItems2(url,category,id,sezon)
        if name == 'playSelectedMovie':
            data = self.getMovieLinkFromXML(category,id)
            self.LOAD_AND_PLAY_VIDEO(data, title, icon)


        
  
