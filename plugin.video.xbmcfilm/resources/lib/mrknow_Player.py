# -*- coding: utf-8 -*-
import re, sys, os, cgi
import urllib, urllib2
import xbmcgui,xbmc, mrknow_pCommon, xbmcaddon, time, xbmcplugin


ptv = xbmcaddon.Addon()
scriptID = ptv.getAddonInfo('id')
scriptname = ptv.getAddonInfo('name')
#dbg = ptv.getSetting('default_debug') in ('true')
ptv = xbmcaddon.Addon(scriptID)

import mrknow_urlparser, mrknow_Pageparser

class mrknow_Player:
    def __init__(self):
        self.cm = mrknow_pCommon.common()
        self.up = mrknow_urlparser.mrknow_urlparser()
        self.pp = mrknow_Pageparser.mrknow_Pageparser()

    def LOAD_AND_PLAY_VIDEO(self, url, title, icon,year='',plot=''):
        progress = xbmcgui.DialogProgress()
        progress.create('Postęp', '')
        message = ptv.getLocalizedString(30406)
        progress.update( 10, "", message, "" )
        xbmc.sleep( 1000 )
        progress.update( 30, "", message, "" )
        progress.update( 50, "", message, "" )
        VideoLink = ''
        subs=''
        VideoLink = self.pp.getVideoLink(url)
        print("Type",type(VideoLink))
        if type(VideoLink) is dict:
            videoUrl = VideoLink[0]
            subs = VideoLink[1]
        elif type(VideoLink) is bool:
            videoUrl = ''
        else:
            videoUrl = VideoLink
        progress.update( 70, "", message, "" )
        pluginhandle = int(sys.argv[1])
        if videoUrl == '':
            progress.close()
            d = xbmcgui.Dialog()
            d.ok('Nie znaleziono streamingu', 'Mo�e to chwilowa awaria.', 'Spr�buj ponownie za jaki� czas')
            return False
        if icon == '' or  icon == 'None':
            icon = "DefaultVideo.png"
        if plot == '' or plot == 'None':
            plot = ''
        liz=xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon, path=videoUrl )
        liz.setInfo( type="video", infoLabels={ "Title": title} )
        xbmcPlayer = xbmc.Player()

        if subs != '':
            subsdir = os.path.join(ptv.getAddonInfo('path'), "subs")
            if not os.path.isdir(subsdir):
                os.mkdir(subsdir)
            query_data = { 'url': subs, 'use_host': False, 'use_header': False, 'use_cookie': False, 'use_post': False, 'return_data': True }
            progress.update( 80, "", message, "" )
            data = self.cm.getURLRequestData(query_data)
            output = open((os.path.join(subsdir, "napisy.txt" )),"w+")
            progress.update( 90, "", message, "" )
            output.write(data)
            output.close()
            progress.update( 100, "", message, "" )
            progress.close()
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)

            for _ in xrange(30):
                if xbmcPlayer.isPlaying():
                    break
                time.sleep(1)
            else:
                raise Exception('No video playing. Aborted after 30 seconds.')
            xbmcPlayer.setSubtitles((os.path.join(subsdir, "napisy.txt" )))
            xbmcPlayer.showSubtitles(True)

        else:
            progress.update( 90, "", message, "" )
            progress.close()
            #listitem = xbmcgui.ListItem(path=videoUrl)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)


        