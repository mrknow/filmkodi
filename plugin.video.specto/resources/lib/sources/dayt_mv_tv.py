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

import re,urlparse

from resources.lib.libraries import cleantitle
from resources.lib import resolvers
from resources.lib.libraries import client
from resources.lib.libraries import client2
from resources.lib.libraries import cache
from resources.lib.libraries import control



class source:
    def __init__(self):
        self.base_link = 'http://dayt.se'
        self.search_link = '/forum/search.php?do=process'
        self.forum_link = '/forum/forum.php'
        self.forum_prefix = '/forum'

        self.headers = {}
    def get_movie(self,imdb, title, year):
        try:
            years = ['(%s)' % str(year), '(%s)' % str(int(year) + 1), '(%s)' % str(int(year) - 1)]
            src = 'http://dayt.se/forum/search.php?do=process'
            post = {'titleonly': 1, 'securitytoken': 'guest', 'do': 'process', 'q': title, 'B1': ''}
            title = cleantitle.movie(title)

            result = client.source(src, post=post)
            result = client.parseDOM(result, 'h3', attrs={'class': 'searchtitle'})
            result = [(client.parseDOM(i, 'a', attrs={'class': 'title'}, ret='href')[0],
                       client.parseDOM(i, 'a', attrs={'class': 'title'})[0]) for i in result]
            result = [i for i in result if title in cleantitle.movie(i[1])]
            result = [i[0] for i in result if any(x in i[1] for x in years)][0]
            result = re.compile('(.+?)(?:&amp)').findall(result)[0]
            return result
        except:
            return

    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            self.mytitle =  tvshowtitle
            result = cache.get(self.dayt_tvcache, 120)
            tvshowtitle = cleantitle.get(tvshowtitle)
            result = [i[0] for i in result if tvshowtitle == i[1]][0]
            url = result
            url = url.encode('utf-8')
            return url
        except:
            return


    def dayt_tvcache(self):
        try:
            url = urlparse.urljoin(self.base_link, self.forum_link)
            result =  client.source(url)
            result = re.compile('<span class="sectiontitle"><a href="([^"]+)">([^<]+)</a></span> <span class="rightrss">').findall(result)
            result = [(re.compile('(.+?)(?:&amp)').findall(i[0]), re.sub('&#\d*;', '', i[1])) for i in result]
            result = [( i[0][0], cleantitle.get(i[1])) for i in result if len(i[0]) > 0]

            return result
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            myurl = urlparse.urljoin(self.base_link, '/forum/' + url)
            mytitile = cleantitle.tv('S%02dE%02d' % (int(season),int(episode))).lower()
            result = client.source(myurl)
            result = client.parseDOM(result, 'h3', attrs={'class': 'threadtitle'})
            result = [(client.parseDOM(i, 'a', attrs={'class': 'title'}, ret='href')[0],client.parseDOM(i, 'a', attrs={'class': 'title'})[0]) for i in result]
            result = [i for i in result if mytitile in i[1].lower()]
            result = [(re.compile('(.+?)(?:&amp)').findall(i[0]), i[1]) for i in result][0][0]
            url=result[0]
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []
            if url == None: return sources
            myurl = urlparse.urljoin(self.base_link, '/forum/' + url)
            result = client2.http_get(myurl)
            result10 = result
            result10 = client.parseDOM(result10, 'div', attrs={'id': '5throw'})[0]
            result10 = client.parseDOM(result10, 'a', attrs={'rel': 'nofollow'}, ret='href')
            mquality = 'HD'
            if '1080'in url: mquality = '1080p'
            for i in result10:
                if 'mail.ru' in i:
                    myresolve = resolvers.request(i)
                    sources.append({'source': 'MAIL.RU', 'quality': mquality, 'provider': 'Dayt', 'url': myresolve})
                if 'yadi.sk' in i:
                    myresolve = resolvers.request(i)
                    sources.append({'source': 'YADISK', 'quality': mquality, 'provider': 'Dayt', 'url': myresolve})

            result = client.parseDOM(result, 'iframe', ret='src')
            result = [i for i in result if 'pasep' in i][0]
            result = client.source(result)
            result = client.parseDOM(result, 'iframe', ret='src')[0]
            result = client.source(result)
            result = client.parseDOM(result, 'iframe', ret='src')[0]
            links = resolvers.request(result)
            for i in links: sources.append({'source': 'gvideo', 'quality': i[1], 'provider': 'Dayt', 'url': i[0]})
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            #url = client.request(url, output='geturl')
            #if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            #else: url = url.replace('https://', 'http://')
            return url
        except:
            return


