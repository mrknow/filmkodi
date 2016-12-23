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

abstractstaticmethod = abc.abstractmethod

class abstractclassmethod(classmethod):
    __isabstractmethod__ = True

    def __init__(self, callable):
        callable.__isabstractmethod__ = True
        super(abstractclassmethod, self).__init__(callable)


class MrknowHost(object):
    __metaclass__ = abc.ABCMeta
    '''
    Your plugin needs to implement the abstract methods in this interface if
    it wants to be able to resolve URLs
    '''

    @abc.abstractmethod
    def get_media_url(self, host, media_id):
        '''
        The method that does the actual resolving. You must implement this method.

        Args:
            host (str): the host the link is on
            media_id (str): the media_id the can be returned by get_host_and_id

        Returns:
            If the media_id could be resolved, a string containing the direct
            URL to the media file, if not, raises ResolverError.
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def get_url(self, host, media_id):
        '''
        The method that converts a host and media_id into a valid url

        Args:
            host (str): the host the link is on
            media_id (str): the media_id the can be returned by get_host_and_id

        Returns:
            a valid url on the host this resolver resolves
        '''
        raise NotImplementedError

    def add(self, service, name, category, title, iconimage, url, desc, rating, folder=True, isPlayable=True, page='',
            year=''):
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

    def handleService(self):
        params = self.parser.getParams()
        name = self.parser.getParam(params, "name")
        category = self.parser.getParam(params, "category")
        url = self.parser.getParam(params, "url")
        title = self.parser.getParam(params, "title")
        icon = self.parser.getParam(params, "icon")
        page = self.parser.getParam(params, "page")
        print("Dane", sys.argv[0], sys.argv[1])
        if page == None:
            page = ''

        if name == None:
            self.listsMainMenu(MENU_TAB)
        elif name == 'main-menu' and category == 'Kategorie':
            log.info('Jest Kategoria: ' + str(url))
            self.listsCategoriesMenu()
        elif name == 'main-menu' and category == 'Nowości':
            log.info('Jest Nowości: ')
            self.listsItemsW(mainUrl)
        elif name == 'main-menu' and category == 'Wszystkie':
            self.listsItemsW(WszyUrl)
        elif name == 'main-menu' and category == "Szukaj":
            key = self.searchInputText()
            # self.listsItems(self.getSearchURL(key),page)
            self.listsItemsW(self.getSearchURL(key))
        elif name == 'categories-menu1' and category != 'None':
            self.listsItemsW(url)
        elif name == 'categories-menu' and category != 'None':
            log.info('url: ' + str(url))
            self.listsItemsW(url)
            # self.listsItems(url,page)
        if name == 'playSelectedMovie':
            log.info('playSelectedMovie: ' + str(url))
            data = self.getMovieLinkFromXML(url)
            self.LOAD_AND_PLAY_VIDEO(data, title, icon)

    # @abc.abstractmethod
    def get_host_and_id(self, url):
        '''
        The method that converts a host and media_id into a valid url

        Args:
            url (str): a valid url on the host this resolver resolves

        Returns:
            host (str): the host the link is on
            media_id (str): the media_id the can be returned by get_host_and_id
        '''
        r = re.search(self.pattern, url, re.I)
        # print r.group(3)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        '''
        Determine whether this plugin is capable of resolving this URL. You must
        implement this method.

        Returns:
            True if this plugin thinks it can hangle the web_url or host
            otherwise False.
        '''
        if isinstance(host, basestring):
            host = host.lower()

        if url:
            return re.search(self.pattern, url, re.I) is not None
        else:
            return any(host in domain.lower() for domain in self.domains)

    @classmethod
    def isUniversal(cls):
        '''
            You need to override this to return True, if you are implementing a univeral resolver
            like real-debrid etc., which handles multiple hosts
        '''
        return False

    def login(self):
        '''
        This method should perform the login to the file host site. This will
        normally involve posting credentials (stored in your plugin's settings)
        to a web page which will set cookies.
        '''
        return True



    @classmethod
    def set_setting(cls, key, value):
        #common.set_setting('%s_%s' % (cls.__name__, key), str(value))
        return True

    @classmethod
    def get_setting(cls, key):
        #return common.get_setting('%s_%s' % (cls.__name__, key))
        return True

    @classmethod
    def _get_priority(cls):
        try:
            return int(cls.get_setting('priority'))
        except:
            return 100

    @classmethod
    def _is_enabled(cls):
        # default behaviour is enabled is True if resolver is enabled, or has login set to "true", or doesn't have the setting
        return cls.get_setting('enabled') == 'true' and cls.get_setting('login') in ['', 'true']


    #def _default_get_url(self, host, media_id, template=None):
    #    if template is None: template = 'http://{host}/embed-{media_id}.html'
    #    host = self._get_host(host)
    #    return template.format(host=host, media_id=media_id)