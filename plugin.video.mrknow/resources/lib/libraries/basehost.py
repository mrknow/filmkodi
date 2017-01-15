#    Mrknow XBMC Addon
#    Copyright (C) 2016 mrknow
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import abc
import sys
import urllib
import xbmcgui, xbmc, xbmcaddon, xbmcplugin


abstractstaticmethod = abc.abstractmethod

class abstractclassmethod(classmethod):
    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)


class MrknowHost(object):
    __metaclass__ = abc.ABCMeta



    @abc.abstractmethod
    def add(self, service, name, category, title, iconimage, url, desc, rating, folder=True, isPlayable=True, page='',year=''):
        u = sys.argv[
                0] + "?service=" + service + "&name=" + name + "&category=" + category + "&title=" + title + "&url=" + urllib.quote_plus(
            url) + "&icon=" + urllib.quote_plus(iconimage) + "&page=" + urllib.quote_plus(
            page) + "&year=" + urllib.quote_plus(year)
        # log.info(str(u))
        if name == 'main-menu' or name == 'categories-menu' or name == 'categories-menu1':
            title = category
        if iconimage == '':
            iconimage = "DefaultVideo.png"
        liz = xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if isPlayable:
            liz.setProperty("IsPlayable", "true")
        liz.setInfo(type="Video", infoLabels={"Title": title})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=folder)

    @abc.abstractmethod
    def LOAD_AND_PLAY_VIDEO(self, url, title, icon, year='', plot='', id=''):
        progress = xbmcgui.DialogProgress()
        progress.create('Postęp', '')
        message = "Pracuje...."
        progress.update(10, "", message, "")
        xbmc.sleep(1000)
        progress.update(30, "", message, "")
        progress.update(50, "", message, "")
        VideoLink = ''
        subs = ''
        VideoLink = self.up.getVideoLink(url)
        if isinstance(VideoLink, basestring):
            videoUrl = VideoLink
        else:
            videoUrl = VideoLink[0]
            subs = VideoLink[1]
        progress.update(70, "", message, "")
        if videoUrl == '':
            progress.close()
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu', 'Może to chwilowa awaria.', 'Spróbuj ponownie za jakiś czas')
            return False
        if icon == '' or icon == 'None':
            icon = "DefaultVideo.png"
        if plot == '' or plot == 'None':
            plot = ''
        liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon, path=videoUrl)
        liz.setInfo(type="video", infoLabels={"Title": title})
        xbmcPlayer = xbmc.Player()
        progress.update(90, "", message, "")
        progress.close()
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

