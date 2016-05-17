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


import re,urllib,urlparse

from resources.lib.libraries import cleantitle
from resources.lib.libraries import cloudflare
from resources.lib.libraries import client
from resources.lib.resolvers import openload
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://movieshd.tv'
        self.search_link = '/?s=%s'


    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query)

            result = client.parseDOM(result, 'ul', attrs = {'class': 'listing-videos.+?'})[0]
            result = client.parseDOM(result, 'li', attrs = {'class': '.+?'})

            title = cleantitle.movie(title)
            years = ['(%s)' % str(year), '(%s)' % str(int(year)+1), '(%s)' % str(int(year)-1)]
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0]) for i in result]
            result = [i for i in result if title == cleantitle.movie(i[1])]
            result = [i[0] for i in result if any(x in i[1] for x in years)][0]

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

            result = client.source(urlparse.urljoin(self.base_link, url))

            quality = client.parseDOM(result, 'title')[0]
            if '[CAM]' in quality or '[TS]' in quality: quality = 'CAM'
            elif '[SCREENER]' in quality: quality = 'SCR'
            else: quality = 'HD'

            result = client.parseDOM(result, 'div', attrs = {'class': 'video-embed'})[0]

            try:
                url = client.parseDOM(result, 'iframe', ret='src')
                url = [i for i in url if 'openload' in i.lower()][0]
                if openload.check(url) == False: raise Exception()
                sources.append({'source': 'Openload', 'quality': quality, 'provider': 'MoviesHD', 'url': url})
            except:
                pass

            try:
                url = re.compile('hashkey=([\w]+)').findall(result)
                url += re.compile('ref=[\'|\"](.+?)[\'|\"]').findall(result)
                url = 'http://videomega.tv/cdn.php?ref=%s' % url[0]
                url = resolvers.request(url)
                if url == None: raise Exception()
                sources.append({'source': 'Videomega', 'quality': quality, 'provider': 'MoviesHD', 'url': url})
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


