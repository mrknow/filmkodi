# -*- coding: utf-8 -*-

'''
    Specto Add-on
    Copyright (C) 2015 lambda

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
'''


import os,xbmc,xbmcaddon,xbmcplugin,xbmcgui,xbmcvfs
import base64, jsunpack
import random, time

tmdb_key = jsunpack.jsunpack_keys()
tvdb_key = base64.urlsafe_b64decode('MUQ2MkYyRjkwMDMwQzQ0NA==')
fanarttv_key = base64.urlsafe_b64decode('YTc4YzhmZWRjN2U3NTE1MjRkMzkyNmNhMmQyOTU3OTg=')
trakt_key = base64.urlsafe_b64decode('NDFjYzI1NjY5Y2Y2OTc0NTg4ZjA0MTMxYjcyZjc4MjEwMzdjY2I1ZTdlMjMzNDVjN2MxZTk3NGI4MGI5ZjI1NQ==')
trakt_secret = base64.urlsafe_b64decode('Y2I4OWExYTViN2ZlYmJiMDM2NmQ3Y2EyNzJjZDc4YTU5MWQ1ODI2Y2UyMTQ1NWVmYzE1ZDliYzQ1ZWNjY2QyZQ==')

scriptID = 'plugin.video.specto'
ptv = xbmcaddon.Addon(scriptID)

lang = xbmcaddon.Addon().getLocalizedString

setting = xbmcaddon.Addon().getSetting

addon = xbmcaddon.Addon

addItem = xbmcplugin.addDirectoryItem

item = xbmcgui.ListItem

directory = xbmcplugin.endOfDirectory

content = xbmcplugin.setContent

property = xbmcplugin.setProperty

addonInfo = xbmcaddon.Addon().getAddonInfo

infoLabel = xbmc.getInfoLabel

condVisibility = xbmc.getCondVisibility

jsonrpc = xbmc.executeJSONRPC

window = xbmcgui.Window(10000)

dialog = xbmcgui.Dialog()

progressDialog = xbmcgui.DialogProgress()

windowDialog = xbmcgui.WindowDialog()

button = xbmcgui.ControlButton

image = xbmcgui.ControlImage

keyboard = xbmc.Keyboard

sleep = xbmc.sleep

execute = xbmc.executebuiltin

skin = xbmc.getSkinDir()

player = xbmc.Player()

playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

resolve = xbmcplugin.setResolvedUrl

openFile = xbmcvfs.File

makeFile = xbmcvfs.mkdir

deleteFile = xbmcvfs.delete

listDir = xbmcvfs.listdir

transPath = xbmc.translatePath

skinPath = xbmc.translatePath('special://skin/')

addonPath = xbmc.translatePath(addonInfo('path'))

dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')

settingsFile = os.path.join(dataPath, 'settings.xml')

databaseFile = os.path.join(dataPath, 'settings.db')

favouritesFile = os.path.join(dataPath, 'favourites.db')

sourcescacheFile = os.path.join(dataPath, 'sources.db')

sourcescachedUrl = os.path.join(dataPath, 'sourcesurl.db')

cachemetaFile = os.path.join(dataPath, 'metacache.db')

libcacheFile = os.path.join(dataPath, 'library.db')

metacacheFile = os.path.join(dataPath, 'meta.db')

cacheFile = os.path.join(dataPath, 'cache.db')

cookieDir = os.path.join(dataPath, 'Cookies')

try:
    makeFile(cookieDir)
except:
    pass

def addonIcon():
    appearance = setting('appearance').lower()
    if appearance in ['-', '']: return addonInfo('icon')
    else: return os.path.join(addonPath, 'resources', 'media', appearance, 'icon.png')


def addonPoster():
    appearance = setting('appearance').lower()
    if appearance in ['-', '']: return 'DefaultVideo.png'
    else: return os.path.join(addonPath, 'resources', 'media', appearance, 'poster.png')


def addonBanner():
    appearance = setting('appearance').lower()
    if appearance in ['-', '']: return 'DefaultVideo.png'
    else: return os.path.join(addonPath, 'resources', 'media', appearance, 'banner.png')


def addonThumb():
    appearance = setting('appearance').lower()
    if appearance == '-': return 'DefaultFolder.png'
    elif appearance == '': return addonInfo('icon')
    else: return os.path.join(addonPath, 'resources', 'media', appearance, 'icon.png')


