# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs

#nie chciało mi się więc
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

if sys.version_info >= (2,7): import json as _json
else: import simplejson as _json

from hashlib import sha1
from utils.crypto.cipher import aes_cbc, base
import binascii, time
import urllib2, urllib, re



mainUrl = 'https://api.tvnplayer.pl/api/?platform=ConnectedTV&terminal=Samsung2&format=json&v=3.6&authKey=453198a80ccc99e8485794789292f061'
mainUrl2 = 'http://api.tvnplayer.pl/api2/?v=3.7&platform=Mobile&terminal=Android&format=json&authKey=4dc7b4f711fb9f3d53919ef94c23890c'
scaleUrl = 'http://redir.atmcdn.pl/scale/o2/tvn/web-content/m/'
log = mrknow_pLog.pLog()

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

        userAgent = tvnplayer.HOST_ANDROID
        self.cm.HEADER = {'User-Agent': userAgent, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        self.itemsPerPage = 30 # config.plugins.iptvplayer.tvp_itemsperpage.value
        self.loggedIn = None
        self.ACCOUNT  = False

    def getDevice(self):
        return "Mobile (Android)"

    def getBaseUrl(self, v='3.0'):
        if self.getDevice() == 'Samsung TV':
            baseUrl = 'https://api.tvnplayer.pl/api?platform=ConnectedTV&terminal=Samsung&format=json&v={0}&authKey=ba786b315508f0920eca1c34d65534cd'.format(v)
        else:
            baseUrl = 'https://api.tvnplayer.pl/api?platform=Mobile&terminal=Android&format=json&v=3.1&authKey=4dc7b4f711fb9f3d53919ef94c23890c' #b4bc971840de63d105b3166403aa1bea
        return baseUrl

    def getBaseUrl2(self, v='3.0'):
        baseUrl = 'https://api.tvnplayer.pl/api?platform=ConnectedTV&terminal=Samsung2&format=json&v=3.6&authKey=453198a80ccc99e8485794789292f061'
        return baseUrl

    def _getJItemStr(self, item, key, default=''):
        try:
            v = item.get(key, None)
            if None == v:
                return default
        except:
            return default
        return (u'%s' % v).encode('utf-8')

    def _getJItemNum(self, item, key, default=0):
        v = item.get(key, None)
        if None != v:
            try:
                NumberTypes = (int, long, float, complex)
            except NameError:
                NumberTypes = (int, long, float)

            if isinstance(v, NumberTypes):
                return v
        return default

    def _getIconUrl(self, cItem):
        iconUrl = ''
        try:
            thumbnails = cItem.get('thumbnail', [])
            if None != thumbnails:
                # prefer jpeg files
                pngUrl = ''
                for item in thumbnails:
                    tmp = self._getJItemStr(item, 'url')
                    if tmp.endswith('jpg') or tmp.endswith('jpeg'):
                        iconUrl = tmp
                        break
                    if tmp.endswith('png'): pngUrl = tmp
                if '' == iconUrl: iconUrl = pngUrl
                if '' != iconUrl: iconUrl = tvnplayer.ICON_URL % iconUrl
        except:
            #printExc()
            log.info('_getIconUrl')
        return iconUrl

    def _generateToken(self, url):
        url = url.replace('http://redir.atmcdn.pl/http/','')
        SecretKey = 'AB9843DSAIUDHW87Y3874Q903409QEWA'
        iv = 'ab5ef983454a21bd'
        KeyStr = '0f12f35aa0c542e45926c43a39ee2a7b38ec2f26975c00a30e1292f7e137e120e5ae9d1cfe10dd682834e3754efc1733'
        salt = sha1()
        salt.update(os.urandom(16))
        salt = salt.hexdigest()[:32]
        tvncrypt = aes_cbc.AES_CBC(SecretKey, base.noPadding(), keySize=32)
        key = tvncrypt.decrypt(binascii.unhexlify(KeyStr), iv=iv)[:32]
        expire = 3600000L + long(time.time()*1000) - 946684800000L
        unencryptedToken = "name=%s&expire=%s\0" % (url, expire)
        pkcs5_pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
        pkcs5_unpad = lambda s : s[0:-ord(s[-1])]
        unencryptedToken = pkcs5_pad(unencryptedToken)
        tvncrypt = aes_cbc.AES_CBC(binascii.unhexlify(key), padding=base.noPadding(), keySize=16)
        encryptedToken = tvncrypt.encrypt(unencryptedToken, iv=binascii.unhexlify(salt))
        encryptedTokenHEX = binascii.hexlify(encryptedToken).upper()
        return "http://redir.atmcdn.pl/http/%s?salt=%s&token=%s" % (url, salt, encryptedTokenHEX)

    def listsCategories(self, url, typ, id,sezon, previd,page):
        if page == None:
            page=0
        if typ == 'Kategorie':
            typ = None
        sezon = int(sezon)
        log.info("TvnVod.listsCategories cItem[%s]" % id)
        cItem = { 'id'       : id,
                  'previd'   :  previd,
                  'title'    : '',
                  'desc'     : '',
                  'icon'     : '',
                  'category' : typ,
                  'season'   : sezon,
                  'page'     : page
                  }
        searchMode = False
        page = 1 + int(cItem.get('page', 0))
        if 'search' == cItem.get('category', None):
            #https://api.tvnplayer.pl/api/?v=3.1&platform=Mobile&terminal=Android&format=json&authKey=4dc7b4f711fb9f3d53919ef94c23890c&limit=30&sort=&m=getSearchItems&isUserLogged=0&page=1&query=film
            searchMode = True
            urlQuery  = '&sort=newest&m=getSearchItems&page=%d&query=%s' % (page, cItem['pattern'])
        elif None != cItem.get('category', None) and None != cItem.get('id', None):
            groupName = 'items'
            urlQuery = '&type=%s&id=%s&limit=%s&page=%s&sort=newest&m=getItems' % (cItem['category'], cItem['id'], self.itemsPerPage, page)
            if 0 < cItem.get('season', 0):
                urlQuery += "&season=%d" % cItem.get('season', 0)
        else:
            groupName = 'categories'
            urlQuery = '&m=mainInfo'

        #try:
        url = self.getBaseUrl() + urlQuery
        data = self.get_jsonparsed_data(url)
        #data = json.loads(data)
        log.info('[data]' % data)

        if 'success' != data['status']:
            log.info("TvnVod.listsCategories status[%s]" % data['status'])
            return

        countItem = self._getJItemNum(data, 'count_items', None)
        if None != countItem and countItem > self.itemsPerPage * page:
            showNextPage = True
        else:
            showNextPage = False

        catalogs = False
        if searchMode:
            seasons = None
            tmp = []
            for resItem in data.get('vodProgramItems', {}).get('category', []):
                tmp.extend(resItem.get('items', []))
            for resItem in data.get('vodArticleItems', {}).get('program', []):
                tmp.extend(resItem.get('items', []))
            data = tmp
            tmp = None
        else:
            seasons  = data.get('seasons', None)
            log.info('[data]' % data)

            # some fix for sub-categories
            # and 0 < len(data.get('items', []))
            if 0 < len(data.get('categories', [])) and cItem.get('previd', '') != cItem.get('id', ''):
            #if 0 < len(data.get('categories', [])):
                catalogs = True
                groupName = 'categories'
                showNextPage = False
            data = data[groupName]


        log.info('[---------------------]')
        log.info('[data]' % data)

        showSeasons = False
        if None != seasons and 0 == cItem.get('season', 0):
            showSeasons = True
            numSeasons = len(seasons)
        else:
            numSeasons = 0

        if 0 != cItem.get('season', 0) or cItem.get('season', 0) == numSeasons:
            for item in data:
                category = self._getJItemStr(item, 'type', '')
                id       = self._getJItemStr(item, 'id', '')
                # some fix for sub-categories
                if catalogs:
                    if 'category' == category:
                        category = 'catalog'
                    if '0' == id:
                        id = cItem['id']

                # get title
                title = self._getJItemStr(item, 'name', '')
                if '' == title: title = self._getJItemStr(item, 'title', 'Brak nazwy')
                tmp = self._getJItemStr(item, 'episode', '')
                if tmp not in ('', '0'): title += ", odcinek " + tmp
                tmp = self._getJItemStr(item, 'season', '')
                if tmp not in ('', '0'): title += ", sezon " + tmp
                try:
                    tmp = self._getJItemStr(item, 'start_date', '')
                    if '' != tmp:
                        tmp = time.strptime(tmp, "%Y-%m-%d %H:%M")
                        if tmp > time.localtime():
                            title += _(" (planowany)")
                except:
                    #printExc()
                    pass

                # get description
                desc = self._getJItemStr(item, 'lead', '')
                # get icon
                icon = self._getIconUrl(item)

                params = { 'id'       : id,
                           'previd'   : cItem.get('id', ''),
                           'title'    : title,
                           'desc'     : desc,
                           'icon'     : icon,
                           'category' : category,
                           'season'   : 0,
                         }
                if 'episode' == category:
                    #self.addVideo(params)
                    log.info('[addVideo 253] %s' % params)
                    self.add('tvnplayer', 'playSelectedMovie', category, title,  icon, 'getItem', 'None', 'None', False, True,id,0)
                else:
                    self.add('tvnplayer', 'items-menu', category, title,  icon, 'getItems', 'None', 'None', True, False,id,0)
                    #self.addDir(params)
                    #add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True,id=0,sezon=0,previd=0):
                    log.info('[addDir 255] %s' % params)
        else:
            showNextPage = False

        if showSeasons:
            for season in seasons:
                params = { 'id'       : cItem['id'],
                           'previd'   : cItem.get('id', ''),
                           'title'    : self._getJItemStr(season, 'name', ''),
                           'desc'     : '',
                           'icon'     : self._getIconUrl(season),
                           'category' : cItem['category'], #self._getJItemStr(season, 'type', ''),
                           'season'   : self._getJItemNum(season, 'id', 0),
                         }
                #self.addDir(params)
                self.add('tvnplayer', 'items-menu', params['category'], params['title'],  params['icon'], 'getItem', 'None', 'None', False, True,params['id'],params['season'])

        if showNextPage:
            params = dict(cItem)
            #params.update({'title':'Następna strona'), 'page': page, 'icon':'', 'desc':''})
            #self.addDir(params)
        #except:
        #    #printExc()
        #    pass

        self.endDir(True)



    def listSearchResults(self, pattern, searchType):
        #log.info("TvnVod.listSearchResults pattern[%s], searchType[%s]" % (pattern, searchType))
        params = { 'id'       : 0,
                   'title'    : '',
                   'desc'     : '',
                   'icon'     : '',
                   'category' : 'search',
                   'pattern'  : pattern,
                   'season'   : 0,
                 }
        self.listsCategories(params)

    def listsMainMenu(self):
        for item in tvnplayer.SERVICE_MENU_TABLE:
            #params = {'name': 'category', 'title': item, 'category': item}
            #self.addDir(params)
            #def add(s, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True,id=0, sezon=0):

            self.add('tvnplayer', 'items-menu', item, item,  'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def resolveLink(self, url):
        #log.info("TvnVod.resolveLink url[%s]" % url)
        videoUrl = ''
        if len(url) > 0:
            if self.getDevice() == 'Mobile (Android)':
                videoUrl = self._generateToken(url).encode('utf-8')
            elif self.getDevice() == 'Samsung TV':
                sts, data  = self.cm.getPage(url)
                if sts and data.startswith('http'):
                    videoUrl =  data.encode('utf-8')
        return videoUrl

    def getLinksForVideo(self, cItem):
        return self.getLinks(cItem['id'])

    def getLinks(self, id, v='3.0'):
        #log.info("TvnVod.getLinks cItem.id[%r]" % id )
        videoUrls = []

        for v in ['3.0', '2.0']:
            url = self.getBaseUrl(v) + '&type=episode&id=%s&limit=%d&page=1&sort=newest&m=%s' % (id, self.itemsPerPage, 'getItem')
            sts, data = self.cm.getPage(url)
            if not sts: continue
            try:
                data = json.loads(data)
                if 'success' == data['status']:
                    data = data['item']
                    # videoTime = 0
                    # tmp = self._getJItemStr(data, 'run_time', '')
                    # if '' != tmp:
                        # tmp = tmp.split(":")
                        # videoTime = int(tmp[0])*60*60+int(tmp[1])*60+int(tmp[2])

                    plot = self._getJItemStr(data, 'lead', '')
                    #log.info("data:\n%s\n" % data)
                    videos = data['videos']['main']['video_content']
                    if None == videos:
                        #SetIPTVPlayerLastHostError("DRM protection.")
                        log.info('DRM protection')
                    else:
                        for video in videos:
                            url = self._getJItemStr(video, 'url', '')
                            if '' == url:
                                #SetIPTVPlayerLastHostError("DRM protection.")
                                log.info('DRM protection')

                            #    url = self._getJItemStr(video, 'src', '')
                            if '' != url:
                                qualityName = self._getJItemStr(video, 'profile_name', '')
                                videoUrls.append({'name':qualityName, 'profile_name':qualityName, 'url':url, 'need_resolve':1})
                    if  1 < len(videoUrls):
                        max_bitrate = int(config.plugins.iptvplayer.TVNDefaultformat.value)
                        max_bitrate ='9999'
                        
                        def __getLinkQuality( itemLink ):
                            return int(TvnVod.QUALITIES_TABLE.get(itemLink['profile_name'], 9999))
                        videoUrls = CSelOneLink(videoUrls, __getLinkQuality, max_bitrate).getSortedLinks()
                        if config.plugins.iptvplayer.TVNUseDF.value:
                            videoUrls = [videoUrls[0]]
            except:
                #printExc()
                pass
            if len(videoUrls):
                break
        return videoUrls

    def getFavouriteData(self, cItem):
        return str(cItem['id'])

    def getLinksForFavourite(self, fav_data):
        return self.getLinks(fav_data)

    def tryTologin(self):
        log.info('tryTologin start')
        if '' == self.LOGIN.strip() or '' == self.PASSWORD.strip():
            log.info('tryTologin wrong login data')
            return False

        post_data = {'email':self.LOGIN, 'password':self.PASSWORD}
        params = {'header':self.HEADER, 'cookiefile':self.COOKIE_FILE, 'use_cookie': True, 'save_cookie':True}
        sts, data = self.cm.getPage( self.MAINURL + "logowanie.html", params, post_data)
        if not sts:
            #log.info('tryTologin problem with login')
            return False

        if 'wyloguj.html' in data:
            #log.info('tryTologin user[%s] logged with VIP accounts' % self.LOGIN)
            return True

        #log.info('tryTologin user[%s] does not have status VIP' % self.LOGIN)
        return False


    def handleService2(self, index, refresh = 0, searchPattern = '', searchType = ''):
        log.info('TvnVod..handleService start')

        if None == self.loggedIn and self.ACCOUNT:
            self.loggedIn = self.tryTologin()
            if not self.loggedIn:
                self.sessionEx.open(MessageBox, 'Problem z zalogowaniem użytkownika "%s".' % self.LOGIN, type = MessageBox.TYPE_INFO, timeout = 10 )
            else:
                self.sessionEx.open(MessageBox, 'Zostałeś poprawnie \nzalogowany.', type = MessageBox.TYPE_INFO, timeout = 10 )

        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)

        # clear hosting tab cache
        self.linksCacheCache = {}

        name     = self.currItem.get("name", '')
        category = self.currItem.get("category", '')
        #log.info( "TvnVod.handleService: ---------> name[%s], category[%s] " % (name, category) )
        self.currList = []

    #MAIN MENU
        if name == None:
            self.listsMainMenu()
    #WYSZUKAJ
        elif category == "Wyszukaj":
            pattern = urllib.quote_plus(searchPattern)
            log.info("Wyszukaj: " + pattern)
            self.listSearchResults(pattern, searchType)
    #HISTORIA WYSZUKIWANIA
        elif category == "Historia wyszukiwania":
            self.listsHistory()
    #KATEGORIE
        else:
            self.listsCategories(self.currItem)

    #def addDir(self, params, isFolders=True, params_keys_needed = None):
    #        self.__play(params, False, isFolders, "dir_video", params_keys_needed)

    def get_jsonparsed_data(self, url):
        log.info('[tvnplayer] url:%s'% url)
        response = urllib2.urlopen(url)
        data = str(response.read())
        response.close()
        return json.loads(data)

    def listsMainMenu1(self):
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
        data = self.get_jsonparsed_data(self.getBaseUrl() + urlQuery)
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
        myurl = self.getBaseUrl2() + '&type=episode&id=%s&limit=%d&page=1&sort=newest&m=%s' % (id, self.itemsPerPage, 'getItem')
        #urlQuery2 = '&m=getItem&id=%s&deviceType=Tablet&os=4.4.2' % (id)
        urlQuery2 = '&m=getItem&id=%s' % (id)

        if ptv.getSetting('checkClientip') == 'False':
            try:
                getItem = opener.open(myurl)
            except Exception, ex:
                ok = xbmcgui.Dialog().ok('TVNPlayer', 'Coś nie tak z Twoim proxy', 'error message', str(ex))
                return ok
        else:
            getItem = urllib2.urlopen(myurl)
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
            log.info('video_content  %s ' % video_content )

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
                log.info('URL: %s ' % stream_url)
                #stream_url = self._generateToken(stream_url).encode('utf-8')
                #return stream_url+'|User-Agent=Apache-HttpClient%2FUNAVAILABLE%20(java%201.4)'
                log.info('URL: %s ' % stream_url)

                if ptv.getSetting('checkClientip') == 'False':
                    new_stream_url = opener.open(stream_url)
                else:
                    new_stream_url = urllib2.urlopen(stream_url)
                link = new_stream_url.read()
                new_stream_url.close()
                #link = new_stream_url
                log.info('URL: %s ' % link)
                #new_stream_url.close()
            else:
                log.info('Data: %s' % data['item']['videos']['main']['video_content'][0]['src'])
                #print("UUUUUUUUUUUUUUUUUUUUUU>>>>>>>>>>>>>>>>>>>>>NIE")
                d = xbmcgui.Dialog()
                d.ok('Plik zaszyfrowany!', 'Na Kodi nie ma mozliwości odtwarzania plików Widevine', 'Spróbuj bezpośrednio na tablecie')
                link =  data['item']['videos']['main']['video_content'][0]['src']
                link = self.resolveLink(link)
                #link = link + '|User-Agent=Mozilla%2F5.0%20(Windows%20NT%206.1%3B%20rv%3A31.0)%20Gecko%2F20100101%20Firefox%2F31.0'
                link = link + '|User-Agent=Mozilla%2f5.0+(iPad%3b+CPU+OS+6_0+like+Mac+OS+X)+AppleWebKit%2f536.26+(KHTML%2c+​like+Gecko)+Version%2f6.0+Mobile%2f10A5355d+Safari%2f8536.25'

        log.info('AAAA %s ' % link)
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


    def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True,id=0,sezon=0,previd=0,page=0):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage)+ "&id=" + urllib.quote_plus(str(id))+ "&sezon=" + urllib.quote_plus(str(sezon))+"&previd=" + urllib.quote_plus(str(previd))+"&page=" + urllib.quote_plus(str(page))
        log.info(str(u))
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
        previd = self.parser.getParam(params, "previd")
        page= self.parser.getParam(params, "page")

        #print ("DANE",name,category,  title,sezon,id)
        #name     = self.currItem.get("name", '')
        #category = self.currItem.get("category", '')
        self.currItem =self.parser.getParam(params, "currItem")
        if name == None:
            self.listsMainMenu()
        elif name == 'items-menu':
            log.info('Jest items-menu: ')
            #self.listsItems(url,category,id,sezon)
            self.listsCategories(url,category,id,sezon,previd,page)
        elif name == 'sezon-menu':
            log.info('Jest sezon-menu: ')
            self.listsItems2(url,category,id,sezon)
        if name == 'playSelectedMovie':
            data = self.getMovieLinkFromXML(category,id)
            self.LOAD_AND_PLAY_VIDEO(data, title, icon)


        
  
