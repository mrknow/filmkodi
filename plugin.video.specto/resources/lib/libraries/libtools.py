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


try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

import os,sys,re,json,urllib,urlparse,datetime,xbmc

from resources.lib.libraries import control


class libmovies:
    def __init__(self):
        self.library_folder = os.path.join(control.transPath(control.setting('movie_library')),'')

        self.check_setting = control.setting('check_movie_link') or 'false'
        self.library_setting = control.setting('update_library') or 'true'
        self.dupe_setting = control.setting('check_library') or 'true'

        self.infoDialog = False


    def add(self, name, title, year, imdb, tmdb, range=False):
        if not control.condVisibility('Window.IsVisible(infodialog)') and not control.condVisibility('Player.HasVideo'):
            control.infoDialog(control.lang(30421).encode('utf-8'), time=10000000)
            self.infoDialog = True

        try:
            if not self.dupe_setting == 'true': raise Exception()

            id = [imdb, tmdb] if not tmdb == '0' else [imdb]
            lib = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"filter":{"or": [{"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}, {"field": "year", "operator": "is", "value": "%s"}]}, "properties" : ["imdbnumber", "originaltitle", "year"]}, "id": 1}' % (year, str(int(year)+1), str(int(year)-1)))
            lib = unicode(lib, 'utf-8', errors='ignore')
            lib = json.loads(lib)['result']['movies']
            lib = [i for i in lib if str(i['imdbnumber']) in id or (i['originaltitle'].encode('utf-8') == title and str(i['year']) == year)][0]
        except:
            lib = []

        try:
            if not lib == []: raise Exception()

            if self.check_setting == 'true':
                from resources.lib.sources import sources
                src = sources().checkSources(name, title, year, imdb, tmdb, '0', '0', None, None, None, '0', None)
                if src == False: raise Exception()

            self.strmFile({'name': name, 'title': title, 'year': year, 'imdb': imdb, 'tmdb': tmdb})
        except:
            pass

        if range == True: return

        if self.infoDialog == True:
            control.infoDialog(control.lang(30423).encode('utf-8'), time=1)

        if self.library_setting == 'true' and not control.condVisibility('Library.IsScanningVideo'):
            control.execute('UpdateLibrary(video)')


    def range(self, url):
        control.idle()

        yes = control.yesnoDialog(control.lang(30425).encode('utf-8'), '', '')
        if not yes: return

        if not control.condVisibility('Window.IsVisible(infodialog)') and not control.condVisibility('Player.HasVideo'):
            control.infoDialog(control.lang(30421).encode('utf-8'), time=10000000)
            self.infoDialog = True

        from resources.lib.indexers import movies
        items = movies.movies().get(url, idx=False)
        if items == None: items = []

        for i in items:
            try:
                if xbmc.abortRequested == True: return sys.exit()
                self.add(i['name'], i['title'], i['year'], i['imdb'], i['tmdb'], range=True)
            except:
                pass

        if self.infoDialog == True:
            control.infoDialog(control.lang(30423).encode('utf-8'), time=1)

        if self.library_setting == 'true' and not control.condVisibility('Library.IsScanningVideo'):
            control.execute('UpdateLibrary(video)')


    def strmFile(self, i):
        try:
            name, title, year, imdb, tmdb = i['name'], i['title'], i['year'], i['imdb'], i['tmdb']

            sysname, systitle = urllib.quote_plus(name), urllib.quote_plus(title)

            transname = name.translate(None, '\/:*?"<>|').strip('.')

            content = '%s?action=play&name=%s&title=%s&year=%s&imdb=%s&tmdb=%s' % (sys.argv[0], sysname, systitle, year, imdb, tmdb)

            control.makeFile(self.library_folder)
            folder = os.path.join(self.library_folder, transname)
            control.makeFile(folder)

            try:
				if not 'ftp://' in folder: raise Exception()
				from ftplib import FTP
				ftparg = re.compile('ftp://(.+?):(.+?)@(.+?):?(\d+)?/(.+/?)').findall(folder)
				ftp = FTP(ftparg[0][2],ftparg[0][0],ftparg[0][1])
				try: ftp.cwd(ftparg[0][4])
				except: ftp.mkd(ftparg[0][4])
				ftp.quit()
            except:
				pass

            stream = os.path.join(folder, transname + '.strm')
            file = control.openFile(stream, 'w')
            file.write(str(content))
            file.close()
        except:
            pass


class libtvshows:
    def __init__(self):
        self.library_folder = os.path.join(control.transPath(control.setting('tv_library')),'')

        self.version = control.version()

        self.check_setting = control.setting('check_episode_link') or 'false'
        self.library_setting = control.setting('update_library') or 'true'
        self.dupe_setting = control.setting('check_library') or 'true'

        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        self.date = (self.datetime - datetime.timedelta(hours = 24)).strftime('%Y%m%d')

        self.infoDialog = False
        self.block = False


    def add(self, tvshowtitle, year, imdb, tmdb, tvdb, tvrage, range=False):
        if not control.condVisibility('Window.IsVisible(infodialog)') and not control.condVisibility('Player.HasVideo'):
            control.infoDialog(control.lang(30421).encode('utf-8'), time=10000000)
            self.infoDialog = True

        from resources.lib.indexers import episodes
        items = episodes.episodes().get(tvshowtitle, year, imdb, tmdb, tvdb, tvrage, idx=False)

        try: items = [{'name': i['name'], 'title': i['title'], 'year': i['year'], 'imdb': i['imdb'], 'tmdb': i['tmdb'], 'tvdb': i['tvdb'], 'tvrage': i['tvrage'], 'season': i['season'], 'episode': i['episode'], 'tvshowtitle': i['tvshowtitle'], 'alter': i['alter'], 'date': i['premiered']} for i in items]
        except: items = []

        try:
            if not self.dupe_setting == 'true': raise Exception()
            if items == []: raise Exception()

            id = [items[0]['imdb'], items[0]['tvdb']]
            if not items[0]['tmdb'] == '0': id += [items[0]['tmdb']]

            lib = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"properties" : ["imdbnumber", "title", "year"]}, "id": 1}')
            lib = unicode(lib, 'utf-8', errors='ignore')
            lib = json.loads(lib)['result']['tvshows']
            lib = [i['title'].encode('utf-8') for i in lib if str(i['imdbnumber']) in id or (i['title'].encode('utf-8') == items[0]['tvshowtitle'] and str(i['year']) == items[0]['year'])][0]

            lib = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"filter":{"and": [{"field": "tvshow", "operator": "is", "value": "%s"}]}, "properties": ["season", "episode"]}, "id": 1}' % lib)
            lib = unicode(lib, 'utf-8', errors='ignore')
            lib = json.loads(lib)['result']['episodes']
            lib = ['S%02dE%02d' % (int(i['season']), int(i['episode'])) for i in lib]

            items = [i for i in items if not 'S%02dE%02d' % (int(i['season']), int(i['episode'])) in lib]
        except:
            pass

        for i in items:
            try:
                if xbmc.abortRequested == True: return sys.exit()

                if self.check_setting == 'true':
                    if i['episode'] == '1':
                        self.block = True
                        from resources.lib.sources import sources
                        src = sources().checkSources(i['name'], i['title'], i['year'], i['imdb'], i['tmdb'], i['tvdb'], i['tvrage'], i['season'], i['episode'], i['tvshowtitle'], i['alter'], i['date'])
                        if src == True: self.block = False
                    if self.block == True: raise Exception()

                if int(self.date) <= int(re.sub('[^0-9]', '', str(i['date']))):
                    from resources.lib.sources import sources
                    src = sources().checkSources(i['name'], i['title'], i['year'], i['imdb'], i['tmdb'], i['tvdb'], i['tvrage'], i['season'], i['episode'], i['tvshowtitle'], i['alter'], i['date'])
                    if src == False: raise Exception()

                self.strmFile(i)
            except:
                pass

        if range == True: return

        if self.infoDialog == True:
            control.infoDialog(control.lang(30423).encode('utf-8'), time=1)

        if self.library_setting == 'true' and not control.condVisibility('Library.IsScanningVideo'):
            control.execute('UpdateLibrary(video)')


    def range(self, url):
        control.idle()

        yes = control.yesnoDialog(control.lang(30425).encode('utf-8'), '', '')
        if not yes: return

        if not control.condVisibility('Window.IsVisible(infodialog)') and not control.condVisibility('Player.HasVideo'):
            control.infoDialog(control.lang(30421).encode('utf-8'), time=10000000)
            self.infoDialog = True

        from resources.lib.indexers import tvshows
        items = tvshows.tvshows().get(url, idx=False)
        if items == None: items = []

        for i in items:
            try:
                if xbmc.abortRequested == True: return sys.exit()
                self.add(i['title'], i['year'], i['imdb'], i['tmdb'], i['tvdb'], i['tvrage'], range=True)
            except:
                pass

        if self.infoDialog == True:
            control.infoDialog(control.lang(30423).encode('utf-8'), time=1)

        if self.library_setting == 'true' and not control.condVisibility('Library.IsScanningVideo'):
            control.execute('UpdateLibrary(video)')


    def strmFile(self, i):
        try:
            name, title, year, imdb, tmdb, tvdb, tvrage, season, episode, tvshowtitle, alter, date = i['name'], i['title'], i['year'], i['imdb'], i['tmdb'], i['tvdb'], i['tvrage'], i['season'], i['episode'], i['tvshowtitle'], i['alter'], i['date']

            episodename, episodetitle = urllib.quote_plus(name), urllib.quote_plus(title)
            systitle, syspremiered = urllib.quote_plus(tvshowtitle), urllib.quote_plus(date)

            if self.version >= 15:
                transname = '%s (%s) S%02dE%02d' % (tvshowtitle.translate(None, '\/:*?"<>|'), year, int(season), int(episode))
                transtitle = '%s (%s)' % (tvshowtitle.translate(None, '\/:*?"<>|'), year)
            else:
                transname = name.translate(None, '\/:*?"<>|').strip('.')
                transtitle = tvshowtitle.translate(None, '\/:*?"<>|').strip('.')

            transseason = 'Season %s' % season.translate(None, '\/:*?"<>|').strip('.')

            content = '%s?action=play&name=%s&title=%s&year=%s&imdb=%s&tmdb=%s&tvdb=%s&tvrage=%s&season=%s&episode=%s&tvshowtitle=%s&alter=%s&date=%s' % (sys.argv[0], episodename, episodetitle, year, imdb, tmdb, tvdb, tvrage, season, episode, systitle, alter, syspremiered)

            control.makeFile(self.library_folder)

            folder = os.path.join(self.library_folder, transtitle)
            control.makeFile(folder)

            try:
				if not 'ftp://' in folder: raise Exception()
				from ftplib import FTP
				ftparg = re.compile('ftp://(.+?):(.+?)@(.+?):?(\d+)?/(.+/?)').findall(folder)
				ftp = FTP(ftparg[0][2],ftparg[0][0],ftparg[0][1])
				try: ftp.cwd(ftparg[0][4])
				except: ftp.mkd(ftparg[0][4])
				ftp.quit()
            except:
				pass

            folder = os.path.join(folder, transseason)
            control.makeFile(folder)

            try:
				if not 'ftp://' in folder: raise Exception()
				from ftplib import FTP
				ftparg = re.compile('ftp://(.+?):(.+?)@(.+?):?(\d+)?/(.+/?)').findall(folder)
				ftp = FTP(ftparg[0][2],ftparg[0][0],ftparg[0][1])
				try: ftp.cwd(ftparg[0][4])
				except: ftp.mkd(ftparg[0][4])
				ftp.quit()
            except:
				pass

            stream = os.path.join(folder, transname + '.strm')
            file = control.openFile(stream, 'w')
            file.write(str(content))
            file.close()
        except:
            pass


