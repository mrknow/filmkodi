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
        self.base_link = 'http://www.serialeonline.pl/'
        self.info_link = '/ajax/em.php'
        #http://www.serialeonline.pl/ajax/em.php?did=MzI0NDUxMzk1ODgzMQ==&trurl=147275377757c8707130a18&w=0

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
            return url
        except:
            return

    def serialeonlinepl_cache(self):
        #try:
        result = client.request(self.base_link)
        result = result.decode('iso-8859-2')
        result = client.parseDOM(result, 'div', attrs={'class':'media menu-row margin-bottom-20'})
        result = [(client.parseDOM(i, 'a', ret='href')[0],  cleantitle.get(client.parseDOM(i, 'a', ret='title')[0])) for i in result]
        #print result
        return result
        #except:
        #    return

    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            result = cache.get(self.serialeonlinepl_cache, 120)
            tvshowtitle = cleantitle.get(tvshowtitle)
            print tvshowtitle
            result = [i[0] for i in result if tvshowtitle in i[1]][0]
            print result
            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return

    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        try:
            if url == None: return
            url = urlparse.urljoin(self.base_link, url)
            result = client.request(url).decode('iso-8859-2')
            result = result.split('<div id="content"')[-1]
            result = client.parseDOM(result, 'li', attrs={'class':'media'})
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a',ret='title')[0]) for i in result]
            myses = 's%02de%02d' % (int(season), int(episode))
            result = [i[0] for i in result if myses in i[0]][0]
            return result
        except:
            return None

    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []
            mylinks = []
            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            result = client.request(url)
            r = re.compile('function ccc.*\s.*\s.*\s.*trurl=(.*)"').findall(result)

            did = client.parseDOM(result, 'img',attrs={'id':'gmodal1'}, ret='data-token')
            myurl = self.info_link + '?did=%s&trurl=%s' % (did,r)
            url = urlparse.urljoin(self.base_link, myurl)
            result = client.request(url)
            #print result
            #  <li><a href="#a4" id="b4" data-toggle="tab" onclick="clearp();">LEKTOR (2)</a></li>
            #nav nav-tabs embedlista
            r1 = client.parseDOM(result, 'ul',attrs={'class':'nav nav-tabs embedlista'})[0]
            r1 = client.parseDOM(r1, 'li')
            r1 = [(client.parseDOM(result, 'a',attrs={'data-toggle':'tab'}, ret='href')[0].replace('#',''),
                   client.parseDOM(result, 'a',attrs={'data-toggle':'tab'})[0]) for i in r1]

            for j in r1:
                r2 = client.parseDOM(result, 'div', attrs={'id': str(j[0])})[0]
                r2 = client.parseDOM(result, 'dd', attrs={'class': 'linkplayer'}, ret='onclick')
                r2 = [re.compile("openplayer\('(.*?)', '(.*?)', this\);").findall(i)[0] for i in r2]

                for i in r2:
                    try:
                        vtype = 'BD'
                        if 'LEKTOR' in str(j[1]): vtype = 'Lektor'
                        if 'NAPISY' in str(j[1]): vtype = 'Napisy'

                        sources.append({'source': i[1].split('.')[-2], 'quality': 'SD', 'provider': 'Serialeonline', 'url': i[0], 'vtype':vtype})
                    except:
                        pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = resolvers.request(url)
            return url
        except:
            return

