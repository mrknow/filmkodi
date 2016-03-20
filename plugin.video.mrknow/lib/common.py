# -*- coding: utf-8 -*-

import os


#------------------------------------------------------------------------------
# xbmc related
#------------------------------------------------------------------------------
import xbmc, xbmcaddon

__settings__ = xbmcaddon.Addon(id='plugin.video.mrknow')
__icon__ = xbmcaddon.Addon(id='plugin.video.mrknow').getAddonInfo('icon')
translate = __settings__.getLocalizedString
enable_debug = True
language = xbmc.getLanguage

class Mode2:
    UPDATE = 100
    VIEW = 110
    PLAY = 102
    QUEUE = 103
    DOWNLOAD = 104
    EXECUTE = 105
    ADDTOFAVOURITES = 106
    REMOVEFROMFAVOURITES = 107
    EDITITEM = 108
    ADDITEM = 109
    DOWNLOADCUSTOMMODULE = 110
    REMOVEFROMCUSTOMMODULES = 111
    INSTALLADDON = 112
    CHROME = 113

class Mode3:
    UPDATE = 200
    VIEW = 210
    PLAY = 202
    QUEUE = 203
    DOWNLOAD = 204
    EXECUTE = 205
    ADDTOFAVOURITES = 206
    REMOVEFROMFAVOURITES = 207
    EDITITEM = 208
    ADDITEM = 209
    DOWNLOADCUSTOMMODULE = 210
    REMOVEFROMCUSTOMMODULES = 211
    INSTALLADDON = 212
    CHROME = 213


"""
def log(msg, level=xbmc.LOGDEBUG):
    plugin = "Mrknow"
    msg = msg.encode('utf-8')
    xbmc.log("[%s] %s" % (plugin, msg.__str__()), level)
"""
def log(msg, level=xbmc.LOGNOTICE):
    plugin = "plugin.video.mrknow"
    msg = msg.encode('utf-8')
    xbmc.log("[%s] %s" % (plugin, msg.__str__()), level)
    print("[%s] %s" % (plugin, msg.__str__()))

def getSetting(name):
    return __settings__.getSetting(name)

def setSetting(name, value):
    __settings__.setSetting(id=name, value=value)

def showNotification(title, message, timeout=2000, icon=__icon__):
    def clean(s):
        return str(s.encode('utf-8', 'ignore'))
    command = ''
    if icon:
        command = 'Notification(%s,%s,%s,%s)' % (clean(title), clean(message), timeout, icon)
    else:
        command = 'Notification(%s,%s,%s)' % (clean(title), clean(message), timeout)
    xbmc.executebuiltin(command)

def runPlugin(url):
    xbmc.executebuiltin('XBMC.RunPlugin(' + url +')')

#------------------------------------------------------------------------------
# dialogs
#------------------------------------------------------------------------------
from dialogs.dialogQuestion import DialogQuestion
from dialogs.dialogBrowser import DialogBrowser
from dialogs.dialogInfo import DialogInfo
from dialogs.dialogError import DialogError

from utils.xbmcUtils import getKeyboard
from utils import fileUtils as fu


def ask(question):
    diaQuestion = DialogQuestion()
    return diaQuestion.ask(question)

def showInfo(message):
    diaInfo = DialogInfo()
    diaInfo.show(message)   

def showError(message):
    diaError = DialogError()
    diaError.show(message)

def browseFolders(head):
    diaFolder = DialogBrowser()
    return diaFolder.browseFolders(head)

def showOSK(defaultText='', title='', hidden=False):
    return getKeyboard(defaultText, title, hidden)

    

#------------------------------------------------------------------------------
# web related
#------------------------------------------------------------------------------
from utils.regexUtils import parseTextToGroups
from utils.webUtils import CachedWebRequest
import cookielib

def getHTML(url, form_data='', referer='', xml=False, mobile=False, ignoreCache=False, demystify=False):
    cookiePath = xbmc.translatePath(os.path.join(Paths.cacheDir, 'cookies.lwp'))
    request = CachedWebRequest(cookiePath, Paths.cacheDir)
    #log('#getHTML: "'+ url + '" from "' + referer + '"')
    return request.getSource(url, form_data, referer, xml, mobile, ignoreCache, demystify)

def getCookies(cookieName, domain):
    cookiePath = xbmc.translatePath(os.path.join(Paths.cacheDir, 'cookies.lwp'))
    
    def load_cookies_from_lwp(filename):
        lwp_cookiejar = cookielib.LWPCookieJar()
        lwp_cookiejar.load(filename, ignore_discard=True)
        return lwp_cookiejar
    
    for cookie in load_cookies_from_lwp(cookiePath):
        if domain in cookie.domain and cookieName in cookie.name:
            return cookie.value

def parseWebsite(source, regex, referer='', variables=[]):
    def parseWebsiteToGroups(url, regex, referer=''):
        data = getHTML(url, None, referer)
        return parseTextToGroups(data, regex)

    groups = parseWebsiteToGroups(source, regex, referer)

    if variables == []:
        if groups:
            return groups[0]
        else:
            return ''
    else:
        resultArr = {}
        i = 0
        for v in variables:
            if groups:
                resultArr[v] = groups[i]
            else:
                resultArr[v] = ''
            i += 1
        return resultArr

def clearCache():
    cacheDir = Paths.cacheDir
    if not os.path.exists(cacheDir):
        os.mkdir(cacheDir, 0777)
        print('Cache directory created' + str(cacheDir))
    else:
        fu.clearDirectory(cacheDir)
        print('Cache directory purged')



#------------------------------------------------------------------------------
# classes with constants
#------------------------------------------------------------------------------
class Paths:
    rootDir = xbmc.translatePath(__settings__.getAddonInfo('path')).decode('utf-8')


    resDir = os.path.join(rootDir, 'resources')
    imgDir = os.path.join(resDir, 'images')
    modulesDir = os.path.join(resDir, 'modules')
    catchersDir = os.path.join(resDir,'catchers')
    dictsDir = os.path.join(resDir,'dictionaries')

    pluginFanart = os.path.join(rootDir, 'fanart.jpg')
    pluginFanart1 = os.path.join(rootDir, 'fanart1.jpg')
    defaultVideoIcon = os.path.join(imgDir, 'video.png')
    defaultCategoryIcon = os.path.join(imgDir, 'folder.png')    

    pluginDataDir = xbmc.translatePath(__settings__.getAddonInfo('profile')).decode('utf-8')
    print("pluginDataDir",pluginDataDir)
    cacheDir = os.path.join(pluginDataDir, 'cache')
    favouritesFolder = os.path.join(pluginDataDir, 'favourites')
    favouritesFile = os.path.join(favouritesFolder, 'favourites.cfg')
    customModulesDir = os.path.join(pluginDataDir, 'custom')
    customModulesFile = os.path.join(customModulesDir, 'custom.cfg')
    
    catchersRepo = ''
    modulesRepo = ''
    customModulesRepo = ''
    
    xbmcFavouritesFile = xbmc.translatePath( 'special://profile/favourites.xml' )

