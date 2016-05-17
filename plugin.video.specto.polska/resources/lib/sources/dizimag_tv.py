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
from resources.lib.libraries import control
from resources.lib.libraries import cloudflare



class source:
    def __init__(self):
        self.base_link = 'http://dizimag.co'
        self.headers = {'X-Requested-With' : 'XMLHttpRequest'}


    def dizimag_shows(self):
        try:
            result = cloudflare.source(self.base_link)

            result = client.parseDOM(result, 'div', attrs = {'id': 'fil'})[0]
            result = zip(client.parseDOM(result, 'a', ret='href'), client.parseDOM(result, 'a'))
            result = [(re.sub('http.+?//.+?/','/', i[0]), cleantitle.tv(i[1])) for i in result]

            return result
        except:
            return


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            result = cache.get(self.dizimag_shows, 72)

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

            result = client.source(url)
            result = client.parseDOM(result, 'a', ret='href')
            result = [i for i in result if '/%01d-sezon-%01d-bolum-' % (int(season), int(episode)) in i][0]

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
            result = re.compile('<script[^>]*>(.*?)</script>', re.DOTALL).findall(result)
            result = [re.compile("var\s+kaynaklar.*?url\s*:\s*\"([^\"]+)\"\s*,\s*data\s*:\s*'([^']+)").findall(i.replace('\n', '')) for i in result]
            result = [i[0] for i in result if len(i) > 0][0]

            url = urlparse.urljoin(self.base_link, result[0])
            post = result[1]

            result = client.source(url, post=post, headers=self.headers)
            result = re.compile('"videolink\d*"\s*:\s*"([^"]+)","videokalite\d*"\s*:\s*"?(\d+)p?').findall(result)
            result = [(i[0].replace('\\/', '/'), i[1])  for i in result]

            try: 
                url = [i for i in result if not 'google' in i[0]]
                url = [('%s|User-Agent=%s&Referer=%s' % (i[0].decode('unicode_escape'), urllib.quote_plus(client.agent()), urllib.quote_plus(sources_url)), i[1]) for i in url]

                try: sources.append({'source': 'Dizimag', 'quality': '1080p', 'provider': 'Dizimag', 'url': [i[0] for i in url if i[1] == '1080'][0]})
                except: pass
                try: sources.append({'source': 'Dizimag', 'quality': 'HD', 'provider': 'Dizimag', 'url': [i[0] for i in url if i[1] == '720'][0]})
                except: pass
                try: sources.append({'source': 'Dizimag', 'quality': 'SD', 'provider': 'Dizimag', 'url': [i[0] for i in url if i[1] == '480'][0]})
                except: sources.append({'source': 'Dizimag', 'quality': 'SD', 'provider': 'Dizimag', 'url': [i[0] for i in url if i[1] == '360'][0]})
            except:
                pass

            try: 
                url = [i for i in result if 'google' in i[0]]

                try: sources.append({'source': 'GVideo', 'quality': '1080p', 'provider': 'Dizimag', 'url': [i[0] for i in url if i[1] == '1080'][0]})
                except: pass
                try: sources.append({'source': 'GVideo', 'quality': 'HD', 'provider': 'Dizimag', 'url': [i[0] for i in url if i[1] == '720'][0]})
                except: pass
                try: sources.append({'source': 'GVideo', 'quality': 'SD', 'provider': 'Dizimag', 'url': [i[0] for i in url if i[1] == '480'][0]})
                except: sources.append({'source': 'GVideo', 'quality': 'SD', 'provider': 'Dizimag', 'url': [i[0] for i in url if i[1] == '360'][0]})
            except:
                pass

            return sources
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