def addonFanart():
    appearance = setting('appearance').lower()
    if appearance == '-': return None
    elif appearance == '': return addonInfo('fanart')
    else: return os.path.join(addonPath, 'resources', 'media', appearance, 'fanart.jpg')


def addonNext():
    appearance = setting('appearance').lower()
    if appearance in ['-', '']: return 'DefaultFolderBack.png'
    else: return os.path.join(addonPath, 'resources', 'media', appearance, 'next.jpg')


def artPath():
    appearance = setting('appearance').lower()
    if appearance in ['-', '']: return None
    else: return os.path.join(addonPath, 'resources', 'media', appearance)


def infoDialog(message, heading=addonInfo('name'), icon=addonIcon(), time=3000):
    try: dialog.notification(heading, message, icon, time, sound=False)
    except: execute("Notification(%s,%s, %s, %s)" % (heading, message, time, icon))


def yesnoDialog(line1, line2, line3, heading=addonInfo('name'), nolabel='', yeslabel=''):
    return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel)


def selectDialog(list, heading=addonInfo('name')):
    return dialog.select(heading, list)


def version():
    num = ''
    try: version = addon('xbmc.addon').getAddonInfo('version')
    except: version = '999'
    for i in version:
        if i.isdigit(): num += i
        else: break
    return int(num)


def refresh():
    return execute('Container.Refresh')


def idle():
    return execute('Dialog.Close(busydialog)')


def queueItem():
    return execute('Action(Queue)')


def openPlaylist():
    return execute('ActivateWindow(VideoPlaylist)')


def openSettings(query=None, id=addonInfo('id')):
    try:
        idle()
        execute('Addon.OpenSettings(%s)' % id)
        if query == None: raise Exception()
        c, f = query.split('.')
        execute('SetFocus(%i)' % (int(c) + 100))
        execute('SetFocus(%i)' % (int(f) + 200))
    except:
        return


def set_setting(id, value):
    if not isinstance(value, basestring): value = str(value)
    ptv.setSetting(id=id, value=value)

def log(msg, level=xbmc.LOGNOTICE):
    #return
    level = xbmc.LOGNOTICE
    print('[SPECTO]: %s' % (msg))

    try:
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')
        xbmc.log('[SPECTO]: %s' % (msg), level)
    except Exception as e:
        try:
            #xbmc.log('Logging Failure: %s' % (e), level)
            a=1
        except: pass  # just give up



def randomagent():
    BR_VERS = [
        ['%s.0' % i for i in xrange(18, 43)],
        ['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101', '38.0.2125.104', '38.0.2125.111', '39.0.2171.71', '39.0.2171.95', '39.0.2171.99', '40.0.2214.93', '40.0.2214.111',
         '40.0.2214.115', '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81', '43.0.2357.124', '44.0.2403.155', '44.0.2403.157', '45.0.2454.101', '45.0.2454.85', '46.0.2490.71',
         '46.0.2490.80', '46.0.2490.86', '47.0.2526.73', '47.0.2526.80'],
        ['11.0']]
    WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1', 'Windows NT 5.0']
    FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
    RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
                'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
                'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko']
    index = random.randrange(len(RAND_UAS))
    return RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[index]))

DEFAULT_TIMEOUT = 30
BR_VERS = [
    ['%s.0' % i for i in xrange(18, 43)],
    ['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101', '38.0.2125.104', '38.0.2125.111', '39.0.2171.71', '39.0.2171.95', '39.0.2171.99', '40.0.2214.93', '40.0.2214.111',
     '40.0.2214.115', '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81', '43.0.2357.124', '44.0.2403.155', '44.0.2403.157', '45.0.2454.101', '45.0.2454.85', '46.0.2490.71',
     '46.0.2490.80', '46.0.2490.86', '47.0.2526.73', '47.0.2526.80'],
    ['11.0']]
WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1', 'Windows NT 5.0']
FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
            'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
            'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko']
MAX_RESPONSE = 1024 * 1024 * 2
USER_AGENT = "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko"

def get_ua():
    try: last_gen = int(setting('last_ua_create'))
    except: last_gen = 0
    if not setting('current_ua') or last_gen < (time.time() - (7 * 24 * 60 * 60)):
        index = random.randrange(len(RAND_UAS))
        user_agent = RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[index]))
        log('Creating New User Agent: %s' % (user_agent))
        set_setting('current_ua', user_agent)
        set_setting('last_ua_create', str(int(time.time())))
    else:
        user_agent = setting('current_ua')
    return user_agent
