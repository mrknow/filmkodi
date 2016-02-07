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


import re,urllib,urlparse,time

from resources.lib.libraries import client
from resources.lib.libraries import workers
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.resolvers import hugefiles
from resources.lib.resolvers import uploadrocket
from resources.lib.resolvers import uptobox
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://tv-release.net'
        self.search_link = '/?s=%s&cat=TV-720p'
        self.go4up_link_2 = 'http://go4up.com/rd/%s/2'


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            url = tvshowtitle
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        try:
            if url == None: return

            url = '%s S%02dE%02d' % (url, int(season), int(episode))
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            self.sources = []

            if url == None: return self.sources

            query = url.replace('\'', '').replace('.', ' ')
            query = re.sub('\s+',' ',query)
            query = self.base_link + self.search_link % urllib.quote_plus(query)

            result = client.source(query)

            result = client.parseDOM(result, 'table', attrs = {'class': 'posts_table'})

            title, hdlr = re.compile('(.+?) (S\d*E\d*)$').findall(url)[0]
            title = cleantitle.tv(title)
            hdlr = [hdlr]

            links = []

            for i in result:
                try:
                    name = client.parseDOM(i, 'a')[-1]
                    name = client.replaceHTMLCodes(name)

                    url = client.parseDOM(i, 'a', ret='href')[-1]
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|3D)(\.|\)|\]|\s)(.+)', '', name)
                    t = cleantitle.tv(t)
                    if not t == title: raise Exception()

                    y = re.compile('[\.|\(|\[|\s](S\d*E\d*)[\.|\)|\]|\s]').findall(name)[-1]
                    if not any(x == y for x in hdlr): raise Exception()

                    fmt = re.sub('(.+)(\.|\(|\[|\s)(S\d*E\d*)(\.|\)|\]|\s)', '', name)
                    fmt = re.split('\.|\(|\)|\[|\]|\s|\-', fmt)
                    fmt = [x.lower() for x in fmt]

                    if not '720p' in fmt: raise Exception()

                    info = ''
                    size = client.parseDOM(i, 'td')
                    size = [x for x in size if x.endswith((' MB', ' GB'))]
                    if len(size) > 0:
                        size = size[-1]
                        if size.endswith(' GB'): div = 1
                        else: div = 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size))/div
                        info += '%.2f GB' % size

                    links.append({'url': url, 'info': info})
                except:
                    pass


            threads = []
            for i in links[::-1][:2]: threads.append(workers.Thread(self.check, i))
            [i.start() for i in threads]
            for i in range(0, 30 * 2):
                is_alive = [x.is_alive() for x in threads]
                if all(x == False for x in is_alive): break
                time.sleep(0.5)


            return self.sources
        except:
            return self.sources


    def check(self, i):
        try:
            result = client.source(i['url'])
            result = client.parseDOM(result, 'td', attrs = {'class': 'td_cols'})[0]
            result = result.split('"td_heads"')
            result = client.parseDOM(result, 'a', ret='href')

            for url in result:
                try:
                    if 'go4up.com' in url:
                        url = re.compile('//.+?/.+?/([\w]+)').findall(url)[0]
                        url = client.source(self.go4up_link_2 % url)
                        url = client.parseDOM(url, 'div', attrs = {'id': 'linklist'})[0]
                        url = client.parseDOM(url, 'a', ret='href')[0]

                    host = urlparse.urlparse(url).netloc
                    host = host.rsplit('.', 1)[0].split('.', 1)[-1]
                    host = host.strip().lower()

                    if not host in ['uptobox', 'hugefiles', 'uploadrocket']: raise Exception()

                    if host == 'hugefiles': check = hugefiles.check(url)
                    elif host == 'uploadrocket': check = uploadrocket.check(url)
                    elif host == 'uptobox': check = uptobox.check(url)

                    if check == False: raise Exception()

                    self.sources.append({'source': host, 'quality': 'HD', 'provider': 'TVrelease', 'url': url, 'info': i['info']})
                except:
                    pass
        except:
            pass


    def resolve(self, url):
        try:
            url = resolvers.request(url)
            return url
        except:
            return


