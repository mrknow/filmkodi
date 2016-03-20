# -*- coding: utf-8 -*-

import common

import urllib
import  os.path
import xbmc, xbmcgui

class Downloader(object):
    def __init__(self):
        self.pDialog = None

    def downloadWithJDownloader(self, url, title):
        common.runPlugin('plugin://plugin.program.jdownloader/?action=addlink&url=' + url)
        common.showNotification('Sent to JDownloader:')

    def downloadMovie(self, url, path, title, extension):
        if not os.path.exists(path):
            common.log('Path does not exist')
            return None
        if title == '':
            common.log('No title given')
            return None

        file_path = xbmc.makeLegalFilename(os.path.join(path, title + extension))
        file_path = urllib.unquote_plus(file_path)
        # Overwrite existing file?
        if os.path.isfile(file_path):
            self.pDialog = xbmcgui.Dialog()

            if not common.ask('File already exists. Overwrite?\n' + os.path.basename(file_path)):
                title = common.showOSK(urllib.unquote_plus(title), common.translate(30102))
                if not title:
                    return None
                file_path = xbmc.makeLegalFilename(os.path.join(path, title + extension))
                file_path = urllib.unquote_plus(file_path)
        
        success = self.__download(url, file_path)
        if success:
            return file_path
        else:
            return None


    def __download(self, url, file_path):
        try:
            # Setup progress dialog and download
            self.pDialog = xbmcgui.DialogProgress()
            self.pDialog.create('SportsDevil', common.translate(30050), common.translate(30051))
            urllib.urlretrieve(url, file_path, self.video_report_hook)
            self.pDialog.close()
            return True
        except IOError:
            self.pDialog.close()
            common.showError(common.translate(30053))
        except KeyboardInterrupt:
            self.pDialog.close()
        return False


    def video_report_hook(self, count, blocksize, totalsize):
        percent = int(float(count * blocksize * 100) / totalsize)
        self.pDialog.update(percent, common.translate(30050), common.translate(30051))
        if self.pDialog.iscanceled():
            raise KeyboardInterrupt
