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


import re,urllib,urlparse,base64
from resources.lib.libraries import client
from resources.lib.libraries import client2
from resources.lib.libraries import control

from resources.lib.libraries import cache
from resources.lib.libraries import cleantitle

from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://onlinedizi.co'


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            result = cache.get(self.onlinedizi_tvcache, 120)

            tvshowtitle = cleantitle.get(tvshowtitle)

            result = [i[0] for i in result if tvshowtitle == i[1]][0]

            url = urlparse.urljoin(self.base_link, result)
            url = urlparse.urlparse(url).path
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def onlinedizi_tvcache(self):
        try:
            result = client2.http_get(self.base_link)
            result = client.parseDOM(result, 'ul', attrs = {'class': 'all-series-list.+?'})[0]
            result = client.parseDOM(result, 'li')
            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a')) for i in result]
            result = [(i[0][-1], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [(re.compile('http.+?//.+?/diziler(/.+?/)').findall(i[0]), re.sub('&#\d*;','', i[1])) for i in result]
            result = [(i[0][0], cleantitle.get(i[1])) for i in result if len(i[0]) > 0]

            return result
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, premiered, season, episode):
        if url == None: return

        url = '/%s-%01d-sezon-%01d-bolum/' % (url.replace('/', ''), int(season), int(episode))
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        return url


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)
            path = urlparse.urlparse(url).path

            result = client2.http_get(url)
            result = re.sub(r'[^\x00-\x7F]+','', result)
            result = client.parseDOM(result, 'li')
            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a')) for i in result]
            result = [i[0] for i in result if len(i[0]) > 0 and path in i[0][0] and len(i[1]) > 0 and 'Altyaz' in i[1][0]][0][0]

            url = urlparse.urljoin(self.base_link, result)

            result = client2.http_get(url)
            result = re.sub(r'[^\x00-\x7F]+','', result)
            result = client.parseDOM(result, 'div', attrs = {'class': 'video-player'})[0]
            result = client.parseDOM(result, 'iframe', ret='src')[-1]
            control.log('RRRR %s' % result)

            try:
                url = base64.b64decode(urlparse.parse_qs(urlparse.urlparse(result).query)['id'][0])
                if not url.startswith('http'): raise Exception()
            except:
                url = client2.http_get(result)
                url = urllib.unquote_plus(url.decode('string-escape'))

                frame = client.parseDOM(url, 'iframe', ret='src')
                control.log('RRRR frame %s' % frame)

                if len(frame) > 0:
                    url = [client2.http_get(frame[-1], allow_redirect = False)]
                else: url = re.compile('"(.+?)"').findall(url)
                url = [i for i in url if 'ok.ru' in i or 'vk.com' in i or 'openload.co' in i][0]

            try: url = 'http://ok.ru/video/%s' % urlparse.parse_qs(urlparse.urlparse(url).query)['mid'][0]
            except: pass

            if 'openload.co' in url: host = 'openload.co' ; direct = False ; url = [{'url': resolvers.request(url), 'quality': 'HD'}]
            elif 'ok.ru' in url: host = 'vk' ; direct = True ;url = [{'url': resolvers.request(url), 'quality': 'HD'}]
            elif 'vk.com' in url: host = 'vk' ; direct = True ; url = [{'url': resolvers.request(url), 'quality': 'HD'}]
            else: raise Exception()

            for i in url: sources.append({'source': host, 'quality': i['quality'], 'provider': 'Onlinedizi', 'url': i['url'], })


            return sources
        except:
            return sources


    def resolve(self, url):
        return url


