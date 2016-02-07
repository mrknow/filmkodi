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


import re,urllib,urllib2,urlparse

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://watchseries.ag'
        self.link_1 = 'http://watchseries.ag'
        self.link_2 = 'http://translate.googleusercontent.com/translate_c?anno=2&hl=en&sl=mt&tl=en&u=http://watchseries.ag'
        self.link_3 = 'https://watchseries.unblocked.pw'
        self.search_link = '/AdvancedSearch/%s-%s/by_popularity/%s'
        self.episode_link = '/episode/%s_s%s_e%s.html'
        self.headers = {}


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            query = self.search_link % (str(int(year)-1), str(int(year)+1), urllib.quote_plus(tvshowtitle))

            result = ''
            links = [self.link_1, self.link_2, self.link_3]
            for base_link in links:
                result = client.source(urlparse.urljoin(base_link, query), headers=self.headers)
                if 'episode-summary' in str(result): break

            result = result.decode('iso-8859-1').encode('utf-8')
            result = client.parseDOM(result, 'div', attrs = {'class': 'episode-summary'})[0]
            result = client.parseDOM(result, 'tr')

            tvshowtitle = cleantitle.tv(tvshowtitle)
            years = ['(%s)' % str(year), '(%s)' % str(int(year)+1), '(%s)' % str(int(year)-1)]
            result = [(re.compile('href=[\'|\"|\s|\<]*(.+?)[\'|\"|\s|\>]').findall(i)[0], client.parseDOM(i, 'a')[-1]) for i in result]
            result = [(i[0], re.sub('<.+?>|</.+?>','', i[1])) for i in result]
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

        url = url.rsplit('/', 1)[-1]
        url = self.episode_link % (url, season, episode)
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        return url


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            url = url.replace('/json/', '/')

            result = ''
            links = [self.link_1, self.link_2, self.link_3]
            for base_link in links:
                result = client.source(urlparse.urljoin(base_link, url), headers=self.headers)
                if 'lang_1' in str(result): break

            result = result.replace('\n','')
            result = result.decode('iso-8859-1').encode('utf-8')
            result = client.parseDOM(result, 'div', attrs = {'id': 'lang_1'})[0]

            links = re.compile('href=[\'|\"|\s|\<]*(.+?)[\'|\"|\s|\>].+?title=[\'|\"|\s|\<]*(.+?)[\'|\"|\s|\>]').findall(result)
            links = [x for y,x in enumerate(links) if x not in links[:y]]

            for i in links:
                try:
                    host = i[1]
                    host = host.split('.', 1)[0]
                    host = host.strip().lower()
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    url = i[0]
                    url = client.replaceHTMLCodes(url)
                    try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
                    except: pass
                    if not url.startswith('http'): url = urlparse.urljoin(self.base_link, url)
                    if not '/cale/' in url: raise Exception()
                    url = url.encode('utf-8')

                    sources.append({'source': host, 'quality': 'SD', 'provider': 'Watchseries', 'url': url})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = url.replace('/json/', '/')
            url = urlparse.urlparse(url).path

            class NoRedirection(urllib2.HTTPErrorProcessor):
                def http_response(self, request, response):
                    return response

            result = ''
            links = [self.link_1, self.link_2, self.link_3]
            for base_link in links:
                try:
                    opener = urllib2.build_opener(NoRedirection)
                    opener.addheaders = [('User-Agent', 'Apple-iPhone')]
                    opener.addheaders = [('Referer', base_link + url)]
                    response = opener.open(base_link + url)
                    result = response.read()
                    response.close()
                except:
                    result = ''
                if 'myButton' in result: break

            url = re.compile('class=[\'|\"]*myButton.+?href=[\'|\"|\s|\<]*(.+?)[\'|\"|\s|\>]').findall(result)[0]
            url = client.replaceHTMLCodes(url)
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
            except: pass
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['url'][0]
            except: pass

            url = resolvers.request(url)
            return url
        except:
            return

