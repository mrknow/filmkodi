# -*- coding: utf-8 -*-

'''
    FanFilm Add-on
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
from resources.lib.libraries import control
from resources.lib.libraries import cache
from resources.lib import resolvers



class source:
    def __init__(self):
        self.base_link = 'http://www.filmxy.cc/'
        #self.base_link = client.source(self.base_link, output='geturl')
        self.search_link = '/wp-admin/admin-ajax.php'
        self.movie_list = '/720p-1080p-bluray-movies-list/'


    def get_movie(self, imdb, title, year):
        try:
            leter = title[0]
            result = cache.get(self.filmxy_cache,9000,leter)
            print "r1",result

            years = ['(%s)' % str(year), '(%s)' % str(int(year)+1), '(%s)' % str(int(year)-1)]
            result = [i for i in result if cleantitle.movie(title) == cleantitle.movie(i[2])]
            print "r2",result
            result = [i[0] for i in result if any(x in i[1] for x in years)][0]
            print "r3",result
            url = client.replaceHTMLCodes(result)
            url = url.encode('utf-8')
            return url
        except Exception as e:
            control.log('Filmxy ERROR %s' % e)
            return

    def filmxy_cache(self, leter=''):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link)
            #control.log('>>>>>>>>>>>>---------- CACHE %s' % url)
            headers = {'X-Requested-With':"XMLHttpRequest"}
            params = {"action":"ajax_process2", "query":leter.upper()}
            params = urllib.urlencode(params)
            result = client.request(url, post=params, headers=headers)

            result = client.parseDOM(result, 'p')
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a')[0], client.parseDOM(i, 'a')[0]) for i in result]
            result = [(re.sub('http.+?//.+?/','/', i[0]), re.findall("\(\d+\)", i[1]), i[2].split('(')[0]) for i in result]
            #control.log('>>>>>>>>>>>>---------- CACHE-4 %s' % result)
            result = [(i[0], i[1][0],  i[2].strip()) for i in result if len(i[1]) > 0]
            return result
        except Exception as e:
            control.log('Filmxy Cache ERROR %s' % e)
            return

    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            print "URL",url

            sources = []
            if url == None: return sources

            url1 = urlparse.urljoin(self.base_link, url)
            result = client.request(url1)
            url1 = client.parseDOM(result, 'a', attrs = {'id': 'main-down'}, ret='href')[0]
            print "LINKS1",url1
            result = client.request(url1)
            print "LINKS2", result

            for quality in ['720p', '1080p']:
                links = client.parseDOM(result, 'div', attrs = {'class': '.+?'+quality})[0]
                links = client.parseDOM(links, 'li')
                links = [(client.parseDOM(i, 'a', ret='href')[0]) for i in links]

                if '1080p' in quality: q = '1080p'
                elif '720p' in quality or 'hd' in quality: q = 'HD'
                else: q = 'SD'
                for j in links:
                    print "j",j
                    host = j.split('/')[2]
                    host = host.strip().lower()
                    host = client.replaceHTMLCodes(host)

                    if not host in hostDict: raise Exception()

                    host = host.encode('utf-8')
                    print "HOST",host, j
                    sources.append({'source': host, 'quality': q, 'provider': 'Filmxy', 'url': j})

            print "LINKS3", links
            return sources
        except Exception as e:
            control.log('Filmxy Source ERROR %s' % e)

            return sources


    def resolve(self, url):
        try:
            #url = client.request(url, output='geturl')
            #if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            #else: url = url.replace('https://', 'http://')
            url = resolvers.request(url)
            return url
        except:
            return

