# -*- coding: utf-8 -*-
import os
import xbmc, xbmcaddon
import common
import urllib
import zipfile

from traceback import print_exc
from dialogs.dialogProgress import DialogProgress
from utils.fileUtils import getFileContent, clearDirectory
from utils.regexUtils import findall

PACKAGE_DIR = "special://home/addons/packages/"
INSTALL_DIR = "special://home/addons/"


DICT = {
        'veetle': 'https://github.com/sissbruecker/xbmc-veetle-plugin/archive/master.zip',
        'jtv': 'https://divingmules-repo.googlecode.com/files/plugin.video.jtv.archives-0.3.6.zip',
        'youtube': 'http://ftp.hosteurope.de/mirror/xbmc.org/addons/frodo/plugin.video.youtube/plugin.video.youtube-4.4.4.zip'
        }

def install(key):
    entry = DICT[key]
    return _install_addon(entry)

def _install_addon(url):
    ri = AddonInstaller()
    compressed = ri.download(url)
    if compressed:
        addonId = ri.install(compressed)
        if addonId:
            xbmc.sleep(100)
            xbmc.executebuiltin('UpdateLocalAddons')
            xbmc.sleep(100)
            try:
                _N_ = xbmcaddon.Addon(id=addonId)
                common.showNotification(_N_.getAddonInfo("name"), 'Addon installed', 2000, _N_.getAddonInfo("icon"))
                return True
            except:
                pass
    return False

def isInstalled(addonId):
    try:
        _N_ = xbmcaddon.Addon(id=addonId)
        return True
    except:
        return False


class AddonInstaller:
    
    def download(self, url, destination=PACKAGE_DIR):
        try:
            dlg = DialogProgress()
            dlg.create('SportsDevil - Installing external addon')
            destination = xbmc.translatePath(destination) + os.path.basename(url)
            def _report_hook(count, blocksize, totalsize):
                percent = int(float(count * blocksize * 100) / totalsize)
                dlg.update(percent, url, destination)
            fp, _ = urllib.urlretrieve(url, destination, _report_hook)
            return fp
        except:
            print_exc()
        dlg.close()
        return ""

    def extract(self, fileOrPath, directory):
        try:               
            if not directory.endswith(':') and not os.path.exists(directory):
                os.mkdir(directory)
            zf = zipfile.ZipFile(fileOrPath)
            for _, name in enumerate(zf.namelist()):
                if name.endswith('/'):
                    path = os.path.join(directory, name)
                    if os.path.exists(path):
                        clearDirectory(path)
                    else:
                        os.makedirs(path, 0777)
                else:
                    outfile = open(os.path.join(directory, name), 'wb')
                    outfile.write(zf.read(name))
                    outfile.flush()
                    outfile.close()
            return zf.filelist

        except:
            print_exc()

        return None
                        
    def install(self, filename):
        destination = xbmc.translatePath(INSTALL_DIR)
        files = self.extract(filename, destination)
        if files:
            addonXml = filter(lambda x: x.filename.endswith('addon.xml'), files)
            if addonXml:
                path = os.path.join(destination, addonXml[0].filename)
                content = getFileContent(path)
                addonId = findall(content, '<addon id="([^"]+)"')
                if addonId:
                    return addonId[0]
        return None
    