class libepisodes:
    def __init__(self):
        self.library_folder = os.path.join(control.transPath(control.setting('tv_library')),'')

        self.library_setting = control.setting('update_library') or 'true'
        self.property = '%s_service_property' % control.addonInfo('name').lower()

        self.datetime = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5))
        self.date = (self.datetime - datetime.timedelta(hours = 24)).strftime('%Y%m%d')

        self.infoDialog = False


    def update(self, query=None, info='true'):
        if not query == None: control.idle()

        try:
            items = []
            season, episode = [], []
            show = [os.path.join(self.library_folder, i) for i in control.listDir(self.library_folder)[0]]
            for s in show:
                try: season += [os.path.join(s, i) for i in control.listDir(s)[0]]
                except: pass
            for s in season:
                try: episode.append([os.path.join(s, i) for i in control.listDir(s)[1] if i.endswith('.strm')][-1])
                except: pass

            for file in episode:
                try:
                    file = control.openFile(file)
                    read = file.read()
                    read = read.encode('utf-8')
                    file.close()

                    if not read.startswith(sys.argv[0]): raise Exception()

                    params = dict(urlparse.parse_qsl(read.replace('?','')))

                    try: tvshowtitle = params['tvshowtitle']
                    except: tvshowtitle = None
                    try: tvshowtitle = params['show']
                    except: pass
                    if tvshowtitle == None or tvshowtitle == '': raise Exception()

                    year, imdb, tvdb = params['year'], params['imdb'], params['tvdb']

                    imdb = 'tt' + re.sub('[^0-9]', '', str(imdb))

                    try: tmdb = params['tmdb']
                    except: tmdb = '0'

                    try: tvrage = params['tvrage']
                    except: tvrage = '0'

                    items.append({'tvshowtitle': tvshowtitle, 'year': year, 'imdb': imdb, 'tmdb': tmdb, 'tvdb': tvdb, 'tvrage': tvrage})
                except:
                    pass

            items = [i for x, i in enumerate(items) if i not in items[x + 1:]]
            if len(items) == 0: raise Exception()
        except:
            return

        try:
            lib = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params": {"properties" : ["imdbnumber", "title", "year"]}, "id": 1}')
            lib = unicode(lib, 'utf-8', errors='ignore')
            lib = json.loads(lib)['result']['tvshows']
        except:
            return

        if info == 'true' and not control.condVisibility('Window.IsVisible(infodialog)') and not control.condVisibility('Player.HasVideo'):
            control.infoDialog(control.lang(30422).encode('utf-8'), time=10000000)
            self.infoDialog = True

        try:
            control.makeFile(control.dataPath)
            dbcon = database.connect(control.libcacheFile)
            dbcur = dbcon.cursor()
            dbcur.execute("CREATE TABLE IF NOT EXISTS tvshows (""id TEXT, ""items TEXT, ""UNIQUE(id)"");")
        except:
            return
        try:
            from resources.lib.indexers import episodes
        except:
            return

        for item in items:
            it = None

            if xbmc.abortRequested == True: return sys.exit()

            try:
                dbcur.execute("SELECT * FROM tvshows WHERE id = '%s'" % item['tvdb'])
                fetch = dbcur.fetchone()
                it = eval(fetch[1].encode('utf-8'))
            except:
                pass

            try:
                if not it == None: raise Exception()

                it = episodes.episodes().get(item['tvshowtitle'], item['year'], item['imdb'], item['tmdb'], item['tvdb'], item['tvrage'], idx=False)

                status = it[0]['status'].lower()

                it = [{'name': i['name'], 'title': i['title'], 'year': i['year'], 'imdb': i['imdb'], 'tmdb': i['tmdb'], 'tvdb': i['tvdb'], 'tvrage': i['tvrage'], 'season': i['season'], 'episode': i['episode'], 'tvshowtitle': i['tvshowtitle'], 'alter': i['alter'], 'date': i['premiered']} for i in it]

                if status == 'continuing': raise Exception()
                dbcur.execute("INSERT INTO tvshows Values (?, ?)", (item['tvdb'], repr(it)))
                dbcon.commit()
            except:
                pass

            try:
                id = [item['imdb'], item['tvdb']]
                if not item['tmdb'] == '0': id += [item['tmdb']]

                ep = [x['title'].encode('utf-8') for x in lib if str(x['imdbnumber']) in id or (x['title'].encode('utf-8') == item['tvshowtitle'] and str(x['year']) == item['year'])][0]
                ep = control.jsonrpc('{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": {"filter":{"and": [{"field": "tvshow", "operator": "is", "value": "%s"}]}, "properties": ["season", "episode"]}, "id": 1}' % ep)
                ep = unicode(ep, 'utf-8', errors='ignore')
                ep = json.loads(ep)['result']['episodes'][-1]

                num = [x for x,y in enumerate(it) if str(y['season']) == str(ep['season']) and str(y['episode']) == str(ep['episode'])][-1]
                it = [y for x,y in enumerate(it) if x > num]
                if len(it) == 0: continue
            except:
                continue

            for i in it:
                try:
                    if xbmc.abortRequested == True: return sys.exit()

                    if int(self.date) <= int(re.sub('[^0-9]', '', str(i['date']))):
                        from resources.lib.sources import sources
                        src = sources().checkSources(i['name'], i['title'], i['year'], i['imdb'], i['tmdb'], i['tvdb'], i['tvrage'], i['season'], i['episode'], i['tvshowtitle'], i['alter'], i['date'])
                        if src == False: raise Exception()

                    libtvshows().strmFile(i)
                except:
                    pass

        if self.infoDialog == True:
            control.infoDialog(control.lang(30423).encode('utf-8'), time=1)

        if self.library_setting == 'true' and not control.condVisibility('Library.IsScanningVideo'):
            control.execute('UpdateLibrary(video)')


    def service(self):
        try:
            control.makeFile(control.dataPath)
            dbcon = database.connect(control.libcacheFile)
            dbcur = dbcon.cursor()
            dbcur.execute("CREATE TABLE IF NOT EXISTS service (""setting TEXT, ""value TEXT, ""UNIQUE(setting)"");")
            dbcur.execute("SELECT * FROM service WHERE setting = 'last_run'")
            fetch = dbcur.fetchone()
            if fetch == None:
                serviceProperty = "1970-01-01 23:59:00.000000"
                dbcur.execute("INSERT INTO service Values (?, ?)", ('last_run', serviceProperty))
                dbcon.commit()
            else:
                serviceProperty = str(fetch[1])
            dbcon.close()
        except:
            try: return dbcon.close()
            except: return

        try: control.window.setProperty(self.property, serviceProperty)
        except: return

        while (not xbmc.abortRequested):
            try:
                serviceProperty = control.window.getProperty(self.property)

                t1 = datetime.timedelta(hours=6)
                t2 = datetime.datetime.strptime(serviceProperty, '%Y-%m-%d %H:%M:%S.%f')
                t3 = datetime.datetime.now()

                check = abs(t3 - t2) > t1
                if check == False: raise Exception()

                if (control.player.isPlaying() or control.condVisibility('Library.IsScanningVideo')): raise Exception()

                serviceProperty = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

                control.window.setProperty(self.property, serviceProperty)

                try:
                    dbcon = database.connect(control.libcacheFile)
                    dbcur = dbcon.cursor()
                    dbcur.execute("CREATE TABLE IF NOT EXISTS service (""setting TEXT, ""value TEXT, ""UNIQUE(setting)"");")
                    dbcur.execute("DELETE FROM service WHERE setting = 'last_run'")
                    dbcur.execute("INSERT INTO service Values (?, ?)", ('last_run', serviceProperty))
                    dbcon.commit()
                    dbcon.close()
                except:
                    try: dbcon.close()
                    except: pass

                if not control.setting('service_update') == 'true': raise Exception()
                info = control.setting('service_notification') or 'true'
                self.update(None, info=info)
            except:
                pass

            control.sleep(10000)


