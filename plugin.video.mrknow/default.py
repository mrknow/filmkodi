# -*- coding: utf-8 -*-
import urllib, re, sys, xbmcplugin, xbmcgui
import os, time
import xbmcaddon, xbmc


# TODO: dodać wtyczkę do freedisc.pl
# TODO: dodać ikonę do dokumentalnych
# TODO: posprzątać pliki cookie #548



if sys.version_info >=  (2, 7):
    import json as json
else:
    import simplejson as json

scriptID = 'plugin.video.mrknow'
scriptname = "Films online"
ptv = xbmcaddon.Addon(scriptID)
datapath = xbmc.translatePath(ptv.getAddonInfo('profile'))

BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "resources" )
sys.path.append( os.path.join( ptv.getAddonInfo('path'), "lib" ) )
sys.path.append( os.path.join( ptv.getAddonInfo('path'), "host" ) )

import common
import mrknow_pCommon

from utils import fileUtils as fu

from utils.regexUtils import parseText
from utils.xbmcUtils import getKeyboard, setSortMethodsForCurrentXBMCList

from parser2 import Parser2, ParsingResult
from favouritesManager import FavouritesManager

import entities.CListItem as ListItem

from utils import xbmcUtils

from customModulesManager import CustomModulesManager
from utils.beta.t0mm0.common.addon import Addon


MENU_TABLE = { #1000: "www.mrknow.pl [filmy online]",
               2100: "filmbox.pl",
               9000: "noobroom.com"
}
TV_ONLINE_TABLE = {
		     2100 : ["Film Box", 'filmbox'],
             2200 : ["Zobacz.jcom.pl", 'zobaczjcompl'],
              2350 : ["Looknij.tv [troche przycina]", 'looknijtv'],
             2500 : ["SCREEN-TV.pl", 'screentv'],
             2700 : ["Typertv.com.pl", 'typertv'],
}
FUN_ONLINE_TABLE = {
               3000: ["Wykop.pl","wykop"],
               #6000: ["Milanos.pl","milanos"],
               4500: ["Testyonline","testyonline"],
               #5000: ["Joemonster.org","joemonster"],
               #5100: ["Wrzuta.pl","wrzuta"],
}
DOC_ONLINE_TABLE= {
               6000: ["filmydokumentalne.eu","filmydokumentalne"],
}
VOD_ONLINE_TABLE= {
               9010: ["Player.pl [TvnPlayer]","tvnplayer"],
               7000: ["VOD Onet PL","vodpl"]

}
BAJKI_ONLINE_TABLE= {
               10010: ["Bajkipopolsku.com","bajkipopolsku"],
               10020: ["Bajkionline.com","bajkionline"],
               10030: ["Kreskowkazone.pl [nie dziala 50% linkow]", "kreskowkazone"],

}

ANIME_ONLINE_TABLE={
                4600: ["Anime-odcinki.pl","animeodcinki"],

}

SERIALE_ONLINE_TABLE = {
               #8000: ["Alekino.tv","kinoliveseriale"],
               #8100: ["Zobaczto.tv Seriale","zobacztoseriale"],
               #8200: ["Tvseriesonline.pl    [dziala 70% stron z linkami]", "tvseriesonlinepl"],
               8300: ["Alltube.tv Seriale","alltubeseriale"],
               8500: ["Cdax.tv Seriale","cdaxseriale"],
               8400: ["eFilmy.tv Seriale","efilmyseriale"],
}

FILM_ONLINE_TABLE = {
            7200: ["Alltube.tv Filmy ","alltubefilmy"],
            7400 : ["Cda.pl", 'cdapl'],
            7700: ["EFilmy.tv","efilmy"],
            7550: ["Filmy.to [32% zrobione]", 'filmyto'],
             7600: ["Segos.se","segos"],
             7300: ["Cdax.tv","cdaxfilmy"],
             #7100: ["Filmbox Movie","filmboxmoovie"],
             7500: ["Zalukaj.tv","zalukaj"],
             #7900: ["Vod.tvpl.pl [testy]","tvppl"],
}

