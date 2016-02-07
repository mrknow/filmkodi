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


import re,urllib,urlparse,base64

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client


class source:
    def __init__(self):
        self.base_link = 'http://www.animeultima.io'
        self.search_link = '/search.html?searchquery=%s'
        self.tvdb_link = 'http://thetvdb.com/api/%s/series/%s/default/%01d/%01d'
        self.tvdb_key = base64.urlsafe_b64decode('MUQ2MkYyRjkwMDMwQzQ0NA==')


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            query = self.search_link % (urllib.quote_plus(tvshowtitle))
            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query)
            result = result.decode('iso-8859-1').encode('utf-8')
            result = client.parseDOM(result, 'ol', attrs = {'id': 'searchresult'})[0]
            result = client.parseDOM(result, 'h2')

            tvshowtitle = cleantitle.tv(tvshowtitle)
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a')[0]) for i in result]
            result = [(i[0], re.sub('<.+?>|</.+?>','', i[1])) for i in result]
            result = [i for i in result if tvshowtitle == cleantitle.tv(i[1])]
            result = result[-1][0]

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

            tvdb_link = self.tvdb_link % (self.tvdb_key, tvdb, int(season), int(episode))
            result = client.source(tvdb_link)

            num = client.parseDOM(result, 'absolute_number')[0]
            url = urlparse.urljoin(self.base_link, url)

            result = client.source(url)
            result = result.decode('iso-8859-1').encode('utf-8')
            result = client.parseDOM(result, 'tr', attrs = {'class': ''})
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'td', attrs = {'class': 'epnum'})[0]) for i in result]
            result = [i[0] for i in result if num == i[1]][0]

            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)
            sources.append({'source': 'Animeultima', 'quality': 'SD', 'provider': 'Animeultima', 'url': url})
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            result = client.request(url)
            result = result.decode('iso-8859-1').encode('utf-8')

            url = client.parseDOM(result, 'div', attrs = {'class': 'player-embed'})[0]
            url = client.parseDOM(url, 'iframe', ret='src')[0]

            if not 'auengine.com' in url:
                url = client.parseDOM(result, 'div', attrs = {'class': 'generic-video-item'})
                url = [i for i in url if 'auengine video' in i.lower()][0]
                url = client.parseDOM(url, 'a', ret='href')[0]
                url = urlparse.urljoin(self.base_link, url)

                result = client.request(url)
                result = result.decode('iso-8859-1').encode('utf-8')

                url = client.parseDOM(result, 'div', attrs = {'class': 'player-embed'})[0]
                url = client.parseDOM(url, 'iframe', ret='src')[0]

            result = client.request(url)

            url = re.compile("video_link *= *'(.+?)'").findall(result)[0]
            url = urllib.unquote_plus(url)
            return url
        except:
            return

