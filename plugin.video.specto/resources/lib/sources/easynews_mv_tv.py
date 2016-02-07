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

from resources.lib.libraries import control
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client


class source:
    def __init__(self):
        self.base_link = 'http://members.easynews.com'
        self.user = control.setting('easynews_user')
        self.password = control.setting('easynews_password')
        self.cookie = 'chickenlicker=%s%%3A%s' % (self.user, self.password)
        self.moviesearch_link = '/2.0/search/solr-search/advanced?st=adv&safeO=0&sb=1&from=&ns=&fex=mkv%%2Cmp4&vc=AVC1%%2CHEVC%%2CH264%%2CH265&ac=&s1=nsubject&s1d=%%2B&s2=nrfile&s2d=%%2B&s3=dsize&s3d=%%2B&fty[]=VIDEO&spamf=1&u=1&gx=1&pby=1000&pno=1&sS=3&d1=&d1t=&d2=&d2t=&b1=&b1t=17&b2=&b2t=28&px1=&px1t=&px2=&px2t=&fps1=&fps1t=&fps2=&fps2t=&bps1=&bps1t=8&bps2=&bps2t=&hz1=&hz1t=&hz2=&hz2t=&rn1=&rn1t=&rn2=&rn2t=&gps=%s&sbj=%s'
        self.tvsearch_link = '/2.0/search/solr-search/advanced?st=adv&safeO=0&sb=1&from=&ns=&fil=&fex=mkv%%2Cmp4%%2Cavi&vc=&ac=&s1=nsubject&s1d=%%2B&s2=nrfile&s2d=%%2B&s3=dsize&s3d=%%2B&fty[]=VIDEO&spamf=1&u=1&gx=1&pby=1000&pno=1&sS=3&d1=&d1t=&d2=&d2t=&b1=&b1t=14&b2=&b2t=26&px1=&px1t=&px2=&px2t=&fps1=&fps1t=&fps2=&fps2t=&bps1=&bps1t=8&bps2=&bps2t=&hz1=&hz1t=&hz2=&hz2t=&rn1=&rn1t=&rn2=&rn2t=&gps=%s&sbj=%s'


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

            title, hdlr = re.compile('(.+?) (\d{4}|S\d*E\d*)$').findall(url)[0]

            if hdlr.isdigit():
                query = self.moviesearch_link % (urllib.quote_plus(url), urllib.quote_plus(url))
                hdlr = [str(hdlr), str(int(hdlr)+1), str(int(hdlr)-1)]
                title = cleantitle.movie(title)
                type = 'movie'
            else:
                query = self.tvsearch_link % (urllib.quote_plus(url), urllib.quote_plus(url))
                hdlr = [hdlr]
                title = cleantitle.tv(title)
                type = 'episode'

            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query, cookie=self.cookie)
            result = json.loads(result)

            links = result['data']

            for i in links:
                try:
                    name = i['10']
                    name = client.replaceHTMLCodes(name)

                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|3D)(\.|\)|\]|\s|)(.+|)', '', name.upper())
                    if type == 'movie': t = cleantitle.movie(t)
                    else: t = cleantitle.tv(t)
                    if not t == title: raise Exception()

                    y = re.compile('[\.|\(|\[|\s](\d{4}|S\d*E\d*)[\.|\)|\]|\s|]').findall(name.upper())[-1]
                    if not any(x == y for x in hdlr): raise Exception()

                    fmt = re.sub('(.+)(\.|\(|\[|\s)(\d{4}|S\d*E\d*)(\.|\)|\]|\s)', '', name.upper())
                    fmt = re.split('\.|\(|\)|\[|\]|\s|\-', fmt)
                    fmt = [x.lower() for x in fmt]

                    if any(x.endswith(('subs', 'sub', 'dubbed', 'dub')) for x in fmt): raise Exception()
                    if any(x in ['extras'] for x in fmt): raise Exception()

                    dur = i['14']
                    if dur.startswith(('0m', '1m', '2m', '3m', '4m')): raise Exception()
                    if not 'm:' in dur: raise Exception()

                    lang = i['alangs']
                    if lang == None: lang = ['eng']
                    if not 'eng' in lang: raise Exception()

                    if not i['virus'] == False: raise Exception()

                    res = int(i['width'])
                    if 1900 <= res <= 1920: quality = '1080p'
                    elif 1200 <= res <= 1280: quality = 'HD'
                    else: quality = 'SD'
                    if any(x in ['dvdscr', 'r5', 'r6'] for x in fmt): quality = 'SCR'
                    elif any(x in ['camrip', 'tsrip', 'hdcam', 'hdts', 'dvdcam', 'dvdts', 'cam', 'ts'] for x in fmt): quality = 'CAM'

                    size = i['4']
                    if size.endswith(' GB'): div = 1
                    else: div = 1024
                    size = float(re.sub('[^0-9|/.|/,]', '', size))/div

                    if '3d' in fmt: q = ' | 3D'
                    else: q = ''

                    info = '%.2f GB%s | %s | %s' % (size, q, i['12'], i['18'])
                    info = info.encode('utf-8')

                    url = urllib.quote('%s%s/%s%s' % (i['0'], i['11'], i['10'], i['11']))
                    url = 'http://members.easynews.com/dl/%s' % url
                    url = url.encode('utf-8')

                    sources.append({'source': 'Easynews', 'quality': quality, 'provider': 'Easynews', 'url': url, 'info': info})
                except:
                    pass

            if not all(i['quality'] in ['CAM', 'SCR'] for i in sources): 
                sources = [i for i in sources if not i['quality'] in ['CAM', 'SCR']]

            return sources
        except:
            return sources


    def resolve(self, url):
        url = '%s|Cookie=%s' % (url, urllib.quote_plus(self.cookie))
        return url


