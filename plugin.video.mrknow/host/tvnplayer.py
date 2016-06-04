# -*- coding: utf-8 -*-
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
from urlparse import urlparse, parse_qs

#nie chciało mi się więc
# @autor - http://svn.sd-xbmc.org/
# Umieszczam stosowne info w changelogu


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

import mrknow_pLog
log = mrknow_pLog.pLog()
#log.info(BASE_RESOURCE_PATH1)

BASE_RESOURCE_PATH1 = os.path.join( ptv.getAddonInfo('path'), 'lib')
sys.path.append( os.path.join( BASE_RESOURCE_PATH1, "utils" ) )

import os, sys, time
import xbmcaddon, xbmcgui
import traceback

if sys.version_info >= (2,7): import json as _json
else: import simplejson as _json

from hashlib import sha1
import crypto.cipher.aes_cbc
import crypto.cipher.base, base64
import binascii
import urllib2, urllib, re


import mrknow_pLog, mrknow_pCommon, mrknow_Parser, mrknow_urlparser, mrknow_Pageparser, mrknow_Player


if sys.version_info >= (2,7): import json as _json
else: import simplejson as _json

dbg=False


SERVICE = 'tvn'
THUMB_SERVICE = 'http://sd-xbmc.org/repository/xbmc-addons/' + SERVICE + '.png'

platform = {
    'Samsung': {
        'platform': 'ConnectedTV',
        'terminal': 'Samsung2',
        'authKey': '453198a80ccc99e8485794789292f061',
        'host': 'Mozilla/5.0 (SmartHub; SMART-TV; U; Linux/SmartTV; Maple2012) AppleWebKit/534.7 (KHTML, like Gecko) SmartTV Safari/534.7',
        'api': '3.6',
        'fallback': 'Android'
    },
    'Android': {
        'platform': 'Mobile',
        'terminal': 'Android',
        'authKey': 'b4bc971840de63d105b3166403aa1bea',
        'host': 'Apache-HttpClient/UNAVAILABLE (java 1.4)',
        'api': '3.0',
        'fallback': 'Android2'
    },
    'Android2': {
        'platform': 'Mobile',
        'terminal': 'Android',
        'authKey': 'b4bc971840de63d105b3166403aa1bea',
        'host': 'Apache-HttpClient/UNAVAILABLE (java 1.4)',
        'api': '2.0',
        'fallback': ''
    }
}

qualities = [
    'HD',
    'Bardzo wysoka',
    'SD',
    'Wysoka',
    'Standard',
    'Średnia'
    'Niska',
    'Bardzo niska'
]

tvn_proxy = ptv.getSetting('tvn_proxy')
tvn_quality = ptv.getSetting('tvn_quality')
tvn_sort = ptv.getSetting('tvn_sort')
tvn_platform = ptv.getSetting('tvn_platform')

tvn_url_keys = ("service", "id", "seriesId", "category")

MAINURL = 'https://api.tvnplayer.pl'
IMAGEURL = 'http://dcs-193-111-38-250.atmcdn.pl/scale/o2/tvn/web-content/m/'


