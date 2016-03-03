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
        self.base_link = 'http://onlinemovies.ws'
        self.search_link = '/?s=%s'


    def get_movie(self, imdb, title, year):
        try:
            url = title.replace('\'', '')
            url = re.sub(r'[^a-zA-Z0-9\s]+', ' ', url).lower().strip()
            url = re.sub('\s\s+' , ' ', url)
            url = url.replace(' ' , '-')
            url = '/%s-%s/' % (url, year)

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

            quality = re.compile('>Quality:(.+?)\n').findall(result)[0]

            if 'CAM' in quality or 'TS' in quality: quality = 'CAM'
            elif 'SCREENER' in quality: quality = 'SCR'
            else: quality = 'HD'

            try:
                url = client.parseDOM(result, 'iframe', ret='src')
                url = [i for i in url if 'videomega' in i.lower()][0]
                url = re.compile('[ref|hashkey]=([\w]+)').findall(url)
                url = 'http://videomega.tv/cdn.php?ref=%s' % url[0]
                url = resolvers.request(url)
                if url == None: raise Exception()
                sources.append({'source': 'Videomega', 'quality': quality, 'provider': 'Onlinemoviesv2', 'url': url})
            except:
                pass

            try:
                url = client.parseDOM(result, 'iframe', ret='src')
                url = [i for i in url if 'openload' in i.lower()][0]
                if openload.check(url) == False: raise Exception()
                sources.append({'source': 'Openload', 'quality': quality, 'provider': 'Onlinemoviesv2', 'url': url})
            except:
                pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            #url = resolvers.request(url)
            return url
        except:
            return


