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
from resources.lib.libraries import cache
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://www.dizibox.com'


    def dizibox_shows(self):
        try:
            result = client.source(self.base_link)

            result = client.parseDOM(result, 'input', {'id': 'filterAllCategories'})[0]
            result = client.parseDOM(result, 'li')
            result = zip(client.parseDOM(result, 'a', ret='href'), client.parseDOM(result, 'a'))
            result = [(re.sub('http.+?//.+?/','/', i[0]), cleantitle.tv(i[1])) for i in result]

            return result
        except:
            return


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            result = cache.get(self.dizibox_shows, 72)

            tvshowtitle = cleantitle.tv(tvshowtitle)

            result = [i[0] for i in result if tvshowtitle == i[1]][0]

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

            url = urlparse.urljoin(self.base_link, url)

            season, episode = '%01d' % int(season), '%01d' % int(episode)

            result = client.source(url)

            if not season == '1':
                url = client.parseDOM(result, 'a', ret='href', attrs = {'class': 'season-.+?'})
                url = [i for i in url if '/%s-sezon-' % season in i][0]
                result = client.source(url)

            result = client.parseDOM(result, 'a', ret='href')
            result = [i for i in result if '%s-sezon-%s-bolum-' % (season, episode) in i][0]

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

            sources_url = urlparse.urljoin(self.base_link, url)

            result = client.source(sources_url, close=False)
            result = re.sub(r'[^\x00-\x7F]+','', result)

            result = re.compile('(<option.*?</option>)', re.DOTALL).findall(result)
            result = [(client.parseDOM(i, 'option', ret='href'), client.parseDOM(i, 'option', ret='value'), client.parseDOM(i, 'option')) for i in result]
            result = [i[0] + i[1] for i in result if len(i[2]) > 0 and i[2][0] == 'Altyazsz'][0][0]

            url = urlparse.urljoin(self.base_link, result)

            result = client.source(url, close=False)

            url = client.parseDOM(result, 'span', attrs = {'class': 'object-wrapper'})[0]
            url = client.parseDOM(url, 'iframe', ret='src')[0]
            url = client.replaceHTMLCodes(url)

            result = client.source(url, close=False)

            try:
                r = re.compile('"?file"?\s*:\s*"([^"]+)"\s*,\s*"?label"?\s*:\s*"(\d+)p?"').findall(result)
                if r == []: raise Exception()
                r = [(i[0].replace('\\/', '/').replace('\\&', '&').decode('unicode_escape'), int(i[1])) for i in r]

                u = [('%s|User-Agent=%s&Referer=%s' % (i[0], urllib.quote_plus(client.agent()), urllib.quote_plus(sources_url)), i[1], 'Dizibox') for i in r if not 'google' in i[0]]
                u += [(i[0], i[1], 'GVideo') for i in r if 'google' in i[0]]

                try: sources.append({'source': [i[2] for i in u if i[1] >= 1080][0], 'quality': '1080p', 'provider': 'Dizibox', 'url': [i[0] for i in u if i[1] >= 1080][0]})
                except: pass
                try: sources.append({'source': [i[2] for i in u if 720 <= i[1] < 1080][0], 'quality': 'HD', 'provider': 'Dizibox', 'url': [i[0] for i in u if 720 <= i[1] < 1080][0]})
                except: pass
                try: sources.append({'source': [i[2] for i in u if i[1] < 720][0], 'quality': 'SD', 'provider': 'Dizibox', 'url': [i[0] for i in u if i[1] < 720][0]})
                except: pass

                return sources
            except:
                pass

            try:
                if '.dizibox.' in url: url = re.compile('location\.href\s*=\s*"(.+?)"').findall(result)[0]

                host = urlparse.urlparse(url).netloc
                host = host.replace('mail.ru', 'mailru.ru').rsplit('.', 1)[0].split('.')[-1].lower()

                strm = resolvers.request(url)
                if strm == url or strm == None: raise Exception()

                if type(strm) == list:
                    for i in strm: sources.append({'source': host, 'quality': i['quality'], 'provider': 'Dizibox', 'url': i['url']})
                else:
                    sources.append({'source': host, 'quality': 'HD', 'provider': 'Dizibox', 'url': strm})

                return sources
            except:
                pass

        except:
            return sources


    def resolve(self, url):
        try:
            if not 'google' in url: return url
            if url.startswith('stack://'): return url

            url = client.request(url, output='geturl')
            if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            else: url = url.replace('https://', 'http://')
            return url
        except:
            return


