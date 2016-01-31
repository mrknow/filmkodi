# -*- coding: utf-8 -*-

'''
    Phoenix Add-on
    Copyright (C) 2015 Blazetamer
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


import re,os,sys,urllib,json,datetime,subprocess

from jars import FuckNeulionClient
from resources.lib.libraries import control
from resources.lib.libraries import client
import xbmc


addonPath = control.addonPath
addonFanart = control.addonInfo('fanart')
addonIcon = os.path.join(addonPath, 'resources/media/nhlcom/hockey.jpg')
jarFile = os.path.join(addonPath, 'jars/FuckNeulionV2.jar')


def nhlDirectory():
    dt = procTimezone(5)
    datex = int(dt.strftime('%Y%m%d'))

    url = 'http://live.nhl.com/GameData/SeasonSchedule-20152016.json'
    result = client.request(url)

    items = json.loads(result)
    items = sorted(items, key=lambda k: k['est'])

    addDirectoryItem(control.lang(30751).encode('utf-8'), 'Scoreboard', 'nhlScoreboard', '0', '0')
    addDirectoryItem(control.lang(30752).encode('utf-8'), 'Archived', 'nhlArchives', '0', '0')
    addDirectoryItem(control.lang(30753).encode('utf-8'), '0', '0', '0', '0')
    addDirectoryItem(control.lang(30754).encode('utf-8'), '0', '0', '0', '0')

    for item in items:
        try:
            est = datetime.datetime.strptime(item['est'], '%Y%m%d %H:%M:%S')
            date = int(est.strftime('%Y%m%d'))
            if not date == datex: raise Exception()

            est = procTimezone(5, est)
            name = '%s at %s  [COLOR gold](%s)[/COLOR]  [COLOR red](%s)[/COLOR]' % (item['a'], item['h'], est.strftime('%H:%M'), est.strftime('%Y-%m-%d'))
            url = str(item['id'])

            addDirectoryItem(name, url, 'nhlStreams', '0', '0')
        except:
            pass

    endDirectory()


def nhlScoreboard():
    dt = procTimezone(5)
    datex = int(dt.strftime('%Y%m%d'))

    url = 'http://live.nhl.com/GameData/Scoreboard.json'

    result = client.request(url)

    items = json.loads(result)
    items = items['games']

    for item in items:
        try:
            est = item['longStartTime']
            est = re.compile('(\d{2})/(\d{2})/(\d{4}) (.+)').findall(est)[0]
            est = '%s%s%s %s' % (est[2], est[0], est[1], est[3])

            item.update({'est': est})
        except:
            pass

    items = sorted(items, key=lambda k: k['est'])[::-1]

    for item in items:
        try:
            try: est = datetime.datetime.strptime(item['est'], '%Y%m%d %H:%M:%S')
            except: est = re.findall('(\d{4})(\d{2})(\d{2}) (\d*:\d*)', item['est'])[0]

            try: date = int(est.strftime('%Y%m%d'))
            except: date = int(est[0]+est[1]+est[2])

            if not date <= datex: raise Exception()

            try: name = '%s at %s  [COLOR gold](%s)[/COLOR]  [COLOR red](%s)[/COLOR]' % (item['awayTeamName'], item['homeTeamName'], (procTimezone(5, est)).strftime('%H:%M'), (procTimezone(5, est)).strftime('%Y-%m-%d'))
            except: name = '%s at %s  [COLOR gold](%s)[/COLOR]  [COLOR red](%s-%s-%s)[/COLOR]' % (item['awayTeamName'], item['homeTeamName'], est[3], est[0], est[1], est[2])

            url = str(item['id'])

            addDirectoryItem(name, url, 'nhlStreams', '0', '0')
        except:
            pass

    endDirectory()


def nhlArchives():
    dt = procTimezone(5)
    datex = int(dt.strftime('%Y%m%d'))

    url = 'http://live.nhl.com/GameData/SeasonSchedule-20152016.json'
    result = client.request(url)

    items = json.loads(result)
    items = sorted(items, key=lambda k: k['est'])[::-1]

    for item in items:
        try:
            try: est = datetime.datetime.strptime(item['est'], '%Y%m%d %H:%M:%S')
            except: est = re.findall('(\d{4})(\d{2})(\d{2}) (\d*:\d*)', item['est'])[0]

            try: date = int(est.strftime('%Y%m%d'))
            except: date = int(est[0]+est[1]+est[2])

            if not date <= datex: raise Exception()

            try: name = '%s at %s  [COLOR gold](%s)[/COLOR]  [COLOR red](%s)[/COLOR]' % (item['a'], item['h'], (procTimezone(5, est)).strftime('%H:%M'), (procTimezone(5, est)).strftime('%Y-%m-%d'))
            except: name = '%s at %s  [COLOR gold](%s)[/COLOR]  [COLOR red](%s-%s-%s)[/COLOR]' % (item['a'], item['h'], est[3], est[0], est[1], est[2])

            url = str(item['id'])

            addDirectoryItem(name, url, 'nhlStreams', '0', '0')
        except:
            pass

    endDirectory()


def nhlStreams(name, url):
    try:
        name = re.sub('\s\[COLOR.+?\].+?\[/COLOR\]', '', name).strip()
        n1 = name + ' [COLOR gold]%s[/COLOR]' ; n2 = name + ' [COLOR red]%s[/COLOR]'

        selectHomeGame = 'x0xe%sx0xehome' % str(url)
        selectAwayGame = 'x0xe%sx0xeaway' % str(url)

        url = re.compile('(\d{4})(\d{2})(\d{4})').findall(url)[0]
        url = 'http://smb.cdnak.neulion.com/fs/nhl/mobile/feed_new/data/streams/%s/ipad/%s_%s.json' % (url[0], url[1], url[2])

        result = client.request(url)
        result = json.loads(result)

        items = result['gameStreams']['ipad']
        h = items['home'] ; a = items['away']
    except:
        pass

    l1 = []; l2 = []

    try: finish = result['finish']
    except: finish = 'true'

    try: image = re.compile('"image" *: *"(.+?)"').findall(json.dumps(h))[-1]
    except: image = '0'

    try: l1.append({'name': n1 % 'Home LIVE', 'url': h['live']['bitrate0'] + selectHomeGame, 'image': image})
    except: pass

    try: l2.append({'name': n2 % 'Home Whole', 'url': h['vod-whole']['bitrate0'], 'image': image})
    except: pass

    try: l2.append({'name': n2 % 'Home Continuous', 'url': h['vod-continuous']['bitrate0'], 'image': image})
    except: pass

    try: l2.append({'name': n2 % 'Home Condensed', 'url': h['vod-condensed']['bitrate0'], 'image': image})
    except: pass

    try: image = re.compile('"image" *: *"(.+?)"').findall(json.dumps(a))[-1]
    except: image = '0'

    try: l1.append({'name': n1 % 'Away LIVE', 'url': a['live']['bitrate0'] + selectAwayGame, 'image': image})
    except: pass

    try: l2.append({'name': n2 % 'Away Whole', 'url': a['vod-whole']['bitrate0'], 'image': image})
    except: pass

    try: l2.append({'name': n2 % 'Away Continuous', 'url': a['vod-continuous']['bitrate0'], 'image': image})
    except: pass

    try: l2.append({'name': n2 % 'Away Condensed', 'url': a['vod-condensed']['bitrate0'], 'image': image})
    except: pass

    if finish == 'false':
        for i in l1: addDirectoryItem(i['name'], i['url'], 'nhlResolve', i['image'], '0', isFolder=False)
    else:
        for i in l2: addDirectoryItem(i['name'], i['url'], 'nhlResolve', i['image'], '0', isFolder=False)

    if l1 == [] and l2 == []:
        return control.infoDialog(control.lang(30755).encode('utf-8'), name, addonIcon)

    endDirectory()


def nhlResolve(url):
    try:
        try: url, selectGame, side = re.compile('(.+?)x0xe(.+?)x0xe(.+?)$').findall(url)[0]
        except: selectGame, side = None, None

        header = '|' + urllib.urlencode({'User-Agent': 'PS4 libhttp/1.76 (PlayStation 4)'})
        base = re.compile('(.*/).+[.]m3u8').findall(url)

        if not url.endswith('m3u8'):
            return player().run(url + header, selectGame ,side)

        result = client.request(url)

        result = re.compile('BANDWIDTH=(\d*)\n(.+?[.]m3u8)').findall(result)
        result = [(int(int(i[0]) / 1000), i[1]) for i in result]
        result = sorted(result, reverse=True)
        result = [(str(i[0]), base[0] + i[1]) for i in result]

        q = [i[0] for i in result]
        u = [i[1] for i in result]
        select = control.selectDialog(q, control.lang(30756).encode('utf-8'))
        if select == -1: return
        url = u[select]

        player().run(url + header, selectGame ,side)
    except:
        return


class player(xbmc.Player):
    def __init__ (self):
        xbmc.Player.__init__(self)


    def run(self, url, selectGame ,side):

        if selectGame == None or side == None:
            return control.resolve(int(sys.argv[1]), True, control.item(path=url))

        command = ['java','-jar',jarFile,selectGame,side]

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        self.process = subprocess.Popen(command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            startupinfo=startupinfo)

        if os.name == 'posix':
            success = False
            success, output = FuckNeulionClient.request_proxy_hack(selectGame,side)

        control.sleep(1000)

        control.resolve(int(sys.argv[1]), True, control.item(path=url))

        for i in range(0, 240):
            if self.isPlayingVideo(): break
            control.sleep(1000)
        while self.isPlayingVideo():
            control.sleep(1000)
        control.sleep(5000)


    def onPlayBackStarted(self):
        return


    def onPlayBackEnded(self):
        try: self.process.kill()
        except: pass


    def onPlayBackStopped(self):
        try: self.process.kill()
        except: pass


def addDirectoryItem(name, url, action, image, fanart, isFolder=True):
    if image == '0': image = addonIcon
    if fanart == '0': fanart = addonFanart

    u = '%s?name=%s&url=%s&image=%s&fanart=%s&action=%s' % (sys.argv[0], urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(image), urllib.quote_plus(fanart), str(action))

    item = control.item(name, iconImage=image, thumbnailImage=image)
    item.setInfo(type='Video', infoLabels = {'title': name})
    item.addContextMenuItems([], replaceItems=False)
    item.setProperty('Fanart_Image', fanart)
    if not isFolder == True: item.setProperty('IsPlayable', 'true')
    control.addItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=isFolder)


def endDirectory():
    control.directory(int(sys.argv[1]), cacheToDisc=True)


def procTimezone(h, dt=0):
    dt1 = datetime.datetime.utcnow() - datetime.timedelta(hours = h)
    d = datetime.datetime(dt1.year, 4, 1)
    dston = d - datetime.timedelta(days=d.weekday() + 1)
    d = datetime.datetime(dt1.year, 11, 1)
    dstoff = d - datetime.timedelta(days=d.weekday() + 1)
    if dston <=  dt1 < dstoff: dt1 = dt1 + datetime.timedelta(hours = 1)
    dt1 = datetime.datetime(dt1.year, dt1.month, dt1.day, dt1.hour, dt1.minute)

    if dt == 0: return dt1

    dt2 = datetime.datetime.now()
    dt2 = datetime.datetime(dt2.year, dt2.month, dt2.day, dt2.hour, dt1.minute)

    dt3 = datetime.datetime.utcnow()
    dt3 = datetime.datetime(dt3.year, dt3.month, dt3.day, dt3.hour, dt1.minute)

    if dt2 >= dt1 :
        dtd = (dt2 - dt1).seconds/60/60
        dt = dt + datetime.timedelta(hours = int(dtd))
    else:
        dtd = (dt1 - dt2).seconds/60/60
        dt = dt - datetime.timedelta(hours = int(dtd))

    return dt


