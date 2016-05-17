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

from resources.lib.libraries import cache
from resources.lib.libraries import cloudflare
from resources.lib.libraries import client
from resources.lib.libraries import client2
from resources.lib.libraries import control
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://dizilab.com'
        self.search_link = '/diziler.xml'


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            result = cache.get(self.dizilab_tvcache, 120)

            result = [i[0] for i in result if imdb == i[1]][0]

            url = urlparse.urljoin(self.base_link, result)
            url = urlparse.urlparse(url).path
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return

    def dizilab_tvcache(self):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link)

            result = cloudflare.source(url)
            result = client.parseDOM(result, 'dizi')
            result = [(client.parseDOM(i, 'url'), client.parseDOM(i, 'imdb')) for i in result]
            result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [(re.sub('http.+?//.+?/', '/', i[0]), i[1]) for i in result]

            return result
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        if url == None: return

        url = '%s/sezon-%01d/bolum-%01d' % (url, int(season), int(episode))
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        return url


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        control.log('######### DIZILAB ## %s ' % url)
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)
            #result = client.source(url)
            result = client2.http_get(url)

            try:
                url = re.compile('"episode_player".*?src="([^"]+)"').findall(result)

                links = [(i[0], '1080p') for i in url if int(i[1]) >= 1080]
                links += [(i[0], 'HD') for i in url if 720 <= int(i[1]) < 1080]
                links += [(i[0], 'SD') for i in url if 480 <= int(i[1]) < 720]
                if not 'SD' in [i[1] for i in links]: links += [(i[0], 'SD') for i in url if 360 <= int(i[1]) < 480]

                for i in links: sources.append({'source': 'gvideo', 'quality': i[1], 'provider': 'Dizilab', 'url': i[0]})
            except:
                pass

            try:
                url = client.parseDOM(result, 'iframe', ret='src')
                url = [i for i in url if 'openload.' in i][0]
                sources.append({'source': 'openload.co', 'quality': client.file_quality_openload(url)['quality'], 'provider': 'Dizilab', 'url': url})
            except:
                pass

            return sources

        except:
            return sources


    def resolve(self, url):
        try:
            if 'openload' in url: return resolvers.request(url)
            if url.startswith('stack://'): return url

            url = client.request(url, output='geturl')
            if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            else: url = url.replace('https://', 'http://')
            return url
        except:
            return

