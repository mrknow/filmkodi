# -*- coding: utf-8 -*-

import os.path
import re
import xbmcgui
import urllib
import common
from string import lower

from entities.CListItem import CListItem
from xml.dom.minidom import parse as parseXml


from utils import fileUtils as fu

from utils.xbmcUtils import getKeyboard, getImage
from utils import regexUtils



class FavouritesManager:

    def __init__(self, favouritesFolder):
        self.cfgBuilder = CfgBuilder()
        
        self._favouritesFolder = favouritesFolder
        if not os.path.exists(self._favouritesFolder):
            os.makedirs(self._favouritesFolder, 0777)

        self._favouritesFile = os.path.join(self._favouritesFolder, 'favourites.cfg')
        if not os.path.exists(self._favouritesFile):
            self._createVirtualFolder('Favourites', self._favouritesFile)

        self._favouritesFoldersFolder = os.path.join(self._favouritesFolder, 'favfolders')
        if not os.path.exists(self._favouritesFoldersFolder):
            os.mkdir(self._favouritesFoldersFolder)




# ----------------------------------------------------------
# Helper functions
# ----------------------------------------------------------

    def _getFullPath(self, path):
        if path.startswith('favfolders'):
            path =  os.path.normpath(os.path.join(self._favouritesFolder, path))
        return path
    
    def _getShortPath(self, path):
        if not path.startswith('favfolders'):
            path = os.path.normpath(path).replace(self._favouritesFolder, '').strip(os.path.sep)
        return path

    def _parseXbmcFavourites(self):
        favItems = None
        xbmcFavsFile = common.Paths.xbmcFavouritesFile 
        if os.path.exists(xbmcFavsFile):
            doc = parseXml(xbmcFavsFile)
            xbmcFavs = doc.documentElement.getElementsByTagName('favourite')
            favItems = []
            for node in xbmcFavs:
                favItem = XbmcFavouriteItem.fromXmlNode(node)
                favItems.append(favItem)
        return favItems 

    def _createItem(self, title, m_type, icon, fanart, cfg, url, catcher):
        data = self.cfgBuilder.buildItem(title, m_type, url, icon, fanart, cfg, catcher)
        return data

    def _createFavourite(self, item):
        title = item.getInfo('title')
        m_type = item.getInfo('type')
        icon = item.getInfo('icon')
        fanart = item.getInfo('fanart')
        cfg = item.getInfo('cfg')
        url = item.getInfo('url')
        catcher = item.getInfo('catcher')
        return self._createItem(title, m_type, icon, fanart, cfg, url, catcher)

# ----------------------------------------------------------
# Virtual folders
# ----------------------------------------------------------
    
    def _virtualFolderSelection(self, name=None, path=None):
        if not name:
            name = 'Favourites'
        if not path:
            path = self._favouritesFile
        
        fullpath = self._getFullPath(path)
        items = self._parseVirtualFolder(fullpath)
        virtualFolders = filter(lambda x: self._isVirtualFolder(x), items)
        if len(virtualFolders) > 0:
            menuItems = ['root(' + name + ')']
            menuItems += map(lambda x: x['title'], virtualFolders)
            select = xbmcgui.Dialog().select('Select destination', menuItems)
            if select == -1:
                return None
            elif select == 0:
                return fullpath
            else:
                selItem = virtualFolders[select-1]
                return self._virtualFolderSelection(selItem['title'], selItem['url'])
        else:
            return fullpath
    
    def _isVirtualFolder(self, item):
        url = item.getInfo('url')
        return url and (url.startswith("favfolders/") or url.startswith("favfolders\\"))    
    
    def _getVirtualFoldersList(self):
        virtualFolders = os.listdir(self._favouritesFoldersFolder)
        return virtualFolders

    def _createVirtualFolder(self, name, path):
        fullPath = self._getFullPath(path)
        data = self.cfgBuilder.buildHeader(name)
        fu.setFileContent(fullPath, data)

    def _removeVirtualFolder(self, path, removeSubfolders=False):
        fullPath = self._getFullPath(path)
        if removeSubfolders:
            items = self._parseVirtualFolder(fullPath)
            subFolders = filter(lambda x: self._isVirtualFolder(x), items)
            for s in subFolders:
                self._removeVirtualFolder(s['url'], True)
        if os.path.exists(fullPath) and os.path.isfile(fullPath):
            os.remove(fullPath)

    def _parseVirtualFolder(self, path):
        fullpath = self._getFullPath(path)
        data = fu.getFileContent(fullpath)
        data = data.replace('\r\n', '\n').split('\n')
        items = []
        for m in data:
            if m and m[0] != '#':
                index = m.find('=')
                if index != -1:
                    key = lower(m[:index]).strip()
                    value = m[index+1:]

                    index = value.find('|')
                    if value[:index] == 'sports.devil.locale':
                        value = common.translate(int(value[index+1:]))
                    elif value[:index] == 'sports.devil.image':
                        value = os.path.join(common.Paths.imgDir, value[index+1:])

                    if key == 'title':
                        tmp = CListItem()
                        tmp['title'] = value
                    elif key == 'url':
                        tmp['url'] = value
                        items.append(tmp)
                        tmp = None
                    elif tmp != None:
                        tmp[key] = value
        return items   




