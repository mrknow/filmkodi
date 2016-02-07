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


import re,urllib,urlparse,json,base64

from resources.lib.libraries import control
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://directdownload.tv'
        self.search_link = 'L2FwaT9rZXk9NEIwQkI4NjJGMjRDOEEyOSZxdWFsaXR5W109SERUViZxdWFsaXR5W109RFZEUklQJnF1YWxpdHlbXT03MjBQJnF1YWxpdHlbXT1XRUJETCZxdWFsaXR5W109V0VCREwxMDgwUCZsaW1pdD0yMCZrZXl3b3JkPQ=='


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

            if (control.setting('realdedrid_user') == '' and control.setting('premiumize_user') == ''): raise Exception()

            query = base64.urlsafe_b64decode(self.search_link) + urllib.quote_plus(url)
            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query)
            result = json.loads(result)

            title, hdlr = re.compile('(.+?) (S\d*E\d*)$').findall(url)[0]
            title = cleantitle.tv(title)
            hdlr = [hdlr]

            links = []

            for i in result:
                try:
                    t = i['showName']
                    t = client.replaceHTMLCodes(t)
                    t = cleantitle.tv(t)
                    if not t == title: raise Exception()

                    y = i['release']
                    y = re.compile('[\.|\(|\[|\s](\d{4}|S\d*E\d*)[\.|\)|\]|\s]').findall(y)[-1]
                    y = y.upper()
                    if not any(x == y for x in hdlr): raise Exception()

                    quality = i['quality']

                    if quality == 'WEBDL1080P': quality = '1080p'
                    elif quality in ['720P', 'WEBDL']: quality = 'HD'
                    else: quality = 'SD'

                    size = i['size']
                    size = float(size)/1024
                    info = '%.2f GB' % size

                    url = i['links']
                    for x in url.keys(): links.append({'url': url[x], 'quality': quality, 'info': info})
                except:
                    pass

            for i in links:
                try:
                    url = i['url']
                    if len(url) > 1: raise Exception()
                    url = url[0]

                    host = (urlparse.urlparse(url).netloc).replace('www.', '').rsplit('.', 1)[0].lower()
                    if not host in hosthdDict: raise Exception()

                    sources.append({'source': host, 'quality': i['quality'], 'provider': 'DirectDL', 'url': url, 'info': i['info']})
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

