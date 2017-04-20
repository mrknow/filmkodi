import sys, re, os
import urllib, urllib2
import urlparse
import xbmcgui
import xbmcplugin
import xbmc, xbmcaddon
import json
import wizja

from resources.lib.lib import client
from resources.lib.lib import control

__scriptID__ = 'plugin.video.wizjatv'
__addon__ = xbmcaddon.Addon(id='plugin.video.wizjatv')

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
VERSION = 2.1

xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

mode = args.get('mode', None)

if mode is None:
    icon = os.path.join( __addon__.getAddonInfo('path'), 'images/icon-tv2.png' )
    url = build_url({'mode': 'tv', 'foldername': 'Telewizja ONLINE'})
    li = xbmcgui.ListItem('Telewizja ONLINE', iconImage=icon)
    li.setArt({'fanart': control.addonFanart2()})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)	

    icon = os.path.join( __addon__.getAddonInfo('path'), 'images/icon-opcje1.png' )
    url = build_url({'mode': 'ustawienia', 'foldername': 'Ustawienia'})
    li = xbmcgui.ListItem('Ustawienia', iconImage=icon)
    li.setArt({'fanart': control.addonFanart2()})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'tv':
    list = []
    try:
        items = wizja.wizjachanels()
        for item in items:
            id = item['id']
            title = item['title']
            title = client.replaceHTMLCodes(title)

            poster = '0'
            try: poster = item['img']
            except: pass
            poster = poster.encode('utf-8')

            try:
                fanart = control.addonFanart()
                fanart = fanart.encode('utf-8')
            except:
                fanart = '0'
                fanart = fanart.encode('utf-8')
                pass

            plot = '0'
            plot = client.replaceHTMLCodes(plot)
            plot = plot.encode('utf-8')
            tagline = '0'
            tagline = tagline.encode('utf-8')

            list.append(
                {'title': title, 'originaltitle': title, 'genre': '0', 'plot': plot, 'name': title, 'tagline': tagline,
                 'poster': poster, 'fanart': fanart, 'id': id, 'service': 'wizja', 'next': next})
            # control.log("##################><><><><> pierwsza item  %s" % self.list)

        import operator
        list.sort(key=operator.itemgetter('title'))

        for s in list:
            url = build_url({'mode': 'play', 'id': s['id'], 'poster':s['poster'], 'name':s['name']})
            ico = s['poster']
            li = xbmcgui.ListItem(s['name'], iconImage=ico, thumbnailImage=ico)
            li.setProperty('IsPlayable', 'true')
            li.setArt({'fanart': control.addonFanart2()})
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li)
        xbmcplugin.endOfDirectory(addon_handle)
    except Exception as e:
        control.log('ERROR TV:%s' % e )
        pass

elif mode[0] == 'play':
    try:
        title =args.get('name', None)[0]
        icon = args.get('poster', None)[0]
        id = args.get('id', None)[0]
        control.infoDialog(control.lang(30492).encode('utf-8'), time=500)
        u = wizja.getstream(id)

        liz = control.item(title, iconImage=icon, thumbnailImage=icon, path=u)
        liz.setInfo(type="video", infoLabels={"Title": title})
        xbmcPlayer = xbmc.Player()

        control.resolve(int(sys.argv[1]), True, liz)

        for i in range(0, 240):
            if xbmcPlayer.isPlayingVideo(): break
            xbmc.sleep(1000)
    except Exception as e:
        control.log('ERROR PLAY:%s' % e)

elif mode[0] == 'ustawienia':
    __addon__.openSettings()
