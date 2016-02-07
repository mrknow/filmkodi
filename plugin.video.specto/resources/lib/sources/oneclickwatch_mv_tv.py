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


import re,urlparse,time

from resources.lib.libraries import client
from resources.lib.libraries import workers
from resources.lib.resolvers import hugefiles
from resources.lib.resolvers import uploadrocket
from resources.lib.resolvers import openload
from resources.lib import resolvers
from resources.lib import sources


class source:
    def __init__(self):
        self.base_link = 'http://oneclickwatch.ws'


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

            if url == None: return self.sources

            url = url.replace('\'', '')
            url = re.sub(r'[^a-zA-Z0-9\s]+', ' ', url).lower().strip()
            url = re.sub('\s\s+' , ' ', url)
            url = url.replace(' ' , '-')

            query = urlparse.urljoin(self.base_link, url)

            result = client.source(query)
            if result == None: raise Exception()

            fmt = re.compile('url *: *[\'|\"](.+?)[\'|\"]').findall(result)
            fmt = fmt[0] if len(fmt) > 0 else ''
            fmt = re.sub('(.+)(\d{4}|s\d*e\d*)-', '', fmt.lower())
            fmt = re.split('-', fmt.replace('/' , ''))

            if any(x in ['dvdscr', 'r5', 'r6', 'camrip', 'tsrip', 'hdcam', 'hdts', 'dvdcam', 'dvdts', 'cam', 'ts'] for x in fmt): raise Exception()
            elif '1080p' in fmt: quality = '1080p'
            elif '720p' in fmt: quality = 'HD'
            else: raise Exception()

            hostdirhdDict = sources.sources().hostdirhdDict

            links = client.parseDOM(result, 'a', attrs = {'rel': 'nofollow'})
            links = [i for i in links if i.startswith('http')]
            links = [(i, quality, hostdirhdDict) for i in links]


            threads = []
            for i in links: threads.append(workers.Thread(self.check, i))
            [i.start() for i in threads]
            for i in range(0, 10 * 2):
                is_alive = [x.is_alive() for x in threads]
                if all(x == False for x in is_alive): break
                time.sleep(0.5)
            return self.sources
        except:
            return self.sources


    def check(self, i):
        try:
            url = client.replaceHTMLCodes(i[0])
            url = url.encode('utf-8')

            host = urlparse.urlparse(url).netloc
            host = host.replace('www.', '').replace('embed.', '')
            host = host.rsplit('.', 1)[0]
            host = host.lower()
            host = client.replaceHTMLCodes(host)
            host = host.encode('utf-8')

            if host in i[2]: check = url = resolvers.request(url)
            elif host == 'hugefiles': check = hugefiles.check(url)
            elif host == 'uploadrocket': check = uploadrocket.check(url)
            elif host == 'openload': check = openload.check(url)
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