# ----------------------------------------------------------
# Add item
# ----------------------------------------------------------
    def add(self, rootFolder=None):
        menuItems = ["Add folder", "Add SportsDevil item", "Add xbmc favourite"]
        select = xbmcgui.Dialog().select('Choose', menuItems)
        if select == 0:
            name = getKeyboard(default = '', heading = 'Set name')
            if name and len(name) > 0:
                return self._addFolder(name, rootFolder)
        elif select == 1:
            common.showInfo('Please browse through SportsDevil and use \ncontext menu entry "Add to SportsDevil favourites"')
        elif select == 2:
            return self._addXbmcFavourite(rootFolder)
        return False


    def _addXbmcFavourite(self, root):      
        xbmcFavs = self._parseXbmcFavourites()
        if xbmcFavs is None:
            common.showInfo('Favourites file not found')
        elif len(xbmcFavs) == 0:
            common.showInfo('No favourites found')
        else:            
            select = xbmcgui.Dialog().select('Choose' , map(lambda x: x.title, xbmcFavs))
            if select == -1:
                return False
            else:
                item = xbmcFavs[select].convertToCListItem()
                self.addItem(item, root)
                return True
        return False   
     
    def _addFolder(self, name, rootFolder=None):
        # create cfg
        filename = urllib.quote_plus(fu.cleanFilename(name))
        virtualFolderFile = filename + '.cfg'
        physicalFolder = os.path.normpath(self._favouritesFoldersFolder)
        virtualFolderPath = os.path.join(physicalFolder, virtualFolderFile)
        if os.path.exists(virtualFolderPath):
            prefix = filename + '-'
            suffix = '.cfg'
            virtualFolderFile = fu.randomFilename(directory=physicalFolder, prefix=prefix, suffix=suffix)
            virtualFolderPath = os.path.join(physicalFolder, virtualFolderFile)
        self._createVirtualFolder(name, virtualFolderPath)

        # create link
        linkToFolder = self._createItem(name, 'rss', '', '', None, 'favfolders/' + virtualFolderFile)
        if not rootFolder or os.path.normpath(rootFolder) == self._favouritesFile:
            rootFolder = self._favouritesFile
        fu.appendFileContent(rootFolder, linkToFolder)
        return True
       
        
    def addItem(self, item, root=None):
        target = root
        if not target:
            # if virtual folders exist
            virtualFolder = self._virtualFolderSelection()
            if virtualFolder:
                target = virtualFolder

        if target and os.path.exists(target):
            fav = self._createFavourite(item)
            fu.appendFileContent(target, fav)



