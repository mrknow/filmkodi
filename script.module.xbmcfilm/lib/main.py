# -*- coding: utf-8 -*-

# Merge xSopcast and SportsDevil
#http://forum.xbmc.org/showthread.php?tid=100031&pid=1101338#pid1101338

#Freedocast fix
#http://forum.xbmc.org/showthread.php?tid=100597&pid=1094333#pid1094333

import os
import xbmcplugin
import xbmc, xbmcgui
import urllib

import common

from utils import fileUtils as fu

from utils.regexUtils import parseText
from utils.xbmcUtils import getKeyboard, setSortMethodsForCurrentXBMCList
from dialogs.dialogProgress import DialogProgress

from parser import Parser, ParsingResult
from downloader import Downloader
from favouritesManager import FavouritesManager

import entities.CListItem as ListItem

from utils import xbmcUtils

from dialogs.dialogQuestion import DialogQuestion

from customModulesManager import CustomModulesManager

from addonInstaller import install

from utils.beta.t0mm0.common.addon import Addon

#from cacheManager import CacheManager


class Mode:
    UPDATE = 0
    VIEW = 1
    PLAY = 2
    QUEUE = 3
    DOWNLOAD = 4
    EXECUTE = 5
    ADDTOFAVOURITES = 6
    REMOVEFROMFAVOURITES = 7
    EDITITEM = 8
    ADDITEM = 9
    DOWNLOADCUSTOMMODULE = 10
    REMOVEFROMCUSTOMMODULES = 11
    INSTALLADDON = 12
    CHROME = 13
    WEBDRIVER = 14