"""
class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, TvnVod(), True, [CDisplayListItem.TYPE_VIDEO, CDisplayListItem.TYPE_AUDIO])

    def getLogoPath(self):
        return RetHost(RetHost.OK, value = [GetLogoDir('tvnvodlogo.png')])

    def getLinksForVideo(self, Index = 0, selItem = None):
        retCode = RetHost.ERROR
        retlist = []
        if not self.isValidIndex(Index): return RetHost(retCode, value=retlist)

        urlList = self.host.getLinksForVideo(self.host.currList[Index])
        for item in urlList:
            need_resolve = 1
            retlist.append(CUrlItem(item["name"], item["url"], need_resolve))

        return RetHost(RetHost.OK, value = retlist)
    # end getLinksForVideo

    def getResolvedURL(self, url):
        # resolve url to get direct url to video file
        url = self.host.resolveLink(url)
        urlTab = []
        if isinstance(url, basestring) and url.startswith('http'):
            urlTab.append(url)
        return RetHost(RetHost.OK, value = urlTab)

    def converItem(self, cItem):
        hostList = []
        searchTypesOptions = []

        hostLinks = []
        type = CDisplayListItem.TYPE_UNKNOWN
        possibleTypesOfSearch = None

        if cItem['type'] == 'category':
            if cItem['title'] == 'Wyszukaj':
                type = CDisplayListItem.TYPE_SEARCH
                possibleTypesOfSearch = searchTypesOptions
            else:
                type = CDisplayListItem.TYPE_CATEGORY
        elif cItem['type'] == 'video':
            type = CDisplayListItem.TYPE_VIDEO
            url = cItem.get('url', '')
            if '' != url:
                hostLinks.append(CUrlItem("Link", url, 1))

        title       =  cItem.get('title', '')
        description =  self.cm.clean_html(cItem.get('desc', ''))
        icon        =  cItem.get('icon', '')

        return CDisplayListItem(name = title,
                                description = description,
                                type = type,
                                urlItems = hostLinks,
                                urlSeparateRequest = 1,
                                iconimage = icon,
                                possibleTypesOfSearch = possibleTypesOfSearch)
    # end converItem

    def getSearchItemInx(self):
        # Find 'Wyszukaj' item
        try:
            list = self.host.getCurrList()
            for i in range( len(list) ):
                if list[i]['category'] == 'Wyszukaj':
                    return i
        except:
            printExc()
            return -1

    def setSearchPattern(self):
        try:
            list = self.host.getCurrList()
            if 'history' == list[self.currIndex].get('name', ''):
                pattern = list[self.currIndex]['title']
                search_type = ''
                self.host.history.addHistoryItem( pattern, search_type)
                self.searchPattern = pattern
                self.searchType = search_type
        except:
            printExc()
            self.searchPattern = ''
            self.searchType = ''
        return
"""