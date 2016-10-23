# -*- coding: utf-8 -*-

'''
    FanFilm Add-on
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


import re,urllib,urlparse, json, base64

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import control
from resources.lib.libraries import videoquality
from resources.lib.libraries import cache



from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://iitv.pl'

    def get_movie(self, imdb, title, year):
        return
        try:
            query = self.moviesearch_link % (urllib.unquote(title))
            query = urlparse.urljoin(self.base_link, query)
            control.log('IITV URL %s' % query)
            result = client.source(query)
            result = json.loads(result)
            result = [i for i in result['suggestions'] if len(i) > 0]
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
            result = [(i['data'].encode('utf8'),i['value'].encode('utf8')) for i in result]
            result = [i for i in result if cleantitle.movie(title) in cleantitle.movie(i[1])]
            result = [i[0] for i in result if any(x in i[1] for x in years)][0]

            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            control.log('ALLTUBE URL %s' % url)
            return url
        except:
            return

    def iitv_cache(self):
        try:
            result = client.source(self.base_link)
            #control.log('>>>>>>>>>>>>---------- CACHE-2 %s' % result)
            result = client.parseDOM(result, 'ul', attrs={'id':'list'})[0]
            result = client.parseDOM(result, 'li')
            print('>>>>>>>>>>>>---------- CACHE-3 %s', result)
            result = [(client.parseDOM(i, 'a', ret='href')[0], cleantitle.get(client.parseDOM(i, 'a')[0])) for i in result]
            print('>>>>>>>>>>>>---------- CACHE-4 ',result)

            return result
        except:
            return

    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            result = cache.get(self.iitv_cache, 120)
            tvshowtitle = cleantitle.get(tvshowtitle)
            print("TV",tvshowtitle)
            result = [i[0] for i in result if tvshowtitle in i[1]][0]
            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        if url == None: return
        query = urlparse.urljoin(self.base_link, url)
        result = client.source(query)
        result = client.parseDOM(result, 'div', attrs={'class': 'episodes-list'})[0]
        result = client.parseDOM(result, 'li')
        r1=[]
        for i in result:
            try:
                r1.append((client.parseDOM(i, 'span', attrs={'class': 'column episode-code'})[0],client.parseDOM(i, 'a', ret='href')[0]))
            except:
                pass
        result = [i for i in r1 if cleantitle.get(i[0]) == cleantitle.get('S%02dE%02d' % (int(season), int(episode)))]
        try:
            url = re.compile('//.+?(/.+)').findall(result[0][1])[0]
            print("U",url[0])
        except: url = result
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        return url


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []
            mylinks = []
            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            result = client.source(url)
            resulttype = client.parseDOM(result, 'ul',attrs={'class':'tab-content'}, ret='id')
            for j in resulttype:
                print("j",j)
                linkstype = client.parseDOM(result, 'ul', attrs={'class': 'tab-content', 'id':j})[0]
                #print("LinkType",linkstype)
                links1 = client.parseDOM(linkstype, 'a', ret='href', attrs={'class':'video-link'})
                links2 = client.parseDOM(linkstype, 'a', attrs={'class':'video-link'})
                #links = [i for i in links if i[0][0].startswith('http')]
                print("links1",links1, len(links1))
                for k in range(len(links1)):
                    print("k",links1[k], links2[k].split('.')[0], j)
                    if links1[k].startswith('http'): mylinks.append([links1[k], links2[k].split('.')[0], j])

            for i in mylinks:
                try:
                    print("i",i)
                    vtype = 'BD'
                    if i[2] == 'lecPL': vtype = 'Lektor'
                    if i[2] == 'subPL': vtype = 'Napisy'
                    if i[2] == 'org': vtype = 'Orginalny'
                    sources.append({'source': i[1], 'quality': 'SD', 'provider': 'IITV', 'url': i[0], 'vtype':vtype})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            control.log('ALLTUBE RESOLVE URL %s' % url)
            result = client.request(url)
            result= client.parseDOM(result, 'iframe', ret='src')
            url = result[0]

            url = resolvers.request(url)
            return url
        except:
            return