class Main:

    MAIN_MENU_FILE = 'mainMenu.cfg'


    def __init__(self):
        
        if not os.path.exists(common.Paths.pluginDataDir):
            os.makedirs(common.Paths.pluginDataDir, 0777)

        self.favouritesManager = FavouritesManager(common.Paths.favouritesFolder)
        self.customModulesManager = CustomModulesManager(common.Paths.customModulesDir, common.Paths.customModulesRepo)
        
        if not os.path.exists(common.Paths.customModulesDir):
            os.makedirs(common.Paths.customModulesDir, 0777)

        self.parser = Parser()
        self.currentlist = None
        
        self.addon = None
        
        common.log('SportsDevil initialized')
        


    def getPlayerType(self):
        sPlayerType = common.getSetting('playerType')
        
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
            xbmc.Player(self.getPlayerType()).play(url, listitem)
    
    def launchChrome(self, url, title):
        action = 'RunPlugin(%s)' % ('plugin://plugin.program.chrome.launcher/?kiosk=yes&mode=showSite&stopPlayback=yes&url=' + url)
        common.log('chrome test:' + str(action))
        xbmc.executebuiltin(action)
        
    def playWebDriver(self, url, title):
        try:
            import liveremote
            video = liveremote.resolve(url)
            liz = xbmcgui.ListItem(title)
            liz.setPath(video)
            liz.setProperty('IsPlayable','true')
            xbmc.Player(self.getPlayerType()).play(video, liz)
        except:
            import sys,traceback
            traceback.print_exc(file = sys.stdout)
            common.showInfo('This is not the option you are looking for.')


    def downloadVideo(self, url, title):
        common.log('Trying to download video ' + str(url))

        # check url
        if url.startswith('plugin'):
            common.log('Video is not downloadable')
            return None

        path = common.getSetting('download_path')
        if not path:
            path = common.browseFolders(common.translate(30017))
            common.setSetting('download_path', path)

        title = getKeyboard(default = fu.cleanFilename(title),heading='SportsDevil')
        if title == None or title == '':
            return None

        downloader = Downloader()
        downloaded_file = downloader.downloadMovie(url, path,  fu.cleanFilename(title), '.flv')

        if downloaded_file == None:
            common.log ('Download cancelled')
        else:
            common.log('Video ' + url + " downloaded to '" + downloaded_file + "'")

        return downloaded_file


    def getVideos(self, lItem, dia = None, percent = 0, percentSpan = 100):
        allitems = []
        
        if dia and dia.isCanceled():
            return allitems
        
        currentName = lItem['title']

        if lItem['type'].find('video') != -1:
            if dia:
                dia.update(percent + percentSpan, thirdline=currentName)
            allitems.append(lItem)
        else:
            tmpList = self.parser.parse(lItem).list
            if tmpList and len(tmpList.items) > 0:
                
                if dia:
                    dia.update(percent, secondline=currentName, thirdline=' ')
                
                inc = percentSpan/len(tmpList.items)
                for item in tmpList.items:
                    
                    if dia and dia.isCanceled():
                        break
                    
                    children = self.getVideos(item, dia, percent, inc)
                    if children:
                        allitems.extend(children)
                    percent += inc

        return allitems


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
        result = self.parser.parse(lItem)
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
            action = 'RunPlugin(%s)' % (self.base + '?mode=' + str(Mode.ADDITEM) + '&url=' + url)
            tmp['url'] = action
            tmpList.items.append(tmp)
        
        # if it's the custom modules  menu, add item 'more...'
        elif url == common.Paths.customModulesFile:            
            tmp = ListItem.create()
            tmp['title'] = 'more...'
            tmp['type'] = 'command'
            #tmp['icon'] = os.path.join(common.Paths.imgDir, 'bookmark_add.png')
            action = 'RunPlugin(%s)' % (self.base + '?mode=' + str(Mode.DOWNLOADCUSTOMMODULE) + '&url=')
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
        elif count > 0 and not (common.getSetting('autoplay') == 'true' and count == 1 and len(tmpList.getVideos()) == 1):
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


    def downloadCustomModule(self):
        success = self.customModulesManager.downloadCustomModules()
        if success == True:            
            # refresh container if SportsDevil is active
            currContainer = xbmcUtils.getContainerFolderPath()
            common.showNotification('SportsDevil', 'Download successful', 1000)
            if currContainer.startswith(self.base):                
                xbmc.executebuiltin('Container.Refresh()')
            return True
        elif success == False:        
            common.showNotification('SportsDevil', 'Download failed', 1000)
        return False


    def removeCustomModule(self, item):
        name = urllib.unquote(item["title"])
        success = self.customModulesManager.removeCustomModule(name)
        if success:
            xbmc.executebuiltin('Container.Refresh()')
            

    def createXBMCListItem(self, item):
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
            contextMenuItem = createContextMenuItem('Queue', Mode.QUEUE, codedItem)
            contextMenuItems.append(contextMenuItem)

            # Favourite
            if definedIn.endswith('favourites.cfg') or definedIn.startswith("favfolders/"):
                # Remove from favourites
                contextMenuItem = createContextMenuItem('Remove', Mode.REMOVEFROMFAVOURITES, codedItem)
                contextMenuItems.append(contextMenuItem)

                # Edit label
                contextMenuItem = createContextMenuItem('Edit', Mode.EDITITEM, codedItem)
                contextMenuItems.append(contextMenuItem)

            else:
                # Custom module
                if definedIn.endswith('custom.cfg'):
                    # Remove from custom modules
                    contextMenuItem = createContextMenuItem('Remove module', Mode.REMOVEFROMCUSTOMMODULES, codedItem)
                    contextMenuItems.append(contextMenuItem)
    
                if lItem['title'] != "Favourites":
                        # Add to favourites
                        contextMenuItem = createContextMenuItem('Add to SportsDevil favourites', Mode.ADDTOFAVOURITES, codedItem)
                        contextMenuItems.append(contextMenuItem)
                contextMenuItem = createContextMenuItem('Open with Chrome launcher', Mode.CHROME, codedItem)
                contextMenuItems.append(contextMenuItem)
                #contextMenuItem = createContextMenuItem('Open with WebDriver', Mode.WEBDRIVER, codedItem)
                #contextMenuItems.append(contextMenuItem)

        liz = self.createXBMCListItem(lItem)

        m_type = lItem['type']
        if not m_type:
            m_type = 'rss'
        
        if m_type == 'video':
            u = self.base + '?mode=' + str(Mode.PLAY) + '&item=' + codedItem
            if lItem['IsDownloadable']:
                contextMenuItem = createContextMenuItem('Download', Mode.DOWNLOAD, codedItem)
                contextMenuItems.append(contextMenuItem)
            isFolder = False
        elif m_type.find('command') > -1:
            u = self.base + '?mode=' + str(Mode.EXECUTE) + '&item=' + codedItem
            isFolder = False
        else:
            u = self.base + '?mode=' + str(Mode.VIEW) + '&item=' + codedItem
            isFolder = True

        liz.addContextMenuItems(contextMenuItems)
        xbmcplugin.addDirectoryItem(handle = self.handle, url = u, listitem = liz, isFolder = isFolder, totalItems = totalItems)


    def clearCache(self):
        cacheDir = common.Paths.cacheDir
        if not os.path.exists(cacheDir):
            os.mkdir(cacheDir, 0777)
            common.log('Cache directory created' + str(cacheDir))
        else:
            fu.clearDirectory(cacheDir)
            common.log('Cache directory purged')


    def update(self):
        
        def checkForUpdates():
            return None
        
        def doUpdates(typeName, updates):
            count = len(updates)
            
            head = "SportsDevil Updates - %s" % typeName
            
            msg = common.translate(30277)
            if count == 1:
                msg = common.translate(30276)
                
            question = ("%s %s: " % (count, msg)) + ', '.join(map(lambda u: u.split('/')[-1], updates.keys())) + '\n'
            question += common.translate(30278)
            
            updates = updates.values()
            
            countFailed = 0
    
            dlg = DialogQuestion()
            dlg.head = head
            if dlg.ask(question):
                dlg = DialogProgress()
                firstline = common.translate(30279)
                dlg.create(head, firstline, " ")
           
                for i in range(0, count):
                    update = updates[i]
                    percent = int((i+1.0)*100/count)
                    dlg.update(percent, firstline, update.name)
                    if not update.do():
                        countFailed += 1
                
                msg = " "
                if countFailed > 0:
                    msg = "%s %s" % (countFailed, common.translate(30280))
                    
                dlg.update(100, msg, " ")
                xbmc.sleep(500)
                dlg.close()
            
        allupdates = checkForUpdates()
        count = len(allupdates)
        if count == 0:
            common.showNotification('SportsDevil', common.translate(30273))
            return
        else:
            for key, value in allupdates.items():
                doUpdates(key, value)


    def queueAllVideos(self, item):
        dia = DialogProgress()
        dia.create('SportsDevil', 'Get videos...' + item['title'])
        dia.update(0)

        items = self.getVideos(item, dia)
        if items:
            for it in items:
                item = self.createXBMCListItem(it)
                queries = {'mode': str(Mode.PLAY), 'url': self.addon.build_plugin_url(it.infos)}
                uc = self.addon.build_plugin_url(queries)
                xbmc.PlayList(xbmc.PLAYLIST_VIDEO).add(uc, item)
            resultLen = len(items)
            msg = 'Queued ' + str(resultLen) + ' video'
            if resultLen > 1:
                msg += 's'
            dia.update(100, msg)
            xbmc.sleep(500)
            dia.update(100, msg,' ',' ')
        else:
            dia.update(0, 'No items found',' ')

        xbmc.sleep(700)
        dia.close()        
                

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


    def _parseParameters(self):
        mode = int(self.addon.queries['mode'])
        queryString = self.addon.queries['item']
        item = ListItem.create()
        if mode in [Mode.CHROME, Mode.ADDTOFAVOURITES, Mode.REMOVEFROMFAVOURITES, Mode.EDITITEM, Mode.WEBDRIVER]:
            item.infos = self.addon.parse_query(urllib.unquote(queryString),{})
        else:
            item.infos = self.addon.parse_query(queryString,{})
        item.infos = dict((k.decode('utf8'), v.decode('utf8')) for k, v in item.infos.items())
        return [mode, item]


    def run(self, argv=None):
        
        self.addon = Addon('plugin.video.SportsDevil', argv)

        common.log('SportsDevil running')
        
        base = argv[0]
        handle = int(argv[1])
        parameter = argv[2]
        self.base = base
        self.handle = handle
        
        paramstring = urllib.unquote_plus(parameter)
        common.log(paramstring)
        
        try:
            
            # if addon is started
            listItemPath = xbmcUtils.getListItemPath()
            if not listItemPath.startswith(self.base):
                if not('mode=' in paramstring and not 'mode=1&' in paramstring):   
                    xbmcplugin.setPluginFanart(self.handle, common.Paths.pluginFanart)
                    self.clearCache()
                     
                    #if common.getSetting('autoupdate') == 'true':    
                    #    self.update()
            
            
            # Main Menu
            if len(paramstring) <= 2:                
                mainMenu = ListItem.create()
                mainMenu['url'] = self.MAIN_MENU_FILE
                tmpList = self.parseView(mainMenu)
                if tmpList:
                    self.currentlist = tmpList
                
            else:
                [mode, item] = self._parseParameters()

                # switch(mode)
                if mode == Mode.VIEW:
                    tmpList = self.parseView(item)
                    if tmpList:
                        self.currentlist = tmpList
                        count = len(self.currentlist.items)
                        if count == 1:
                            # Autoplay single video
                            autoplayEnabled = common.getSetting('autoplay') == 'true'
                            if autoplayEnabled:
                                videos = self.currentlist.getVideos()
                                if len(videos) == 1:
                                    self.playVideo(videos[0], True)


                elif mode == Mode.ADDITEM:
                    tmp = os.path.normpath(paramstring.split('url=')[1])
                    if tmp:
                        suffix = tmp.split(os.path.sep)[-1]
                        tmp = tmp.replace(suffix,'') + urllib.quote_plus(suffix)
                    if self.favouritesManager.add(tmp):
                        xbmc.executebuiltin('Container.Refresh()')


                elif mode in [Mode.ADDTOFAVOURITES, Mode.REMOVEFROMFAVOURITES, Mode.EDITITEM]:

                    if mode == Mode.ADDTOFAVOURITES:
                        self.favouritesManager.addItem(item)
                    elif mode == Mode.REMOVEFROMFAVOURITES:
                        self.favouritesManager.removeItem(item)
                        xbmc.executebuiltin('Container.Refresh()')
                    elif mode == Mode.EDITITEM:
                        if self.favouritesManager.editItem(item):
                            xbmc.executebuiltin('Container.Refresh()')


                elif mode == Mode.EXECUTE:
                    self.executeItem(item)

                elif mode == Mode.PLAY:
                    self.playVideo(item)
                
                elif mode == Mode.WEBDRIVER:
                    url = urllib.quote(item['url'])
                    title = item['title']
                    self.playWebDriver(url, title)

                elif mode == Mode.QUEUE:
                    self.queueAllVideos(item)

                elif mode == Mode.DOWNLOAD:
                    url = urllib.unquote(item['url'])
                    title = item['title']
                    self.downloadVideo(url, title)
                
                elif mode == Mode.CHROME:
                    url = urllib.quote(item['url'])
                    title = item['title']
                    self.launchChrome(url, title)
                
                elif mode == Mode.REMOVEFROMCUSTOMMODULES:
                    self.removeCustomModule(item)
                
                #elif mode == Mode.UPDATE:
                #    self.update()
                    
                elif mode == Mode.DOWNLOADCUSTOMMODULE:
                    self.downloadCustomModule()
                
                elif mode == Mode.INSTALLADDON:
                    success = install(item['url'])
                    if success:
                        xbmc.sleep(100)
                        if xbmcUtils.getCurrentWindowXmlFile() == 'DialogAddonSettings.xml':
                            # workaround to update settings dialog
                            common.setSetting('', '')
                            

        except Exception, e:
            common.showError('Error running SportsDevil')
            common.log('Error running SportsDevil. Reason:' + str(e))
