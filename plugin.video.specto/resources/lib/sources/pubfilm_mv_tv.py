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
from resources.lib.libraries import cache



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
            years = ['%s' % str(year)]

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

    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def pubfilm_tvcache(self):
        try:
            query = self.tvsearch_link
            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query)
            result = re.compile('showResult\((.*)\)').findall(result)[0]
            result = json.loads(result)
            result = result['feed']['entry']

            result = [i for i in result if 'series' in [x['term'].lower() for x in i['category']]]
            result = [[x for x in i['link'] if x['rel'] == 'alternate' and x['type'] == 'text/html'][0] for i in result]
            result = [(i['href'], i['title']) for i in result]
            result = [(i[0], re.compile('(.+?) \d{4}.+? Season (\d*) ').findall(i[1])) for i in result]
            result = [(i[0], i[1][0][0], i[1][0][1]) for i in result if len(i[1]) > 0]
            result = [(i[0], i[1], i[2]) for i in result if len(i[1]) > 0]
            result = [(re.sub('http.+?//.+?/', '/', i[0]), re.sub('&#\d*;', '', i[1]), i[2]) for i in result]
            result = [(i[0], cleantitle.get(i[1]), i[2]) for i in result]

            return result
        except:
            return

    def get_episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            tvshowtitle = cleantitle.get(data['tvshowtitle'])
            year = re.findall('(\d{4})', premiered)[0]
            season = '%01d' % int(season)
            episode = '%01d' % int(episode)

            result = cache.get(self.pubfilm_tvcache, 120)

            result = [i for i in result if tvshowtitle == i[1]]
            result = [i[0] for i in result if season == '%01d' % int(i[2])]
            result = [(i, re.findall('(\d{4})', [x for x in i.split('/') if not x == ''][-1])[0]) for i in result]
            result = [i[0] for i in result if i[1] == year][0]

            url = urlparse.urljoin(self.base_link, result)
            url = urlparse.urlparse(url).path
            url += '?episode=%01d' % int(episode)
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

            try:
                url, episode = re.compile('(.+?)\?episode=(\d*)$').findall(url)[0]
            except:
                pass

            result = client.source(url)

            url = zip(client.parseDOM(result, 'a', ret='href', attrs={'target': 'player_iframe'}),
                      client.parseDOM(result, 'a', attrs={'target': 'player_iframe'}))
            url = [(i[0], re.compile('(\d+)').findall(i[1])) for i in url]
            url = [(i[0], i[1][-1]) for i in url if len(i[1]) > 0]

            if content == 'episode':
                url = [i for i in url if i[1] == '%01d' % int(episode)]

            links = [client.replaceHTMLCodes(i[0]) for i in url]

            for u in links:

                try:
                    result = client.source(u)
                    result = re.findall('sources\s*:\s*\[(.+?)\]', result)[0]
                    result = re.findall('"file"\s*:\s*"(.+?)".+?"label"\s*:\s*"(.+?)"', result)

                    url = [{'url': i[0], 'quality': '1080p'} for i in result if '1080' in i[1]]
                    url += [{'url': i[0], 'quality': 'HD'} for i in result if '720' in i[1]]

                    for i in url:
                        sources.append(
                            {'source': 'gvideo', 'quality': i['quality'], 'provider': 'Pubfilm', 'url': i['url'],
                             'direct': True, 'debridonly': False})
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