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
        self.base_link = 'http://movie.pubfilmno1.com'
        self.moviesearch_link = '/feeds/posts/summary?alt=json&q=%s&max-results=10&callback=showResult'
        self.tvsearch_link = '/feeds/posts/summary?alt=json&q=season&max-results=3000&callback=showResult'


    def get_movie(self, imdb, title, year):
        try:
            query = self.moviesearch_link % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query)
            result = re.compile('showResult\((.*)\)').findall(result)[0]
            result = json.loads(result)
            result = result['feed']['entry']

            title = cleantitle.get(title)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = [i for i in result if 'movies' in [x['term'].lower() for x in i['category']]]
            result = [[x for x in i['link'] if x['rel'] == 'alternate' and x['type'] == 'text/html'][0] for i in result]
            result = [(i['href'], i['title']) for i in result]
            result = [(i[0], re.compile('(.+?) (\d{4})(.+)').findall(i[1])) for i in result]
            result = [(i[0], i[1][0][0], i[1][0][1], i[1][0][2]) for i in result if len(i[1]) > 0]
            result = [(i[0], i[1], i[2]) for i in result if not 'TS' in i[3] and not 'CAM' in i[3]]
            result = [i for i in result if title == cleantitle.get(i[1])]
            result = [i[0] for i in result if any(x in i[2] for x in years)][0]

            url = urlparse.urljoin(self.base_link, result)
            url = urlparse.urlparse(url).path
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

            content = re.compile('(.+?)\?episode=\d*$').findall(url)
            content = 'movie' if len(content) == 0 else 'episode'

            try: url, episode = re.compile('(.+?)\?episode=(\d*)$').findall(url)[0]
            except: pass

            result = client.source(url)

            if content == 'movie':
                url = client.parseDOM(result, 'iframe', ret='src')[0]
            else:
                url = zip(client.parseDOM(result, 'a', ret='href', attrs = {'target': 'player_iframe'}), client.parseDOM(result, 'a', attrs = {'target': 'player_iframe'}))
                url = [(i[0], re.compile('(\d+)').findall(i[1])) for i in url]
                url = [(i[0], i[1][-1]) for i in url if len(i[1]) > 0]
                url = [i[0] for i in url if i[1] == '%01d' % int(episode)][0]

            url = client.replaceHTMLCodes(url)

            result = client.source(url)

            headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': url}
            url = 'http://player.pubfilm.com/smplayer/plugins/gkphp/plugins/gkpluginsphp.php'
            post = re.compile('link\s*:\s*"([^"]+)').findall(result)[0]
            post = urllib.urlencode({'link': post})

            result = client.source(url, post=post, headers=headers)

            r = re.compile('"?link"?\s*:\s*"([^"]+)"\s*,\s*"?label"?\s*:\s*"(\d+)p?"').findall(result)
            if not r: r = [(i, 480) for i in re.compile('"?link"?\s*:\s*"([^"]+)').findall(result)]
            r = [(i[0].replace('\\/', '/'), i[1]) for i in r]

            links = [(i[0], '1080p') for i in r if int(i[1]) >= 1080]
            links += [(i[0], 'HD') for i in r if 720 <= int(i[1]) < 1080]
            links += [(i[0], 'SD') for i in r if 480 <= int(i[1]) < 720]
            if not 'SD' in [i[1] for i in links]: links += [(i[0], 'SD') for i in r if 360 <= int(i[1]) < 480]

            for i in links: sources.append({'source': 'gvideo', 'quality': i[1], 'provider': 'Pubfilm', 'url': i[0], 'direct': True, 'debridonly': False})

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