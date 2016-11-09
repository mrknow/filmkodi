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
        self.base_link = 'http://alltube.tv'
        self.moviesearch_link = '/index.php?url=search/autocomplete/&phrase=%s'
        self.tvsearch_cache = 'http://alltube.tv/seriale-online/'
        self.episode_link = '-Season-%01d-Episode-%01d'


    def get_movie(self, imdb, title, year):
        print("ALLtube originaltitle:%s" % title)
        print cleantitle.query(title)
        try:
            query = self.moviesearch_link % urllib.quote_plus(cleantitle.query2(title))
            query = urlparse.urljoin(self.base_link, query)
            control.log('ALLTUBE T URL %s' % query)
            result = client.source(query)
            result = json.loads(result)

            result = [i for i in result['suggestions'] if len(i) > 0]
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
            result = [(i['data'].encode('utf8'),i['value'].encode('utf8')) for i in result]
            result = [i for i in result if cleantitle.movie(title) in cleantitle.movie(i[1])]
            result = [i[0] for i in result if any(x in i[1] for x in years)][0]
            print("ALLtube result :", result)

            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            control.log('ALLTUBE URL %s' % url)
            return url
        except:
            try:
                query = self.moviesearch_link % cleantitle.query_quote(originaltitle)
                query = urlparse.urljoin(self.base_link, query)
                control.log('ALLTUBE T URL %s' % query)
                result = client.source(query)
                result = json.loads(result)

                result = [i for i in result['suggestions'] if len(i) > 0]
                years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
                result = [(i['data'].encode('utf8'),i['value'].encode('utf8')) for i in result]
                print result
                result = [i for i in result if cleantitle.movie(originaltitle) in cleantitle.movie(i[1])]
                result = [i[0] for i in result if any(x in i[1] for x in years)][0]
                print("ALLtube result :", result)

                try: url = re.compile('//.+?(/.+)').findall(result)[0]
                except: url = result
                url = client.replaceHTMLCodes(url)
                url = url.encode('utf-8')
                control.log('ALLTUBE URL %s' % url)
                return url
            except:
                return


    def tvshow_cache(self):
        try:
            result = client.source(self.tvsearch_cache)
            #control.log('>>>>>>>>>>>>---------- CACHE-2 %s' % result)
            result = client.parseDOM(result, 'li', attrs={'data-letter':'+?'})
            #print('>>>>>>>>>>>>---------- CACHE-3 %s', result)
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a')[0].encode('utf8')) for i in result]
            #print('>>>>>>>>>>>>---------- CACHE-4 ',result)
            return result
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
            print url
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            print url
            result = cache.get(self.tvshow_cache, 120)
            tvshowtitle = cleantitle.get(url['tvshowtitle'])
            for i in result:
                if cleantitle.get(tvshowtitle) in cleantitle.get(i[1]):
                    print("MAM", i)

            result = [i[0] for i in result if cleantitle.get(tvshowtitle) in cleantitle.get(i[1])][0]
            txts = 's%02de%02d' % (int(season),int(episode))
            print result,title,txts

            result = client.source(result)
            result = client.parseDOM(result, 'li', attrs = {'class': 'episode'})
            result = [i for i in result if txts in i][0]
            url = client.parseDOM(result, 'a', ret='href')[0]
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            result = client.source(url)
            links = client.parseDOM(result, 'tr')
            links = [(client.parseDOM(i, 'a', attrs = {'class': 'watch'}, ret='data-iframe')[0],
                    client.parseDOM(i, 'img', ret='alt')[0],
                    client.parseDOM(i, 'td', attrs={'class':'text-center'})[0]) for i in links]

            for i in links:
                try:
                    result = client.source(i[0].decode('base64'))
                    url= client.parseDOM(result, 'iframe', ret='src')[0]
                    url = url.encode('utf-8')
                    #print ("Q",videoquality.solvequality(url),url)
                    sources.append({'source': i[1], 'quality': 'SD', 'provider': 'Alltube', 'url': url, 'vtype':i[2]})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            control.log('ALLTUBE RESOLVE URL %s' % url)
            #url = client.request(url, output='geturl')
            url = resolvers.request(url)
            return url
        except:
            return

