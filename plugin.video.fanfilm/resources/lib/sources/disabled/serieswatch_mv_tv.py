# -*- coding: utf-8 -*-

'''
    FanFilm Add-on
    Copyright (C) 2015 mrknow

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


import re,urlparse,datetime, urllib,zipfile
import os,base64,StringIO,time

from resources.lib.libraries import client
from resources.lib.libraries import cleantitle

from resources.lib.libraries import workers
from resources.lib.libraries import control
from resources.lib.resolvers import cloudzilla
from resources.lib.resolvers import openload
from resources.lib.resolvers import uptobox
from resources.lib.resolvers import zstream
from resources.lib.resolvers import videomega

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

from resources.lib import resolvers


class source:
    def __init__(self):
        self.data_link = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL21ya25vdy9kYXRhYmFzZS9tYXN0ZXIvc2VyaWVzd2F0Y2guemlw'
        self.sources = []

    def get_movie(self, imdb, title, year):
        return None
        try:
            url = '%s %s' % (title, year)
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            url = tvshowtitle
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        try:
            if url == None: return

            url = '%s S%02dE%02d' % (url, int(season), int(episode))
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return



    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources
            data = os.path.join(control.dataPath, 'serieswatch.db')

            download = True

            try: download = abs(datetime.datetime.fromtimestamp(os.path.getmtime(data)) - (datetime.datetime.now())) > datetime.timedelta(days=7)
            except: pass

            if download == True:
                result = client.request(base64.b64decode(self.data_link))
                print(len(result))
                control.log(">>>>>>>>>>>>>>> ONEC Downloading" )
                zip = zipfile.ZipFile(StringIO.StringIO(result))
                zip.extractall(control.dataPath)
                zip.close()

            dbcon = database.connect(data)
            dbcur = dbcon.cursor()
            content = re.compile('(.+?)\sS\d*E\d*$').findall(url)

            if len(content) == 0:
                title, year = re.compile('(.+?) (\d{4})$').findall(url)[0]
                title = cleantitle.movie(title)
                dbcur.execute("SELECT * FROM movies WHERE title like '%"+title+"%' and title like '%"+year+"%'" )
                result = dbcur.fetchall()

            else:
                tvshowtitle, season, episode = re.compile('(.+?)\sS(\d*)E(\d*)$').findall(url)[0]
                tvshowtitle = cleantitle.movie(tvshowtitle)
                myses = 's%se%s' % (season,episode)
                control.log(">>>>>>>>>>>>>>> ONEC %s season |%s|" % (tvshowtitle,myses))
                mysql = "SELECT * FROM movies WHERE title like '%"+tvshowtitle+"%' and title like '%"+myses+"%'"
                control.log(">>>>>>>>>>>>>>> ONEC SQL  |%s|" % (mysql))
                dbcur.execute(mysql)
                result = dbcur.fetchall()



            for myurl in result:
                result = myurl[1]
                if any(word in result.lower() for word in ['camrip', 'tsrip', 'hdcam', 'hdts', 'dvdcam', 'dvdts', 'cam', 'ts']):
                    quality = 'CAM'
                elif '1080' in result:
                    quality = '1080p'
                elif '720p' in result:
                    quality = 'HD'
                else:
                    quality = 'SD'
                links = myurl[0]
                #links = [i for i in links if i.startswith('http')]
                if not any(word in links.lower() for word in ['mp3', 'farsi', 'ganool']):
                    #print("Mamy", links)
                    sources.append({'source': 'Serieswatch', 'quality': quality, 'provider': 'Serieswatch', 'url': links})

            return sources
        except:
            return


    def resolve(self, url):
        try:
            url = resolvers.request(url)
            return url
        except:
            return