# ----------------------------------------------------------
# Change or remove item
# ----------------------------------------------------------

    def editItem(self, item):
        menuItems = ["Change label", "Change icon", "Change fanart"]
        virtualFolders = self._getVirtualFoldersList()
        if len(virtualFolders) > 0 and not item.getInfo('url').startswith('favfolders/'):
            menuItems.append("Move to folder")
        select = xbmcgui.Dialog().select('Choose' , menuItems)
        if select == -1:
            return False
        cfgFile = self._favouritesFile
        definedIn = item.getInfo('definedIn')
        if definedIn and definedIn.startswith('favfolders/'):
            cfgFile = os.path.join(self._favouritesFoldersFolder, definedIn.split('/')[1])
        if select == 0:
            newLabel = getKeyboard(default = item.getInfo('title'), heading = 'Change label')
            if not newLabel or newLabel == "":
                return False
            self.changeLabel(item, newLabel)
        elif select == 1:
            newIcon = getImage('Change icon')
            if not newIcon:
                return False
            self.changeIcon(item, newIcon)
        elif select == 2:
            newFanart = getImage('Change fanart')
            if not newFanart:
                return False
            self.changeFanart(item, newFanart)
        elif select == 3:
            newCfgFile = self._virtualFolderSelection()
            if not newCfgFile or cfgFile == newCfgFile:
                return False
            self.moveToFolder(cfgFile, item, newCfgFile)
        return True


    def _findItem(self, item): 
        cfgFile = self._favouritesFile
        definedIn = item.getInfo('definedIn')
        if definedIn and definedIn.startswith('favfolders/'):
            cfgFile = os.path.join(self._favouritesFolder, definedIn)
        if os.path.exists(cfgFile):
            data = fu.getFileContent(cfgFile)
            regex = self.cfgBuilder.buildItem(re.escape(item.getInfo('title')), "[^#]*", re.escape(item.getInfo('url')))
            matches = regexUtils.findall(data, regex)        
            if matches:
                return (cfgFile, data, matches[0])
        return None
    
    def changeLabel(self, item, newLabel):
        found = self._findItem(item)
        if found:
            item['title'] = newLabel
            [cfgFile, data, fav] = found
            # if it's a virtual folder, rename file, rename header, update link
            if self._isVirtualFolder(item):           
                url = item.getInfo('url')
                oldFile = self._getFullPath(url)
                newFilename = urllib.quote_plus(fu.cleanFilename(newLabel))
                virtualFolderFile = newFilename + '.cfg'
                physicalFolder = os.path.normpath(self._favouritesFoldersFolder)
                virtualFolderPath = os.path.join(physicalFolder, virtualFolderFile)
                # check if new target is valid
                if os.path.exists(virtualFolderPath):
                    prefix = newFilename + '-'
                    suffix = '.cfg'
                    virtualFolderFile = fu.randomFilename(directory=physicalFolder, prefix=prefix, suffix=suffix)
                    virtualFolderPath = os.path.join(physicalFolder, virtualFolderFile)
                # update header
                content = fu.getFileContent(oldFile)
                oldHeader = self.cfgBuilder.buildHeader(item['title'])
                newHeader = self.cfgBuilder.buildHeader(newLabel)
                content = content.replace(oldHeader, newHeader)
                # rename file
                self._removeVirtualFolder(oldFile, False)
                fu.setFileContent(virtualFolderPath, content)                
                # update link
                item['url'] = self._getShortPath(virtualFolderPath)
            newfav = self._createFavourite(item)
            new = data.replace(fav, newfav.encode('utf-8'))
            fu.setFileContent(cfgFile, new)


    def changeIcon(self, item, newIcon):
        found = self._findItem(item)
        if found:
            [cfgFile, data, fav] = found
            newfav = self._createFavourite(item, icon=newIcon)
            new = data.replace(fav, newfav.encode('utf-8'))
            fu.setFileContent(cfgFile, new)

    def changeFanart(self, item, newFanart):
        found = self._findItem(item)
        if found:
            [cfgFile, data, fav] = found
            newfav = self._createFavourite(item, fanart=newFanart)
            new = data.replace(fav, newfav.encode('utf-8'))
            fu.setFileContent(cfgFile, new)

    def moveToFolder(self, cfgFile, item, newCfgFile):
        found = self._findItem(item)
        if found:
            [cfgFile, data, fav] = found
            if os.path.exists(newCfgFile):
                new = data.replace(fav,'')
                fu.setFileContent(cfgFile, new)
                fu.appendFileContent(newCfgFile, fav)

    def removeItem(self, item):
        found = self._findItem(item)
        if found:
            try:
                # delete virtual folder
                if self._isVirtualFolder(item):
                    self._removeVirtualFolder(item['url'], True)
                # delete link
                [cfgFile, data, fav] = found
                new = data.replace(fav,'')
                fu.setFileContent(cfgFile, new)
                return True
            except:
                return False 
        return False



        
    
    
    

class XbmcFavouriteItem:
    def __init__(self, title, icon, url):
        self.title = title
        self.icon = icon
        self.url = url


    @classmethod
    def fromXmlNode(cls, node):
        try:
            title = node.attributes['name'].nodeValue
        except:
            title = ''
        try:
            icon = node.attributes['thumb'].nodeValue
        except:
            icon = ''
        try:
            url = node.childNodes[0].nodeValue
        except:
            url = ''
        return cls(title, icon, url)


    def convertToCListItem(self):
        item = CListItem()
        item.setInfo('title', self.title)
        item.setInfo('type', 'command')
        item.setInfo('icon', self.icon)
        item.setInfo('url', self.url)
        return item


class CfgBuilder:
    
    def __init__(self):
        self.minWidth = 52
        pass
    
    def buildSeperator(self, title):
        titleLength = len(title)
        width = max(titleLength, self.minWidth) + 4  # '# ' and ' #' = 4 chars
        sepLine = '#' * width
        return sepLine      
    
    def buildHeader(self, title):
        titleLength = len(title)
        sepLine = self.buildSeperator(title)
        space = len(sepLine) - titleLength - 4
        titleLine = '# ' + title.upper() + ' ' * space + ' #'
        data = [sepLine, titleLine, sepLine]
        return '\n'.join(data)
    
    def buildItem(self, title, m_type, url, icon=None, fanart=None, cfg=None, catcher=None):
        sepLine = self.buildSeperator(title)
        data = [
            '\n' + sepLine,
            'title=' + title,
            'type=' + m_type
            ]
        if icon:
            data.append('icon=' + icon)
        if fanart:
            data.append('fanart=' + fanart)
        if cfg:
            data.append('cfg=' + cfg)
        if catcher:
            data.append('catcher=' + catcher)
        data.append('url=' + url)
        return '\n'.join(data)