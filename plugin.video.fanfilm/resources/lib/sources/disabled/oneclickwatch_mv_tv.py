# -*- coding: utf-8 -*-

'''
    FanFilm Add-on
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
        self.data_link = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL21ya25vdy9kYXRhYmFzZS9tYXN0ZXIvb25lY2xpY2sxLnppcA=='
        self.sources = []

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
        try:
            self.sources = []
            sources = []
            mylinks = []
            mysources=[]

            if url == None: return sources
            data = os.path.join(control.dataPath, 'oneclick1.db')

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
            #control.log(">>>>>>>>>>>>>>> ONEC content "  )

            content = re.compile('(.+?)\sS\d*E\d*$').findall(url)
            #control.log(">>>>>>>>>>>>>>> ONEC aaa content %s" % len(content))

            if len(content) == 0:
                title, year = re.compile('(.+?) (\d{4})$').findall(url)[0]
                title = cleantitle.movie(title)

                dbcur.execute("SELECT * FROM movies WHERE title like '%"+title+"%' and title like '%"+year+"%'" )
                result = dbcur.fetchall()
                for i in result:
                    print(i[0])
                    mysources.append(i[0])

            else:
                #control.log(">>>>>>>>>>>>>>> ONEC %ELSE ")

                tvshowtitle, season, episode = re.compile('(.+?)\sS(\d*)E(\d*)$').findall(url)[0]
                tvshowtitle = cleantitle.movie(tvshowtitle)
                myses = 's%se%s' % (season,episode)
                control.log(">>>>>>>>>>>>>>> ONEC %s season |%s|" % (tvshowtitle,myses))
                mysql = "SELECT * FROM movies WHERE title like '%"+tvshowtitle+"%' and title like '%"+myses+"%'"
                #mysql = "SELECT * FROM movies WHERE title like '%" + tvshowtitle + "%'"

                #control.log(">>>>>>>>>>>>>>> ONEC SQL  |%s|" % (mysql))
                dbcur.execute(mysql)
                result = dbcur.fetchall()

                for i in result:
                    mysources.append(i[0])
                    #control.log(">>>>>>>>>>>>>>> ONEC result %s" % (i[0]))



            mylinks = []
            for myurl in mysources:
                result = client.request(myurl,mobile=True)
                mytitle = re.compile('<title>(.*?)</title>', re.DOTALL).findall(result)[0]
                if any(word in mytitle.lower() for word in ['camrip', 'tsrip', 'hdcam', 'hdts', 'dvdcam', 'dvdts', 'cam', 'ts']):
                    quality = 'CAM'
                elif '1080' in mytitle:
                    quality = '1080p'
                elif '720p' in mytitle:
                    quality = 'HD'
                else:
                    quality = 'SD'
                links = client.parseDOM(result, 'a', attrs={'rel': 'nofollow'})
                links = [i for i in links if i.startswith('http')]
                for a in links:
                    #control.log(">>>>>>>>>>>>>>> ONE CHECK  %s" % (a))
                    mylinks.append([a,quality])

            threads = []
            for i in mylinks: threads.append(workers.Thread(self.check, i))
            [i.start() for i in threads]
            for i in range(0, 10 * 4):
                is_alive = [x.is_alive() for x in threads]
                if all(x == False for x in is_alive): break
                time.sleep(2)
            return self.sources
        except:
            return self.sources


    def check(self, i):
        try:
            #control.log(">>>>>>>>>>>>>>> ONE CHECK  %s" % (i[0]))
            url = client.replaceHTMLCodes(i[0])
            url = url.encode('utf-8')

            host = urlparse.urlparse(url).netloc
            host = host.replace('www.', '').replace('embed.', '')
            host = host.rsplit('.', 1)[0]
            host = host.lower()
            host = client.replaceHTMLCodes(host)
            host = host.encode('utf-8')
            #control.log("##OneClickWatch %s - url %s" % (host, i[0]))
            #if host in i[2]: check = url = resolvers.request(url)

            if host == 'openload': check = openload.check(url)
            elif host == 'uptobox': check = uptobox.check(url)
            elif host == 'cloudzilla': check = cloudzilla.check(url)
            elif host == 'zstream': check = zstream.check(url)
            elif host == 'videomega': check = videomega.check(url)

            else: raise Exception()

            if check == None or check == False: raise Exception()

            self.sources.append({'source': host, 'quality': i[1], 'provider': 'Oneclickwatch', 'url': url})
        except:
            pass


    def resolve(self, url):
        try:
            url = resolvers.request(url)
            return url
        except:
            return


