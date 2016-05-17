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


import re,urllib,urlparse,json, random

from resources.lib.libraries import control
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import cache
from resources.lib.libraries import client2



class source:
    def __init__(self):
        self.base_link = 'http://fmovies.to/'
        self.search_link = '/sitemap'
        self.search_link2 = 'http://fmovies.to/ajax/film/search?sort=year%3Adesc&funny=1&keyword=%s'
        self.hash_link = '/ajax/episode/info'

    def get_movie(self, imdb, title, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            #X - Requested - With:"XMLHttpRequest"
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


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):

        try:
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'],  url['season'], url['episode'] = title, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return

    def fmovies_cache(self):
        try:
            url = urlparse.urljoin(self.base_link, self.search_link)
            control.log('>>>>>>>>>>>>---------- CACHE %s' % url)

            #result = client.source(url)
            result = client2.http_get(url)
            result = result.split('>Movies and Series<')[-1]
            control.log('>>>>>>>>>>>>---------- CACHE-2 %s' % result)
            result = client.parseDOM(result, 'ul')[0]
            control.log('>>>>>>>>>>>>---------- CACHE-3 %s' % result)

            result = re.compile('href="(.+?)">(.+?)<').findall(result)

            result = [(re.sub('http.+?//.+?/','/', i[0]), re.sub('&#\d*;','', i[1])) for i in result]
            control.log('>>>>>>>>>>>>---------- CACHE-4 ')

            return result
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        return
        try:
            sources = []

            if url == None: return sources

            if not str(url).startswith('http'):
                try:
                    data = urlparse.parse_qs(url)
                    data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

                    title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

                    year = re.findall('(\d{4})', data['premiered'])[0] if 'tvshowtitle' in data else data['year']

                    try: episode = data['episode']
                    except: pass

                    query = {'keyword': title, 's':''}
                    #query.update(self.__get_token(query))
                    search_url = urlparse.urljoin(self.base_link, '/search')
                    search_url = search_url + '?' + urllib.urlencode(query)
                    print("R",search_url)
                    result = client2.http_get(search_url)
                    print("r", result)

                    r = client.parseDOM(result, 'div', attrs = {'class': '[^"]*movie-list[^"]*'})[0]
                    r = client.parseDOM(r, 'div', attrs = {'class': 'item'})
                    r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', attrs = {'class': 'name'})) for i in r]
                    r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and  len(i[1]) > 0]
                    r = [(re.sub('http.+?//.+?/','/', i[0]), re.sub('&#\d*;','', i[1])) for i in r]

                    if 'season' in data:
                        url = [(i[0], re.findall('(.+?) (\d*)$', i[1])) for i in r]
                        url = [(i[0], i[1][0][0], i[1][0][1]) for i in url if len(i[1]) > 0]
                        url = [i for i in url if cleantitle.get(title) == cleantitle.get(i[1])]
                        url = [i for i in url if '%01d' % int(data['season']) == '%01d' % int(i[2])]
                    else:
                        url = [i for i in r if cleantitle.get(title) == cleantitle.get(i[1])]



                    """
                    r = cache.get(self.fmovies_cache, 120)

                    if 'season' in data:
                        url = [(i[0], re.findall('(.+?) (\d*)$', i[1]), i[2]) for i in r]
                        url = [(i[0], i[1][0][0], i[1][0][1], i[2]) for i in url if len(i[1]) > 0]
                        url = [i for i in url if cleantitle.get(title) == cleantitle.get(i[1])]
                        url = [i for i in url if i[3] == year] + [i for i in url if i[3] == data['year']]
                        url = [i for i in url if '%01d' % int(data['season']) == '%01d' % int(i[2])]
                    else:
                        url = [i for i in r if cleantitle.get(title) == cleantitle.get(i[1]) and i[2] == year]

                    """
                    url = url[0][0]
                    url = urlparse.urljoin(self.base_link, url)
                    print("r2", url)

                except:
                    url == self.base_link


            try: url, episode = re.compile('(.+?)\?episode=(\d*)$').findall(url)[0]
            except: pass

            referer = url
            #xtoken = self.__get_xtoken()

            result = client.source(url, safe=True)
            #xtoken = self.__get_xtoken()
            print("r22", result)

            alina = client.parseDOM(result, 'title')[0]
            print( re.findall('(\d{4})', alina))

            atr = [i for i in client.parseDOM(result, 'title') if len(re.findall('(\d{4})', i)) > 0][-1]
            if 'season' in data:
                result = result if year in atr or data['year'] in atr else None
            else:
                result = result if year in atr else None

            print("r3",result)

            try: quality = client.parseDOM(result, 'span', attrs = {'class': 'quality'})[0].lower()
            except: quality = 'hd'
            if quality == 'cam' or quality == 'ts': quality = 'CAM'
            elif quality == 'hd' or 'hd ' in quality: quality = 'HD'
            else: quality = 'SD'

            result = client.parseDOM(result, 'ul', attrs = {'data-range-id':"0"})
            print("r3",result,quality)

            servers = []
            #servers = client.parseDOM(result, 'li', attrs = {'data-type': 'direct'})
            servers = zip(client.parseDOM(result, 'a', ret='data-id'), client.parseDOM(result, 'a'))
            servers = [(i[0], re.findall('(\d+)', i[1])) for i in servers]
            servers = [(i[0], ''.join(i[1][:1])) for i in servers]
            print("r3",servers)

            try: servers = [i for i in servers if '%01d' % int(i[1]) == '%01d' % int(episode)]
            except: pass

            for s in servers[:3]:
                try:
                    headers = {'X-Requested-With': 'XMLHttpRequest'}

                    hash_url = urlparse.urljoin(self.base_link, self.hash_link)
                    query = {'id': s[0], 'update': '0'}
                    query.update(self.__get_token(query))
                    hash_url = hash_url + '?' + urllib.urlencode(query)
                    headers['Referer'] = url
                    result = client2.http_get(hash_url, headers=headers, cache_limit=.5)
                    print("r100",result)


                    query = {'id': s[0], 'update': '0'}
                    query.update(self.__get_token(query))
                    url = url + '?' + urllib.urlencode(query)
                    result = client.source(url, headers=headers, referer=referer, safe=True)
                    print("r100",result)
                    result = json.loads(result)

                    query = result['params']
                    query['mobile'] = '0'
                    query.update(self.__get_token(query))
                    grabber = result['grabber'] + '?' + urllib.urlencode(query)

                    result = client.source(grabber, headers=headers, referer=url, safe=True)
                    result = json.loads(result)

                    result = result['data']
                    result = [i['file'] for i in result if 'file' in i]

                    for i in result:
                        try: sources.append({'source': 'gvideo', 'quality': client.googletag(i)[0]['quality'], 'provider': 'Fmovies', 'url': i})
                        except: pass
                except:
                    pass

            if quality == 'CAM':
                for i in sources: i['quality'] = 'CAM'

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = client.request(url, output='geturl')
            if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            else: url = url.replace('https://', 'http://')
            return url
        except:
            return


    def __get_token(self, data):
        n = 0
        for key in data:
            if not key.startswith('_'):
                for i, c in enumerate(data[key]):
                    n += ord(c) * (i + 123456 + len(data[key]))
        return {'_token': hex(n)[2:]}

    def __get_xtoken(self):
        url = urlparse.urljoin(self.base_link, 'fghost?%s' % (random.random()))
        html = client.source(url, safe=True)
        k = self.__get_dict('k', html)
        v = self.__get_dict('v', html)
        if k and v:
            data = {}
            l = 0
            while l < len(k):
                for i in k:
                    if k[i] == l:
                        data[k[i]] = v[i]
                        l = len(data)

            token = ''.join([str(data[key]) for key in data])
            rt = str(len(token))
            s = urlparse.urlparse(self.base_link).hostname
            for i, c in enumerate(token):
                rt += '.' + c
                try: nc = str(ord(s[i]))
                except: nc = str(random.randint(0, 5))
                rt += '.' + nc
            return rt

    def __get_dict(self, var, html):
        match = re.search('\s+%s\s*=\s*({[^}]+})' % (var), html)
        if match:
            return eval(match.group(1))