def mydump(obj):
  '''return a printable representation of an object for debugging'''
  newobj=obj
  if '__dict__' in dir(obj):
    newobj=obj.__dict__
    if ' object at ' in unicode(obj) and not newobj.has_key('__type__'):
      newobj['__type__']=unicode(obj)
    for attr in newobj:
      newobj[attr]=mydump(newobj[attr])
  return newobj


class StopDownloading(Exception):
        def __init__(self, value):
            self.value = value
        def __str__(self):
            return repr(self.value)

class MrknowFilms:



    def __init__(self):
        #BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
        BASE_RESOURCE_PATH = os.path.join( ptv.getAddonInfo('path'), "resources" )
        #BASE_RESOURCE_PATH = os.path.join( ptv2.getAddonInfo('path'), "resources" )

        sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
        sys.path.append( os.path.join( BASE_RESOURCE_PATH, "resources" ) )

        sys.path.append( os.path.join( ptv.getAddonInfo('path'), "host" ) )
        import mrknow_pLog, settings, mrknow_Parser, mrknow_pCommon

        self.cm = mrknow_pCommon.common()
        self.log = mrknow_pLog.pLog()
        self.settings = settings.TVSettings()
        self.parser = mrknow_Parser.mrknow_Parser()
        #self.log.info("DIR " + common.Paths.modulesDir + 'mainMenu.cfg')
        if ptv.getSetting('adults') == 'false':
            self.MAIN_MENU_FILE = 'mainMenu.cfg'
        else:
            self.MAIN_MENU_FILE = 'mainMenuAdult.cfg'
        self.SPORT_MENU_FILE = 'sportMenu.cfg'

        if not os.path.exists(common.Paths.pluginDataDir):
            os.makedirs(common.Paths.pluginDataDir, 0777)

        self.favouritesManager = FavouritesManager(common.Paths.favouritesFolder)
        self.customModulesManager = CustomModulesManager(common.Paths.customModulesDir, common.Paths.customModulesRepo)

        if not os.path.exists(common.Paths.customModulesDir):
            os.makedirs(common.Paths.customModulesDir, 0777)

        self.parser2 = Parser2()
        self.currentlist = None

        self.addon = None
        self.log.info('Filmy online www.mrknow.pl')
        common.clearCache()


    def _parseParameters(self):
        mode = int(self.addon.queries['mode'])
        queryString = self.addon.queries['item']
        item = ListItem.create()
        if mode in [common.Mode2.CHROME, common.Mode2.ADDTOFAVOURITES, common.Mode2.REMOVEFROMFAVOURITES, common.Mode2.EDITITEM]:
            item.infos = self.addon.parse_query(urllib.unquote(queryString),{})
        else:
            item.infos = self.addon.parse_query(queryString,{})
        item.infos = dict((k.decode('utf8'), v.decode('utf8')) for k, v in item.infos.items())
        return [mode, item]

    def showListOptions(self,argv=None):
        params = self.parser.getParams()
        mode = self.parser.getIntParam(params, "mode")
        name = self.parser.getParam(params, "name")
        service = self.parser.getParam(params, "service")
        self.addon = Addon(scriptID, argv)
        #print("MMMMMMMM",mode,params)
        mymodes = [common.Mode2.VIEW ,common.Mode2.PLAY, common.Mode2.ADDTOFAVOURITES, common.Mode2.EXECUTE]
        mymodes2 = [common.Mode3.VIEW ,common.Mode3.PLAY]

        base = argv[0]
        handle = int(argv[1])
        parameter = argv[2]
        self.base = base
        self.handle = handle

        paramstring = urllib.unquote_plus(parameter)

        self.log.info(paramstring)
        self.log.info('Base: '+ base)
        self.log.info('Handle: '+ str(handle))
        self.log.info('Parameter: '+ parameter)
        self.log.info('LEN: ' + str(len(paramstring)))
        self.log.info('mode: ' + str(mode))


        if mode == None and name == None and service == None:
            self.log.info('Wyświetlam kategorie')
            self.CATEGORIES()
            #self.LIST(MENU_TABLE)
        elif mode == 1:
            self.LIST(TV_ONLINE_TABLE)
        elif mode == 4:
            self.LIST(FUN_ONLINE_TABLE)
        elif mode == 2:
            self.LIST(FILM_ONLINE_TABLE)
        elif mode == 3:
            self.LIST(SERIALE_ONLINE_TABLE)
        elif mode == 5:
            self.LIST(DOC_ONLINE_TABLE)
        elif mode == 6:
            self.LIST(VOD_ONLINE_TABLE)
        elif mode == 7:
            self.LIST(BAJKI_ONLINE_TABLE)
        elif mode == 9:
            self.LIST(ANIME_ONLINE_TABLE)



        elif mode == 20:
            self.log.info('Wyświetlam ustawienia')
            self.settings.showSettings()
        elif mode == 30:
            from resources.lib.libraries import loguploader
            loguploader.Luguploader()

        elif mode in mymodes:
            #try:

            # if addon is started
            listItemPath = xbmcUtils.getListItemPath()
            if not listItemPath.startswith(self.base):
                if not('mode=' in paramstring and not 'mode=110&' in paramstring):
                    xbmcplugin.setPluginFanart(self.handle, common.Paths.pluginFanart)

                    #if common.getSetting('autoupdate') == 'true':
                    #    self.update()


            # Main Menu
            if len(paramstring) <= 9:
                mainMenu = ListItem.create()
                mainMenu['url'] = self.MAIN_MENU_FILE
                tmpList = self.parseView(mainMenu)
                if tmpList:
                    self.currentlist = tmpList
            else:
                [mode, item] = self._parseParameters()
                #print("MMMMMMMM",mode,mydump(item))


                # switch(mode)
                if mode == common.Mode2.VIEW:
                    tmpList = self.parseView(item)
                    #print("MMMMMMMM",item,vars(item))
                    if tmpList:
                        self.currentlist = tmpList
                        count = len(self.currentlist.items)
                        if count == 1:
                            # Autoplay single video
                            autoplayEnabled = ptv.getSetting('autoplay') == 'true'
                            if autoplayEnabled:
                                videos = self.currentlist.getVideos()
                                if len(videos) == 1:
                                    self.playVideo(videos[0], True)


                elif mode == common.Mode2.ADDITEM:
                    tmp = os.path.normpath(paramstring.split('url=')[1])
                    if tmp:
                        suffix = tmp.split(os.path.sep)[-1]
                        tmp = tmp.replace(suffix,'') + urllib.quote_plus(suffix)
                    if self.favouritesManager.add(tmp):
                        xbmc.executebuiltin('Container.Refresh()')


                elif mode in [common.Mode2.ADDTOFAVOURITES, common.Mode2.REMOVEFROMFAVOURITES, common.Mode2.EDITITEM]:

                    if mode == common.Mode2.ADDTOFAVOURITES:
                        self.favouritesManager.addItem(item)
                    elif mode == common.Mode2.REMOVEFROMFAVOURITES:
                        self.favouritesManager.removeItem(item)
                        xbmc.executebuiltin('Container.Refresh()')
                    elif mode == common.Mode2.EDITITEM:
                        if self.favouritesManager.editItem(item):
                            xbmc.executebuiltin('Container.Refresh()')

                elif mode == common.Mode2.EXECUTE:
                    self.executeItem(item)

                elif mode == common.Mode2.PLAY:
                    self.playVideo(item)

            #except Exception, e:
            #    common.showError('Error running Mrknow')
            #    self.log.info('Error running Mrknow. m1 Reason:' + str(e))

        elif mode in mymodes2:
            try:

                # if addon is started
                listItemPath = xbmcUtils.getListItemPath()
                if not listItemPath.startswith(self.base):
                    if not('mode=' in paramstring and not 'mode=210&' in paramstring):
                        xbmcplugin.setPluginFanart(self.handle, common.Paths.pluginFanart)

                        #if common.getSetting('autoupdate') == 'true':
                        #    self.update()


                # Main Menu
                if len(paramstring) <= 9:
                    mainMenu = ListItem.create()
                    mainMenu['url'] = self.SPORT_MENU_FILE
                    tmpList = self.parseView(mainMenu)
                    if tmpList:
                        self.currentlist = tmpList
                else:
                    [mode, item] = self._parseParameters()
                    #print("MMMMMMMM",mode,mydump(item))


                    # switch(mode)
                    if mode == common.Mode2.VIEW:
                        tmpList = self.parseView(item)
                        #print("MMMMMMMM",item,vars(item))
                        if tmpList:
                            self.currentlist = tmpList
                            count = len(self.currentlist.items)
                            if count == 1:
                                # Autoplay single video
                                autoplayEnabled = ptv.getSetting('autoplay') == 'true'
                                if autoplayEnabled:
                                    videos = self.currentlist.getVideos()
                                    if len(videos) == 1:
                                        self.playVideo(videos[0], True)
            except Exception, e:
                common.showError('Error running Mrknow')
                self.log.info('Error running Mrknow. m2 Reason:' + str(e))



        elif mode == 4500 or service == 'testyonline':
            tv = testyonline.testyonline()
            tv.handleService()
        elif mode == 4600 or service == 'animeodcinki':
            import animeodcinki
            tv = animeodcinki.Animeodcinki()
            tv.handleService()

        elif mode == 10010 or service == 'bajkipopolsku':
            import bajkipopolsku
            tv = bajkipopolsku.bajkipopolsku()
            tv.handleService()
        elif mode == 10020 or service == 'bajkionline':
            import bajkionline
            tv = bajkionline.bajkionline()
            tv.handleService()
        elif mode == 10030 or service == 'kreskowkazone':
            import kreskowkazone
            tv = kreskowkazone.kreskowkazone()
            tv.handleService()
        elif mode == 8300 or service == 'alltubeseriale':
            import alltubeseriale
            tv = alltubeseriale.alltubeseriale()
            tv.handleService()
        elif mode == 8400 or service == 'efilmyseriale':
            import efilmyseriale
            tv = efilmyseriale.efilmyseriale()
            tv.handleService()
        elif mode == 7000 or service == 'vodpl':
            import vodpl
            tv = vodpl.vodpl()
            tv.handleService()
        elif mode == 7200 or service == 'alltubefilmy':
            import alltubefilmy
            tv = alltubefilmy.alltubefilmy()
            tv.handleService()
        elif mode == 7300 or service == 'cdaxfilmy':
            import cdaxfilmy
            tv = cdaxfilmy.cdaxfilmy()
            tv.handleService()
        elif mode == 7400 or service == 'cdapl':
            import cdapl
            tv = cdapl.cdapl()
            tv.handleService()
        elif mode == 7500 or service == 'zalukaj':
            tv = zalukaj.zalukaj()
            tv.handleService()
        elif mode == 7550 or service == 'filmyto':
            import filmyto
            tv = filmyto.Filmyto()
            tv.handleService()

        elif mode == 7600 or service == 'segos':
            import segos
            tv = segos.Segos()
            tv.handleService()
        elif mode == 7700 or service == 'efilmy':
            import efilmy
            tv = efilmy.efilmy()
            tv.handleService()

        elif mode == 7900 or service == 'tvppl':
            import tvppl
            tv = tvppl.tvppl()
            tv.handleService()

        elif mode == 8500 or service == 'cdaxseriale':
            import cdaxseriale
            tv = cdaxseriale.cdaxseriale()
            tv.handleService()
        elif mode == 3000 or service == 'wykop':
            import wykop
            tv = wykop.WYKOP()
            tv.handleService()
        elif mode == 6000 or service == 'filmydokumentalne':
            import filmydokumentalne
            tv = filmydokumentalne.filmydokumentalne()
            tv.handleService()
        elif mode == 9010 or service == 'tvn':
            import tvnplayer
            tv = tvnplayer.tvn()
            tv.handleService()

    def CATEGORIES(self):
        #self.addDir("Telewizja", 1, False, 'Telewizja', False)
        self.addDir('Telewizja', common.Mode2.VIEW, False, 'telewizja', False)
        self.addDir("Filmy", 2, False, 'filmy', False)
        self.addDir("Seriale", 3, False, 'seriale', False)
        self.addDir("Polskie serwisy VOD", 6, False, 'servisyvod', False)
        self.addDir("Bajki", 7, False, 'bajki', False)
        self.addDir("Anime", 9, False, 'anime', False)
        self.addDir("Rozrywka", 4, False, 'rozrywka', False)
        self.addDir("Sport [testy działa 15% kanałów]", common.Mode3.VIEW, False, 'sport', False)
        self.addDir("Filmy popularno-naukowe i dokumentalne", 5, False, 'dokumentalne', False)
        self.addDir('Ustawienia', 20, True, 'ustawienia', False)
        self.addDir('Wyślij logi diagnostyczne', 30, True, 'ustawienia', False)

        #loguploader.py

        #self.addDir('[COLOR yellow]Aktualizuj LIBRTMP - aby dzialy kanaly TV - Patche KSV[/COLOR]',30, False, 'Ustawienia', False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def listsTable(self, table):
        for num, val in table.items():
            nTab.append(val)
        return nTab

    def executeItem(self, item):
        url = item['url']
        if '(' in url:
            xbmcCommand = parseText(url,'([^\(]*).*')
            if xbmcCommand.lower() in ['activatewindow', 'runscript', 'runplugin', 'playmedia']:
                if xbmcCommand.lower() == 'activatewindow':
                    params = parseText(url, '.*\(\s*(.+?)\s*\).*').split(',')
                    for i in range(len(params)-1,-1,-1):
                        p = params[i]
                        if p == 'return':
                            params.remove(p)
                    path = params[len(params)-1]
                    xbmc.executebuiltin('Container.Update(' + path + ')')
                    return
                xbmc.executebuiltin(url)

    def LIST(self, table = {}):
        valTab = []
        strTab = []
        for num, tab in table.items():
            strTab.append(num)
            strTab.append(tab[0])
            strTab.append(tab[1])
            valTab.append(strTab)
            strTab = []
        valTab.sort(key = lambda x: x[1])
        for i in range(len(valTab)):
            if valTab[i][2] == '': icon = False
            else: icon = valTab[i][2]
            self.addDir(valTab[i][1], valTab[i][0], False, icon, False)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def addDir(self, name, mode, autoplay, icon, isPlayable = True, category='', murl=''):
        #print("Dane",name, mode, autoplay, icon, isPlayable)
        #u=sys.argv[0] + "?mode=" + str(mode) + "&category="+ category + "&murl="+ murl + "&name="+ name
        u=sys.argv[0] + "?mode=" + str(mode)
        if icon != False:
          icon = os.path.join(ptv.getAddonInfo('path'), "images/") + icon + '.png'
        else:
          icon = "DefaultVideoPlaylists.png"
        liz=xbmcgui.ListItem(name, iconImage=icon, thumbnailImage='')
        if autoplay and isPlayable:
          liz.setProperty("IsPlayable", "true")
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,listitem=liz, isFolder= not autoplay)
        #xbmcplugin.setPluginFanart(int(sys.argv[1]), common.Paths.pluginFanart1)

    def playVideo(self, videoItem, isAutoplay = False):
        if not videoItem:
            return

        listitem = self.createXBMCListItem(videoItem)

        title = videoItem['videoTitle']
        if title:
            listitem.setInfo('video', {'title': title})


        if not isAutoplay:
            xbmcplugin.setResolvedUrl(self.handle, True, listitem)
        else:
            url = urllib.unquote_plus(videoItem['url'])
            mrknow_pCommon.mystat(url)
            #xbmc.Player(self.getPlayerType()).play(url, listitem)
            xbmc.Player().play(url, listitem)

    def getPlayerType(self):
        return True
        sPlayerType = ptv.getSetting('playerType')

        if (sPlayerType == '0'):
            return xbmc.PLAYER_CORE_AUTO
        elif (sPlayerType == '1'):
            return xbmc.PLAYER_CORE_MPLAYER
        elif (sPlayerType == '2'):
            return xbmc.PLAYER_CORE_DVDPLAYER
        # PLAYER_CORE_AMLPLAYER
        elif (sPlayerType == '3'):
            return 5

        return xbmc.PLAYER_CORE_AUTO
    def parseView(self, lItem):

        def endOfDirectory(succeeded=True):
            xbmcplugin.endOfDirectory(handle=self.handle, succeeded=succeeded, cacheToDisc=True)

        if not lItem:
            endOfDirectory(False)
            return None

        if lItem['type'] == 'search':
            search_phrase = self.getSearchPhrase()
            if not search_phrase:
                common.log("search canceled")
                endOfDirectory(False)
                return None
            else:
                lItem['type'] = 'rss'
                lItem['url'] =  lItem['url'] % (urllib.quote_plus(search_phrase))

        url = lItem['url']

        if url == common.Paths.customModulesFile:
            self.customModulesManager.getCustomModules()

        tmpList = None
        result = self.parser2.parse(lItem)

        if result.code == ParsingResult.Code.SUCCESS:
            tmpList = result.list
        elif result.code == ParsingResult.Code.CFGFILE_NOT_FOUND:
            common.showError("Cfg file not found")
            endOfDirectory(False)
            return None
        elif result.code == ParsingResult.Code.CFGSYNTAX_INVALID:
            common.showError("Cfg syntax invalid")
            endOfDirectory(False)
            return None
        elif result.code == ParsingResult.Code.WEBREQUEST_FAILED:
            common.showError("Web request failed")
            if len(result.list.items) > 0:
                tmpList = result.list
            else:
                endOfDirectory(False)
                return None

        # if it's the main menu, add folder 'Favourites' and 'Custom Modules
        if url == self.MAIN_MENU_FILE:
            tmp = ListItem.create()
            tmp['title'] = 'Favourites'
            tmp['type'] = 'rss'
            tmp['icon'] = os.path.join(common.Paths.imgDir, 'bookmark.png')
            tmp['url'] = str(common.Paths.favouritesFile)
            tmpList.items.insert(0, tmp)

            #tmp = ListItem.create()
            #tmp['title'] = '[COLOR red]Custom Modules[/COLOR]'
            #tmp['type'] = 'rss'
            #tmp['url'] = os.path.join(common.Paths.customModulesDir, 'custom.cfg')
            #tmpList.items.insert(0, tmp)

        # if it's the favourites menu, add item 'Add item'
        elif url == common.Paths.favouritesFile or url.startswith('favfolders'):

            if url.startswith('favfolders'):
                url = os.path.normpath(os.path.join(common.Paths.favouritesFolder, url))

            tmp = ListItem.create()
            tmp['title'] = 'Add item...'
            tmp['type'] = 'command'
            tmp['icon'] = os.path.join(common.Paths.imgDir, 'bookmark_add.png')
            action = 'RunPlugin(%s)' % (self.base + '?mode=' + str(common.Mode2.ADDITEM) + '&url=' + url)
            tmp['url'] = action
            tmpList.items.append(tmp)

        # if it's the custom modules  menu, add item 'more...'
        elif url == common.Paths.customModulesFile:
            tmp = ListItem.create()
            tmp['title'] = 'more...'
            tmp['type'] = 'command'
            #tmp['icon'] = os.path.join(common.Paths.imgDir, 'bookmark_add.png')
            action = 'RunPlugin(%s)' % (self.base + '?mode=' + str(common.Mode2.DOWNLOADCUSTOMMODULE) + '&url=')
            tmp['url'] = action
            tmpList.items.append(tmp)


        # Create menu or play, if it's a single video and autoplay is enabled
        proceed = False

        count = len(tmpList.items)
        if count == 0:
            if url.startswith('favfolders'):
                proceed = True
            else:
                common.showInfo('No stream available')
        elif count > 0 and not (ptv.getSetting('autoplay') == 'true' and count == 1 and len(tmpList.getVideos()) == 1):
            # sort methods
            sortKeys = tmpList.sort.split('|')
            setSortMethodsForCurrentXBMCList(self.handle, sortKeys)

            # Add items to XBMC list
            for m in tmpList.items:
                self.addListItem(m, len(tmpList.items))

            proceed = True

        endOfDirectory(proceed)
        common.log('End of directory')
        return tmpList

    def addListItem(self, lItem, totalItems):
        def createContextMenuItem(label, mode, codedItem):
            action = 'XBMC.RunPlugin(%s)' % (self.addon.build_plugin_url({'mode': str(mode), 'item': codedItem}))
            return (label, action)

        def encoded_dict(in_dict):
            out_dict = {}
            for k, v in in_dict.iteritems():
                if isinstance(v, unicode):
                    v = v.encode('utf8')
                elif isinstance(v, str):
                    # Must be encoded in UTF-8
                    v.decode('utf8')
                out_dict[k] = v
            return urllib.urlencode(out_dict)

        contextMenuItems = []
        definedIn = lItem['definedIn']

        codedItem = urllib.quote(encoded_dict(lItem.infos))

        if definedIn:
            # Queue
            contextMenuItem = createContextMenuItem('Queue', common.Mode2.QUEUE, codedItem)
            contextMenuItems.append(contextMenuItem)

            # Favourite
            if definedIn.endswith('favourites.cfg') or definedIn.startswith("favfolders/"):
                # Remove from favourites
                contextMenuItem = createContextMenuItem('Remove', common.Mode2.REMOVEFROMFAVOURITES, codedItem)
                contextMenuItems.append(contextMenuItem)

                # Edit label
                contextMenuItem = createContextMenuItem('Edit', common.Mode2.EDITITEM, codedItem)
                contextMenuItems.append(contextMenuItem)

            else:
                # Custom module
                if definedIn.endswith('custom.cfg'):
                    # Remove from custom modules
                    contextMenuItem = createContextMenuItem('Remove module', common.Mode2.REMOVEFROMCUSTOMMODULES, codedItem)
                    contextMenuItems.append(contextMenuItem)

                if lItem['title'] != "Favourites":
                        # Add to favourites
                        contextMenuItem = createContextMenuItem('Add to SportsDevil favourites', common.Mode2.ADDTOFAVOURITES, codedItem)
                        contextMenuItems.append(contextMenuItem)
                contextMenuItem = createContextMenuItem('Open with Chrome launcher', common.Mode2.CHROME, codedItem)
                contextMenuItems.append(contextMenuItem)

        liz = self.createXBMCListItem(lItem)

        m_type = lItem['type']
        if not m_type:
            m_type = 'rss'

        if m_type == 'video':
            u = self.base + '?mode=' + str(common.Mode2.PLAY) + '&item=' + codedItem
            if lItem['IsDownloadable']:
                contextMenuItem = createContextMenuItem('Download', common.Mode2.DOWNLOAD, codedItem)
                contextMenuItems.append(contextMenuItem)
            isFolder = False
        elif m_type.find('command') > -1:
            u = self.base + '?mode=' + str(common.Mode2.EXECUTE) + '&item=' + codedItem
            isFolder = False
        else:
            u = self.base + '?mode=' + str(common.Mode2.VIEW) + '&item=' + codedItem
            isFolder = True

        liz.addContextMenuItems(contextMenuItems)
        xbmcplugin.addDirectoryItem(handle = self.handle, url = u, listitem = liz, isFolder = isFolder, totalItems = totalItems)

    def createXBMCListItem(self, item):
        #print("MMMMMMMM",vars(item))

        title = item['title']

        m_type = item['type']

        icon = item['icon']

        if icon and not icon.startswith('http'):
            try:
                if not fu.fileExists(icon):
                    tryFile = os.path.join(common.Paths.modulesDir, icon)
                    if not fu.fileExists(tryFile):
                        tryFile = os.path.join(common.Paths.customModulesDir, icon)
                    if fu.fileExists(tryFile):
                        icon = tryFile
            except:
                pass

        if not icon:
            if m_type == 'video':
                icon = common.Paths.defaultVideoIcon
            else:
                icon = common.Paths.defaultCategoryIcon

        liz = xbmcgui.ListItem(title, title, iconImage=icon, thumbnailImage=icon)

        fanart = item['fanart']
        if not fanart:
            fanart = common.Paths.pluginFanart
        liz.setProperty('fanart_image', fanart)

        """
        General Values that apply to all types:
            count         : integer (12) - can be used to store an id for later, or for sorting purposes
            size          : long (1024) - size in bytes
            date          : string (%d.%m.%Y / 01.01.2009) - file date

        Video Values:
            genre         : string (Comedy)
            year          : integer (2009)
            episode       : integer (4)
            season        : integer (1)
            top250        : integer (192)
            tracknumber   : integer (3)
            rating        : float (6.4) - range is 0..10
            watched       : depreciated - use playcount instead
            playcount     : integer (2) - number of times this item has been played
            overlay       : integer (2) - range is 0..8.  See GUIListItem.h for values
            cast          : list (Michal C. Hall)
            castandrole   : list (Michael C. Hall|Dexter)
            director      : string (Dagur Kari)
            mpaa          : string (PG-13)
            plot          : string (Long Description)
            plotoutline   : string (Short Description)
            title         : string (Big Fan)
            originaltitle : string (Big Fan)
            duration      : string (3:18)
            studio        : string (Warner Bros.)
            tagline       : string (An awesome movie) - short description of movie
            writer        : string (Robert D. Siegel)
            tvshowtitle   : string (Heroes)
            premiered     : string (2005-03-04)
            status        : string (Continuing) - status of a TVshow
            code          : string (tt0110293) - IMDb code
            aired         : string (2008-12-07)
            credits       : string (Andy Kaufman) - writing credits
            lastplayed    : string (%Y-%m-%d %h:%m:%s = 2009-04-05 23:16:04)
            album         : string (The Joshua Tree)
            votes         : string (12345 votes)
            trailer       : string (/home/user/trailer.avi)
        """

        infoLabels = {}
        for video_info_name in item.infos.keys():
            infoLabels[video_info_name] = item[video_info_name]
        infoLabels['title'] = title

        liz.setInfo('video', infoLabels)

        url = urllib.unquote_plus(item['url'])
        liz.setPath(url)

        if m_type == 'video':
            liz.setProperty('IsPlayable','true')
            #liz.setMimeType('text')

        return liz
    def getSearchPhrase(self):
        searchCache = os.path.join(common.Paths.cacheDir, 'search')
        default_phrase = fu.getFileContent(searchCache)
        if not default_phrase:
            default_phrase = ''

        search_phrase = common.showOSK(default_phrase, common.translate(30102))
        if search_phrase == '':
            return None
        xbmc.sleep(10)
        fu.setFileContent(searchCache, search_phrase)

        return search_phrase

    def _pbhook(self,numblocks, blocksize, filesize, dp, start_time):
            try:
                percent = min(numblocks * blocksize * 100 / filesize, 100)
                currently_downloaded = float(numblocks) * blocksize / (1024 * 1024)
                kbps_speed = numblocks * blocksize / (time.time() - start_time)
                if kbps_speed > 0: eta = (filesize - numblocks * blocksize) / kbps_speed
                else: eta = 0
                kbps_speed = kbps_speed / 1024
                total = float(filesize) / (1024 * 1024)
                mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total)
                e = 'Speed: %.02f Kb/s ' % kbps_speed
                e += 'ETA: %02d:%02d' % divmod(eta, 60)
                dp.update(percent, mbs, e)
            except:
                percent = 100
                dp.update(percent)
            if dp.iscanceled():
                dp.close()
                raise StopDownloading('Stopped Downloading')

    def downloadFileWithDialog(self,url,dest):
        try:
            dp = xbmcgui.DialogProgress()
            dp.create("mrknow.pl","Downloading & Copying File",'')
            urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: self._pbhook(nb,bs,fs,dp,time.time()))
        except Exception, e:
            dialog = xbmcgui.Dialog()
            #main.ErrorReport(e)
            dialog.ok("Mash Up", "Report the error below at ", str(e), "We will try our best to help you")

init = MrknowFilms()
init.showListOptions(sys.argv)
