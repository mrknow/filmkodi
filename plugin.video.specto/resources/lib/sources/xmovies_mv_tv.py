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


import re,urllib,urlparse,json,random

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client2
from resources.lib.libraries import client
from resources.lib.libraries import control

from resources.lib.resolvers import googleplus


class source:
    def __init__(self):
        self.base_link = 'http://xmovies8.tv'
        self.base_link_2 = 'http://xmovies8.tv'
        self.search_link = '/movies/search?s=%s'
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}
        self.player_link = '/lib/picasa.php'
        self.player_post_1 = 'mx=%s&isseries=0&part=0'
        self.player_post_2 = 'mx=%s&isseries=1&part=0'
        self.player_post_3 = 'mx=%s&isseries=1&part=%s'


    def get_movie(self, imdb, title, year):
        try:
            query = urlparse.urljoin(self.base_link_2, self.search_link)
            query = query % urllib.quote_plus(title)

            r = client.request(query)
            t = cleantitle.get(title)

            r = zip(client.parseDOM(r, 'a', ret='href', attrs = {'class': 'movie-item-link'}), client.parseDOM(r, 'a', ret='title', attrs = {'class': 'movie-item-link'}))
            r = [(i[0], i[1], re.findall('(\d{4})', i[1])) for i in r]
            #control.log('R %s' % r)
            r = [(i[0], i[1], i[2][-1]) for i in r if len(i[2]) > 0]
            #control.log('R %s' % r)
            r = [i[0] for i in r if t == cleantitle.get(i[1]) and year == i[2]][0]
            #control.log('R %s' % r)

            url = urlparse.urljoin(self.base_link, r)
            url = urlparse.urlparse(url).path
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            pass

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

            season, episode = '%01d' % int(season), '%01d' % int(episode)

            query = '%s season %s' % (tvshowtitle, season)
            query = self.search_link % (urllib.quote_plus(query))

            result = client.source(query)
            result = json.loads(result)
            result = result['results']

            tvshowtitle = cleantitle.tv(tvshowtitle)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = [(i['url'], i['titleNoFormatting']) for i in result]
            result = [(i[0], re.compile('(^Watch Full "|^Watch |)(.+?[(]\d{4}[)])').findall(i[1])) for i in result]
            result = [(i[0], i[1][0][-1].lower()) for i in result if len(i[1]) > 0]
            result = [(i[0], re.compile('(.+) season (\d+)\s*[(](\d{4})[)]').findall(i[1])) for i in result]
            result = [(i[0], cleantitle.tv(i[1][0][0]), i[1][0][1], i[1][0][2]) for i in result if len(i[1]) > 0]
            result = [i for i in result if tvshowtitle == cleantitle.tv(i[1])]
            result = [i for i in result if season == i[2]]
            result = [(i[0], i[1], str(int(i[3]) - int(i[2]) + 1)) for i in result]
            result = [i[0] for i in result if any(x in i[2] for x in years)][0]

            result += '?S%02dE%02d' % (int(season), int(episode))

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

            u = urlparse.urljoin(self.base_link, url)

            r = client2.http_get(u)
            #control.log('R %s' % r)

            r = re.findall("load_player\(\s*'([^']+)'\s*,\s*'?(\d+)\s*'?", r)
            r = list(set(r))
            r = [i for i in r if i[1] == '0' or int(i[1]) >= 720]
            control.log('R %s' % r)

            links = []

            for p in r:
                try:
                    headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': u}

                    player = urlparse.urljoin(self.base_link, '/ajax/movie/load_player')

                    post = urllib.urlencode({'id': p[0], 'quality': p[1]})

                    result = client2.http_get(player, data=post, headers=headers)
                    #control.log('result %s' % result)

                    frame = client.parseDOM(result, 'iframe', ret='src')
                    embed = client.parseDOM(result, 'embed', ret='flashvars')

                    if frame:
                        if 'player.php' in frame[0]:
                            frame = client.parseDOM(result, 'input', ret='value', attrs={'type': 'hidden'})[0]

                            headers = {'Referer': urlparse.urljoin(self.base_link, frame[0])}

                            url = client.request(frame, headers=headers, output='geturl')

                            links += [
                                {'source': 'gvideo', 'url': url, 'quality': client.googletag(url)[0]['quality'],
                                 'direct': True}]

                        elif 'openload.' in frame[0]:
                            links += [{'source': 'openload.co', 'url': frame[0], 'quality': 'HD', 'direct': False}]

                        elif 'videomega.' in frame[0]:
                            links += [{'source': 'videomega.tv', 'url': frame[0], 'quality': 'HD', 'direct': False}]

                    elif embed:
                        url = urlparse.parse_qs(embed[0])['fmt_stream_map'][0]

                        url = [i.split('|')[-1] for i in url.split(',')]

                        for i in url:
                            try: links.append({'source': 'gvideo', 'url': i, 'quality': client.googletag(i)[0]['quality'],'direct': True})
                            except: pass

                except:
                    pass

            for i in links:
                #sources.append({'source': i['source'], 'quality': i['quality'], 'provider': 'Xmovies', 'url': i['url'], 'direct': i['direct'], 'debridonly': False})
                sources.append({'source':  i['source'], 'quality': i['quality'], 'provider': 'Xmovies', 'url': i['url']})


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


