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
from resources.lib.libraries import pyaes
from resources.lib.libraries import cloudflare
from resources.lib.libraries import client
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://tunemovie.is'
        self.search_link = '/search/%s.html'


    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query)
            result = client.parseDOM(result, 'div', attrs = {'id': 'post-.+?'})

            title = cleantitle.movie(title)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0], client.parseDOM(i, 'div', attrs = {'class': 'status status-year'}), client.parseDOM(i, 'div', attrs = {'class': 'mark-8'})) for i in result]
            result = [(i[0], i[1], i[2][0], i[3]) for i in result if len(i[2]) > 0]
            result = [(i[0], i[1], i[2], i[3], re.compile('Season (\d*)$').findall(i[1])) for i in result]
            result = [(i[0], i[1], i[2], i[3]) for i in result if len(i[4]) == 0]
            result = [(i[0], i[1], i[2]) for i in result if len(i[3]) == 0]
            result = [i for i in result if title == cleantitle.movie(i[1])]
            result = [i[0] for i in result if any(x in i[2] for x in years)][0]

            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            url = '%s (%s)' % (tvshowtitle, year)
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        try:
            tvshowtitle, year = re.compile('(.+?) [(](\d{4})[)]$').findall(url)[0]

            query = self.search_link % (urllib.quote_plus(tvshowtitle))
            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query)
            result = client.parseDOM(result, 'div', attrs = {'id': 'post-.+?'})

            tvshowtitle = cleantitle.tv(tvshowtitle)
            season = '%01d' % int(season)
            episode = '%01d' % int(episode)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0], client.parseDOM(i, 'div', attrs = {'class': 'status status-year'})) for i in result]
            result = [x for y,x in enumerate(result) if x not in result[:y]]
            result = [(i[0], i[1], i[2][0]) for i in result if len(i[2]) > 0]
            result = [(i[0], re.compile('(.+?) Season (\d*)$').findall(i[1]), i[2]) for i in result]
            result = [(i[0], i[1][0][0], i[1][0][1], i[2]) for i in result if len(i[1]) > 0]
            result = [i for i in result if tvshowtitle == cleantitle.tv(i[1])]
            result = [i for i in result if season == i[2]]
            result = [(i[0], i[1], str(int(i[3]) - int(i[2]) + 1)) for i in result]
            result = [i[0] for i in result if any(x in i[2] for x in years)][0]

            url = urlparse.urljoin(self.base_link, result)

            result = client.source(url)
            result = client.parseDOM(result, 'div', attrs = {'id': 'episode_show'})[0]
            result = re.compile('(<a.+?</a>)').findall(result)
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a')[0]) for i in result]
            result = [i[0] for i in result if episode == i[1]][0]

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

            links = client.parseDOM(result, 'div', attrs = {'class': 'server_line.+?'})

            for i in links:
                try:
                    host = client.parseDOM(i, 'p', attrs = {'class': 'server_servername'})[0]
                    host = re.compile('Server (.+?)$').findall(host)[0]
                    host = host.strip().lower()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    url = client.parseDOM(i, 'a', ret='href')[0]
                    url = client.replaceHTMLCodes(url)
                    url = urlparse.urljoin(self.base_link, url)
                    url = url.encode('utf-8')

                    if 'google' in host:
                        url = self.__resolve(client.source(url))
                        for u in url: sources.append({'source': 'GVideo', 'quality': u['quality'], 'provider': 'Tunemovie', 'url': u['url']})

                    elif host in hostDict:
                        raise Exception()
                        sources.append({'source': host, 'quality': 'SD', 'provider': 'Tunemovie', 'url': url})

                except:
                    pass

            return sources
        except:
            return sources


    def __resolve(self, result):
        try:
            result = client.parseDOM(result, 'div', attrs = {'id': 'player'})[0]

            try: url = client.parseDOM(result, 'iframe', ret='src')[0]
            except: pass
            try: url = base64.b64decode(re.compile('decode\("(.+?)"').findall(result)[0])
            except: pass

            if 'proxy.link=tunemovie' in url:
                url = re.compile('proxy[.]link=tunemovie[*]([^&]+)').findall(url)[-1]

                key = base64.b64decode('Q05WTmhPSjlXM1BmeFd0UEtiOGg=')
                decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationECB(key + (24 - len(key)) * '\0'))
                url = url.decode('hex')
                url = decrypter.feed(url) + decrypter.feed()

            url = resolvers.request(url)
            return url
        except:
            return


    def resolve(self, url):
        try:
            if urlparse.urlparse(url).netloc in self.base_link:
                return self.__resolve(client.request(url))

            if url.startswith('stack://'): return url

            url = client.request(url, output='geturl')
            if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            else: url = url.replace('https://', 'http://')
            return url
        except:
            return

