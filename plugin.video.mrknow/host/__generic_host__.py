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
from resources.lib.libraries import history

__version__ = '0.0.0.1'

class GenericHost():
    __metaclass__ = abc.ABCMeta

    """
    Generic Host
    ___
    """
    from resources.lib.libraries import control
    from resources.lib.libraries import client
    from resources.lib.libraries import cache
    from resources.lib.libraries import fixtxt


    scriptID = 'plugin.video.mrknow'
    host = 'generichost'
    icon =''
    scriptname = "Filmy online www.mrknow.pl - %s" % host
    systime = (datetime.datetime.utcnow()).strftime('%Y%m%d%H%M%S%f')

    MENU_TAB = {1: "Start"}

    def __init__(self):
        ptv = xbmcaddon.Addon(self.scriptID)
        self.parser = mrknow_Parser.mrknow_Parser()
        self.control.log('Starting %s' % self.scriptname)
        self.s = requests.session()
        self.history = history.history()

    def request(self,url, headers={}, utf=True):
        try:
            myheaders = {}
            for i in headers:
                myheaders[i] = headers[i]
            myheaders['User-Agent'] = self.cache.get(self.control.randomagent, 1)
            self.control.log('RandomAgent %s' % str(myheaders))
            link = self.s.get(url, headers=myheaders, verify=False).text
            if utf:
                try:
                    #link = unicode(link, 'utf-8')
                    link = link.encode('utf-8', 'ignore')
                except Exception as e:
                    self.control.log('Request encoding error: %s' % e)
                    pass
            return link
        except:
            return ''

    def listsMainMenu(self, table):
        for val in table:
            #control.log('%s |' %(val))
            self.add(self.host, 'main-menu', val['mod'], val['title'], 'None', 'None', True, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsHistory(self, table):
        print "here"

        for i in range(len(table)):
            if table[i] <> '':
                self.add(self.host, 'history', 'items', table[i], 'DefaultFolder.png', 'None', True, True)
        #xbmcplugin.endOfDirectory(int(sys.argv[1]))
        self.control.directory(int(sys.argv[1]))

    def searchInputText(self,SERVICE, heading='Wyszukaj'):
        text = u''
        k = xbmc.Keyboard('',heading, False)
        k.doModal()
        if (k.isConfirmed()):
            text = k.getText()

            text = text.encode('utf-8')
            #try:
            #    text = text.encode('utf-8', 'ignore')
            #except:
            #    text = text.decode('ascii', 'xmlcharrefreplace')

            if text != None or text != '':
                self.control.log('Szukaj: %s' % (text))
                self.history.addHistoryItem(SERVICE, text)
                return urllib.quote_plus(text)
            return None
        else:
            return None

    def add(self, service, name, category, title, iconimage, url, folder = True, isPlayable = True):
        u=sys.argv[0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + urllib.quote_plus(self.fixtxt.encode_obj(title)) + "&url=" + urllib.quote_plus(url) + "&icon=" + urllib.quote_plus(iconimage.encode("ascii","xmlcharrefreplace"))
        #self.control.log('MYURL:%s' % u)
        if iconimage == '':
            iconimage = "DefaultVideo.png"
        liz=xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if isPlayable:
            liz.setProperty("IsPlayable", "true")
        liz.setInfo( type="Video", infoLabels={ "Title": title } )
        #xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=folder)
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
        return ok

    def add2(self, i):

        if not 'originaltitle' in i:
            i.update({'originaltitle': i['title']})
        if not 'year' in i:
            i.update({'year': ''})
        if not 'isplayable' in i:
            i['isplayable'] = 'false'
        if not 'url' in i:
            i['url']=''

        sysaddon = sys.argv[0]
        syshandle = int(sys.argv[1])
        #self.control.log('SYSHANDLE: %s' % syshandle)
        addonPoster, addonBanner = self.control.addonPoster(), self.control.addonBanner()
        addonFanart, settingFanart = self.control.addonFanart(), self.control.setting('fanart')
        isPlayable = 'true' if i['isplayable'] == 'true' else 'false'
        isFolder = False if isPlayable == 'true' else True

        label = '%s (%s)' % (i['title'], i['year'])
        title, year =  i['title'], i['year']
        sysname = urllib.quote_plus('%s' % (i['name']))
        syscat = urllib.quote_plus('%s' % i['category'])
        systitle = urllib.quote_plus(self.fixtxt.encode_obj(title))
        service = i['service']

        meta = dict((k, v) for k, v in i.iteritems() if not v == '0')
        meta.update({'mediatype': 'movie'})
        # meta.update({'trailer': 'plugin://script.extendedinfo/?info=playtrailer&&id=%s' % imdb})
        if not 'duration' in i:
            meta.update({'duration': ''})
        elif i['duration'] == '0':
            meta.update({'duration': '90'})
        try:
            meta.update({'duration': str(int(meta['duration']) * 60)})
        except:
            pass
        if not 'originaltitle' in meta:
            meta.update({'originaltitle': meta['title']})
        if not 'year' in meta:
            meta.update({'year': '2017'})

        sysmeta = urllib.quote_plus(json.dumps(meta))

        url = '%s?service=%s&name=%s&category=%s&title=%s&year=%s&meta=%s&url=%s' % (
        sysaddon, service, sysname, syscat, systitle, year, sysmeta, i['url'])
        #sysurl = urllib.quote_plus(url)
        #path = '%s?action=play&title=%s&year=%s&' % (sysaddon, systitle, year)

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
        #self.control.log('META %s' % meta)
        item.setArt(art)
        item.setProperty('IsPlayable', isPlayable)
        item.setInfo(type='Video', infoLabels=meta)

        self.control.addItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)

    def dirend(self,syshandle):
        self.control.directory(syshandle)
        self.control.content(syshandle, 'movies')
        self.control.directory(syshandle, cacheToDisc=True)
        #self.views.setView('movies', {'skin.estuary': 55, 'skin.confluence': 500})


    def LOAD_AND_PLAY_VIDEO(self, videoUrl, params):
        ok = True
        if videoUrl == '' or videoUrl == None:
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu.', 'Może to chwilowa awaria.', 'Spróbuj ponownie za jakiś czas')
            return True

        #liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
        #liz.setInfo(type="Video", infoLabels={"Title": title,})
        try:
            title = params['title']
        except:
            title = ''
        try:
            icon = params['icon']
        except:
            icon = ''

        liz=xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon, path=videoUrl )
        liz.setInfo( type="video", infoLabels={ "Title": title})
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

        return ok

    def urlresolve(self,url):
        linkVideo=''
        hmf = urlresolver.HostedMediaFile(url=url, include_disabled=True, include_universal=False)
        if hmf.valid_url() == True:
            linkVideo = hmf.resolve()
            #self.control.log('3 PLAYYYYYYERRRRRRRRRRRR [%s]' % linkVideo)
        else:
            self.control.log('3 PLAYYYYYYERRRRRRRRRRRR not valid ')
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
        try:
            self.control.log (u"DANE:[%s]" % (name, category,url,title,icon, params))
        except:
            pass

        if name == None:
            self.listsMainMenu(self.MENU_TAB)
        if category == 'find':
            key = self.searchInputText(self.host)
            if not key == None:
                if len(key)>0 :
                    #self.control.log('XXXXXXXX %s |%s|' % (key, len(key)))
                    self.listsSearchResults(key)

        if category == 'history':
            t = self.history.loadHistoryFile(self.host)
            self.listsHistory(t)

        if name == 'history':
            self.listsSearchResults(title)

        if name == 'main-menu':
            self.sub_handleService(params)
        if name == 'categories-menu':
            self.sub_handleService(params)
        if name == 'items-menu':
            self.sub_handleService(params)
        if name == 'playselectedmovie':
            data = self.getMovieLinkFromXML(url)
            self.control.log('url: ' + str(data))
            if data != None:
                self.LOAD_AND_PLAY_VIDEO(data,params={})

