# -*- coding: utf-8 -*-

'''
    Specto Add-on
    Copyright (C) 2016 mrknow

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


import re,urllib,urlparse, json

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import client2
from resources.lib import resolvers
from resources.lib.libraries import control



class source:
    def __init__(self):
        self.base_link = 'http://123movies.to'
        self.search_link = '/movie/search/%s'


    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link % urllib.quote(title)
            query = urlparse.urljoin(self.base_link, query)
            result = client2.http_get(query)
            title = cleantitle.movie(title)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
            r = client.parseDOM(result, 'div', attrs = {'class': 'ml-item'})
            r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in r]
            r = [(i[0][0], i[1][-1]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            r = [(re.sub('http.+?//.+?/','', i[0]), i[1]) for i in r]
            r = [('/'.join(i[0].split('/')[:2]), i[1]) for i in r]
            r = [x for y,x in enumerate(r) if x not in r[:y]]
            r = [i for i in r if title == cleantitle.movie(i[1])]
            u = [i[0] for i in r][0]

            url = urlparse.urljoin(self.base_link, u)
            url = urlparse.urlparse(url).path
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            control.log("@@@@@@@@@@@@@@@ URL  %s" % url)

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

            query = self.search_link % urllib.quote(tvshowtitle)
            query = urlparse.urljoin(self.base_link, query)

            #result = client.source(query)
            result = client2.http_get(query)


            tvshowtitle = cleantitle.tv(tvshowtitle)
            season = '%01d' % int(season)
            episode = '%01d' % int(episode)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = client.parseDOM(result, 'div', attrs = {'class': 'ml-item'})
            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'h2'), re.compile('class *= *[\'|\"]jt-info[\'|\"]>(\d{4})<').findall(i)) for i in result]
            result = [(i[0][0], i[1][0], i[2][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]
            result = [(i[0], re.compile('(.+?) - Season (\d*)$').findall(i[1]), i[2]) for i in result]
            result = [(i[0], i[1][0][0], i[1][0][1], i[2]) for i in result if len(i[1]) > 0]
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

            url = urlparse.urljoin(self.base_link, url)

            content = re.compile('(.+?)\?episode=\d*$').findall(url)
            content = 'movie' if len(content) == 0 else 'episode'

            try: url, episode = re.compile('(.+?)\?episode=(\d*)$').findall(url)[0]
            except: pass

            url = urlparse.urljoin(self.base_link, url) + '/watching.html'
            result = client2.http_get(url)

            movie = client.parseDOM(result, 'div', ret='movie-id', attrs = {'id': 'media-player'})[0]
            mtoken =  client.parseDOM(result, 'div', ret='player-token', attrs = {'id': 'media-player'})[0]
            try:
                quality = client.parseDOM(result, 'span', attrs = {'class': 'quality'})[0].lower()
            except: quality = 'hd'
            if quality == 'cam' or quality == 'ts': quality = 'CAM'
            elif quality == 'hd': quality = 'HD'
            else: quality = 'SD'
            url = '/ajax/get_episodes/%s/%s' % (movie, mtoken)
            url = urlparse.urljoin(self.base_link, url)
            result = client2.http_get(url)
            result = client.parseDOM(result, 'div', attrs = {'class': 'les-content'})
            result = zip(client.parseDOM(result, 'a', ret='onclick'), client.parseDOM(result, 'a', ret='episode-id'), client.parseDOM(result, 'a'))
            result = [(re.sub('[^0-9]', '', i[0].split(',')[0]), re.sub('[^0-9a-fA-F]', '', i[0].split(',')[-1]), i[1], ''.join(re.findall('(\d+)', i[2])[:1])) for i in result]
            result = [(i[0], i[1], i[2], i[3]) for i in result]
            if content == 'episode': result = [i for i in result if i[3] == '%01d' % int(episode)]

            links = [('/ajax/load_episode/%s/%s' % (i[2], i[1]), 'gvideo') for i in result if 2 <= int(i[0]) <= 11]

            for i in links:
                url1 = urlparse.urljoin(self.base_link, i[0])
                sources.append({'source': i[1], 'quality': quality, 'provider': 'Muchmovies', 'url': i[0]})

            links = []
            links += [('/ajax/load_embed/%s/%s' % (i[2], i[1]), 'openload') for i in result if i[0] == '14']
            links += [('/ajax/load_embed/%s/%s' % (i[2], i[1]), 'videomega') for i in result if i[0] == '13']
            #links += [('movie/loadEmbed/%s/%s' % (i[2], i[1]), 'videowood.tv') for i in result if i[0] == '12']

            for i in links:
                url1 = urlparse.urljoin(self.base_link, i[0])
                sources.append({'source': i[1], 'quality': quality, 'provider': 'Muchmovies', 'url': i[0]})
            return sources
        except:
            return sources


    def resolve(self, url):

        try:
            headers = {'Referer': url}
            url = urlparse.urljoin(self.base_link, url)
            result = client.source(url, headers=headers)
            if 'load_embed' in url:
                result = json.loads(result)
                result = resolvers.request(result['embed_url'])
                return result

        except:
            pass

        try:
            url = re.compile('"?file"?\s*=\s*"(.+?)"\s+"?label"?\s*=\s*"(\d+)p?"').findall(result)
            url = [(int(i[1]), i[0]) for i in url]
            url = sorted(url, key=lambda k: k[0])
            url = url[-1][1]
            url = client.request(url, output='geturl')
            if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            else: url = url.replace('https://', 'http://')
            return url

        except:
            pass