class sdGUI:
    def __init__(self):
        self.cm = mrknow_pCommon.common()
        #self.history = sdCommon.history()
        self.parser = mrknow_Parser.mrknow_Parser()

    def searchInput(self, SERVICE, heading='Wyszukaj'):
        keyboard = xbmc.Keyboard('', heading, False)
        keyboard.doModal()
        if keyboard.isConfirmed():
            text = keyboard.getText()
            self.history.addHistoryItem(SERVICE, text)
            return text

    def dialog(self):
        return xbmcgui.Dialog()

    def percentDialog(self):
        return xbmcgui.DialogProgress()

    def notification(self, title=" ", msg=" ", time=5000):
        xbmc.executebuiltin("XBMC.Notification(" + title + "," + msg + "," + str(time) + ")")

    def getBaseImagePath(self):
        return 'http://sd-xbmc.org/repository/xbmc-addons/'

    def getThumbNext(self):
        return self.getBaseImagePath() + "dalej.png"

    def getLogoImage(self, title, ext="png"):
        return self.getBaseImagePath() + title + "." + ext

    def __setInfoLabels(self, params, pType):
        InfoLabels = {}
        if pType == "video":
            infoLabelsKeys = ["genre", "year", "episode", "season", "top250", "tracknumber", "rating", "playcount",
                              "overlay",
                              "cast", "castandrole", "director", "mpaa", "plot", "plotoutline", "title",
                              "originaltitle", "sorttitle",
                              "duration", "studio", "tagline", "writer", "tvshowtitle", "premiered", "status", "code",
                              "aired", "credits",
                              "lastplayed", "album", "artist", "votes", "trailer", "dateadded"]
        elif pType == "music":
            infoLabelsKeys = ["tracknumber", "duration", "year", "genre", "album", "artist", "title", "rating",
                              "lyrics", "playcount", "lastplayed"]

        for key, value in params.items():
            if key in infoLabelsKeys:
                InfoLabels[key] = value
        return InfoLabels

    def __play(self, params, isPlayable=False, isFolders=False, pType="video", params_keys_needed=None):
        if pType == "video":
            params['name'] = 'playSelectedVideo'
        elif pType == "music":
            params['name'] = 'playSelectedAudio'
        # uproszczenie urli / niezbedne żeby dobrze działał status "watched"
        if params_keys_needed == None:
            u = sys.argv[0] + self.parser.setParam(params)
        else:
            needed_params = {}
            for k in params_keys_needed:
                if params.has_key(k):
                    needed_params[k] = params[k]
            u = sys.argv[0] + self.parser.setParam(needed_params)

        pType = pType.replace("dir_", "")

        params['icon'] = params.get('icon') or "DefaultVideo.png"

        if dbg == True:
            log.info(" - " + pType + ": ")
            self.parser.debugParams(params, True)

        params['title'] = params.get('title') or None
        if params['title'] == None: return False
        params['series'] = params.get('series') or None
        params['file_name'] = params['title']
        if params['series'] != None:
            params['file_name'] = "%s - %s" % (params['series'], params['title'])

        liz = xbmcgui.ListItem(params['title'], iconImage="DefaultFolder.png", thumbnailImage=params['icon'])
        if isPlayable:
            liz.setProperty("IsPlayable", "true")

        params['fanart'] = params.get('fanart') or "http://sd-xbmc.org/repository/repository.sd-xbmc.org/fanart.jpg"

        params['banner'] = params.get('banner') or params['icon']
        params['poster'] = params.get('poster') or params['icon']

        meta = self.__setInfoLabels(params, pType)

        liz.setProperty("fanart_image", params['fanart'])
        liz.setArt({'banner': params['banner'], 'poster': params['poster']})
        liz.setInfo(type=pType, infoLabels=meta)
        if isPlayable and params_keys_needed != None:  # uproszone url = wsparcje dla "watched"
            liz.addContextMenuItems([('Oznacz jako (nie)obejrzane', 'Action(ToggleWatched)')])
        # liz.addStreamInfo('video', { 'codec': 'h264', 'aspect': 1.78, 'width': 1280,'height': 720})
        if self.cm.isEmptyDict(params, 'page'): params['page'] = ''
        if (not self.cm.isEmptyDict(params, 'dstpath')) and pType == "video":
            cm = self.__addDownloadContextMenu(
                {'service': params['service'], 'title': params['file_name'], 'url': params['page'],
                 'path': os.path.join(params['dstpath'], params['service'])})
            liz.addContextMenuItems(cm, replaceItems=False)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=isFolders)

    def __addDownloadContextMenu(self, params={}):
        params['action'] = 'download'
        param = self.parser.setParam(params)
        cm = []
        cm.append(('Ściągnij', "XBMC.RunPlugin(%s%s)" % (sys.argv[0], param)))
        cm.append(('Informacje', "XBMC.Action(Info)",))
        return cm

    def playVideo(self, params, isPlayable=False, isFolders=False, params_keys_needed=None):
        self.__play(params, isPlayable, isFolders, "video", params_keys_needed)

    def playAudio(self, params, isPlayable=False, isFolders=False, params_keys_needed=None):
        self.__play(params, isPlayable, isFolders, "music", params_keys_needed)

    def addDir(self, params, isFolders=True, params_keys_needed=None):
        self.__play(params, False, isFolders, "dir_video", params_keys_needed)

    def endDir(self, sort=False, content=None, viewMode=None, ps=None):
        '''
        ToDo:
        Check is Confluence, not? other View Mode
        Confluence View Modes:
        http://www.xbmchub.com/forums/general-python-development/717-how-set-default-view-type-xbmc-lists.html#post4683
        https://github.com/xbmc/xbmc/blob/master/addons/skin.confluence/720p/MyVideoNav.xml
        '''
        if ps == None:
            ps = int(sys.argv[1])
        if sort == True:
            xbmcplugin.addSortMethod(ps, xbmcplugin.SORT_METHOD_LABEL)
        canBeContent = ["files", "songs", "artists", "albums", "movies", "tvshows", "episodes", "musicvideos"]
        if content in canBeContent:
            xbmcplugin.setContent(ps, content)
        if viewMode != None:
            viewList = {}
            if 'confluence' in xbmc.getSkinDir():
                viewList = {
                    'List': '50',
                    'Big List': '51',
                    'ThumbnailView': '500',
                    'PosterWrapView': '501',
                    'PosterWrapView2_Fanart': '508',
                    'MediaInfo': '504',
                    'MediaInfo2': '503',
                    'MediaInfo3': '515',
                    'WideIconView': '505',
                    'MusicVideoInfoListView': '511',
                    'AddonInfoListView1': '550',
                    'AddonInfoThumbView1': '551',
                    'LiveTVView1': '560'
                }
            if viewMode in viewList:
                view = viewList[viewMode]
            else:
                view = 'None'
            xbmc.executebuiltin("Container.SetViewMode(%s)" % (view))
        xbmcplugin.endOfDirectory(ps)

    def new_playlist(self, playlist='audio'):
        playlists = {'audio': 0, 'video': 1}
        if playlist not in playlists.keys():
            log.info('Playlista "%s" jest inwalidą ;).' % playlist)
        selected_playlist = xbmc.PlayList(playlists[playlist])
        selected_playlist.clear()
        return selected_playlist

    def add_to_playlist(self, playlist, items):
        if isinstance(items, list):
            for item in items:
                playlist.add(item)
        elif isinstance(items, str):
            playlist.add(items)

    def __LOAD_AND_PLAY(self, url, title, player=True, pType='video'):
        if url == '':
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu', 'Może to chwilowa awaria.', 'Spróbuj ponownie za jakiś czas')
            return False
        thumbnail = xbmc.getInfoImage("ListItem.Thumb")
        liz = xbmcgui.ListItem(title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail)
        liz.setInfo(type="pType", infoLabels={"Title": title})
        try:
            if player != True:
                print "custom player pCommon"
                xbmcPlayer = player
            else:
                print "default player pCommon"
                xbmcPlayer = xbmc.Player()
            xbmcPlayer.play(url, liz)
        except:
            d = self.dialog()
            if pType == "video":
                d.ok('Wystąpił błąd!', 'Błąd przy przetwarzaniu, lub wyczerpany limit czasowy oglądania.',
                     'Zarejestruj się i opłać abonament.', 'Aby oglądać za darmo spróbuj ponownie za jakiś czas.')
            elif pType == "music":
                d.ok('Wystąpił błąd!', 'Błąd przy przetwarzaniu.', 'Aby wysłuchać spróbuj ponownie za jakiś czas.')
            return False
        return True

    def __LOAD_AND_PLAY_WATCHED(self, url,
                                pType='video'):  # NOWE wersja używa xbmcplugin.setResolvedUrl wspiera status "watched"
        if url == '':
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu', 'Może to chwilowa awaria.', 'Spróbuj ponownie za jakiś czas')
            return False
        liz = xbmcgui.ListItem(path=url)
        try:
            return xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
        except:
            d = self.dialog()
            if pType == "video":
                d.ok('Wystąpił błąd!', 'Błąd przy przetwarzaniu, lub wyczerpany limit czasowy oglądania.',
                     'Zarejestruj się i opłać abonament.', 'Aby oglądać za darmo spróbuj ponownie za jakiś czas.')
            elif pType == "music":
                d.ok('Wystąpił błąd!', 'Błąd przy przetwarzaniu.', 'Aby wysłuchać spróbuj ponownie za jakiś czas.')
            return False

    def LOAD_AND_PLAY_VIDEO(self, url, title, player=True):
        if url != False:
            self.__LOAD_AND_PLAY(url, title, player, "video")
        else:
            d = xbmcgui.Dialog()
            d.ok('Brak linku!', 'Przepraszamy, chwilowa awaria.', 'Zapraszamy w innym terminie.')

    def LOAD_AND_PLAY_VIDEO_WATCHED(self, url):  # NOWE wersja używa xbmcplugin.setResolvedUrl wspiera status "watched"
        if url != False:
            return self.__LOAD_AND_PLAY_WATCHED(url, 'video')
        else:
            d = xbmcgui.Dialog()
            d.ok('Brak linku!', 'Przepraszamy, chwilowa awaria.', 'Zapraszamy w innym terminie.')
            return False

    def LOAD_AND_PLAY_AUDIO(self, url, title, player=True):
        if url != False:
            self.__LOAD_AND_PLAY(url, title, player, "music")
        else:
            d = xbmcgui.Dialog()
            d.ok('Brak linku!', 'Przepraszamy, chwilowa awaria.', 'Zapraszamy w innym terminie.')

    def LOAD_AND_PLAY_AUDIO_WATCHED(self, url):  # NOWE wersja używa xbmcplugin.setResolvedUrl wspiera status "watched"
        if url != False:
            return self.__LOAD_AND_PLAY_WATCHED(url, 'audio')
        else:
            d = xbmcgui.Dialog()
            d.ok('Brak linku!', 'Przepraszamy, chwilowa awaria.', 'Zapraszamy w innym terminie.')
            return False

