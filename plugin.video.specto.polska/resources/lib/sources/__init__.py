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


import sys,pkgutil,re,json,urllib,urlparse,datetime,time

try: import xbmc
except: pass

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

from resources.lib.libraries import control
from resources.lib.libraries import alterepisode
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import workers
from resources.lib.resolvers import realdebrid
from resources.lib.resolvers import premiumize
from resources.lib import resolvers


class sources:
    def __init__(self):
        self.sources = [] ; self.sourcesDictionary()


    def play(self, name, title, year, imdb, tmdb, tvdb, tvrage, season, episode, tvshowtitle, alter, date, meta, url):
        try:
            if not control.infoLabel('Container.FolderPath').startswith('plugin://'):
                control.playlist.clear()

            control.resolve(int(sys.argv[1]), True, control.item(path=''))
            control.execute('Dialog.Close(okdialog)')

            if imdb == '0': imdb = '0000000'
            imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

            content = 'movie' if tvshowtitle == None else 'episode'

            self.sources = self.getSources(name, title, year, imdb, tmdb, tvdb, tvrage, season, episode, tvshowtitle, alter, date)
            if self.sources == []: raise Exception()

            self.sources = self.sourcesFilter()

            if control.window.getProperty('PseudoTVRunning') == 'True':
                url = self.sourcesDirect()

            elif url == 'dialog://':
                url = self.sourcesDialog()

            elif url == 'direct://':
                url = self.sourcesDirect()

            elif not control.infoLabel('Container.FolderPath').startswith('plugin://') and control.setting('autoplay_library') == 'false':
                url = self.sourcesDialog()

            elif control.infoLabel('Container.FolderPath').startswith('plugin://') and control.setting('autoplay') == 'false':
                url = self.sourcesDialog()

            else:
                url = self.sourcesDirect()

            if url == None: raise Exception()
            if url == 'close://': return

            if control.setting('playback_info') == 'true':
                control.infoDialog(self.selectedSource, heading=name)

            control.sleep(200)

            from resources.lib.libraries.player import player
            player().run(content, name, url, year, imdb, tvdb, meta)

            return url
        except:
            control.infoDialog(control.lang(30501).encode('utf-8'))


    def addItem(self, name, title, year, imdb, tmdb, tvdb, tvrage, season, episode, tvshowtitle, alter, date, meta):
        try:
            if imdb == '0': imdb = '0000000'
            imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

            content = 'movie' if tvshowtitle == None else 'episode'

            self.sources = self.getSources(name, title, year, imdb, tmdb, tvdb, tvrage, season, episode, tvshowtitle, alter, date)
            if self.sources == []: raise Exception()
            self.progressDialog = control.progressDialog
            self.progressDialog.create(control.addonInfo('name'), '')
            self.progressDialog.update(0, control.lang(30515).encode('utf-8'), str(' '))

            self.sources = self.sourcesFilter()
            infoMenu = control.lang(30502).encode('utf-8') if content == 'movie' else control.lang(30503).encode('utf-8')

            sysmeta = urllib.quote_plus(meta)
            sysaddon = sys.argv[0]

            meta = json.loads(meta)

            poster = meta['poster'] if 'poster' in meta else '0'
            banner = meta['banner'] if 'banner' in meta else '0'
            thumb = meta['thumb'] if 'thumb' in meta else poster
            fanart = meta['fanart'] if 'fanart' in meta else '0'

            if poster == '0': poster = control.addonPoster()
            if banner == '0' and poster == '0': banner = control.addonBanner()
            elif banner == '0': banner = poster
            if thumb == '0' and fanart == '0': thumb = control.addonFanart()
            elif thumb == '0': thumb = fanart
            if control.setting('fanart') == 'true' and not fanart == '0': pass
            else: fanart = control.addonFanart()

            for i in range(len(self.sources)):
                try:
                    if self.progressDialog.iscanceled(): break

                    self.progressDialog.update(int((100 / float(len(self.sources))) * i))
                    url, label, provider = self.sources[i]['url'], self.sources[i]['label'], self.sources[i]['provider']


                    sysname, sysurl, sysimage, sysprovider = urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(poster), urllib.quote_plus(provider)

                    syssource = urllib.quote_plus(json.dumps([self.sources[i]]))
                    if i == 0:
                        query = 'action=playItem&content=%s&name=%s&year=%s&imdb=%s&tvdb=%s&source=%s&meta=%s' % (content, sysname, year, imdb, tvdb, syssource, sysmeta)
                    else:
                        query = 'action=playItem&content=%s&name=%s&year=%s&imdb=%s&tvdb=%s&source=%s' % (content, sysname, year, imdb, tvdb, syssource)

                    cm = []
                    cm.append((control.lang(30504).encode('utf-8'), 'RunPlugin(%s?action=queueItem)' % sysaddon))
                    cm.append((control.lang(30505).encode('utf-8'), 'RunPlugin(%s?action=download&name=%s&image=%s&url=%s&provider=%s)' % (sysaddon, sysname, sysimage, sysurl, sysprovider)))
                    cm.append((infoMenu, 'Action(Info)'))
                    cm.append((control.lang(30506).encode('utf-8'), 'RunPlugin(%s?action=refresh)' % sysaddon))
                    cm.append((control.lang(30507).encode('utf-8'), 'RunPlugin(%s?action=openSettings)' % sysaddon))
                    cm.append((control.lang(30508).encode('utf-8'), 'RunPlugin(%s?action=openPlaylist)' % sysaddon))

                    item = control.item(label=label, iconImage='DefaultVideo.png', thumbnailImage=thumb)
                    try: item.setArt({'poster': poster, 'tvshow.poster': poster, 'season.poster': poster, 'banner': banner, 'tvshow.banner': banner, 'season.banner': banner})
                    except: pass
                    item.setInfo(type='Video', infoLabels = meta)
                    if not fanart == None: item.setProperty('Fanart_Image', fanart)
                    item.setProperty('Video', 'true')
                    #item.setProperty('IsPlayable', 'true')
                    item.addContextMenuItems(cm, replaceItems=True)

                    control.addItem(handle=int(sys.argv[1]), url='%s?%s' % (sysaddon, query), listitem=item, isFolder=False)
                except:
                    pass

            control.directory(int(sys.argv[1]), cacheToDisc=True)
            try: self.progressDialog.close()
            except: pass
        except:
            control.infoDialog(control.lang(30501).encode('utf-8'))
            try: self.progressDialog.close()
            except: pass


    def playItem(self, content, name, year, imdb, tvdb, source):
        try:
            control.resolve(int(sys.argv[1]), True, control.item(path=''))
            control.execute('Dialog.Close(okdialog)')

            next = [] ; prev = [] ; total = []
            meta = None

            for i in range(1,10000):
                try:
                    u = control.infoLabel('ListItem(%s).FolderPath' % str(i))
                    if u in total: raise Exception()
                    total.append(u)
                    u = dict(urlparse.parse_qsl(u.replace('?','')))
                    if 'meta' in u: meta = u['meta']
                    u = json.loads(u['source'])[0]
                    next.append(u)
                except:
                    break
            for i in range(-10000,0)[::-1]:
                try:
                    u = control.infoLabel('ListItem(%s).FolderPath' % str(i))
                    if u in total: raise Exception()
                    total.append(u)
                    u = dict(urlparse.parse_qsl(u.replace('?','')))
                    if 'meta' in u: meta = u['meta']
                    u = json.loads(u['source'])[0]
                    prev.append(u)
                except:
                    break

            items = json.loads(source)

            source, quality = items[0]['source'], items[0]['quality']
            items = [i for i in items+next+prev if i['quality'] == quality and i['source'] == source][:10]
            items += [i for i in next+prev if i['quality'] == quality and not i['source'] == source][:10]

            self.progressDialog = control.progressDialog
            self.progressDialog.create(control.addonInfo('name'), '')
            self.progressDialog.update(0)

            block = None

            for i in range(len(items)):
                try:
                    self.progressDialog.update(int((100 / float(len(items))) * i), str(items[i]['label']), str(' '))

                    if items[i]['source'] == block: raise Exception()

                    w = workers.Thread(self.sourcesResolve, items[i]['url'], items[i]['provider'])
                    w.start()

                    m = ''

                    for x in range(3600):
                        if self.progressDialog.iscanceled(): return self.progressDialog.close()
                        if xbmc.abortRequested == True: return sys.exit()
                        k = control.condVisibility('Window.IsActive(virtualkeyboard)')
                        if k: m += '1'; m = m[-1]
                        if (w.is_alive() == False or x > 30) and not k: break
                        time.sleep(1)

                    for x in range(30):
                        if m == '': break
                        if self.progressDialog.iscanceled(): return self.progressDialog.close()
                        if xbmc.abortRequested == True: return sys.exit()
                        if w.is_alive() == False: break
                        time.sleep(1)


                    if w.is_alive() == True: block = items[i]['source']

                    if self.url == None: raise Exception()

                    try: self.progressDialog.close()
                    except: pass

                    control.sleep(200)

                    if control.setting('playback_info') == 'true':
                        control.infoDialog(items[i]['label'], heading=name)

                    from resources.lib.libraries.player import player
                    player().run(content, name, self.url, year, imdb, tvdb, meta)

                    return self.url
                except:
                    pass

            try: self.progressDialog.close()
            except: pass

            raise Exception()

        except:
            control.infoDialog(control.lang(30501).encode('utf-8'))
            pass


    def getSources(self, name, title, year, imdb, tmdb, tvdb, tvrage, season, episode, tvshowtitle, alter, date):
        sourceDict = []
        for package, name, is_pkg in pkgutil.walk_packages(__path__):
            sourceDict.append((name, is_pkg))
        sourceDict = [i[0] for i in sourceDict if i[1] == False]

        content = 'movie' if tvshowtitle == None else 'episode'


        if content == 'movie':
            sourceDict = [i for i in sourceDict if i.endswith(('_mv', '_mv_tv'))]
            try: sourceDict = [(i, control.setting(re.sub('_mv_tv$|_mv$|_tv$', '', i))) for i in sourceDict]
            except: sourceDict = [(i, 'true') for i in sourceDict]
        else:
            sourceDict = [i for i in sourceDict if i.endswith(('_tv', '_mv_tv'))]
            try: sourceDict = [(i, control.setting(re.sub('_mv_tv$|_mv$|_tv$', '', i) + '_tv')) for i in sourceDict]
            except: sourceDict = [(i, 'true') for i in sourceDict]

        threads = []

        control.makeFile(control.dataPath)
        self.sourceFile = control.sourcescacheFile

        sourceDict = [i[0] for i in sourceDict if i[1] == 'true']

        if content == 'movie':
            title = cleantitle.normalize(title)
            for source in sourceDict: threads.append(workers.Thread(self.getMovieSource, title, year, imdb, re.sub('_mv_tv$|_mv$|_tv$', '', source), __import__(source, globals(), locals(), [], -1).source()))
        else:
            tvshowtitle = cleantitle.normalize(tvshowtitle)
            season, episode = alterepisode.alterepisode().get(imdb, tmdb, tvdb, tvrage, season, episode, alter, title, date)
            for source in sourceDict: threads.append(workers.Thread(self.getEpisodeSource, title, year, imdb, tvdb, season, episode, tvshowtitle, date, re.sub('_mv_tv$|_mv$|_tv$', '', source), __import__(source, globals(), locals(), [], -1).source()))


        try: timeout = int(control.setting('sources_timeout_40'))
        except: timeout = 40

        [i.start() for i in threads]

        control.idle()

        sourceLabel = [re.sub('_mv_tv$|_mv$|_tv$', '', i) for i in sourceDict]
        sourceLabel = [re.sub('v\d+$', '', i).upper() for i in sourceLabel]


        self.progressDialog = control.progressDialog
        self.progressDialog.create(control.addonInfo('name'), '')
        self.progressDialog.update(0)

        string1 = control.lang(30512).encode('utf-8')
        string2 = control.lang(30513).encode('utf-8')
        string3 = control.lang(30514).encode('utf-8')

        for i in range(0, timeout * 2):
            try:
                if xbmc.abortRequested == True: return sys.exit()

                try: info = [sourceLabel[int(re.sub('[^0-9]', '', str(x.getName()))) - 1] for x in threads if x.is_alive() == True]
                except: info = []

                if len(info) > 5: info = len(info)

                self.progressDialog.update(int((100 / float(len(threads))) * len([x for x in threads if x.is_alive() == False])), str('%s: %s %s' % (string1, int(i * 0.5), string2)), str('%s: %s' % (string3, str(info).translate(None, "[]'"))))

                if self.progressDialog.iscanceled(): break

                is_alive = [x.is_alive() for x in threads]
                if all(x == False for x in is_alive): break
                time.sleep(0.5)
            except:
                pass

        self.progressDialog.close()

        return self.sources


    def checkSources(self, name, title, year, imdb, tmdb, tvdb, tvrage, season, episode, tvshowtitle, alter, date):
        sourceDict = []
        for package, name, is_pkg in pkgutil.walk_packages(__path__): sourceDict.append((name, is_pkg))
        sourceDict = [i[0] for i in sourceDict if i[1] == False]

        content = 'movie' if tvshowtitle == None else 'episode'


        if content == 'movie':
            sourceDict = [i for i in sourceDict if i.endswith(('_mv', '_mv_tv'))]
            try: sourceDict = [(i, control.setting(re.sub('_mv_tv$|_mv$|_tv$', '', i))) for i in sourceDict]
            except: sourceDict = [(i, 'true') for i in sourceDict]
        else:
            sourceDict = [i for i in sourceDict if i.endswith(('_tv', '_mv_tv'))]
            try: sourceDict = [(i, control.setting(re.sub('_mv_tv$|_mv$|_tv$', '', i) + '_tv')) for i in sourceDict]
            except: sourceDict = [(i, 'true') for i in sourceDict]

        threads = []

        control.makeFile(control.dataPath)
        self.sourceFile = control.sourcescacheFile

        sourceDict = [i[0] for i in sourceDict if i[1] == 'true']

        if content == 'movie':
            title = cleantitle.normalize(title)
            for source in sourceDict: threads.append(workers.Thread(self.getMovieSource, title, year, imdb, re.sub('_mv_tv$|_mv$|_tv$', '', source), __import__(source, globals(), locals(), [], -1).source()))
        else:
            tvshowtitle = cleantitle.normalize(tvshowtitle)
            season, episode = alterepisode.alterepisode().get(imdb, tmdb, tvdb, tvrage, season, episode, alter, title, date)
            for source in sourceDict:
                control.log("SOURCE S2 %s" % source)
                threads.append(workers.Thread(self.getEpisodeSource, title, year, imdb, tvdb, season, episode, tvshowtitle, date, re.sub('_mv_tv$|_mv$|_tv$', '', source), __import__(source, globals(), locals(), [], -1).source()))


        try: timeout = int(control.setting('sources_timeout_40'))
        except: timeout = 40

        [i.start() for i in threads]

        for i in range(0, timeout * 2):
            try:
                if xbmc.abortRequested == True: return sys.exit()
                if len(self.sources) >= 10: break

                is_alive = [x.is_alive() for x in threads]
                if all(x == False for x in is_alive): break
                time.sleep(0.5)
            except:
                pass

        if len(self.sources) >= 10: return True
        else: return False


    def getMovieSource(self, title, year, imdb, source, call):
        try:
            dbcon = database.connect(self.sourceFile)
            dbcur = dbcon.cursor()
            dbcur.execute("CREATE TABLE IF NOT EXISTS rel_url (""source TEXT, ""imdb_id TEXT, ""season TEXT, ""episode TEXT, ""rel_url TEXT, ""UNIQUE(source, imdb_id, season, episode)"");")
            dbcur.execute("CREATE TABLE IF NOT EXISTS rel_src (""source TEXT, ""imdb_id TEXT, ""season TEXT, ""episode TEXT, ""hosts TEXT, ""added TEXT, ""UNIQUE(source, imdb_id, season, episode)"");")
        except:
            pass

        try:
            sources = []
            dbcur.execute("SELECT * FROM rel_src WHERE source = '%s' AND imdb_id = '%s' AND season = '%s' AND episode = '%s'" % (source, imdb, '', ''))
            match = dbcur.fetchone()
            t1 = int(re.sub('[^0-9]', '', str(match[5])))
            t2 = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
            update = abs(t2 - t1) > 60
            if update == False:
                sources = json.loads(match[4])
                return self.sources.extend(sources)
        except:
            pass

        try:
            url = None
            dbcur.execute("SELECT * FROM rel_url WHERE source = '%s' AND imdb_id = '%s' AND season = '%s' AND episode = '%s'" % (source, imdb, '', ''))
            url = dbcur.fetchone()
            url = url[4]
        except:
            pass

        try:
            if url == None: url = call.get_movie(imdb, title, year)
            if url == None: raise Exception()
            dbcur.execute("DELETE FROM rel_url WHERE source = '%s' AND imdb_id = '%s' AND season = '%s' AND episode = '%s'" % (source, imdb, '', ''))
            dbcur.execute("INSERT INTO rel_url Values (?, ?, ?, ?, ?)", (source, imdb, '', '', url))
            dbcon.commit()
        except:
            pass

        try:
            sources = []
            sources = call.get_sources(url, self.hosthdfullDict, self.hostsdfullDict, self.hostlocDict)
            if sources == None: sources = []
            self.sources.extend(sources)
            dbcur.execute("DELETE FROM rel_src WHERE source = '%s' AND imdb_id = '%s' AND season = '%s' AND episode = '%s'" % (source, imdb, '', ''))
            dbcur.execute("INSERT INTO rel_src Values (?, ?, ?, ?, ?, ?)", (source, imdb, '', '', json.dumps(sources), datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
            dbcon.commit()
        except:
            pass


    def getEpisodeSource(self, title, year, imdb, tvdb, season, episode, tvshowtitle, date, source, call):
        #control.log('# UPDATE    2121 %s %s' % (source,call))
        try:
            dbcon = database.connect(self.sourceFile)
            dbcur = dbcon.cursor()
            dbcur.execute("CREATE TABLE IF NOT EXISTS rel_url (""source TEXT, ""imdb_id TEXT, ""season TEXT, ""episode TEXT, ""rel_url TEXT, ""UNIQUE(source, imdb_id, season, episode)"");")
            dbcur.execute("CREATE TABLE IF NOT EXISTS rel_src (""source TEXT, ""imdb_id TEXT, ""season TEXT, ""episode TEXT, ""hosts TEXT, ""added TEXT, ""UNIQUE(source, imdb_id, season, episode)"");")
        except:
            pass

        try:
            sources = []
            dbcur.execute("SELECT * FROM rel_src WHERE source = '%s' AND imdb_id = '%s' AND season = '%s' AND episode = '%s'" % (source, imdb, season, episode))
            match = dbcur.fetchone()
            t1 = int(re.sub('[^0-9]', '', str(match[5])))
            t2 = int(datetime.datetime.now().strftime("%Y%m%d%H%M"))
            update = abs(t2 - t1) > 60
            #control.log('# UPDATE 1002 %s ' % update)

            if update == False:
                sources = json.loads(match[4])
                #control.log('# UPDATE2121 %s' % match)
                return self.sources.extend(sources)
        except:
            pass

        try:
            url = None
            dbcur.execute("SELECT * FROM rel_url WHERE source = '%s' AND imdb_id = '%s' AND season = '%s' AND episode = '%s'" % (source, imdb, '', ''))
            url = dbcur.fetchone()
            url = url[4]
            #control.log('### SOURCES URL %s' % url)
        except:
            pass

        try:
            if url == None: url = call.get_show(imdb, tvdb, tvshowtitle, year)
            control.log('### SOURCES AFTER  URL %s | Call:%s' % (url,call))

            if url == None: raise Exception()
            dbcur.execute("DELETE FROM rel_url WHERE source = '%s' AND imdb_id = '%s' AND season = '%s' AND episode = '%s'" % (source, imdb, '', ''))
            dbcur.execute("INSERT INTO rel_url Values (?, ?, ?, ?, ?)", (source, imdb, '', '', url))
            dbcon.commit()
        except:
            pass

        try:
            ep_url = None
            dbcur.execute("SELECT * FROM rel_url WHERE source = '%s' AND imdb_id = '%s' AND season = '%s' AND episode = '%s'" % (source, imdb, season, episode))
            ep_url = dbcur.fetchone()
            ep_url = ep_url[4]
        except:
            pass

        try:
            if url == None: raise Exception()
            if ep_url == None: ep_url = call.get_episode(url, imdb, tvdb, title, date, season, episode)
            if ep_url == None: raise Exception()
            dbcur.execute("DELETE FROM rel_url WHERE source = '%s' AND imdb_id = '%s' AND season = '%s' AND episode = '%s'" % (source, imdb, season, episode))
            dbcur.execute("INSERT INTO rel_url Values (?, ?, ?, ?, ?)", (source, imdb, season, episode, ep_url))
            dbcon.commit()
        except:
            pass

        try:
            sources = []
            sources = call.get_sources(ep_url, self.hosthdfullDict, self.hostsdfullDict, self.hostlocDict)
            if sources == None: sources = []
            self.sources.extend(sources)
            dbcur.execute("DELETE FROM rel_src WHERE source = '%s' AND imdb_id = '%s' AND season = '%s' AND episode = '%s'" % (source, imdb, season, episode))
            dbcur.execute("INSERT INTO rel_src Values (?, ?, ?, ?, ?, ?)", (source, imdb, season, episode, json.dumps(sources), datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
            dbcon.commit()
        except:
            pass


    def alterSources(self, url, meta):
        try:
            setting = control.setting('autoplay')
            if setting == 'false': url += '&url=direct://'
            else: url += '&url=dialog://'

            control.execute('RunPlugin(%s)' % url)
        except:
            pass


    def clearSources(self):
        try:
            control.idle()

            yes = control.yesnoDialog(control.lang(30510).encode('utf-8'), '', '')
            if not yes: return

            control.makeFile(control.dataPath)
            dbcon = database.connect(control.sourcescacheFile)
            dbcur = dbcon.cursor()
            dbcur.execute("DROP TABLE IF EXISTS rel_src")
            dbcur.execute("VACUUM")
            dbcon.commit()

            control.infoDialog(control.lang(30511).encode('utf-8'))
        except:
            pass


    def sourcesFilter(self):
        self.sourcesReset()
        try: customhdDict = [control.setting('hosthd50001'), control.setting('hosthd50002'), control.setting('hosthd50003'), control.setting('hosthd50004'), control.setting('hosthd50005'), control.setting('hosthd50006'), control.setting('hosthd50007'), control.setting('hosthd50008'), control.setting('hosthd50009'), control.setting('hosthd50010'), control.setting('hosthd50011'), control.setting('hosthd50012'), control.setting('hosthd50013'), control.setting('hosthd50014'), control.setting('hosthd50015'), control.setting('hosthd50016'), control.setting('hosthd50017'), control.setting('hosthd50018'), control.setting('hosthd50019'), control.setting('hosthd50020')]
        except: customhdDict = []
        try: customsdDict = [control.setting('host50001'), control.setting('host50002'), control.setting('host50003'), control.setting('host50004'), control.setting('host50005'), control.setting('host50006'), control.setting('host50007'), control.setting('host50008'), control.setting('host50009'), control.setting('host50010'), control.setting('host50011'), control.setting('host50012'), control.setting('host50013'), control.setting('host50014'), control.setting('host50015'), control.setting('host50016'), control.setting('host50017'), control.setting('host50018'), control.setting('host50019'), control.setting('host50020')]
        except: customsdDict = []

        hd_rank = []
        hd_rank += [i for i in self.rdDict if i in self.hostprDict + self.hosthdDict]
        hd_rank += [i for i in self.pzDict if i in self.hostprDict + self.hosthdDict]
        hd_rank += customhdDict
        hd_rank += [i['source'] for i in self.sources if i['quality'] in ['1080p', 'HD'] and not i['source'] in customhdDict + self.hostprDict + self.hosthdDict]
        hd_rank += self.hosthdDict
        hd_rank = [i.lower() for i in hd_rank]
        hd_rank = [x for y,x in enumerate(hd_rank) if x not in hd_rank[:y]]

        sd_rank = []
        sd_rank += [i for i in self.rdDict if i in self.hostprDict + self.hosthqDict]
        sd_rank += [i for i in self.pzDict if i in self.hostprDict + self.hosthqDict]
        sd_rank += customsdDict
        sd_rank += [i['source'] for i in self.sources if i['quality'] == 'SD' and not i['source'] in customsdDict + self.hostprDict + self.hosthqDict + self.hostmqDict + self.hostlqDict]
        sd_rank += self.hosthqDict + self.hostmqDict + self.hostlqDict
        sd_rank = [i.lower() for i in sd_rank]
        sd_rank = [x for y,x in enumerate(sd_rank) if x not in sd_rank[:y]]

        for i in range(len(self.sources)): self.sources[i]['source'] = self.sources[i]['source'].lower()
        self.sources = sorted(self.sources, key=lambda k: k['source'])

        filter = []
        for host in hd_rank: filter += [i for i in self.sources if i['quality'] == '1080p' and i['source'] == host]
        for host in hd_rank: filter += [i for i in self.sources if i['quality'] == 'HD' and i['source'] == host]
        for host in sd_rank: filter += [i for i in self.sources if i['quality'] == 'SD' and i['source'] == host]
        if len(filter) < 10: filter += [i for i in self.sources if i['quality'] == 'SCR']
        if len(filter) < 10: filter += [i for i in self.sources if i['quality'] == 'CAM']
        self.sources = filter

        try: playback_quality = control.setting('playback_quality')
        except: playback_quality = '0'

        if playback_quality == '1':
            self.sources = [i for i in self.sources if not i['quality'] == '1080p']
        elif playback_quality == '2':
            self.sources = [i for i in self.sources if not i['quality'] in ['1080p', 'HD']]
        elif playback_quality == '3':
            self.sources = [i for i in self.sources if not i['quality'] in ['1080p', 'HD'] and i['source'] in self.hostmqDict + self.hostlqDict]
        elif playback_quality == '4':
            self.sources = [i for i in self.sources if not i['quality'] in ['1080p', 'HD'] and i['source'] in self.hostlqDict]

        try: playback_captcha = control.setting('playback_captcha_hosts')
        except: playback_captcha = 'false'

        try: playback_1080p = control.setting('playback_1080p_hosts')
        except: playback_1080p = 'true'

        try: playback_720p = control.setting('playback_720p_hosts')
        except: playback_720p = 'true'

        if playback_captcha == 'false':
            self.sources = [i for i in self.sources if not i['source'] in self.hostcapDict]

        if playback_1080p == 'false':
            self.sources = [i for i in self.sources if not (i['quality'] == '1080p' and i['source'] in self.hosthdDict and not i['source'] in self.rdDict + self.pzDict)]

        if playback_720p == 'false':
            self.sources = [i for i in self.sources if not (i['quality'] == 'HD' and i['source'] in self.hosthdDict and not i['source'] in self.rdDict + self.pzDict)]

        for i in range(len(self.sources)):
            #control.log("------------------------------ %s  | %s " % (self.sources[i]['source'], self.sources[i]))
            s = self.sources[i]['source'].lower()
            p = self.sources[i]['provider']
            p = re.sub('v\d*$', '', p)

            q = self.sources[i]['quality']
            if q == 'SD' and s in self.hostmqDict: q = 'MQ'
            elif q == 'SD' and s in self.hostlqDict: q = 'LQ'
            elif q == 'SD': q = 'HQ'

            try: d = self.sources[i]['info']
            except: d = ''
            if not d == '': d = ' | [I]%s [/I]' % d

            if s in self.rdDict: label = '%02d | [B]realdebrid[/B] | ' % int(i+1)
            elif s in self.pzDict: label = '%02d | [B]premiumize[/B] | ' % int(i+1)
            else: label = '%02d | [B]%s[/B] | ' % (int(i+1), p)

            if q in ['1080p', 'HD']: label += '%s%s | [B][I]%s [/I][/B]' % (s, d, q)
            else: label += '%s%s | [I]%s [/I]' % (s, d, q)

            self.sources[i]['label'] = label.upper()

        return self.sources


    def sourcesReset(self):
        try:
            if control.setting('hosthd1') == '': return

            settingsFile = control.settingsFile
            file = control.openFile(settingsFile) ; read = file.read().splitlines() ; file.close()

            write = unicode( '<settings>' + '\n', 'UTF-8' )
            for line in read:
                if len(re.findall('<settings>', line)) > 0: continue
                elif len(re.findall('</settings>', line)) > 0: continue
                elif len(re.findall('id="(host|hosthd)500\d*"', line)) > 0: pass
                elif len(re.findall('id="(host|hosthd)\d*"', line)) > 0: continue
                write += unicode(line.rstrip() + '\n', 'UTF-8')
            write += unicode('</settings>' + '\n', 'UTF-8')

            file = control.openFile(settingsFile, 'w') ; file.write(str(write)) ; file.close()
        except:
            return


    def sourcesResolve(self, url, provider):
        try:
            provider = provider.lower()

            if not provider.endswith(('_mv', '_tv', '_mv_tv')):
                sourceDict = []
                for package, name, is_pkg in pkgutil.walk_packages(__path__): sourceDict.append((name, is_pkg))
                provider = [i[0] for i in sourceDict if i[1] == False and i[0].startswith(provider + '_')][0]

            source = __import__(provider, globals(), locals(), [], -1).source()
            url = source.resolve(url)
            #control.log("[suurces]   my url 1 ************ %s " % url)
            #url = resolvers.request(url)
            #control.log("[sources]   my url 2 ************ %s " % url)

            try: headers = dict(urlparse.parse_qsl(url.rsplit('|', 1)[1]))
            except: headers = dict('')

            result = client.request(url.split('|')[0], headers=headers, output='chunk', timeout='20')
            if result == None: raise Exception()
            #control.log("!!!!!!!!!!!!!!!!!!!  %s prov: %s" % (url,provider))
            self.url = url
            return url
        except:
            return


    def sourcesDialog(self):
        try:
            sources = [{'label': '00 | [B]%s[/B]' % control.lang(30509).encode('utf-8').upper()}] + self.sources

            labels = [i['label'] for i in sources]

            select = control.selectDialog(labels)
            if select == 0: return self.sourcesDirect()
            if select == -1: return 'close://'

            items = [self.sources[select-1]]

            next = [y for x,y in enumerate(self.sources) if x >= select]
            prev = [y for x,y in enumerate(self.sources) if x < select][::-1]

            source, quality = items[0]['source'], items[0]['quality']
            items = [i for i in items+next+prev if i['quality'] == quality and i['source'] == source][:10]
            items += [i for i in next+prev if i['quality'] == quality and not i['source'] == source][:10]

            self.progressDialog = control.progressDialog
            self.progressDialog.create(control.addonInfo('name'), '')
            self.progressDialog.update(0)

            block = None

            for i in range(len(items)):
                try:
                    if self.progressDialog.iscanceled(): break

                    self.progressDialog.update(int((100 / float(len(items))) * i), str(items[i]['label']), str(' '))

                    if items[i]['source'] == block: raise Exception()

                    w = workers.Thread(self.sourcesResolve, items[i]['url'], items[i]['provider'])
                    w.start()

                    m = ''

                    for x in range(3600):
                        if self.progressDialog.iscanceled(): return self.progressDialog.close()
                        if xbmc.abortRequested == True: return sys.exit()
                        k = control.condVisibility('Window.IsActive(virtualkeyboard)')
                        if k: m += '1'; m = m[-1]
                        if (w.is_alive() == False or x > 30) and not k: break
                        time.sleep(1)

                    for x in range(30):
                        if m == '': break
                        if self.progressDialog.iscanceled(): return self.progressDialog.close()
                        if xbmc.abortRequested == True: return sys.exit()
                        if w.is_alive() == False: break
                        time.sleep(1)


                    if w.is_alive() == True: block = items[i]['source']

                    if self.url == None: raise Exception()

                    self.selectedSource = items[i]['label']
                    self.progressDialog.close()

                    return self.url
                except:
                    pass

            try: self.progressDialog.close()
            except: pass

        except:
            try: self.progressDialog.close()
            except: pass


    def sourcesDirect(self):
        self.sources = [i for i in self.sources if not i['source'] in self.hostcapDict]

        self.sources = [i for i in self.sources if not (i['quality'] in ['1080p', 'HD'] and i['source'] in self.hosthdDict and not i['source'] in self.rdDict + self.pzDict)]

        self.sources = [i for i in self.sources if not i['source'] in ['easynews', 'furk', 'vk']]

        if control.setting("playback_auto_sd") == 'true':
            self.sources = [i for i in self.sources if not i['quality'] in ['1080p', 'HD']]

        u = None

        self.progressDialog = control.progressDialog
        self.progressDialog.create(control.addonInfo('name'), '')
        self.progressDialog.update(0)

        for i in range(len(self.sources)):
            try:
                if self.progressDialog.iscanceled(): break

                self.progressDialog.update(int((100 / float(len(self.sources))) * i), str(self.sources[i]['label']), str(' '))

                if xbmc.abortRequested == True: return sys.exit()

                url = self.sourcesResolve(self.sources[i]['url'], self.sources[i]['provider'])
                if url == None: raise Exception()
                if u == None: u = url

                self.selectedSource = self.sources[i]['label']
                self.progressDialog.close()

                return url
            except:
                pass

        try: self.progressDialog.close()
        except: pass

        return u


    def sourcesDictionary(self):
        hosts = resolvers.info()
        hosts = [i for i in hosts if 'host' in i]

        self.rdDict = realdebrid.getHosts()
        self.pzDict = premiumize.getHosts()

        self.hostlocDict = [i['netloc'] for i in hosts if i['quality'] == 'High' and i['captcha'] == False]
        try: self.hostlocDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hostlocDict)]
        except: pass
        self.hostlocDict = [x for y,x in enumerate(self.hostlocDict) if x not in self.hostlocDict[:y]]

        self.hostdirhdDict = [i['netloc'] for i in resolvers.info() if 'quality' in i and i['quality'] == 'High' and 'captcha' in i and i['captcha'] == False and 'a/c' in i and i['a/c'] == False]
        try: self.hostdirhdDict = [i.lower().rsplit('.', 1)[0] for i in reduce(lambda x, y: x+y, self.hostdirhdDict)]
        except: pass
        self.hostdirhdDict = [x for y,x in enumerate(self.hostdirhdDict) if x not in self.hostdirhdDict[:y]]

        self.hostprDict = [i['host'] for i in hosts if i['a/c'] == True]
        try: self.hostprDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hostprDict)]
        except: pass
        self.hostprDict = [x for y,x in enumerate(self.hostprDict) if x not in self.hostprDict[:y]]

        self.hostcapDict = [i['host'] for i in hosts if i['captcha'] == True]
        try: self.hostcapDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hostcapDict)]
        except: pass
        self.hostcapDict = [i for i in self.hostcapDict if not i in self.rdDict + self.pzDict]

        self.hosthdDict = [i['host'] for i in hosts if i['quality'] == 'High' and i['a/c'] == False and i['captcha'] == False]
        self.hosthdDict += [i['host'] for i in hosts if i['quality'] == 'High' and i['a/c'] == False and i['captcha'] == True]
        try: self.hosthdDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hosthdDict)]
        except: pass

        self.hosthqDict = [i['host'] for i in hosts if i['quality'] == 'High' and i['a/c'] == False and i['captcha'] == False]
        try: self.hosthqDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hosthqDict)]
        except: pass

        self.hostmqDict = [i['host'] for i in hosts if i['quality'] == 'Medium' and i['a/c'] == False and i['captcha'] == False]
        try: self.hostmqDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hostmqDict)]
        except: pass

        self.hostlqDict = [i['host'] for i in hosts if i['quality'] == 'Low' and i['a/c'] == False and i['captcha'] == False]
        try: self.hostlqDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hostlqDict)]
        except: pass

        self.hostsdfullDict = self.hostprDict + self.hosthqDict + self.hostmqDict + self.hostlqDict

        self.hosthdfullDict = self.hostprDict + self.hosthdDict


