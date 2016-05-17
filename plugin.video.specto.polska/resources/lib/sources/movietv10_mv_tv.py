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


import os,re,urllib,urlparse,json,zipfile,StringIO,datetime,base64

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

from resources.lib.libraries import control
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client


class source:
    def __init__(self):
        self.base_link = 'http://movietv.to'
        self.data_link = 'aHR0cHM6Ly9vZmZzaG9yZWdpdC5jb20vbGFtYmRhODEvZGF0YWJhc2VzL21vdmlldHYyLnppcA=='
        self.extra_link = 'aHR0cDovL2p1c3RwYXN0ZS5pdC9vYzVj'


    def get_movie(self, imdb, title, year):
        try:
            data = os.path.join(control.dataPath, 'movietv.db')
            try: control.deleteFile(data)
            except: pass

            data = os.path.join(control.dataPath, 'movietv2.db')

            download = True

            try: download = abs(datetime.datetime.fromtimestamp(os.path.getmtime(data)) - (datetime.datetime.now())) > datetime.timedelta(days=7)
            except: pass

            if download == True:
                result = client.source(base64.b64decode(self.data_link))
                zip = zipfile.ZipFile(StringIO.StringIO(result))
                zip.extractall(control.dataPath)
                zip.close()

            dbcon = database.connect(data)
            dbcur = dbcon.cursor()

            dbcur.execute("SELECT * FROM movies WHERE year = '%s'" % year)
            result = dbcur.fetchone()
            result = eval(result[1].encode('utf-8'))

            title = cleantitle.movie(title)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = [i for i in result if title == cleantitle.movie(i[2])]
            result = [i[0] for i in result if any(x in i[3] for x in years)][0]

            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            data = os.path.join(control.dataPath, 'movietv.db')
            try: control.deleteFile(data)
            except: pass

            data = os.path.join(control.dataPath, 'movietv2.db')

            download = True

            try: download = abs(datetime.datetime.fromtimestamp(os.path.getmtime(data)) - (datetime.datetime.now())) > datetime.timedelta(days=7)
            except: pass

            if download == True:
                result = client.source(base64.b64decode(self.data_link))
                zip = zipfile.ZipFile(StringIO.StringIO(result))
                zip.extractall(control.dataPath)
                zip.close()

            dbcon = database.connect(data)
            dbcur = dbcon.cursor()

            dbcur.execute("SELECT * FROM tvshows WHERE year = '%s'" % year)
            result = dbcur.fetchone()
            result = eval(result[1].encode('utf-8'))

            tvshowtitle = cleantitle.tv(tvshowtitle)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = [i for i in result if tvshowtitle == cleantitle.tv(i[2])]
            result = [i[0] for i in result if any(x in i[3] for x in years)][0]

            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        try:
            if url == None: return

            if not '%01d' % int(season) == '1': return
            if '%01d' % int(episode) > '3': return

            url += '?S%02dE%02d' % (int(season), int(episode))
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            data = os.path.join(control.dataPath, 'movietv.db')
            try: control.deleteFile(data)
            except: pass

            data = os.path.join(control.dataPath, 'movietv2.db')

            download = True

            try: download = abs(datetime.datetime.fromtimestamp(os.path.getmtime(data)) - (datetime.datetime.now())) > datetime.timedelta(days=7)
            except: pass

            if download == True:
                result = client.source(base64.b64decode(self.data_link))
                zip = zipfile.ZipFile(StringIO.StringIO(result))
                zip.extractall(control.dataPath)
                zip.close()

            dbcon = database.connect(data)
            dbcur = dbcon.cursor()


            content = re.compile('(.+?)\?S\d*E\d*$').findall(url)

            try: url, handler = re.compile('(.+?)\?(S\d*E\d*)$').findall(url)[0]
            except: pass

            if len(content) == 0:
                dbcur.execute("SELECT * FROM movies")
                result = dbcur.fetchall()
                result = [eval(i[1].encode('utf-8')) for i in result]
                result = sum(result, [])
                result = [i for i in result if i[0] == url][0]

            else:
                dbcur.execute("SELECT * FROM tvshows")
                result = dbcur.fetchall()
                result = [eval(i[1].encode('utf-8')) for i in result]
                result = sum(result, [])
                result = [i for i in result if i[0] == url]
                result = [i for i in result if i[4] == handler][0]


            url = '%s|Referer=%s' % (result[1], urllib.quote_plus(urlparse.urljoin(self.base_link, result[0])))

            sources.append({'source': 'MovieTV', 'quality': 'HD', 'provider': 'MovieTV', 'url': url})

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            result = client.source(base64.b64decode(self.extra_link))

            extra = client.parseDOM(result, 'p')
            extra = [i for i in extra if 'User-Agent=' in i][0]
            extra = client.replaceHTMLCodes(extra)

            url += extra
            return url
        except:
            return


