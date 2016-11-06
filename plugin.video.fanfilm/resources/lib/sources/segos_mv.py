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

from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://segos.es'
        self.search_link = '/szukaj.php?title=%s'
        #self.episode_link = '-Season-%01d-Episode-%01d'


    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.query2(title)))
            query = urlparse.urljoin(self.base_link, query)
            result = client.request(query)
            title = cleantitle.movie(title)
            result = client.parseDOM(result, 'div', attrs={'class':'well_2'})
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a')[0],str(re.findall(r"(\d{4})", client.parseDOM(i, 'a')[0])[0])) for i in result]
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
            result = [i for i in result if title in cleantitle.movie(i[1])]
            result = [i[0] for i in result if any(x in i[2] for x in years)][0]

            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            control.log('Segos URL %s' % url)
            return url
        except:
            return


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            query = self.moviesearch_link % (urllib.unquote(tvshowtitle))
            query = urlparse.urljoin(self.base_link, query)
            control.log('ALLTUBE URL %s' % query)

            result = client.source(query)
            result = json.loads(result)
            control.log('ALLTUBE URL %s' % result)

            control.log('ALLTUBE tvshowtitle %s' % tvshowtitle)

            tvshowtitle = cleantitle.tv(tvshowtitle)
            control.log('ALLTUBE tvshowtitle %s' % tvshowtitle)

            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'h2', ret='title')[0], client.parseDOM(i, 'span', attrs = {'itemprop': 'copyrightYear'})) for i in result]
            result = [i for i in result if len(i[2]) > 0]
            result = [i for i in result if tvshowtitle == cleantitle.tv(i[1])]
            result = [i[0] for i in result if any(x in i[2][0] for x in years)][0]

            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        if url == None: return

        url += self.episode_link % (int(season), int(episode))
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        return url


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            result = client.request(url)
            vtype = re.findall('<div class="col-lg-9 col-md-9 col-sm-9">\s.*<b>Język</b>:(.*?)\.*</div>',result)[0].strip()
            q = re.findall('<div class="col-lg-9 col-md-9 col-sm-9">\s.*<b>Jakość</b>:(.*?)\.*</div>', result)[0].strip()
            print "v",vtype, q
            quality = 'SD'
            if '720' in q: quality = 'HD'
            if '1080' in q: quality = '1080p'

            links = client.parseDOM(result, 'div', attrs={'id':'Film'})
            print links
            links = [client.parseDOM(i, 'a', ret='href', attrs={'target':'_blank'})[0] for i in links]
            print "links",links
            for i in links:
                try:
                    host = urlparse.urlparse(i).netloc
                    host = host.split('.')
                    host = host[-2]+"."+host[-1]
                    host = host.lower()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'provider': 'SEGOS', 'url': i, 'vtype':vtype})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        control.log('CDA-ONLINE RESOLVE URL %s' % url)

        try:
            url = resolvers.request(url)
            return url
        except:
            return

