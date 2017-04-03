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
        self.base_link = 'https://cdax.tv'
        self.search_link = '/wyszukiwarka?phrase=%s'
        self.search_link2 = 'https://api.searchiq.xyz/api/search/results?q=%s&engineKey=%s&page=0&itemsPerPage=40&group=1'
        #self.episode_link = '-Season-%01d-Episode-%01d'


    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)
            control.log('cda-online URL %s' % query)
            result = client.request(query)
            result = re.findall('engineKey: "(.*?)"', result)[0]
            headers = {'Referer':query, 'Accept':'application/json, text/javascript, */*; q=0.01'}
            result  = client.request(self.search_link2 %(urllib.quote_plus(title), result), headers=headers)
            result = json.loads(result)
            result = [(client.cleanhtmltags(i['title']), i['url'])for i in result['main']['records']]
            result = [(i[0], re.findall('(\d{4})', i[0]),i[1]) for i in result]
            #for i in result:
            #    print('cda-online3', i[0], i[1])
            result = [i for i in result if cleantitle.movie(title) in cleantitle.movie(i[0])]
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
            print('>>cda-online4',result)

            result = [i[2] for i in result if any(x in i[1] for x in years)][0]
            print('cda-online4',result)
            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            control.log('CDAX URL %s' % url)
            return url
        except Exception as e:
            control.log('CDAX getmovie ERROR  %s' % e)
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
            tvshowtitle = url['tvshowtitle'][0]
            year = url['year'][0]
            print url, url['tvshowtitle'][0]
            query = self.search_link % (urllib.quote_plus(tvshowtitle))
            query = urlparse.urljoin(self.base_link, query)
            control.log('cda-online URL %s' % query)
            result = client.request(query)
            result = re.findall('engineKey: "(.*?)"', result)[0]
            headers = {'Referer':query, 'Accept':'application/json, text/javascript, */*; q=0.01'}
            result  = client.request(self.search_link2 %(urllib.quote_plus(tvshowtitle), result), headers=headers)
            result = json.loads(result)
            result = [(client.cleanhtmltags(i['title']), i['url'])for i in result['main']['records']]
            result = [i for i in result if 'seriale' in i[1]]

            result = [i for i in result if cleantitle.movie(tvshowtitle) in cleantitle.movie(i[0])]
            print "r",result, result[0][1]
            result = client.request(result[0][1])
            myyear = client.parseDOM(result, 'sup')
            myepisode = '[s%02de%02d]' % (int(season), int(episode))
            print "r",year, myepisode
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            if not any(x in myyear for x in years): return
            r = client.parseDOM(result, 'div', {"id": "accordion"})[0]
            r = client.parseDOM(r, 'li')
            r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a')) for i in r]
            r = [i[0][0] for i in r if myepisode in i[1][0]]
            try: url = re.compile('//.+?(/.+)').findall(r[0])[0]
            except: url = result

            return url
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            link = client.request(url)
            #print "Link", link
            r = client.parseDOM(link, 'tr')


            r = [(client.parseDOM(i, 'a', ret='href'),
                  client.parseDOM(i, 'img', ret='alt'),
                  client.parseDOM(i, 'td')
                  ) for i in r]


            #for i in r:
            #    control.log('CDAX0 HOSTS %s' % str(i))

            r = [(i[0][1], i[1][0], i[2][0], i[2][1]) for i in r if len(i[0]) > 0]

            #for i in r:
            #    control.log('CDAX HOSTS %s' % str(i))

            for i in r:
                try:
                    host = i[1]
                    host = host.replace('www.', '').replace('embed.', '')
                    host = host.lower()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    sources.append({'source': host, 'quality': 'HD', 'provider': 'CdaOnline', 'url': i[0], 'vtype':i[2]})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        control.log('CDA-ONLINE RESOLVE URL %s' % url)

        try:
            if 'cdax.tv/link/redirect' in url:
                link = client.request(url)
                match = re.search('<a href="(.*?)" class="btn btn-primary">Link do strony z video</a>', link)
                if match:
                    linkVideo = match.group(1).split('http')[-1]
                    linkVideo = 'http' + linkVideo
                    return resolvers.request(linkVideo)
            return resolvers.request(url)
        except:
            return

