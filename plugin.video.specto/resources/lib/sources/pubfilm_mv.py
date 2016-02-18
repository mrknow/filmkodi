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
from resources.lib.libraries import client


class source:
    def __init__(self):
        self.base_link = 'http://www.pubfilm.com/'
        #self.base_link = client.source(self.base_link, output='geturl')
        self.search_link = '/feeds/posts/summary?alt=json&q=%s&max-results=100&callback=showResult'


    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query)
            result = re.compile('showResult\((.*)\)').findall(result)[0]
            result = json.loads(result)
            result = result['feed']['entry']

            title = cleantitle.movie(title)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = [i for i in result if 'movies' in [x['term'].lower() for x in i['category']]]
            result = [[x for x in i['link'] if x['rel'] == 'alternate' and x['type'] == 'text/html'][0] for i in result]
            result = [(i['href'], i['title']) for i in result]
            result = [(i[0], re.compile('(.+?) (\d{4})(.+)').findall(i[1])) for i in result]
            result = [(i[0], i[1][0][0], i[1][0][1], i[1][0][2]) for i in result if len(i[1]) > 0]
            result = [(i[0], i[1], i[2]) for i in result if not 'TS' in i[3] and not 'CAM' in i[3]]
            result = [i for i in result if title == cleantitle.movie(i[1])]
            result = [i[0] for i in result if any(x in i[2] for x in years)][0]

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

            url = client.parseDOM(result, 'iframe', ret='src', attrs = {'allowfullscreen': '.+?'})
            url += client.parseDOM(result, 'a', ret='href', attrs = {'target': 'EZWebPlayer'})

            links = [x for y,x in enumerate(url) if x not in url[:y]]
            links = [client.replaceHTMLCodes(i) for i in links][:3]

            for u in links:
                try:
                    result = client.source(u)

                    try: sources.append({'source': 'GVideo', 'quality': '1080p', 'provider': 'Pubfilm', 'url': re.compile('file *: *"(.+?)"').findall([i for i in re.compile('({.+?})').findall(result) if '"1080p"' in i][0])[0]})
                    except: pass

                    try: sources.append({'source': 'GVideo', 'quality': 'HD', 'provider': 'Pubfilm', 'url': re.compile('file *: *"(.+?)"').findall([i for i in re.compile('({.+?})').findall(result) if '"720p"' in i][0])[0]})
                    except: pass

                    try: sources.append({'source': 'GVideo', 'quality': '1080p', 'provider': 'Pubfilm', 'url': client.parseDOM(result, 'source', ret='src', attrs = {'data-res': '1080P'})[0]})
                    except: pass

                    try: sources.append({'source': 'GVideo', 'quality': 'HD', 'provider': 'Pubfilm', 'url': client.parseDOM(result, 'source', ret='src', attrs = {'data-res': '720P'})[0]})
                    except: pass
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            if url.startswith('stack://'): return url

            url = client.request(url, output='geturl')
            if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            else: url = url.replace('https://', 'http://')
            return url
        except:
            return

