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

import re,urllib,urlparse,json

from resources.lib.libraries import cleantitle
from resources.lib.libraries import cloudflare
from resources.lib.libraries import client
from resources.lib.libraries import client2
from resources.lib.libraries import cache
from resources.lib.libraries import control



class source:
    def __init__(self):
        self.base_link = 'http://sezonlukdizi.com'
        self.search_link = '/js/dizi.js'
        self.video_link = '/ajax/dataEmbed.asp'

    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            result = cache.get(self.sezonlukdizi_tvcache, 120)

            tvshowtitle = cleantitle.get(tvshowtitle)

            result = [i[0] for i in result if tvshowtitle == i[1]][0]

            url = urlparse.urljoin(self.base_link, result)
            url = urlparse.urlparse(url).path
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def sezonlukdizi_tvcache(self):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link)

            result =  client2.http_get(url)
            result = re.compile('{(.+?)}').findall(result)

            result = [(re.findall('u\s*:\s*(?:\'|\")(.+?)(?:\'|\")', i), re.findall('d\s*:\s*(?:\'|\")(.+?)(?:\'|\")', i)) for i in result]
            result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [(re.compile('/diziler(/.+?)(?://|\.|$)').findall(i[0]), re.sub('&#\d*;','', i[1])) for i in result]
            result = [(i[0][0] + '/', cleantitle.get(i[1])) for i in result if len(i[0]) > 0]

            return result
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, premiered, season, episode):
        if url == None: return
        url = '%s%01d-sezon-%01d-bolum.html' % (url.replace('.html', ''), int(season), int(episode))
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        return url


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            result = client2.http_get(url)
            result = re.sub(r'[^\x00-\x7F]+', ' ', result)

            pages = []
            try:
                r = client.parseDOM(result, 'div', attrs = {'id': 'embed'})[0]
                pages.append(client.parseDOM(r, 'iframe', ret='src')[0])
            except:
                pass
            try:
                r = client.parseDOM(result, 'div', attrs = {'id': 'playerMenu'})[0]
                r = client.parseDOM(r, 'div', ret='data-id', attrs = {'class': 'item'})[0]
                r = cloudflare.source(urlparse.urljoin(self.base_link, self.video_link), post=urllib.urlencode( {'id': r} ))
                pages.append(client.parseDOM(r, 'iframe', ret='src')[0])
            except:
                pass

            for page in pages:
                try:
                    result = client2.http_get(page)

                    captions = re.search('kind\s*:\s*(?:\'|\")captions(?:\'|\")', result)
                    if not captions: raise Exception()

                    result = re.compile('"?file"?\s*:\s*"([^"]+)"\s*,\s*"?label"?\s*:\s*"(\d+)p?[^"]*"').findall(result)

                    links = [(i[0], '1080p') for i in result if int(i[1]) >= 1080]
                    links += [(i[0], 'HD') for i in result if 720 <= int(i[1]) < 1080]
                    links += [(i[0], 'SD') for i in result if 480 <= int(i[1]) < 720]

                    for i in links: sources.append({'source': 'gvideo', 'quality': i[1], 'provider': 'Sezonlukdizi', 'url': i[0]})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            #url = client.request(url, output='geturl')
            if 'sezonlukdizi.com' in url: url = client2.http_get(url,allow_redirect=False)
            control.log('############ SEZONLUKIDZ res-0 %s' % url)
            url = client2.http_get(url,allow_redirect=False)
            control.log('############ SEZONLUKIDZ res-1 %s' % url)
            if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            #else: url = url.replace('https://', 'http://')
            return url
        except:
            return


