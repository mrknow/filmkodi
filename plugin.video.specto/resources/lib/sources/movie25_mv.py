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
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://www.movie25.hk'
        self.search_link = '/search.php?key=%s'


    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link % urllib.quote_plus(title)
            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query)

            result = result.decode('iso-8859-1').encode('utf-8')
            result = client.parseDOM(result, 'div', attrs = {'class': 'movie_table'})

            title = cleantitle.movie(title)
            years = ['(%s)' % str(year), '(%s)' % str(int(year)+1), '(%s)' % str(int(year)-1)]
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[1]) for i in result]
            result = [i for i in result if title == cleantitle.movie(i[1])]
            result = [i[0] for i in result if any(x in i[1] for x in years)][0]

            url = client.replaceHTMLCodes(result)
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
            except: pass
            url = urlparse.urlparse(url).path
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

            result = result.decode('iso-8859-1').encode('utf-8')
            result = result.replace('\n','')

            quality = re.compile('>Links - Quality(.+?)<').findall(result)[0]
            quality = quality.strip()
            if quality == 'CAM' or quality == 'TS': quality = 'CAM'
            elif quality == 'SCREENER': quality = 'SCR'
            else: quality = 'SD'

            links = client.parseDOM(result, 'div', attrs = {'id': 'links'})[0]
            links = client.parseDOM(links, 'ul')

            for i in links:
                try:
                    host = client.parseDOM(i, 'li', attrs = {'id': 'link_name'})[-1]
                    host = host.strip().lower()
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    url = client.parseDOM(i, 'a', ret='href')[0]
                    url = client.replaceHTMLCodes(url)
                    url = urlparse.urljoin(self.base_link, url)
                    url = url.encode('utf-8')

                    sources.append({'source': host, 'quality': quality, 'provider': 'Movie25', 'url': url})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            result = client.request(url)
            result = result.decode('iso-8859-1').encode('utf-8')

            url = client.parseDOM(result, 'div', attrs = {'id': 'showvideo'})[0]
            url = url.replace('<IFRAME', '<iframe').replace(' SRC=', ' src=')
            url = client.parseDOM(url, 'iframe', ret='src')[0]
            url = client.replaceHTMLCodes(url)
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['url'][0]
            except: pass

            url = resolvers.request(url)
            return url
        except:
            return

