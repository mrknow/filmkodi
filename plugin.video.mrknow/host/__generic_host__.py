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
import urllib, urllib2, re, os, sys, math
import xbmcgui, xbmc, xbmcaddon, xbmcplugin
import urllib
import mrknow_Parser
import urlresolver9 as urlresolver


#sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib"))


class GenericHost():
    __metaclass__ = abc.ABCMeta

    """
    Generic Host
    ___
    """
    from lib import control
    from lib import client

    scriptID = 'plugin.video.mrknow'
    host = 'generichost'
    scriptname = "Filmy online www.mrknow.pl - %s" % host

    MENU_TAB = {1: "Start"}

    def __init__(self):
        ptv = xbmcaddon.Addon(self.scriptID)
        self.parser = mrknow_Parser.mrknow_Parser()
        self.control.log('Starting %s' % self.scriptname)

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