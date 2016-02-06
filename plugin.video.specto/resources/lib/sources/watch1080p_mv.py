# -*- coding: utf-8 -*-

'''
    Genesis Add-on
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
import base64


class source:
    def __init__(self):
        self.base_link = 'http://watch1080p.com'
        self.search_link = '/search.php?q=%s&limit=1'

    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query).decode('utf-8').encode('utf-8')
            result = result.decode('utf-8').encode('utf-8')
            result = client.parseDOM(result, 'li')
            title = cleantitle.movie(title)
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a')[0]) for i in result]
            result = [(i[0], re.sub('<.+?>|</.+?>','', i[1])) for i in result]
            result = [i for i in result if title == cleantitle.movie(i[1])]
            result = result[-1][0]
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
            result = client.parseDOM(result, 'a', attrs = {'class': 'icons btn_watch_detail'},ret='href')
            result = client.source(result[0])
            result = client.parseDOM(result,'div',attrs= {'class':'server'})
            result = re.compile('(<a.*?</a>)', re.DOTALL).findall(result[0])
            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a')) for i in result]
            for i in range(len(result)):
                url = result[i][0][0]
                quality = 'SD'
                if '1080' in result[i][1][0]: quality = '1080p'
                elif '720' in result[i][1][0]: quality = 'HD'
                elif '480' in result[i][1][0]: quality = 'SD'
                sources.append({'source': 'watch1080p', 'quality': quality, 'provider': 'Watch1080p', 'url': url})

            return sources
        except:
            return sources


    def resolve(self, url):
        link = client.source(url)
        url=re.compile('src="(.+?)" style').findall(link)[0]
        link = client.source(url)
        try:
                url=re.compile("window.atob\('(.+?)'\)\)").findall(link)[0]
                content=base64.b64decode(url)
                data=base64.b64decode(content)
                url=re.compile("<source src='(.+?)'").findall(data)[0]
                url = url + 'User-Agent%3DMozilla%2F5.0%20(X11%3B%20Linux%20x86_64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F48.0.2564.82%20Safari%2F537.36%27'

        except:
                try:
                    url=re.compile('src="(.+?)"').findall(link)[0]

                    host = urlparse.urlparse(url).netloc
                    host = host.replace('www.', '').replace('embed.', '')
                    host = host.rsplit('.', 1)[0]
                    host = host.lower()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = resolvers.request(url)

                except:pass
        return url
