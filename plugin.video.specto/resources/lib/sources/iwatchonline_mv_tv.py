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
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://www.iwatchonline.ag'
        self.link_1 = 'http://www.iwatchonline.video'
        self.link_2 = 'http://translate.googleusercontent.com/translate_c?anno=2&hl=en&sl=mt&tl=en&u=http://www.iwatchonline.ag'
        self.link_3 = 'https://iwatchonline.unblocked.pw'
        self.search_link = '/advance-search'
        self.show_link = '/tv-shows/%s'
        self.episode_link = '/episode/%s-s%02de%02d'
        self.headers = {}


    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link
            post = {'searchquery': title, 'searchin': '1'}

            result = ''
            links = [self.link_1, self.link_3]
            for base_link in links:
                result = client.source(urlparse.urljoin(base_link, query), post=post, headers=self.headers)
                if 'widget search-page' in str(result): break

            result = client.parseDOM(result, 'div', attrs = {'class': 'widget search-page'})[0]
            result = client.parseDOM(result, 'td')

            title = cleantitle.movie(title)
            years = ['(%s)' % str(year), '(%s)' % str(int(year)+1), '(%s)' % str(int(year)-1)]
            result = [(client.parseDOM(i, 'a', ret='href')[-1], client.parseDOM(i, 'a')[-1]) for i in result]
            result = [i for i in result if title == cleantitle.movie(i[1])]
            result = [i[0] for i in result if any(x in i[1] for x in years)][0]

            url = client.replaceHTMLCodes(result)
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
            except: pass
            url = urlparse.urlparse(url).path
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            query = self.search_link
            post = {'searchquery': tvshowtitle, 'searchin': '2'}

            result = ''
            links = [self.link_1, self.link_3]
            for base_link in links:
                result = client.source(urlparse.urljoin(base_link, query), post=post, headers=self.headers)
                if 'widget search-page' in str(result): break

            result = client.parseDOM(result, 'div', attrs = {'class': 'widget search-page'})[0]
            result = client.parseDOM(result, 'td')

            tvshowtitle = cleantitle.tv(tvshowtitle)
            years = ['(%s)' % str(year), '(%s)' % str(int(year)+1), '(%s)' % str(int(year)-1)]
            result = [(client.parseDOM(i, 'a', ret='href')[-1], client.parseDOM(i, 'a')[-1]) for i in result]
            result = [i for i in result if tvshowtitle == cleantitle.tv(i[1])]
            result = [i[0] for i in result if any(x in i[1] for x in years)][0]

            url = client.replaceHTMLCodes(result)
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
            except: pass
            url = urlparse.urlparse(url).path
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        if url == None: return

        url = url.rsplit('/', 1)[-1]
        url = self.episode_link % (url, int(season), int(episode))
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        return url


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            result = ''
            links = [self.link_1, self.link_2, self.link_3]
            for base_link in links:
                result = client.source(urlparse.urljoin(base_link, url), headers=self.headers)
                if 'original-title' in str(result): break

            links = client.parseDOM(result, 'tr', attrs = {'id': 'pt.+?'})

            for i in links:
                try:
                    lang = re.compile('<img src=[\'|\"|\s|\<]*(.+?)[\'|\"|\s|\>]').findall(i)[1]
                    if not 'English' in lang: raise Exception()

                    host = re.compile('<img src=[\'|\"|\s|\<]*(.+?)[\'|\"|\s|\>]').findall(i)[0]
                    host = host.split('/')[-1]
                    host = host.split('.')[-3]
                    host = host.strip().lower()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    if '>Cam<' in i or '>TS<' in i: quality = 'CAM'
                    elif '>HD<' in i and host in hosthdDict: quality = 'HD'
                    else: quality = 'SD'

                    if quality == 'HD' and not host in hosthdDict: raise Exception()
                    if quality == 'SD' and not host in hostDict: raise Exception()

                    if '>3D<' in i: info = '3D'
                    else: info = ''

                    url = re.compile('href=[\'|\"|\s|\<]*(.+?)[\'|\"|\s|\>]').findall(i)[0]
                    url = client.replaceHTMLCodes(url)
                    try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
                    except: pass
                    if url.startswith('http'): url = urlparse.urlparse(url).path
                    if not url.startswith('http'): url = urlparse.urljoin(self.base_link, url)
                    url = url.encode('utf-8')

                    sources.append({'source': host, 'quality': quality, 'provider': 'Iwatchonline', 'url': url, 'info': info})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = urlparse.urlparse(url).path

            result = ''
            links = [self.link_1, self.link_2, self.link_3]
            for base_link in links:
                result = client.request(urlparse.urljoin(base_link, url), headers=self.headers)
                if 'frame' in str(result): break
            #print("Result >>> result",result)
            url = re.compile('class=[\'|\"]*frame.+?src=[\'|\"|\s|\<]*(.+?)[\'|\"|\s|\>]').findall(result)[0]
            url = client.replaceHTMLCodes(url)
            print("Result >>> url",url)
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
            except: pass
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['url'][0]
            except: pass
            print("Result >>> url2 >>>>>>>>>>>>>>>>>>>>",url)

            url = resolvers.request(url)
            print("Result >>> url3 +++++++++++++++++++++",url)

            return url
        except:
            return

