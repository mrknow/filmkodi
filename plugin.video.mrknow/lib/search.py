# -*- coding: utf-8 -*-

import xbmcgui, xbmc, xbmcaddon, xbmcplugin
import urllib
import sys
import os
from utils import convert
import common


# TODO: Localizaton
def _(t):   # --- XXX  Only temporary  XXX ---
    texts = {
        u'Search':       u'Szukaj',
        u'New search':   u'Nowe wyszukiwanie',
        u'Remove':       u'Usuń',
        u'Rename':       u'Zmień',
        u'Clean':        u'Wyczyść historię',
        u'Edit search':  u'Edycja wyszukiwania',
    }
    t = unicode(t)
    return texts.get(t, t)


scriptID = 'plugin.video.mrknow'
addon = xbmcaddon.Addon(scriptID)


class Search(object):
    """Host search handler.

    Search() handle search box (with history, count > 1).

    Args:
        url           Host search URL with '%(quoted)s or '%(text)s' for unqouted.
        pluginUrl     URL for plugin. argv[0]+'?service=SERVICE' is used if None.
        service       Service (host) name, used in history filename.
        listItemsFun  Callback function to add movie items from given URL.
        count         History length, 0 - off, 1 - last search only,
                      2 or more – history submenu. Default 10.
        title         Title in keyboard box, default "Search".
        argv          Plugin paramters, sys.argv is used if None.

    Examples:

        # Just get search text.
        s = Search()
        text = s.handleService()

        # Just get search url.
        s = Search(url='http://example.com/search?q=%(quoted)s&order=a', service='cdapl')
        url = s.handleService()
        if url:
            if url is not True:  # skip user cancel
                self.listsItems(url)
            return   # return from plugin handleService()

        # Just do it all.
        s = Search(url='http://example.com/search?q=%(quoted)s&order=a',
                   listItemsFun=self.listsItems, service='cdapl')
        if s.handleService():
            return   # return from plugin handleService()

        # And even more.
        s = Search(count=10,
                   url='http://example.com/search?q=%(quoted)s&order=a',
                   pluginUrl=sys.argv[0] + '?service=cdapl&category=search&answer=42',
                   listItemsFun=self.listsItems,
                   service='cdapl')
        if s.handleService():
            return   # return from plugin handleService()
    """

    def __init__(self, url=None, pluginUrl=None, service=None, listItemsFun=None, count=None,
                 title=None, argv=None):
        self.url = url
        self.listItemsFun = listItemsFun
        self.count = 10 if count is None else count
        self.title = title or _('Search')
        self.argv = sys.argv if argv is None else argv
        self.service = service
        self.pluginUrl = pluginUrl
        self._addon = xbmcaddon.Addon()
        self._addonHandle = int(self.argv[1])
        self._spath = xbmc.translatePath('special://profile/addon_data/%s/search' % self._addon.getAddonInfo('id'))
        self.history = []
        self.loadHistory()

    def inputText(self, title=None, text=None):
        """Grab search text from user."""
        kbd = xbmc.Keyboard()
        if title:
            kbd.setHeading(title)
        if text:
            kbd.setDefault(text)
        kbd.doModal()
        if kbd.isConfirmed():
            return kbd.getText()

    def buildPluginUrl(self, **kwargs):
        """Create internal plugin URL with given arguments. [internal]"""
        url = self.pluginUrl or (self.argv[0] + '?service=%s' % (self.service or ''))
        if kwargs:
            url += '&' if '?' in url else '?'
            url += convert.urlencode(kwargs)
        return url

    def addMenuItem(self, name, iconImage=None, folder=True, menu=True, **kwargs):
        """Add one submenu item to the list. [internal]"""
        if not iconImage:
            iconImage = 'DefaultAddonsSearch.png'
        # general menu item
        # liz = xbmcgui.ListItem(title, iconImage="DefaultFolder.png", thumbnailImage=iconImage)
        # liz.setInfo(type="Video", infoLabels={"Title": title})
        url = self.buildPluginUrl(name=name, **kwargs)
        xbmc.log('SEARCH: create menu item %s, query:"%s", url:"%s"' % (name, kwargs.get('query'), url))
        li = xbmcgui.ListItem(kwargs.get('title', ''), iconImage="DefaultFolder.png", thumbnailImage=iconImage)
        li.addContextMenuItems([
            (_('Remove'), 'RunPlugin(%s)' % (url + '&action=remove')),
            (_('Rename'), 'RunPlugin(%s)' % (url + '&action=rename')),
            (_('Clean'),  'RunPlugin(%s)' % (url + '&action=clean')),
        ])
        xbmcplugin.addDirectoryItem(handle=self._addonHandle, url=url, listitem=li, isFolder=folder)

    def listMenu(self):
        """Create menu list (submenu items). [internal]"""
        icon = os.path.join(common.Paths.imgDir, 'new_search.png')
        self.addMenuItem('.search.new', menu=False, iconImage=icon, title='[B]%s[/B]' % _('New search'))
        icon = os.path.join(common.Paths.imgDir, 'search_item.png')
        for query in self.history:
            self.addMenuItem('.search.query', iconImage=icon, query=query, title=query)
        #wnd = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        #wnd.getControl(wnd.getFocusId()).selectItem(self._selectItem)
        xbmcplugin.endOfDirectory(self._addonHandle, cacheToDisc=False)
        return True

    def listSearch(self, text):
        """Create list of found movies. [interal]"""
        if text is None:
            return True
        if not self.url:
            return text
        q = urllib.quote_plus(text)
        if '%s' in self.url:
            # shortcut, just URL with simple "%s" for quoted query
            url = self.url % q
        else:
            # full format URL with "%(quoted)s" for quoted query
            # and "%(text)s" for unquoted query
            url = self.url % (dict(q=q, quoted=q, text=text))
        if self.listItemsFun:
            xbmc.log('SEARCH: searching "%s"' % url)
            self.listItemsFun(url)
        return url

    def updateHistory(self, select=None):
        """Update changed history, save and refresh page. [internal]
        
        Args:
            select  if not None, item to select (0 - New search, 1... - history)
        """
        if len(self.history) > self.count:
            # limit the list
            self.history = self.history[ : self.count]
        self.saveHistory()
        xbmc.executebuiltin("Container.Refresh")
        # select - ignored, I can select item after refresh

    def addSearchToHistory(self, text):
        """Add new search to the history list"""
        if text and self.count:
            if text in self.history:
                if self.history[0] == text:
                    return  # already on the top
                # move alredy used search to the top
                self.history.remove(text)
            # put on the top
            self.history.insert(0, text)
            self.updateHistory(select=1)

    def handleNewSearch(self):
        """New search dailog. [interal]"""
        text = None
        if self.count == 1:
            text = 'Last search'
        text = self.inputText(text=text, title=self.title)
        self.addSearchToHistory(text)
        return self.listSearch(text)

    def handleAction(self, action, query=None):
        """Handle action from context menu on query."""
        if action == 'remove':
            if query and query in self.history:
                index = self.history.index(query)
                del self.history[index]
                self.updateHistory(select=index-1)  
        elif action == 'rename':
            if query and query in self.history:
                text = self.inputText(text=query, title=_('Edit search'))
                if text and text != query:
                    index = self.history.index(query)
                    self.history[index] = text
                    self.updateHistory(select=index)
        elif action == 'clean':
            if self.history:
                self.history = []
                self.updateHistory()
        else:
            xbmcgui.Dialog().ok('Action', 'Unknown action', action)
        return True

    def handleService(self, params=None, force=False):
        """Handle plugin service URL

        Args:
            params   Plugin parameters or None to use defaults.
            force    Force search handling, don't check if it's correct main search menu

        Returns:
            search text if self.url doesn't exist
            search URL if self.url exists, and extra call self.listItemsFun if exists
            True if handled but user cancel search or on submenu
            False if not handled.
        """
        if params is None:
            params = convert.urldecode(self.argv[2])
        name = params.get('name')
        xbmc.log("SEARCH: name:%s force:%s" % (name, force))
        # main search menu
        if force or name == '.search':
            if self.count > 1:
                return self.listMenu()
            return self.handleNewSearch()
        # new search submenu
        elif name == '.search.new':
            return self.handleNewSearch()
        # search history
        elif name == '.search.query':
            query = params.get('query')
            action = params.get('action')
            if action:
                return self.handleAction(action, query=query)
            self.addSearchToHistory(query)
            return self.listSearch(query)
        return False

    def loadHistory(self):
        """Load history form file"""
        spath = os.path.join(self._spath, self.service + '.search.txt')
        if os.path.exists(spath):
            with open(spath, 'r') as f:
                self.history = [unicode(h, 'utf8').strip() for h in f]

    def saveHistory(self):
        """Save history to file"""
        if not os.path.exists(self._spath):
            os.makedirs(self._spath)
        spath = os.path.join(self._spath, self.service + '.search.txt')
        with open(spath, 'w') as f:
            f.write('\n'.join((convert.utf8(h) for h in self.history)))

