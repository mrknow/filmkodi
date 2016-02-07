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


class source:
    def __init__(self):
        self.base_link = 'https://beinmovie.com'
        self.search_link = '/movies-list.php?b=search&v=%s'
        self.detail_link = '/movie-detail.php?%s'
        self.player_link = '/movie-player.php?%s'


    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query)
            result = client.parseDOM(result, 'li', attrs = {'class': '[^"]*movie[^"]*'})

            title = cleantitle.movie(title)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'h4')) for i in result]
            result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [i for i in result if title == cleantitle.movie(i[1])]
            result = [i[0] for i in result][0]

            url = re.compile('movie-detail/(.+?)/').findall(result)[0]
            url = self.detail_link % url
            url = url.encode('utf-8')

            if len(result) > 1:
                y = client.source(urlparse.urljoin(self.base_link, url))
                y = re.compile('(\d{4})-\d{2}-\d{2}').findall(y)[-1]
                if not str(y) in years: raise Exception()

            return url
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)
            result = client.source(url)

            url = client.parseDOM(result, 'div', attrs = {'class': '[^"]*movie_langs_list[^"]*'})
            url = client.parseDOM(url, 'a', ret='href')
            url = [i for i in url if 'movie_lang=en' in i][0]
            url = re.compile('movie-player/(.*)').findall(url)[0]
            url = self.player_link % url
            url = urlparse.urljoin(self.base_link, url)

            result = client.source(url)

            links = client.parseDOM(result, 'ul', {'class': 'servers'})[0]
            links = client.parseDOM(result, 'li')

            for link in links:
                try:
                    url = client.parseDOM(link, 'a', ret='href')[0]
                    url = re.compile('movie-player/(.*)').findall(url)[0]
                    url = self.player_link % url
                    url = urlparse.urljoin(self.base_link, url)
                    url = url.encode('utf-8')

                    quality = client.parseDOM(link, 'span')[-1]
                    if 'HD' in quality: quality = 'HD'
                    else: quality = 'SD'

                    sources.append({'source': 'GVideo', 'quality': quality, 'provider': 'Beinmovie', 'url': url})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            result = client.request(url)

            url = client.parseDOM(result, 'source', ret='src', attrs = {'type': 'video.+?'})[0]

            url = client.request(url, output='geturl')
            if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            else: url = url.replace('https://', 'http://')
            return url
        except:
            return


