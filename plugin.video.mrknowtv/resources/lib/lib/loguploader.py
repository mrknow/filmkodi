import os
import re
import socket
from urllib import urlencode
from urllib import FancyURLopener
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs
import platform

ADDON        = xbmcaddon.Addon()
ADDONID      = ADDON.getAddonInfo('id')
ADDONNAME    = ADDON.getAddonInfo('name')
ADDONVERSION = ADDON.getAddonInfo('version')
CWD          = ADDON.getAddonInfo('path').decode('utf-8')
xbmc_version = xbmc.getInfoLabel( "System.BuildVersion" )
LANGUAGE     = ADDON.getLocalizedString

socket.setdefaulttimeout(5)

URL      = 'http://paste.filmkodi.com/api/create'
MAINURL  = 'http://paste.filmkodi.com/%s'
LOGPATH  = xbmc.translatePath('special://logpath')
LOGFILE  = os.path.join(LOGPATH, 'kodi.log')
OLDLOG   = os.path.join(LOGPATH, 'kodi.old.log')
REPLACES = (('//.+?:.+?@', '//USER:PASSWORD@'),('<user>.+?</user>', '<user>USER</user>'),('<pass>.+?</pass>', '<pass>PASSWORD</pass>'),)

def log(txt):
    if isinstance (txt,str):
        txt = txt.decode('utf-8')
    message = u'%s: %s' % (ADDONID, txt)
    xbmc.log(msg=message.encode('utf-8'), level=xbmc.LOGDEBUG)

# Custom urlopener to set user-agent
class pasteURLopener(FancyURLopener):
    version = '%s: %s' % (ADDONID, ADDONVERSION)

class Luguploader:
    def __init__(self):
        self.getSettings()
        files = self.getFiles()
        for item in files:
            filetype = item[0]
            if filetype == 'log':
                error = LANGUAGE(32011)
                name = LANGUAGE(32031)
            elif filetype == 'oldlog':
                error = LANGUAGE(32012)
                name = LANGUAGE(32032)
            succes, data = self.readLog(item[1])
            if succes:
                content = self.cleanLog(data)
                succes, result = self.postLog(content)
                if succes:
                    self.showResult(LANGUAGE(32005) % (name, result))
                else:
                    self.showResult('%s[CR]%s' % (error, result))
            else:
                self.showResult('%s[CR]%s' % (error, result))

    def getSettings(self):
        self.oldlog = False

    def getFiles(self):
        logfiles = []
        logfiles.append(['log', LOGFILE])
        if self.oldlog:
            if xbmcvfs.exists(OLDLOG):
                logfiles.append(['oldlog', OLDLOG])
            else:
                self.showResult(LANGUAGE(32021))
        return logfiles

    def readLog(self, path):
        try:
            lf = xbmcvfs.File(path)
            content = lf.read()
            lf.close()
            if content:
                return True, content
            else:
                log('file is empty')
                return False, LANGUAGE(32001)
        except:
            log('unable to read file')
            return False, LANGUAGE(32002)

    def cleanLog(self, content):
        for pattern, repl in REPLACES:
            content = re.sub(pattern, repl, content)
            return content

    def postLog(self, data):
        params = {}
        params['title'] = '%s-%s|%s' % (ADDONID,ADDONVERSION, xbmc_version)
        params['title'] = params['title'].replace('plugin.video.','')[0:29]
        params['text'] = data
        params['lang'] = 'text'
        params['name'] = '%s, %s' %(platform.system(), platform.release())
        params = urlencode(params)

        #url_opener = pasteURLopener()
        #import json
        import urllib2
        req = urllib2.Request(URL, params)
        #req.add_header('Content-Type', 'application/json')
        #req.add_header('User-Agent', '%s: %s' % (ADDONID, ADDONVERSION))
        #response = urllib2.urlopen(req, json.dumps(params))

        try:
            #page = url_opener.open(URL, params)
            response = urllib2.urlopen(req)

        except Exception as e:
            log('failed to connect to the server %s' % e)
            #log('DATA %s' % data)
            return False, LANGUAGE(32003)

        try:
            page_url = response.read()
            log(page_url)
            return True, '%s' % page_url
        except:
            log('unable to retrieve the paste url')
            return False, LANGUAGE(32004)

    def showResult(self, message):
        dialog = xbmcgui.Dialog()
        confirm = dialog.ok(ADDONNAME, message)

