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
        self.base_link = 'http://watchseries-online.li'
        self.search_link = 'index'


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            tvshowtitle = cleantitle.tv(tvshowtitle)

            query = urlparse.urljoin(self.base_link, self.search_link)

            result = client.source(query)

            result = re.compile('(<li>.+?</li>)').findall(result)
            result = [re.compile('href="(.+?)">(.+?)<').findall(i) for i in result]
            result = [i[0] for i in result if len(i[0]) > 0]
            result = [i for i in result if tvshowtitle == cleantitle.tv(i[1])]
            result = [i[0] for i in result][0]

            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        try:
            if url == None: return

            year, month = re.compile('(\d{4})-(\d{2})').findall(date)[-1]
            if int(year) <= 2008: raise Exception()

            cat = urlparse.urljoin(self.base_link, url)
            cat = cat.split('category/', 1)[-1].rsplit('/')[0]


            url = urlparse.urljoin(self.base_link, '/episode/%s-s%02de%02d' % (cat, int(season), int(episode)))
            result = client.source(url, output='response', error=True)

            if '404' in result[0]:
                url = urlparse.urljoin(self.base_link, '/%s/%s/%s-s%02de%02d' % (year, month, cat, int(season), int(episode)))
                result = client.source(url, output='response', error=True)

            if '404' in result[0]:
                url = urlparse.urljoin(self.base_link, '/%s/%s/%s-%01dx%01d' % (year, month, cat, int(season), int(episode)))
                result = client.source(url, output='response', error=True)

            if '404' in result[0]: raise Exception()

            try: url = re.compile('//.+?(/.+)').findall(url)[0]
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
            links = client.parseDOM(result, 'td', attrs = {'class': 'even tdhost'})
            links += client.parseDOM(result, 'td', attrs = {'class': 'odd tdhost'})

            for i in links:
                try:
                    host = client.parseDOM(i, 'a')[0]
                    host = host.split('<', 1)[0]
                    host = host.rsplit('.', 1)[0].split('.', 1)[-1]
                    host = host.strip().lower()
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    url = client.parseDOM(i, 'a', ret='href')[0]
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    sources.append({'source': host, 'quality': 'SD', 'provider': 'WSOnline', 'url': url})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            result = client.request(url)

            try: url = client.parseDOM(result, 'a', ret='href', attrs = {'class': 'wsoButton'})[0]
            except: pass

            url = resolvers.request(url)
            return url
        except:
            return


