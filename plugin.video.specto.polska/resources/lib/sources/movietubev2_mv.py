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
from resources.lib.libraries import client
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://www.movie-tube.co'
        self.search_link = '/index.php?do=search'
        self.search_post = 'do=search&subaction=search&search_start=0&full_search=0&result_from=1&story=%s'


    def get_movie(self, imdb, title, year):
        try:
            post = '%s %s' % (title, year)
            post = self.search_post % (urllib.quote_plus(post))

            query = urlparse.urljoin(self.base_link, self.search_link)

            result = client.source(query, post=post)
            result = client.parseDOM(result, 'div', attrs = {'id': 'dle-content'})[0]

            title = cleantitle.movie(title)

            result = client.parseDOM(result, 'div', attrs = {'class': 'short-film'})
            result = client.parseDOM(result, 'h5')
            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a')) for i in result]
            result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [i for i in result if title == cleantitle.movie(i[1])]
            if not len(result) == 1: raise Exception()
            result = result[0][0]

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

            quality = client.parseDOM(result, 'li')
            quality = [i for i in quality if '>Quality :<' in i][0]
            quality = client.parseDOM(quality, 'p')[0]

            if 'CAM' in quality or 'TS' in quality: quality = 'CAM'
            elif 'SCREENER' in quality: quality = 'SCR'
            else: quality = 'HD'

            url = client.parseDOM(result, 'iframe', ret='src')
            url = [i for i in url if 'videomega' in i.lower()][0]
            url = re.compile('[ref|hashkey]=([\w]+)').findall(url)
            url = 'http://videomega.tv/cdn.php?ref=%s' % url[0]

            url = resolvers.request(url)

            if url == None: raise Exception()

            sources.append({'source': 'Videomega', 'quality': quality, 'provider': 'Movietubev2', 'url': url})

            return sources
        except:
            return sources


    def resolve(self, url):
        return url


