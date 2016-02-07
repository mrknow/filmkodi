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


import os,re,urllib,zipfile,StringIO,urlparse,datetime,base64

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

from resources.lib.libraries import control
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://filmikz.ch'
        self.data_link = 'aHR0cHM6Ly9vZmZzaG9yZWdpdC5jb20vbGFtYmRhODEvZGF0YWJhc2VzL2ZpbG1pa3ouemlw'



    def get_movie(self, imdb, title, year):
        try:
            data = os.path.join(control.dataPath, 'filmikz.db')

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

            result = [i[0] for i in result if title == cleantitle.movie(i[1])][0]

            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            result = client.source(url)
            links = re.compile("/watch\.php\?q=(.+?)'").findall(result)

            for i in links:
                try:
                    url = base64.urlsafe_b64decode(i.encode('utf-8'))
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    host = base64.urlsafe_b64decode(i.encode('utf-8'))
                    host = urlparse.urlparse(host).netloc
                    host = host.rsplit('.', 1)[0].split('.', 1)[-1]
                    host = host.strip().lower()
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    sources.append({'source': host, 'quality': 'SD', 'provider': 'Filmikz', 'url': url})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = resolvers.request(url)
            return url
        except:
            return


