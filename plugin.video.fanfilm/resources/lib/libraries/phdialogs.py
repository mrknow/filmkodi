# -*- coding: utf-8 -*-

'''
    Phoenix Add-on
    Copyright (C) 2015 Blazetamer

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

import urllib2,os,time
import xbmc,xbmcgui,xbmcaddon,xbmcplugin

supportsite = 'tvaddons.ag'


def openDialog(image,audio):
    audio = audio
    print 'MUSIC IS  '+audio
    path = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.phstreams/resources/skins/DefaultSkin','media'))
    popimage=os.path.join(path, 'tempimage.jpg')
    downloadFile(image,popimage)
    musicsound=os.path.join(path, 'tempsound.mp3')
    downloadFile(audio,musicsound)
    if xbmc.getCondVisibility('system.platform.ios'):
        if not xbmc.getCondVisibility('system.platform.atv'):
            popup = dialog('pop1.xml',xbmcaddon.Addon().getAddonInfo('path'),'DefaultSkin',close_time=20,logo_path='%s/resources/skins/DefaultSkin/media/Logo/'%xbmcaddon.Addon().getAddonInfo('path'),)
    if xbmc.getCondVisibility('system.platform.android'):
        popup = dialog('pop1.xml',xbmcaddon.Addon().getAddonInfo('path'),'DefaultSkin',close_time=20,logo_path='%s/resources/skins/DefaultSkin/media/Logo/'%xbmcaddon.Addon().getAddonInfo('path'))
    else:
        popup = dialog('pop.xml',xbmcaddon.Addon().getAddonInfo('path'),'DefaultSkin',close_time=20,logo_path='%s/resources/skins/DefaultSkin/media/Logo/'%xbmcaddon.Addon().getAddonInfo('path'))
    popup.doModal()
    del popup


def downloadFile(url,dest,silent = False,cookie = None):
    try:
        import urllib2
        file_name = url.split('/')[-1]
        print "Downloading: %s" % (file_name)
        if cookie:
            import cookielib
            cookie_file = os.path.join(os.path.join(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')),'Cookies'), cookie+'.cookies')
            cj = cookielib.LWPCookieJar()
            if os.path.exists(cookie_file):
                try: cj.load(cookie_file,True)
                except: cj.save(cookie_file,True)
            else: cj.save(cookie_file,True)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        else:
            opener = urllib2.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')]
        u = opener.open(url)
        f = open(dest, 'wb')
        meta = u.info()
        if meta.getheaders("Content-Length"):
            file_size = int(meta.getheaders("Content-Length")[0])
        else: file_size = 'Unknown'
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer: break
            file_size_dl += len(buffer)
            f.write(buffer)
        print "Downloaded: %s %s Bytes" % (file_name, file_size)
        f.close()
        return True
    except Exception:
        print 'Error downloading file ' + url.split('/')[-1]
        #ErrorReport(e)
        if not silent:
            dialog = xbmcgui.Dialog()
            dialog.ok("Phoenix Streams", "Report any errors  at " + supportsite,  "We will try our best to help you")
        return False


class dialog( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        self.shut = kwargs['close_time'] 
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        xbmc.executebuiltin( "Skin.SetBool(AnimeWindowXMLDialogClose)" )

    def onInit( self):
        xbmc.Player().play('%s/resources/skins/DefaultSkin/media/tempsound.mp3'%xbmcaddon.Addon().getAddonInfo('path'))# Music   
        #xbmc.Player().play(musicsound)# Music
        while self.shut > 0:
            xbmc.sleep(1000)
            self.shut -= 1
        xbmc.Player().stop()
        self._close_dialog()
            
    def onFocus( self, controlID ): pass

    def onClick( self, controlID ): 
        if controlID == 12 or controlID == 7:
            xbmc.Player().stop()
        self._close_dialog()

    def onAction( self, action ):
        if action in [ 5, 6, 7, 9, 10, 92, 117 ] or action.getButtonCode() in [ 275, 257, 261 ]:
            xbmc.Player().stop()
            self._close_dialog()

    def _close_dialog( self ):
        path = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.phstreams/resources/skins/DefaultSkin','media'))
        popimage=os.path.join(path, 'tempimage.jpg')
        musicsound=os.path.join(path, 'tempsound.mp3')
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        time.sleep( .4 )
        self.close()
        os.remove(popimage)
        os.remove(musicsound)


