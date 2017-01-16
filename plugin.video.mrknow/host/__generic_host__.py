# -*- coding: utf-8 -*-

"""
    Kodi Generic Host
    Copyright (C) 2017  mrknow

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import abc
import urllib, urllib2, re, os, sys
import json
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
import urllib
import mrknow_Parser
import urlresolver9 as urlresolver
import requests
import datetime

class GenericHost():
    __metaclass__ = abc.ABCMeta

    """
    Generic Host
    ___
    """
    from resources.lib.libraries import control
    from resources.lib.libraries import client
    from resources.lib.libraries import cache
    from resources.lib.libraries import views

    scriptID = 'plugin.video.mrknow'
    host = 'generichost'
    scriptname = "Filmy online www.mrknow.pl - %s" % host
    systime = (datetime.datetime.utcnow()).strftime('%Y%m%d%H%M%S%f')

    MENU_TAB = {1: "Start"}

    def __init__(self):
        ptv = xbmcaddon.Addon(self.scriptID)
        self.parser = mrknow_Parser.mrknow_Parser()
        self.control.log('Starting %s' % self.scriptname)
        self.s = requests.session()

    def request(self,url):
        try:
            headers = {}
            headers['User-Agent'] = self.cache.get(self.control.randomagent, 1)
            self.control.log('RandomAgent %s' % headers['User-Agent'])
            link = self.s.get(url, headers=headers, verify=False).text
            return link
        except:
            pass

    def listsMainMenu(self, table):
        for val in table:
            #control.log('%s |' %(val))
            self.add(self.host, 'main-menu', val['mod'], val['title'], 'None', 'None', 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def searchInputText(self):
        text = None
        k = xbmc.Keyboard()
        k.doModal()
        if (k.isConfirmed()):
            text = k.getText()
            self.control.log('Szukaj:'+str(text))
            return urllib.quote_plus(text)
        else:
            return

    def add(self, service, name, category, title, iconimage, url, desc, rating, folder = True, isPlayable = True):
        #self.control.log("service:%s, name:%s, category:%s, title:%s, iconimage:%s, url:%s, desc:%s, rating:%s" %(service, name, category, title, iconimage, url, desc, rating))
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + urllib.quote_plus(title) + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage.encode("ascii","ignore"))
        #log.info(str(u))
        #if name == 'main-menu' or name == 'categories-menu':
        #    title = category
        if iconimage == '':
            iconimage = "DefaultVideo.png"
        liz=xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if isPlayable:
            liz.setProperty("IsPlayable", "true")
        liz.setInfo( type="Video", infoLabels={ "Title": title } )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder)

    def add2(self, i):
        sysaddon = sys.argv[0]
        syshandle = int(sys.argv[1])
        addonPoster, addonBanner = self.control.addonPoster(), self.control.addonBanner()
        addonFanart, settingFanart = self.control.addonFanart(), self.control.setting('fanart')
        isPlayable = 'true' if i['isplayable'] == 'true' else 'false'

        label = '%s (%s)' % (i['title'], i['year'])
        title, year =  i['originaltitle'], i['year']
        sysname = urllib.quote_plus('%s (%s)' % (title, year))
        systitle = urllib.quote_plus(title)
        service = i['service']

        meta = dict((k, v) for k, v in i.iteritems() if not v == '0')
        meta.update({'mediatype': 'movie'})
        # meta.update({'trailer': 'plugin://script.extendedinfo/?info=playtrailer&&id=%s' % imdb})
        if not 'duration' in i:
            meta.update({'duration': '90'})
        elif i['duration'] == '0':
            meta.update({'duration': '90'})
        try:
            meta.update({'duration': str(int(meta['duration']) * 60)})
        except:
            pass

        sysmeta = urllib.quote_plus(json.dumps(meta))

        url = '%s?service=%s&name=playselectedmovie&title=%s&year=%s&meta=%s&url=%s' % (
        sysaddon, service, systitle, year, sysmeta, i['url'])
        sysurl = urllib.quote_plus(url)

        path = '%s?action=play&title=%s&year=%s&' % (sysaddon, systitle, year)

        item = self.control.item(label=label)

        art = {}

        if 'poster3' in i and not i['poster3'] == '0':
            art.update({'icon': i['poster3'], 'thumb': i['poster3'], 'poster': i['poster3']})
        elif 'poster' in i and not i['poster'] == '0':
            art.update({'icon': i['poster'], 'thumb': i['poster'], 'poster': i['poster']})
        elif 'poster2' in i and not i['poster2'] == '0':
            art.update({'icon': i['poster2'], 'thumb': i['poster2'], 'poster': i['poster2']})
        else:
            art.update({'icon': addonPoster, 'thumb': addonPoster, 'poster': addonPoster})

        if 'banner' in i and not i['banner'] == '0':
            art.update({'banner': i['banner']})
        else:
            art.update({'banner': addonBanner})

        if 'clearlogo' in i and not i['clearlogo'] == '0':
            art.update({'clearlogo': i['clearlogo']})

        if 'clearart' in i and not i['clearart'] == '0':
            art.update({'clearart': i['clearart']})

        if settingFanart == 'true' and 'fanart2' in i and not i['fanart2'] == '0':
            item.setProperty('Fanart_Image', i['fanart2'])
        elif settingFanart == 'true' and 'fanart' in i and not i['fanart'] == '0':
            item.setProperty('Fanart_Image', i['fanart'])
        elif not addonFanart == None:
            item.setProperty('Fanart_Image', addonFanart)

        item.setArt(art)
        item.setProperty('IsPlayable', isPlayable)
        item.setInfo(type='Video', infoLabels=meta)

        self.control.addItem(handle=syshandle, url=url, listitem=item, isFolder=False)

    def dirend(self,syshandle):
        self.control.directory(syshandle)
        self.control.content(syshandle, 'movies')
        self.control.directory(syshandle, cacheToDisc=True)
        #self.views.setView('movies', {'skin.estuary': 55, 'skin.confluence': 500})


    def LOAD_AND_PLAY_VIDEO(self, videoUrl, title='', icon=''):
        ok = True
        if videoUrl == '' or videoUrl == None:
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu.', 'Może to chwilowa awaria.', 'Spróbuj ponownie za jakiś czas')
            return True

        #liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
        #liz.setInfo(type="Video", infoLabels={"Title": title,})
        liz=xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon, path=videoUrl )
        liz.setInfo( type="video", infoLabels={ "Title": title})
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

        return ok

    def urlresolve(self,url):
        linkVideo=''
        hmf = urlresolver.HostedMediaFile(url=url, include_disabled=True, include_universal=False)
        if hmf.valid_url() == True: linkVideo = hmf.resolve()
        self.control.log('XYXYXYXYXYYXYXYX   YXYXYYX   PLAYYYYYYERRRRRRRRRRRR [%s]' % linkVideo)
        #if linkVideo == False:
        #    linkVideo = self.up.getVideoLink(srcVideo, url)
        return linkVideo

    def handleService(self):
    	params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        if name == None:
            self.listsMainMenu(self.MENU_TAB)
        elif name == 'playselectedmovie':
            self.control.log('url: ' + str(url))
            self.LOAD_AND_PLAY_VIDEO(url,'','')
        else:
            self.control.log('AAAAAAAAAAAA')

    def byteify(self, input):
        if isinstance(input, dict):
            return {self.byteify(key):self.byteify(value) for key,value in input.iteritems()}
        elif isinstance(input, list):
            return [self.byteify(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input