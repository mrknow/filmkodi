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
        self.base_link = 'http://filiser.tv/'
        self.search_link = '/szukaj?q=%s'
        self.tvsearch_cache = 'http://alltube.tv/seriale-online/'
        self.episode_link = '-Season-%01d-Episode-%01d'
        self.url_transl = 'embed?salt=%s'



    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.query2(title)))
            query = urlparse.urljoin(self.base_link, query)
            result = client.request(query)
            result = result.decode('utf-8-sig')
            result = client.parseDOM(result, 'ul', attrs={'id': 'resultList2'})[0]
            result = client.parseDOM(result, 'li')
            result = [(client.parseDOM(i,'div', attrs={'class':'title'}),
                       client.parseDOM(i, 'div', attrs={'class': 'info'}),
                       client.parseDOM(i, 'a', ret='href')[0]) for i in result]
            result = [(i[0][0], re.findall(r"(\d{4})", i[1][0])[0], i[2]) for i in result]

            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
            result = [i for i in result if cleantitle.movie(title) in cleantitle.movie(i[0])]
            result = [i[2] for i in result if any(x in i[1] for x in years)][0]

            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
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
            query = self.search_link % (urllib.quote_plus(cleantitle.query2(tvshowtitle)))
            query = urlparse.urljoin(self.base_link, query)
            result = client.request(query)
            result = result.decode('utf-8-sig')
            result = client.parseDOM(result, 'ul', attrs={'id': 'resultList2'})[0]
            result = client.parseDOM(result, 'li')
            result = [(client.parseDOM(i,'div', attrs={'class':'title'}),
                       client.parseDOM(i, 'div', attrs={'class': 'info'}),
                       client.parseDOM(i, 'a', ret='href')[0]) for i in result]
            result = [(i[0][0], re.findall(r"(\d{4})", i[1][0])[0], i[2]) for i in result]

            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
            result = [i for i in result if cleantitle.movie(tvshowtitle) in cleantitle.movie(i[0])]
            result = [i[2] for i in result if any(x in i[1] for x in years)][0]

            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            print url
            return url

        except:
            return

    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        try:
            if url == None: return

            url = urlparse.urljoin(self.base_link, url)
            result = client.request(url)
            result = client.parseDOM(result, 'ul', attrs={'data-season-num': season})[0]
            result = client.parseDOM(result, 'li')
            for i in result:
                s = client.parseDOM(i, 'a', attrs={'class': 'episodeNum'})[0]
                e = int(s[7:-1])
                if e == int(episode):
                    return client.parseDOM(i, 'a', attrs={'class': 'episodeNum'}, ret='href')[0]

        except:
            return

    def get_sources(self, url, hosthdDict, hostDict, locDict):
        #sources.append({'source': i[1], 'quality': 'SD', 'provider': 'Alltube', 'url': url, 'vtype':i[2]})
        sources = []
        try:

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            result = client.request(url)
            result = client.parseDOM(result, 'div', attrs={'id': 'links'})
            attr = client.parseDOM(result, 'ul', ret='data-type')
            result = client.parseDOM(result, 'ul')
            for x in range(0, len(result)):
                transl_type = attr[x]
                links = result[x]
                sources += self.extract_sources(transl_type, links)

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            url_to_exec = urlparse.urljoin(self.base_link, self.url_transl) % url
            result = client.request(url_to_exec)

            m = re.search("(?<=var url = ')(.*\n?)(?=')", result)

            result_url = m.group(0)
            result_url = result_url.replace('#WIDTH', '100')
            result_url = result_url.replace('#HEIGHT', '100')
            url = resolvers.request(result_url)
            return url
        except:
            return


    def extract_sources(self, transl_type, links):
        sources = []
        data_refs = client.parseDOM(links, 'li', ret='data-ref')
        result = client.parseDOM(links, 'li')

        lang, info = self.get_lang_by_type(transl_type)

        for i in range(0, len(result)):

            el = result[i];
            host = client.parseDOM(el, 'span', attrs={'class': 'host'})[0]
            quality = client.parseDOM(el, 'span', attrs={'class': 'quality'})[0]
            q = 'SD'
            if quality.endswith('720p'):
                q = 'HD'
            elif quality.endswith('1080p'):
                q = '1080p'

            sources.append({'provider': 'Filister', 'source': host, 'quality': q, 'url': data_refs[i], 'vtype': info})

        return sources

    def get_lang_by_type(self, lang_type):
        if lang_type == 'DUBBING':
            return 'pl', 'Dubbing'
        elif lang_type == 'NAPISY_PL':
            return 'pl', 'Napisy'
        if lang_type == 'LEKTOR_PL':
            return 'pl', 'Lektor'
        elif lang_type == 'POLSKI':
            return 'pl', None
        return 'en', None