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
from resources.lib.libraries import client2
from resources.lib.libraries import control

from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'https://cda-online.pl'
        self.search_link = '/?s=%s'
        #self.episode_link = '-Season-%01d-Episode-%01d'


    def get_movie(self, imdb, title, year,originaltitle):
        print("cda online originaltitle:%s" % originaltitle)
        try:
            query = self.search_link % (urllib.unquote(title))
            query = urlparse.urljoin(self.base_link, query)
            control.log('cda-online URL %s' % query)
            result = client2.http_get(query)
            result = client.parseDOM(result, 'div', attrs={'class':'item'})
            #print('cda-online',result)
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'h2')[0], client.parseDOM(i, 'span', attrs={'class':'year'})[0]) for i in result]
            #print('cda-online2',result)
            result = [i for i in result if cleantitle.movie(title) in cleantitle.movie(i[1])]
            #print('cda-online3',result)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
            result = [i[0] for i in result if any(x in i[2] for x in years)][0]
            #print('cda-online4',result)
            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            control.log('ALLTUBE URL %s' % url)
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

            result = client2.http_get(url)
            links = client.parseDOM(result, 'div', attrs={'class':'movieplay'})
            links = [client.parseDOM(i, 'iframe', ret='src')[0] for i in links]

            for i in links:
                try:
                    host = urlparse.urlparse(i).netloc
                    host = host.replace('www.', '').replace('embed.', '')
                    host = host.rsplit('.', 1)[0]
                    host = host.lower()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({'source': host, 'quality': 'SD', 'provider': 'CdaOnline', 'url': i, 'vtype':'BD'})
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

