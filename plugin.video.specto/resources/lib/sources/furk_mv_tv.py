# -*- coding: utf-8 -*-

'''
    Genesis Add-on
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

from resources.lib.libraries import control
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client


class source:
    def __init__(self):
        self.base_link = 'http://api.furk.net'
        self.search_link = '/api/plugins/metasearch'
        self.login_link = '/api/login/login'
        self.user = control.setting('furk_user')
        self.password = control.setting('furk_password')


    def get_movie(self, imdb, title, year):
        try:
            if (self.user == '' or self.password == ''): raise Exception()

            url = '%s %s' % (title, year)
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            if (self.user == '' or self.password == ''): raise Exception()

            url = tvshowtitle
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        try:
            if url == None: return

            if (self.user == '' or self.password == ''): raise Exception()

            url = '%s S%02dE%02d' % (url, int(season), int(episode))
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            if (self.user == '' or self.password == ''): raise Exception()

            query = urlparse.urljoin(self.base_link, self.login_link)
            post = urllib.urlencode({'login': self.user, 'pwd': self.password})
            cookie = client.source(query, post=post, output='cookie')

            query = urlparse.urljoin(self.base_link, self.search_link)
            post = urllib.urlencode({'sort': 'relevance', 'filter': 'all', 'moderated': 'yes', 'offset': '0', 'limit': '100', 'match': 'all', 'q': url})
            result = client.source(query, post=post, cookie=cookie)
            result = json.loads(result)
            links = result['files']

            title, hdlr = re.compile('(.+?) (\d{4}|S\d*E\d*)$').findall(url)[0]

            if hdlr.isdigit():
                type = 'movie'
                title = cleantitle.movie(title)
                hdlr = [str(hdlr), str(int(hdlr)+1), str(int(hdlr)-1)]
            else:
                type = 'episode'
                title = cleantitle.tv(title)
                hdlr = [hdlr]

            for i in links:
                try:
                    name = i['name']
                    name = client.replaceHTMLCodes(name)

                    info = i['video_info']
                    if type == 'movie' and not '#0:1(eng): Audio:' in info: raise Exception()

                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|3D)(\.|\)|\]|\s)(.+)', '', name)
                    if type == 'movie': t = cleantitle.movie(t)
                    else: t = cleantitle.tv(t)
                    if not t == title: raise Exception()

                    y = re.compile('[\.|\(|\[|\s](\d{4}|S\d*E\d*)[\.|\)|\]|\s]').findall(name)[-1]
                    if not any(x == y for x in hdlr): raise Exception()

                    fmt = re.sub('(.+)(\.|\(|\[|\s)(\d{4}|S\d*E\d*)(\.|\)|\]|\s)', '', name)
                    fmt = re.split('\.|\(|\)|\[|\]|\s|\-', fmt)
                    fmt = [x.lower() for x in fmt]

                    if any(x.endswith(('subs', 'sub', 'dubbed', 'dub')) for x in fmt): raise Exception()
                    if any(x in ['extras'] for x in fmt): raise Exception()

                    res = i['video_info'].replace('\n','')
                    res = re.compile(', (\d*)x\d*').findall(res)[0]
                    res = int(res)
                    if 1900 <= res <= 1920: quality = '1080p'
                    elif 1200 <= res <= 1280: quality = 'HD'
                    else: quality = 'SD'
                    if any(x in ['dvdscr', 'r5', 'r6'] for x in fmt): quality = 'SCR'
                    elif any(x in ['camrip', 'tsrip', 'hdcam', 'hdts', 'dvdcam', 'dvdts', 'cam', 'ts'] for x in fmt): quality = 'CAM'

                    size = i['size']
                    size = float(size)/1073741824
                    if int(size) > 2 and not quality in ['1080p', 'HD']: raise Exception()
                    if int(size) > 5: raise Exception()

                    info = i['video_info'].replace('\n','')
                    v = re.compile('Video: (.+?),').findall(info)[0]
                    a = re.compile('Audio: (.+?), .+?, (.+?),').findall(info)[0]
                    if '3d' in fmt: q = ' | 3D'
                    else: q = ''

                    info = '%.2f GB%s | %s | %s | %s' % (size, q, v, a[0], a[1])
                    info = re.sub('\(.+?\)', '', info)
                    info = info.replace('stereo', '2.0')
                    info = ' '.join(info.split())

                    url = i['url_pls']
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    sources.append({'source': 'Furk', 'quality': quality, 'provider': 'Furk', 'url': url, 'info': info})
                except:
                    pass

            if not all(i['quality'] in ['CAM', 'SCR'] for i in sources): 
                sources = [i for i in sources if not i['quality'] in ['CAM', 'SCR']]

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            query = urlparse.urljoin(self.base_link, self.login_link)
            post = urllib.urlencode({'login': self.user, 'pwd': self.password})
            cookie = client.request(query, post=post, output='cookie')

            result = client.request(url, cookie=cookie)
            url = client.parseDOM(result, 'location')[0]
            return url
        except:
            return

