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
import HTMLParser



class source:
    def __init__(self):
        self.base_link = 'http://filmy.to'
        self.search_link = '/szukaj?q=%s'
        self.verify = '/ajax/view'
        self.provision = '/ajax/provision/%s'

        self.html_parser = HTMLParser.HTMLParser()

    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)
            result = client.request(query)
            result = client.parseDOM(result, 'div', attrs={'class': 'movie clearfix'})
            result = [(client.parseDOM(i, 'a', ret='href'),
                  client.parseDOM(i, 'span', attrs={'class': 'title-pl'}),
                  client.parseDOM(i, 'span', attrs={'class': 'title-en'}),
                  client.parseDOM(i, 'img', ret='src'),
                  client.parseDOM(i, 'p'),
                  client.parseDOM(i, 'p', attrs={'class': 'plot'})) for i in result ]

            result = [(i[0][0], u" ".join(i[1]+i[2]),  re.findall('(\d{4})', i[4][0])) for i in result]

            result = [i for i in result if cleantitle.movie(title) in cleantitle.movie(i[1])]
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
            result = [i[0] for i in result if any(x in i[2] for x in years)][0]


            try: url = re.compile('//.+?(/.+)').findall(result)[0]
            except: url = result
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            control.log('FILMYTO URL %s' % url)
            return url
        except Exception as e:
            control.log('FILMYTO getmovie ERROR  %s' % e)
            return


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            query = self.search_link % (urllib.quote_plus(tvshowtitle))
            query = urlparse.urljoin(self.base_link, query)
            result = client.request(query)
            result = client.parseDOM(result, 'div', attrs={'class': 'movie clearfix'})
            result = [(client.parseDOM(i, 'a', ret='href'),
                  client.parseDOM(i, 'span', attrs={'class': 'title-pl'}),
                  client.parseDOM(i, 'span', attrs={'class': 'title-en'}),
                  client.parseDOM(i, 'img', ret='src'),
                  client.parseDOM(i, 'p'),
                  client.parseDOM(i, 'p', attrs={'class': 'plot'})) for i in result ]

            result = [(i[0][0], u" ".join(i[1]+i[2]),  re.findall('(\d{4})', i[4][0])) for i in result]
            result = [i for i in result if 'serial' in i[0]]
            result = [i for i in result if cleantitle.movie(tvshowtitle) in cleantitle.movie(i[1])]
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
            result = [i[0] for i in result if any(x in i[2] for x in years)][0]
            url = result
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        try:
            if url == None: return
            myurl = re.findall('(s\d{2}e\d{2})',url)[0]
            myepisode = 's%02de%02d' % (int(season), int(episode))
            url = url.replace(myurl,myepisode)

            return url
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            control.log('Filmyto URL %s' % url)

            sources = []

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)
            result,headers,oth,cookie = client.request(url, output='extended')
            r = client.parseDOM(result, 'iframe',attrs={'class':'hidden'}, ret='src')
            headers['cookie']=cookie
            csrftoken = re.findall('post\("/ajax/view", {"view": "(.*?)"}\);', result)[0]
            provision = client.parseDOM(result, 'meta', attrs={'property':'provision'}, ret='content')[0]
            post = urllib.urlencode({'view': csrftoken})
            headers['X-CSRFToken'] = csrftoken
            headers['X-Requested-With']="XMLHttpRequest"
            r2 = client.request(urlparse.urljoin(self.base_link, self.verify), post=post, headers=headers)
            #http://filmy.to/ajax/view
            r = client.request(r[0])
            r = client.request(urlparse.urljoin(self.base_link, self.provision % provision), headers=headers)
            r = client.parseDOM(r, 'div', attrs={'class':'host-container pull-left'})

            r = [(client.parseDOM(i, 'div', attrs={'class': 'url'}, ret='data-url'),
                  client.parseDOM(i, 'span', attrs={'class':'label label-default'}),
                  client.parseDOM(i, 'img', attrs={'class': 'ttip'}, ret='title'),
                  ) for i in r]

            r = [(self.html_parser.unescape(i[0][0]), i[1][0], i[2][0]) for i in r]
            r = [(client.parseDOM(i[0], 'iframe', ret='src'), i[1], i[2]) for i in r]
            r = [(i[0][0], i[1], i[2]) for i in r if len(i[0])>0]

            for i in r:
                try:
                    control.log('Filmyto SOURCES %s' % str(i))

                    host = urlparse.urlparse(i[0]).netloc
                    host = host.replace('www.', '').replace('embed.', '')
                    host = host.lower()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    vtype = 'BD'
                    if i[1] == 'Lektor PL': vtype = 'Lektor'
                    if i[1] == 'Napisy PL': vtype = 'Napisy'
                    if i[1] == 'Oryginalna': vtype = 'Orginalny'
                    if i[1] == 'Film polski': vtype = 'Film polski'
                    q='SD'
                    if 'Wysoka' in i[2]: q='HD'
                    #control.log('Filmyto SOURCES %s' % str(q))

                    sources.append({'source': host, 'quality': q, 'provider': 'Filmyto', 'url': i[0], 'vtype':vtype})
                except:
                    pass

            return sources
        except Exception as e:
            control.log('Filmyto sources error %s' % e)

            return sources


    def resolve(self, url):
        control.log('FilmyTO RESOLVE URL %s' % url)

        try:
            myurl =  resolvers.request(url)
            return myurl
        except:
            return

