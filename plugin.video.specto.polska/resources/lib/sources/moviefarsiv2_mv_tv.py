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


import os,re,urllib,zipfile,StringIO,datetime,base64

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

from resources.lib.libraries import control
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client


class source:
    def __init__(self):
        self.data_link = 'aHR0cHM6Ly9vZmZzaG9yZWdpdC5jb20vbGFtYmRhODEvZGF0YWJhc2VzL21vdmllZmFyc2kuemlw'


    def get_movie(self, imdb, title, year):
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
        return

        try:
            sources = []

            if url == None: return sources

            data = os.path.join(control.dataPath, 'moviefarsi.db')

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

            content = re.compile('(.+?)\sS\d*E\d*$').findall(url)


            if len(content) == 0:
                title, year = re.compile('(.+?) (\d{4})$').findall(url)[0]
                title = cleantitle.movie(title)

                dbcur.execute("SELECT * FROM movies WHERE year = '%s'" % year)
                result = dbcur.fetchone()
                result = eval(result[1].encode('utf-8'))

                links = [(i, re.sub('(\.|\(|\[|\s)(\d{4}|3D)(\.|\)|\]|\s|)(.+|)', '', i)) for i in result]
                links = [i[0] for i in links if title == cleantitle.movie(os.path.basename(i[1]))]

                for i in links:
                    try:
                        url = client.replaceHTMLCodes(i)
                        url = url.encode('utf-8')

                        if not url.endswith(('mp4', 'mkv')): raise Exception()

                        fmt = re.sub('(.+)(\.|\(|\[|\s)(\d{4})(\.|\)|\]|\s)', '', i)
                        fmt = re.split('\.|\(|\)|\[|\]|\s|\-|\_', fmt)
                        fmt = [x.lower() for x in fmt]

                        if '1080p' in fmt: quality = '1080p'
                        elif '720p' in fmt or 'hd' in fmt: quality = 'HD'
                        else: quality = 'SD'

                        if '3d' in fmt: info = '3D'
                        else: info = ''
                        control.log('### FARSI ')
                        sources.append({'source': 'Moviefarsi', 'quality': quality, 'provider': 'Moviefarsiv2', 'url': url, 'info': info})
                    except:
                        pass


            else:
                tvshowtitle, season, episode = re.compile('(.+?)\sS(\d*)E(\d*)$').findall(url)[0]
                tvshowtitle = cleantitle.tv(tvshowtitle)

                dbcur.execute("SELECT * FROM tvshows WHERE tvshowtitle = '%s'" % tvshowtitle)
                result = dbcur.fetchone()
                result = eval(result[1].encode('utf-8'))

                match = ['S%sE%s' % (season, episode), 'S%s E%s' % (season, episode)]

                links = [(i, os.path.basename(i)) for i in result]
                links = [i[0] for i in links if any(x in i[1] for x in match)]

                for i in links:
                    try:
                        url = client.replaceHTMLCodes(i)
                        url = url.encode('utf-8')

                        fmt = os.path.basename(url).lower()

                        if '1080p' in fmt: quality = '1080p'
                        elif '720p' in fmt or 'hd' in fmt: quality = 'HD'
                        else: quality = 'SD'

                        sources.append({'source': 'Moviefarsi', 'quality': quality, 'provider': 'Moviefarsiv2', 'url': url})
                    except:
                        pass

            return sources
        except:
            return sources


    def resolve(self, url):
        return
        url = '%s|User-Agent=%s' % (url, urllib.quote_plus(client.agent()))
        return url


