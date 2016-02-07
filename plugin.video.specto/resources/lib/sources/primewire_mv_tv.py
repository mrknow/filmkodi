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

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://www.primewire.ag'
        self.key_link = '/index.php?search'
        self.link_1 = 'http://www.primewire.ag'
        self.link_2 = 'http://www.primewire.org'
        self.link_3 = 'http://www.primewire.is'
        self.moviesearch_link = '/index.php?search_keywords=%s&key=%s&search_section=1'
        self.tvsearch_link = '/index.php?search_keywords=%s&key=%s&search_section=2'
        self.headers = {'Connection' : 'keep-alive'}


    def get_movie(self, imdb, title, year):
        try:
            result = ''
            links = [self.link_1, self.link_2, self.link_3]
            for base_link in links:
                result = client.source(urlparse.urljoin(base_link, self.key_link), headers=self.headers)
                if 'searchform' in str(result): break

            key = client.parseDOM(result, 'input', ret='value', attrs = {'name': 'key'})[0]
            query = self.moviesearch_link % (urllib.quote_plus(re.sub('\'', '', title)), key)

            result = client.source(urlparse.urljoin(base_link, query), headers=self.headers)
            result = result.decode('iso-8859-1').encode('utf-8')
            result = client.parseDOM(result, 'div', attrs = {'class': 'index_item.+?'})

            title = 'watch' + cleantitle.movie(title)
            years = ['(%s)' % str(year), '(%s)' % str(int(year)+1), '(%s)' % str(int(year)-1)]
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0]) for i in result]
            result = [i for i in result if any(x in i[1] for x in years)]

            result = [(client.replaceHTMLCodes(i[0]), i[1]) for i in result]
            try: result = [(urlparse.parse_qs(urlparse.urlparse(i[0]).query)['u'][0], i[1]) for i in result]
            except: pass
            result = [(urlparse.urlparse(i[0]).path, i[1]) for i in result]

            match = [i[0] for i in result if title == cleantitle.movie(i[1])]

            match2 = [i[0] for i in result]
            match2 = [x for y,x in enumerate(match2) if x not in match2[:y]]
            if match2 == []: return

            for i in match2[:5]:
                try:
                    if len(match) > 0:
                        url = match[0]
                        break
                    result = client.source(base_link + i, headers=self.headers)
                    if str(imdb) in str(result):
                        url = i
                        break
                except:
                    pass

            url = url.encode('utf-8')
            return url
        except:
            return


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            result = ''
            links = [self.link_1, self.link_2, self.link_3]
            for base_link in links:
                result = client.source(urlparse.urljoin(base_link, self.key_link), headers=self.headers)
                if 'searchform' in str(result): break

            key = client.parseDOM(result, 'input', ret='value', attrs = {'name': 'key'})[0]
            query = self.tvsearch_link % (urllib.quote_plus(re.sub('\'', '', tvshowtitle)), key)

            result = client.source(urlparse.urljoin(base_link, query), headers=self.headers)
            result = result.decode('iso-8859-1').encode('utf-8')
            result = client.parseDOM(result, 'div', attrs = {'class': 'index_item.+?'})

            tvshowtitle = 'watch' + cleantitle.tv(tvshowtitle)
            years = ['(%s)' % str(year), '(%s)' % str(int(year)+1), '(%s)' % str(int(year)-1)]
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0]) for i in result]
            result = [i for i in result if any(x in i[1] for x in years)]

            result = [(client.replaceHTMLCodes(i[0]), i[1]) for i in result]
            try: result = [(urlparse.parse_qs(urlparse.urlparse(i[0]).query)['u'][0], i[1]) for i in result]
            except: pass
            result = [(urlparse.urlparse(i[0]).path, i[1]) for i in result]

            match = [i[0] for i in result if tvshowtitle == cleantitle.tv(i[1])]

            match2 = [i[0] for i in result]
            match2 = [x for y,x in enumerate(match2) if x not in match2[:y]]
            if match2 == []: return

            for i in match2[:5]:
                try:
                    if len(match) > 0:
                        url = match[0]
                        break
                    result = client.source(base_link + i, headers=self.headers)
                    if str(imdb) in str(result):
                        url = i
                        break
                except:
                    pass

            url = url.encode('utf-8')
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        if url == None: return

        url = url.replace('/watch-','/tv-')
        url += '/season-%01d-episode-%01d' % (int(season), int(episode))
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        return url


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            result = ''
            links = [self.link_1, self.link_2, self.link_3]
            for base_link in links:
                result = client.source(urlparse.urljoin(base_link, url), headers=self.headers)
                if 'choose_tabs' in str(result): break

            result = result.decode('iso-8859-1').encode('utf-8')
            links = client.parseDOM(result, 'tbody')

            for i in links:
                try:
                    u = client.parseDOM(i, 'a', ret='href')[0]
                    u = client.replaceHTMLCodes(u)
                    try: u = urlparse.parse_qs(urlparse.urlparse(u).query)['u'][0]
                    except: pass

                    host = urlparse.parse_qs(urlparse.urlparse(u).query)['domain'][0]
                    host = base64.urlsafe_b64decode(host.encode('utf-8'))
                    host = host.rsplit('.', 1)[0]
                    host = host.strip().lower()
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    url = urlparse.parse_qs(urlparse.urlparse(u).query)['url'][0]
                    url = base64.urlsafe_b64decode(url.encode('utf-8'))
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    quality = client.parseDOM(i, 'span', ret='class')[0]
                    if quality == 'quality_cam' or quality == 'quality_ts': quality = 'CAM'
                    elif quality == 'quality_dvd': quality = 'SD'
                    else:  raise Exception()

                    sources.append({'source': host, 'quality': quality, 'provider': 'Primewire', 'url': url})
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

