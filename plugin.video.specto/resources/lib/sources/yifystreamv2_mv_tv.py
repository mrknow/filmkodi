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


import re,urllib,urlparse,base64,random

from resources.lib.libraries import cleantitle
from resources.lib.libraries import cloudflare
from resources.lib.libraries import client
from resources.lib.resolvers import openload
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://yss.rocks/'
        self.tvbase_link = 'http://tv.yify-streaming.com'
        self.search_link = '/?s='


    def __proxy(self):
         return random.choice([
         'http://unblock-proxy.com/browse.php?b=20&u=',
         'http://quickprox.com/browse.php?b=20&u=',
         'https://zendproxy.com/bb.php?b=20&u=',
         'http://dontfilter.us/browse.php?b=20&u=',
         'http://www.youtubeunblockproxy.com/browse.php?b=20&u=',
         'http://www.unblockmyweb.com/browse.php?b=20&u=',
         'http://www.proxy2014.net/index.php?hl=3e5&q=',
         'http://www.unblockyoutubefree.net/browse.php?b=20&u=',
         'http://www.freeopenproxy.com/browse.php?b=20&u=',
         'http://www.justproxy.co.uk/index.php?hl=2e5&q=',
         'https://hidemytraxproxy.ca/browse.php?b=20&u=',
         'http://www.greatestfreeproxy.com/browse.php?b=20&u=',
         'http://www.webproxyfree.net/browse.php?b=20&u=',
         'https://losangeles-s02-i01.cg-dialup.net/go/browse.php?b=20&u=',
         'https://frankfurt-s02-i01.cg-dialup.net/go/browse.php?b=20&u=',
         'https://www.4proxy.us/index.php?hl=2e5&q=',
         'https://www.3proxy.us/index.php?hl=2e5&q=',
         'http://www.usproxy24.com/id.php?b=20&u=',
         'http://www.fakeip.org/index.php?hl=3c0&q=',
         'http://www.gumm.org/index.php?hl=2e5&q=',
         'http://free-proxyserver.com/browse.php?b=20&u='
         ])


    def get_movie(self, imdb, title, year):

        try:
            query = urlparse.urljoin(self.base_link, self.search_link + urllib.quote_plus(title))

            result = client.source(query)

            #if result == None: result = client.source(self.__proxy() + urllib.quote_plus(query))

            r = client.parseDOM(result, 'li', attrs = {'class': 'first element.+?'})
            r += client.parseDOM(result, 'li', attrs = {'class': 'element.+?'})
            r += client.parseDOM(result, 'header', attrs = {'class': 'entry-heade.+?'})

            title = cleantitle.movie(title)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a')) for i in r]
            result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [(i[0], re.compile('(.+?)(\.|\(|\[|\s)(\d{4})').findall(i[1])) for i in result]
            result = [(i[0], i[1][0][0], i[1][0][-1]) for i in result if len(i[1]) > 0]
            result = [i for i in result if title == cleantitle.movie(i[1])]
            result = [i[0] for i in result if any(x in i[2] for x in years)][0]

            url = client.replaceHTMLCodes(result)
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
            except: pass
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['q'][0]
            except: pass
            url = urlparse.urlparse(url).path
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_show(self, imdb, tvdb, tvshowtitle, year):

        try:
            url = tvshowtitle
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):

        try:
            if url == None: return

            query = '%s S%02dE%02d' % (url, int(season), int(episode))
            query = urlparse.urljoin(self.tvbase_link, self.search_link + urllib.quote_plus(query))

            result = client.source(query)

            #if result == None: result = client.source(self.__proxy() + urllib.quote_plus(query))

            r = client.parseDOM(result, 'li', attrs = {'class': 'first element.+?'})
            r += client.parseDOM(result, 'li', attrs = {'class': 'element.+?'})
            r += client.parseDOM(result, 'header', attrs = {'class': 'entry-heade.+?'})

            tvshowtitle = cleantitle.tv(url)
            hdlr = 'S%02dE%02d' % (int(season), int(episode))

            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a')) for i in r]
            result = [(i[0][0], i[1][0].upper()) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [(i[0], re.compile('(.+?) (S\d+E\d+)').findall(i[1])) for i in result]
            result = [(i[0], i[1][0][0], i[1][0][-1]) for i in result if len(i[1]) > 0]
            result = [i for i in result if tvshowtitle == cleantitle.tv(i[1])]
            result = [i[0] for i in result if hdlr == i[2]][0]

            url = client.replaceHTMLCodes(result)
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
            except: pass
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['q'][0]
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

            content = re.compile('(s\d+e\d+)').findall(url)

            if len(content) == 0: url = urlparse.urljoin(self.base_link, url)
            else: url = urlparse.urljoin(self.tvbase_link, url)

            result = client.source(url)

            #if result == None: result = client.source(self.__proxy() + urllib.quote_plus(url))

            result = client.parseDOM(result, 'iframe', ret='src')

            url = [i for i in result if 'openload.' in i][0]
            url = client.replaceHTMLCodes(url)
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
            except: pass
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['q'][0]
            except: pass

            if openload.check(url) == False: raise Exception()
            sources.append({'source': 'Openload', 'quality': 'HD', 'provider': 'YIFYstreamv2', 'url': url})

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = resolvers.request(url)
            return url
        except:
            return


