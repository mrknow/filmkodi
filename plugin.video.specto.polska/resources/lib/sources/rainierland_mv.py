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


import re,urllib,urlparse, json

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client2
from resources.lib.libraries import client
from resources.lib.libraries import control
from resources.lib import resolvers



class source:
    def __init__(self):
        self.base_link = 'http://rainierland.com'
        self.search_link = '/?s=%s'


    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link % urllib.quote(title)
            query = urlparse.urljoin(self.base_link, query)
            #control.log("rainierland-0 @@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" % query)
            result = client2.http_get(query)
            title = cleantitle.movie(title)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
            r = client.parseDOM(result, 'div', attrs = {'class': 'thumb'})
            #control.log("rainierland-1 @@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" % r)

            r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in r]
            #control.log("rainierland-2 @@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" % r)

            r = [(i[0][0], i[1][-1]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            #control.log("rainierland-3 @@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" % r)

            r = [(re.sub('http.+?//.+?/','', i[0]), i[1]) for i in r]
            #control.log("rainierland-4 @@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" % r)

            r = [('/'.join(i[0].split('/')[:2]), i[1]) for i in r]
            r = [x for y,x in enumerate(r) if x not in r[:y]]
            r = [i for i in r if title == cleantitle.movie(i[1])]
            u = [i[0] for i in r][0]

            url = urlparse.urljoin(self.base_link, u)
            url = urlparse.urlparse(url).path
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            #control.log("rainierland url @@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" % url)

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

            result = client.source(query)

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
        sources = []
        #control.log("rainierland-sources-0 @@@@@@@@@@@@@@@@@@@@@@@@@@@@ ")

        try:
            r = urlparse.urljoin(self.base_link, url)

            result = client2.http_get(r)
            #control.log("rainierland-sources-1 @@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" % result)
            r = client.parseDOM(result, 'div', attrs = {'class': 'screen fluid-width-video-wrapper'})[0]
            #control.log("rainierland-sources-2 @@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" % r)
            r = re.compile('src="(.*?)"').findall(r)
            #control.log("rainierland-sources-3 @@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" % r)
            if len(r) > 0:
                t = urlparse.urljoin(self.base_link, r[0])
                r2 = client2.http_get(t)
                #control.log("rainierland-sources-4 @@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" % r2)
                r3 = re.compile('<source src="(.*?)"').findall(r2)
                for i in r3:
                    try:
                        sources.append({'source': 'gvideo', 'quality': client.googletag(i)[0]['quality'], 'provider': 'Rainierland', 'url': i})
                    except:
                        pass
                #control.log("rainierland-sources-5 @@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" % r3)
                r4 =  client.parseDOM(r2, 'a', ret='href')
                #control.log("rainierland-sources-5 @@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" % r4)
                for i in r4:
                    try:
                        url = resolvers.request(i)
                        sources.append({'source': 'openload', 'quality': 'HD', 'provider': 'Rainierland', 'url': url})
                    except:
                        pass

            return sources

        except:
            return sources


    def resolve(self, url):
        control.log("rainierland-sources-0 @@@@@@@@@@@@@@@@@@@@@@@@@@@@ %s" % url)

        try:
            if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
            else: url = url.replace('https://', 'http://')
            return url
        except:
            pass