class tvn:
    def __init__(self):
        log.info('Loading ' + SERVICE)
        self.parser = mrknow_Parser.mrknow_Parser()
        self.gui = sdGUI()
        self.common = mrknow_pCommon.common()
        self.api = API()



    def getMenu(self, args):
        data = self.api.getAPI(args)
        for item in data['categories']:
            # pomin ULUBIONE i KONTYNUUJ / PAKIETY
            if item['type'] != 'favorites' and item['type'] != 'pauses' and item['type'] != 'open_market' and item[
                'type'] != 'landing_page' and item['type'] != 'stream':
                if item['thumbnail'] != None:
                    icon = self.api.getImage(item['thumbnail'][0]['url'])
                else:
                    icon = THUMB_SERVICE
                params = {'service': SERVICE, 'category': item['type'], 'id': item['id'],
                          'title': item['name'].encode('UTF-8'), 'icon': icon}
                self.gui.addDir(params, params_keys_needed=tvn_url_keys)
        self.gui.endDir()

    def getItems(self, args):
        sort = True
        data = self.api.getAPI(args)

        if (not 'seasons' in data) or (len(data['seasons']) == 0) or (
            'season=' in args):  # bez sezonow albo odcinki w sezonie
            for item in data['items']:
                try:
                    icon = self.api.getImage(item['thumbnail'][0]['url'])
                except Exception, exception:
                    icon = THUMB_SERVICE

                title = item['title'].encode('UTF-8')

                if item['type'] == 'episode':
                    sort = False
                    if item['season'] != 0 and item['season'] != None:
                        title = title + ', sezon ' + str(item['season'])
                    if item['episode'] != 0 and item['episode'] != None:
                        title = title + ', odcinek ' + str(item['episode'])

                    # 'preview_catchup' or 'preview_prepremier'
                    if ('preview_' in item['type_episode']):
                        title = title + ' [COLOR FFFF0000](' + item['start_date'].encode('UTF-8') + ')[/COLOR]'

                if item['type'] == 'series':
                    # tu wsadzic wlaczanie/wylaczanie sortowania
                    if tvn_sort == "Alfabetycznie":
                        sort = True
                    else:
                        sort = False

                    if item['season'] != 0 and item['season'] != None:
                        title = title + ', sezon ' + str(item['season'])

                subtitle = item.get('sub_title', None)
                if subtitle != None and len(subtitle) > 0:
                    title = title + ' - ' + subtitle.encode('UTF-8')

                params = {'service': SERVICE, 'category': item['type'], 'id': item['id'], 'title': title.strip(),
                          'icon': icon, 'fanart': icon}

                duration = item.get('end_credits_start', None)  # Czas trwania to |end_credits_start| lub |run_time|
                if duration != None and len(duration) == 8:  # format 00:23:34
                    l = duration.split(':')
                    sec = int(l[0]) * 3600 + int(l[1]) * 60 + int(l[2])
                    params.update({'duration': str(sec)})

                rating = item.get('rating', None)
                if rating != None and len(rating) > 0:
                    if rating != '0':
                        params.update({'mpaa': 'Od ' + rating + ' lat'})
                    else:
                        params.update({'mpaa': 'Bez ograniczeń'})

                plot = item.get('lead', None)
                if plot != None:
                    params.update({'plot': plot.replace('&quot;', '"').encode('UTF-8')})
                if item['type'] == 'episode':
                    self.gui.playVideo(params, isPlayable=True, params_keys_needed=tvn_url_keys)
                else:
                    self.gui.addDir(params, params_keys_needed=tvn_url_keys)
        else:  # listuj sezony
            for item in data['seasons']:
                if item['thumbnail'] != None:
                    icon = self.api.getImage(item['thumbnail'][0]['url'])
                else:
                    icon = THUMB_SERVICE
                t = data['items'][0]['title'].encode('UTF-8')
                params = {'service': SERVICE, 'category': item['type'], 'id': item['id'],
                          'title': t + ' - ' + item['name'].encode('UTF-8'), 'icon': icon, 'fanart': icon,
                          'seriesId': item['vdp_id']}
                self.gui.addDir(params, params_keys_needed=tvn_url_keys)
        self.gui.endDir(sort)

    def getVideoUrl(self, args):
        ret = ''
        fallback = False

        if tvn_proxy == 'true':
            useProxy = True
        else:
            useProxy = False

        data = self.api.getAPI(args, useProxy)

        # brak video - spróbuj w innej wersji api
        if data['item']['videos']['main']['video_content'] == None or len(
                data['item']['videos']['main']['video_content']) == 0 or \
                ('video_content_license_type' in data['item']['videos']['main'] and data['item']['videos']['main'][
                    'video_content_license_type'] == 'WIDEVINE'):  # DRM v3.6
            data = self.api.getAPI(args, useProxy, 'fallback')
            fallback = True
        if not ('item' in data) or not ('videos' in data['item']) or not (
            'main' in data['item']['videos']):  # proba uzycia Api zapasowego czasami konczy sie strzalem w próżnię
            d = xbmcgui.Dialog()
            d.ok(SERVICE, 'Brak materiału video', '')
            exit()
        # znajdz jakosc z settings wtyczki
        if data['item']['videos']['main']['video_content'] != None and len(
                data['item']['videos']['main']['video_content']) != 0:
            url = ''
            for item in data['item']['videos']['main']['video_content']:
                if item['profile_name'].encode('UTF-8') == tvn_quality:
                    url = item['url']  # znalazlem wybrana jakosc
                    break;
            # jesli jakosc nie znaleziona (lub Maksymalna) znajdz pierwsza najwyzsza jakosc
            if url == '':
                for q in qualities:
                    for item in data['item']['videos']['main']['video_content']:
                        if item['profile_name'].encode('UTF-8') == q:
                            url = item['url']
                            break
                    if url != '':
                        break
            if fallback:
                pl = platform[tvn_platform]['fallback']
            else:
                pl = tvn_platform
            # dodaj token tylko do Androida
            if pl != 'Samsung':  # pl == AndroidX
                ret = self.api.generateToken(url).encode('UTF-8')
            else:
                query_data = {'url': url, 'use_host': True, 'host': platform[pl]['host'], 'use_header': False,
                              'use_cookie': False, 'use_post': False, 'return_data': True}
                try:
                    ret = self.common.getURLRequestData(query_data)
                except Exception, exception:
                    traceback.print_exc()
                    self.exception.getError(str(exception))
                    exit()

        # 02/07/2016
        if useProxy:
            opener = urllib2.build_opener(NoRedirectHandler())
            urllib2.install_opener(opener)
            response = urllib2.urlopen(urllib2.Request(ret))
            ret = response.info().getheader('Location')
            ret = re.sub('n-(.+?)\.dcs\.redcdn\.pl', 'n-1-25.dcs.redcdn.pl', ret)

        return ret

    def handleService(self):
        params = self.parser.getParams()
        category = str(self.parser.getParam(params, "category"))
        id = str(self.parser.getParam(params, "id"))
        seriesId = str(self.parser.getParam(params, "seriesId"))

        # MAINMENU
        if category == 'None':
            if self.api.geoCheck():
                self.getMenu('m=mainInfo')

        # WSZYSTKO
        if category != 'None' and category != 'episode' and seriesId == 'None':
            self.getItems('m=getItems&sort=newest&limit=500&type=' + category + '&id=' + id)

        # ODCINKI W SEZONIE
        if seriesId != 'None':
            self.getItems('m=getItems&sort=newest&limit=500&type=series&id=' + seriesId + '&season=' + id)

        # VIDEO
        if category == 'episode':
            videoUrl = self.getVideoUrl('m=getItem&type=' + category + '&id=' + id)
            mrknow_pCommon.mystat(videoUrl)
            self.gui.LOAD_AND_PLAY_VIDEO_WATCHED(videoUrl)


class NoRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        infourl = urllib.addinfourl(fp, headers, req.get_full_url())
        infourl.status = code
        infourl.code = code
        return infourl

    http_error_300 = http_error_302
    http_error_301 = http_error_302
    http_error_303 = http_error_302
    http_error_307 = http_error_302


class API:
    def __init__(self):
        #self.exception = sdErrors.Exception()
        self.common = mrknow_pCommon.common()
        #self.proxy = sdCommon.proxy()

    def geoCheck(self):
        ret = True
        if tvn_proxy != 'true':
            data = self.getAPI('m=checkClientIp', False)
            if data['result'] == False:
                d = xbmcgui.Dialog()
                d.ok(SERVICE, 'Serwis niedostepny na terenie twojego kraju.',
                     'Odwiedz sd-xbmc.org w celu uzyskania dostepu.')
            ret = data['result']
        return ret

    def getAPIurl(self, fallback=''):
        if fallback == 'fallback':
            pl = platform[tvn_platform]['fallback']
        else:
            pl = tvn_platform
        return MAINURL + '/api/?platform=%s&terminal=%s&format=json&authKey=%s&v=%s&' % (
        platform[pl]['platform'], platform[pl]['terminal'],
        platform[pl]['authKey'], platform[pl]['api'])

    def getAPI(self, args, useProxy=False, fallback=''):

        url = self.getAPIurl(fallback) + args

        if useProxy:
            url = self.proxy.useProxy(url)

        if fallback == 'fallback':
            pl = platform[tvn_platform]['fallback']
        else:
            pl = tvn_platform
        query_data = {'url': url, 'use_host': True, 'host': platform[pl]['host'], 'use_header': False,
                      'use_cookie': False, 'use_post': False, 'return_data': True}
        try:
            data = self.common.getURLRequestData(query_data)
            if (useProxy and self.proxy.isAuthorized(data)) or useProxy == False:
                result = _json.loads(data)
                if not 'status' in result or result['status'] != 'success':
                    d = xbmcgui.Dialog()
                    d.ok(SERVICE, 'Blad API', '')
                    exit()
                return result
            else:
                exit()

        except Exception, exception:
            traceback.print_exc()
            self.exception.getError(str(exception))
            exit()

    def getImage(self, path):
        return IMAGEURL + path + '?quality=85&dstw=870&dsth=560&type=1'

    def generateToken(self, url):
        url = url.replace('http://redir.atmcdn.pl/http/', '')
        SecretKey = 'AB9843DSAIUDHW87Y3874Q903409QEWA'
        iv = 'ab5ef983454a21bd'
        KeyStr = '0f12f35aa0c542e45926c43a39ee2a7b38ec2f26975c00a30e1292f7e137e120e5ae9d1cfe10dd682834e3754efc1733'
        salt = sha1()
        salt.update(os.urandom(16))
        salt = salt.hexdigest()[:32]

        tvncrypt = crypto.cipher.aes_cbc.AES_CBC(SecretKey, padding=crypto.cipher.base.noPadding(), keySize=32)
        key = tvncrypt.decrypt(binascii.unhexlify(KeyStr), iv=iv)[:32]

        expire = 3600000L + long(time.time() * 1000) - 946684800000L

        unencryptedToken = "name=%s&expire=%s\0" % (url, expire)

        pkcs5_pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
        pkcs5_unpad = lambda s: s[0:-ord(s[-1])]

        unencryptedToken = pkcs5_pad(unencryptedToken)

        tvncrypt = crypto.cipher.aes_cbc.AES_CBC(binascii.unhexlify(key), padding=crypto.cipher.base.noPadding(),
                                                 keySize=16)
        encryptedToken = tvncrypt.encrypt(unencryptedToken, iv=binascii.unhexlify(salt))
        encryptedTokenHEX = binascii.hexlify(encryptedToken).upper()

        return "http://redir.atmcdn.pl/http/%s?salt=%s&token=%s" % (url, salt, encryptedTokenHEX)