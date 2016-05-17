# -*- coding: utf-8 -*-

import xbmcgui, xbmc, xbmcplugin

enable_debug = False

#######################################
# Xbmc Helpers
#######################################

def select(title, menuItems):
    select = xbmcgui.Dialog().select(title, menuItems)
    if select == -1:
        return None
    else:
        return menuItems[select]


def getKeyboard(default = '', heading = '', hidden = False):
    kboard = xbmc.Keyboard(default, heading, hidden)
    kboard.doModal()
    if kboard.isConfirmed():
        return kboard.getText()
    return ''


def getImage(title):
    dialog = xbmcgui.Dialog()
    image = dialog.browse(1, title, 'pictures', '.jpg|.png', True)
    return image


def showMessage(msg):
    xbmc.executebuiltin('Notification(SportsDevil,' + str(msg.encode('utf-8', 'ignore')) + ')')
    
    
def showBusyAnimation():
    xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
    
def hideBusyAnimation():
    xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )

    
def closeAllDialogs():
    xbmc.executebuiltin('Dialog.Close(all, true)') 
    
    
def log(msg):
    if enable_debug:
        try:
            xbmc.log(msg)
        except:
            xbmc.log(msg.encode('utf-8'))        


def setSortMethodsForCurrentXBMCList(handle, sortKeys):
    
    def addSortMethod(method):
        xbmcplugin.addSortMethod(handle = handle, sortMethod = method)
    
    if not sortKeys or sortKeys==[]: 
        addSortMethod(xbmcplugin.SORT_METHOD_UNSORTED)
    else:     
        if 'name' in sortKeys:
            addSortMethod(xbmcplugin.SORT_METHOD_LABEL)
        if 'size' in sortKeys:
            addSortMethod(xbmcplugin.SORT_METHOD_SIZE)
        if 'duration' in sortKeys:
            addSortMethod(xbmcplugin.SORT_METHOD_DURATION)
        if 'genre' in sortKeys:
            addSortMethod(xbmcplugin.SORT_METHOD_GENRE)
        if 'rating' in sortKeys:
            addSortMethod(xbmcplugin.SORT_METHOD_VIDEO_RATING)
        if 'date' in sortKeys:
            addSortMethod(xbmcplugin.SORT_METHOD_DATE)
        if 'file' in sortKeys:
            addSortMethod(xbmcplugin.SORT_METHOD_FILE)
            
            
            
def getContainerFolderPath():   
    return xbmc.getInfoLabel('Container.FolderPath')

def getListItemPath():
    return xbmc.getInfoLabel('ListItem.Path')

def getCurrentWindow():
    return xbmc.getInfoLabel('System.CurrentWindow')

def getCurrentControl():
    return xbmc.getInfoLabel('System.CurrentControl')

def getCurrentWindowXmlFile():
    return xbmc.getInfoLabel('Window.Property(xmlfile)')