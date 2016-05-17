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
from resources.lib.libraries import cloudflare
from resources.lib.libraries import client
from resources.lib.resolvers import googleplus


class source:
    def __init__(self):
        self.base_link_1 = 'http://megashare9.tv'
        self.base_link_2 = 'http://xmovies8.tv'
        self.search_link = 'https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=10&hl=en&cx=010516920160860608720:7uiuzaiwcfg&googlehost=www.google.com&q=%s'
        self.headers = {'X-Requested-With': 'XMLHttpRequest'}
        self.player_link = '/lib/picasa.php'
        self.player_post_1 = 'mx=%s&isseries=0&part=0'
        self.player_post_2 = 'mx=%s&isseries=1&part=0'
        self.player_post_3 = 'mx=%s&isseries=1&part=%s'


    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link % (urllib.quote_plus(title))

            result = client.source(query)
            result = json.loads(result)
            result = result['results']

            title = cleantitle.movie(title)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = [(i['url'], i['titleNoFormatting']) for i in result]
            result = [i for i in result if any(x in i[0] for x in years) or any(x in i[1] for x in years)]
            result = [(i[0], re.compile('(^Watch Full "|^Watch |)(.+? [(]\d{4}[)])').findall(i[1])) for i in result]
            result = [(i[0], i[1][0][-1]) for i in result if len(i[1]) > 0]
            result = [i[0] for i in result if title == cleantitle.movie(i[1])][0]

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

            content = re.compile('(.+?)\?S\d*E\d*$').findall(url)

            try: url, season, episode = re.compile('(.+?)\?S(\d*)E(\d*)$').findall(url)[0]
            except: pass

            self.base_link = random.choice([self.base_link_1, self.base_link_2])

            post_id = re.compile('/.+?/(.+)').findall(url)[0].rsplit('/')[0]

            player = urlparse.urljoin(self.base_link, self.player_link)


            if len(content) == 0:
                post = self.player_post_1 % post_id
            else:
                post = client.source(player, post=self.player_post_2 % post_id, headers=self.headers)
                post = client.parseDOM(post, 'ul', attrs = {'class': 'movie-parts'})[0]
                post = client.parseDOM(post, 'li')
                post = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a')) for i in post]
                post = [(i[0][0], i[1][0]) for i in post if len(i[0]) > 0 and len(i[1]) > 0]
                post = [i[0] for i in post if '%01d' % int(episode) == i[1]][0]
                post = urlparse.parse_qs(urlparse.urlparse(post).query)['part_id'][0]
                post = self.player_post_3 % (post_id, post)


            url = client.source(player, post=post, headers=self.headers)
            url = re.compile('<source\s+src="([^"]+)').findall(url)[0]
            url = client.replaceHTMLCodes(url)

            if 'google' in url: quality = googleplus.tag(url)[0]['quality']
            else: quality = 'HD'

            sources.append({'source': 'GVideo', 'quality': quality, 'provider': 'Xmovies', 'url': url})

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


