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
        try:
            query = self.moviesearch_link % urllib.quote_plus(cleantitle.query2(title))
            query = urlparse.urljoin(self.base_link, query)
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
            try:
                query = self.moviesearch_link % cleantitle.query_quote(originaltitle)
                query = urlparse.urljoin(self.base_link, query)
                result = client.source(query)
                result = json.loads(result)

                result = [i for i in result['suggestions'] if len(i) > 0]
                years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]
                result = [(i['data'].encode('utf8'),i['value'].encode('utf8')) for i in result]
                result = [i for i in result if cleantitle.movie(originaltitle) in cleantitle.movie(i[1])]
                result = [i[0] for i in result if any(x in i[1] for x in years)][0]

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
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        try:
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            result = cache.get(self.tvshow_cache, 120)
            tvshowtitle = cleantitle.get(url['tvshowtitle'])
            for i in result:
                if cleantitle.get(tvshowtitle) in cleantitle.get(i[1]):
                    #print("MAM", i)
                    a=1

            result = [i[0] for i in result if cleantitle.get(tvshowtitle) in cleantitle.get(i[1])][0]
            txts = 's%02de%02d' % (int(season),int(episode))

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
            #c = client.request(u output='cookie', error=True)

            links = client.parseDOM(result, 'tr')
            links = [(client.parseDOM(i, 'a', attrs = {'class': 'watch'}, ret='data-iframe')[0],
                    client.parseDOM(i, 'img', ret='alt')[0],
                    client.parseDOM(i, 'td', attrs={'class':'text-center'})[0]) for i in links]

            for i in links:
                try:
                    url1 = '%s?%s' % (url, i[0])
                    url1 = url1.encode('utf-8')
                    #print ("Q",videoquality.solvequality(url),url)
                    sources.append({'source': i[1].encode('utf-8'), 'quality': 'SD', 'provider': 'Alltube', 'url': url1, 'vtype':i[2].encode('utf-8')})
                except Exception as e:
                    control.log('Alltube sources Exception: %s' % e)
                    pass
            #control.log('Alltube sources : %s' % sources)

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            myurl = url.split('?')

            control.log('ALLTUBE RESOLVE URL %s' % str(myurl))
            control.log('ALLTUBE RESOLVE URL %s' % str(myurl[-1].decode('base64')))


            try:
                mycookie = client.request(myurl[0], output='cookie', error=True)

                tmp = 'ZGVmIGFiYyhpbl9hYmMpOg0KICAgIGRlZiByaGV4KGEpOg0KICAgICAgICBoZXhfY2hyID0gJzAxMjM0NTY3ODlhYmNkZWYnDQogICAgICAgIHJldCA9ICcnDQogICAgICAgIGZvciBpIGluIHJhbmdlKDQpOg0KICAgICAgICAgICAgcmV0ICs9IGhleF9jaHJbKGEgPj4gKGkgKiA4ICsgNCkpICYgMHgwRl0gKyBoZXhfY2hyWyhhID4+IChpICogOCkpICYgMHgwRl0NCiAgICAgICAgcmV0dXJuIHJldA0KICAgIGRlZiBoZXgodGV4dCk6DQogICAgICAgIHJldCA9ICcnDQogICAgICAgIGZvciBpIGluIHJhbmdlKGxlbih0ZXh0KSk6DQogICAgICAgICAgICByZXQgKz0gcmhleCh0ZXh0W2ldKQ0KICAgICAgICByZXR1cm4gcmV0DQogICAgZGVmIGFkZDMyKGEsIGIpOg0KICAgICAgICByZXR1cm4gKGEgKyBiKSAmIDB4RkZGRkZGRkYNCiAgICBkZWYgY21uKGEsIGIsIGMsIGQsIGUsIGYpOg0KICAgICAgICBiID0gYWRkMzIoYWRkMzIoYiwgYSksIGFkZDMyKGQsIGYpKTsNCiAgICAgICAgcmV0dXJuIGFkZDMyKChiIDw8IGUpIHwgKGIgPj4gKDMyIC0gZSkpLCBjKQ0KICAgIGRlZiBmZihhLCBiLCBjLCBkLCBlLCBmLCBnKToNCiAgICAgICAgcmV0dXJuIGNtbigoYiAmIGMpIHwgKCh+YikgJiBkKSwgYSwgYiwgZSwgZiwgZykNCiAgICBkZWYgZ2coYSwgYiwgYywgZCwgZSwgZiwgZyk6DQogICAgICAgIHJldHVybiBjbW4oKGIgJiBkKSB8IChjICYgKH5kKSksIGEsIGIsIGUsIGYsIGcpDQogICAgZGVmIGhoKGEsIGIsIGMsIGQsIGUsIGYsIGcpOg0KICAgICAgICByZXR1cm4gY21uKGIgXiBjIF4gZCwgYSwgYiwgZSwgZiwgZykNCiAgICBkZWYgaWkoYSwgYiwgYywgZCwgZSwgZiwgZyk6DQogICAgICAgIHJldHVybiBjbW4oYyBeIChiIHwgKH5kKSksIGEsIGIsIGUsIGYsIGcpDQogICAgZGVmIGNyeXB0Y3ljbGUodGFiQSwgdGFiQik6DQogICAgICAgIGEgPSB0YWJBWzBdDQogICAgICAgIGIgPSB0YWJBWzFdDQogICAgICAgIGMgPSB0YWJBWzJdDQogICAgICAgIGQgPSB0YWJBWzNdDQogICAgICAgIGEgPSBmZihhLCBiLCBjLCBkLCB0YWJCWzBdLCA3LCAtNjgwODc2OTM2KTsNCiAgICAgICAgZCA9IGZmKGQsIGEsIGIsIGMsIHRhYkJbMV0sIDEyLCAtMzg5NTY0NTg2KTsNCiAgICAgICAgYyA9IGZmKGMsIGQsIGEsIGIsIHRhYkJbMl0sIDE3LCA2MDYxMDU4MTkpOw0KICAgICAgICBiID0gZmYoYiwgYywgZCwgYSwgdGFiQlszXSwgMjIsIC0xMDQ0NTI1MzMwKTsNCiAgICAgICAgYSA9IGZmKGEsIGIsIGMsIGQsIHRhYkJbNF0sIDcsIC0xNzY0MTg4OTcpOw0KICAgICAgICBkID0gZmYoZCwgYSwgYiwgYywgdGFiQls1XSwgMTIsIDEyMDAwODA0MjYpOw0KICAgICAgICBjID0gZmYoYywgZCwgYSwgYiwgdGFiQls2XSwgMTcsIC0xNDczMjMxMzQxKTsNCiAgICAgICAgYiA9IGZmKGIsIGMsIGQsIGEsIHRhYkJbN10sIDIyLCAtNDU3MDU5ODMpOw0KICAgICAgICBhID0gZmYoYSwgYiwgYywgZCwgdGFiQls4XSwgNywgMTc3MDAzNTQxNik7DQogICAgICAgIGQgPSBmZihkLCBhLCBiLCBjLCB0YWJCWzldLCAxMiwgLTE5NTg0MTQ0MTcpOw0KICAgICAgICBjID0gZmYoYywgZCwgYSwgYiwgdGFiQlsxMF0sIDE3LCAtNDIwNjMpOw0KICAgICAgICBiID0gZmYoYiwgYywgZCwgYSwgdGFiQlsxMV0sIDIyLCAtMTk5MDQwNDE2Mik7DQogICAgICAgIGEgPSBmZihhLCBiLCBjLCBkLCB0YWJCWzEyXSwgNywgMTgwNDYwMzY4Mik7DQogICAgICAgIGQgPSBmZihkLCBhLCBiLCBjLCB0YWJCWzEzXSwgMTIsIC00MDM0MTEwMSk7DQogICAgICAgIGMgPSBmZihjLCBkLCBhLCBiLCB0YWJCWzE0XSwgMTcsIC0xNTAyMDAyMjkwKTsNCiAgICAgICAgYiA9IGZmKGIsIGMsIGQsIGEsIHRhYkJbMTVdLCAyMiwgMTIzNjUzNTMyOSk7DQogICAgICAgIGEgPSBnZyhhLCBiLCBjLCBkLCB0YWJCWzFdLCA1LCAtMTY1Nzk2NTEwKTsNCiAgICAgICAgZCA9IGdnKGQsIGEsIGIsIGMsIHRhYkJbNl0sIDksIC0xMDY5NTAxNjMyKTsNCiAgICAgICAgYyA9IGdnKGMsIGQsIGEsIGIsIHRhYkJbMTFdLCAxNCwgNjQzNzE3NzEzKTsNCiAgICAgICAgYiA9IGdnKGIsIGMsIGQsIGEsIHRhYkJbMF0sIDIwLCAtMzczODk3MzAyKTsNCiAgICAgICAgYSA9IGdnKGEsIGIsIGMsIGQsIHRhYkJbNV0sIDUsIC03MDE1NTg2OTEpOw0KICAgICAgICBkID0gZ2coZCwgYSwgYiwgYywgdGFiQlsxMF0sIDksIDM4MDE2MDgzKTsNCiAgICAgICAgYyA9IGdnKGMsIGQsIGEsIGIsIHRhYkJbMTVdLCAxNCwgLTY2MDQ3ODMzNSk7DQogICAgICAgIGIgPSBnZyhiLCBjLCBkLCBhLCB0YWJCWzRdLCAyMCwgLTQwNTUzNzg0OCk7DQogICAgICAgIGEgPSBnZyhhLCBiLCBjLCBkLCB0YWJCWzldLCA1LCA1Njg0NDY0MzgpOw0KICAgICAgICBkID0gZ2coZCwgYSwgYiwgYywgdGFiQlsxNF0sIDksIC0xMDE5ODAzNjkwKTsNCiAgICAgICAgYyA9IGdnKGMsIGQsIGEsIGIsIHRhYkJbM10sIDE0LCAtMTg3MzYzOTYxKTsNCiAgICAgICAgYiA9IGdnKGIsIGMsIGQsIGEsIHRhYkJbOF0sIDIwLCAxMTYzNTMxNTAxKTsNCiAgICAgICAgYSA9IGdnKGEsIGIsIGMsIGQsIHRhYkJbMTNdLCA1LCAtMTQ0NDY4MTQ2Nyk7DQogICAgICAgIGQgPSBnZyhkLCBhLCBiLCBjLCB0YWJCWzJdLCA5LCAtNTE0MDM3ODQpOw0KICAgICAgICBjID0gZ2coYywgZCwgYSwgYiwgdGFiQls3XSwgMTQsIDE3MzUzMjg0NzMpOw0KICAgICAgICBiID0gZ2coYiwgYywgZCwgYSwgdGFiQlsxMl0sIDIwLCAtMTkyNjYwNzczNCk7DQogICAgICAgIGEgPSBoaChhLCBiLCBjLCBkLCB0YWJCWzVdLCA0LCAtMzc4NTU4KTsNCiAgICAgICAgZCA9IGhoKGQsIGEsIGIsIGMsIHRhYkJbOF0sIDExLCAtMjAyMjU3NDQ2Myk7DQogICAgICAgIGMgPSBoaChjLCBkLCBhLCBiLCB0YWJCWzExXSwgMTYsIDE4MzkwMzA1NjIpOw0KICAgICAgICBiID0gaGgoYiwgYywgZCwgYSwgdGFiQlsxNF0sIDIzLCAtMzUzMDk1NTYpOw0KICAgICAgICBhID0gaGgoYSwgYiwgYywgZCwgdGFiQlsxXSwgNCwgLTE1MzA5OTIwNjApOw0KICAgICAgICBkID0gaGgoZCwgYSwgYiwgYywgdGFiQls0XSwgMTEsIDEyNzI4OTMzNTMpOw0KICAgICAgICBjID0gaGgoYywgZCwgYSwgYiwgdGFiQls3XSwgMTYsIC0xNTU0OTc2MzIpOw0KICAgICAgICBiID0gaGgoYiwgYywgZCwgYSwgdGFiQlsxMF0sIDIzLCAtMTA5NDczMDY0MCk7DQogICAgICAgIGEgPSBoaChhLCBiLCBjLCBkLCB0YWJCWzEzXSwgNCwgNjgxMjc5MTc0KTsNCiAgICAgICAgZCA9IGhoKGQsIGEsIGIsIGMsIHRhYkJbMF0sIDExLCAtMzU4NTM3MjIyKTsNCiAgICAgICAgYyA9IGhoKGMsIGQsIGEsIGIsIHRhYkJbM10sIDE2LCAtNzIyNTIxOTc5KTsNCiAgICAgICAgYiA9IGhoKGIsIGMsIGQsIGEsIHRhYkJbNl0sIDIzLCA3NjAyOTE4OSk7DQogICAgICAgIGEgPSBoaChhLCBiLCBjLCBkLCB0YWJCWzldLCA0LCAtNjQwMzY0NDg3KTsNCiAgICAgICAgZCA9IGhoKGQsIGEsIGIsIGMsIHRhYkJbMTJdLCAxMSwgLTQyMTgxNTgzNSk7DQogICAgICAgIGMgPSBoaChjLCBkLCBhLCBiLCB0YWJCWzE1XSwgMTYsIDUzMDc0MjUyMCk7DQogICAgICAgIGIgPSBoaChiLCBjLCBkLCBhLCB0YWJCWzJdLCAyMywgLTk5NTMzODY1MSk7DQogICAgICAgIGEgPSBpaShhLCBiLCBjLCBkLCB0YWJCWzBdLCA2LCAtMTk4NjMwODQ0KTsNCiAgICAgICAgZCA9IGlpKGQsIGEsIGIsIGMsIHRhYkJbN10sIDEwLCAxMTI2ODkxNDE1KTsNCiAgICAgICAgYyA9IGlpKGMsIGQsIGEsIGIsIHRhYkJbMTRdLCAxNSwgLTE0MTYzNTQ5MDUpOw0KICAgICAgICBiID0gaWkoYiwgYywgZCwgYSwgdGFiQls1XSwgMjEsIC01NzQzNDA1NSk7DQogICAgICAgIGEgPSBpaShhLCBiLCBjLCBkLCB0YWJCWzEyXSwgNiwgMTcwMDQ4NTU3MSk7DQogICAgICAgIGQgPSBpaShkLCBhLCBiLCBjLCB0YWJCWzNdLCAxMCwgLTE4OTQ5ODY2MDYpOw0KICAgICAgICBjID0gaWkoYywgZCwgYSwgYiwgdGFiQlsxMF0sIDE1LCAtMTA1MTUyMyk7DQogICAgICAgIGIgPSBpaShiLCBjLCBkLCBhLCB0YWJCWzFdLCAyMSwgLTIwNTQ5MjI3OTkpOw0KICAgICAgICBhID0gaWkoYSwgYiwgYywgZCwgdGFiQls4XSwgNiwgMTg3MzMxMzM1OSk7DQogICAgICAgIGQgPSBpaShkLCBhLCBiLCBjLCB0YWJCWzE1XSwgMTAsIC0zMDYxMTc0NCk7DQogICAgICAgIGMgPSBpaShjLCBkLCBhLCBiLCB0YWJCWzZdLCAxNSwgLTE1NjAxOTgzODApOw0KICAgICAgICBiID0gaWkoYiwgYywgZCwgYSwgdGFiQlsxM10sIDIxLCAxMzA5MTUxNjQ5KTsNCiAgICAgICAgYSA9IGlpKGEsIGIsIGMsIGQsIHRhYkJbNF0sIDYsIC0xNDU1MjMwNzApOw0KICAgICAgICBkID0gaWkoZCwgYSwgYiwgYywgdGFiQlsxMV0sIDEwLCAtMTEyMDIxMDM3OSk7DQogICAgICAgIGMgPSBpaShjLCBkLCBhLCBiLCB0YWJCWzJdLCAxNSwgNzE4Nzg3MjU5KTsNCiAgICAgICAgYiA9IGlpKGIsIGMsIGQsIGEsIHRhYkJbOV0sIDIxLCAtMzQzNDg1NTUxKTsNCiAgICAgICAgdGFiQVswXSA9IGFkZDMyKGEsIHRhYkFbMF0pOw0KICAgICAgICB0YWJBWzFdID0gYWRkMzIoYiwgdGFiQVsxXSk7DQogICAgICAgIHRhYkFbMl0gPSBhZGQzMihjLCB0YWJBWzJdKTsNCiAgICAgICAgdGFiQVszXSA9IGFkZDMyKGQsIHRhYkFbM10pDQogICAgZGVmIGNyeXB0YmxrKHRleHQpOg0KICAgICAgICByZXQgPSBbXQ0KICAgICAgICBmb3IgaSBpbiByYW5nZSgwLCA2NCwgNCk6DQogICAgICAgICAgICByZXQuYXBwZW5kKG9yZCh0ZXh0W2ldKSArIChvcmQodGV4dFtpKzFdKSA8PCA4KSArIChvcmQodGV4dFtpKzJdKSA8PCAxNikgKyAob3JkKHRleHRbaSszXSkgPDwgMjQpKQ0KICAgICAgICByZXR1cm4gcmV0DQogICAgZGVmIGpjc3lzKHRleHQpOg0KICAgICAgICB0eHQgPSAnJzsNCiAgICAgICAgdHh0TGVuID0gbGVuKHRleHQpDQogICAgICAgIHJldCA9IFsxNzMyNTg0MTkzLCAtMjcxNzMzODc5LCAtMTczMjU4NDE5NCwgMjcxNzMzODc4XQ0KICAgICAgICBpID0gNjQNCiAgICAgICAgd2hpbGUgaSA8PSBsZW4odGV4dCk6DQogICAgICAgICAgICBjcnlwdGN5Y2xlKHJldCwgY3J5cHRibGsodGV4dFsnc3Vic3RyaW5nJ10oaSAtIDY0LCBpKSkpDQogICAgICAgICAgICBpICs9IDY0DQogICAgICAgIHRleHQgPSB0ZXh0W2kgLSA2NDpdDQogICAgICAgIHRtcCA9IFswLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwLCAwXQ0KICAgICAgICBpID0gMA0KICAgICAgICB3aGlsZSBpIDwgbGVuKHRleHQpOg0KICAgICAgICAgICAgdG1wW2kgPj4gMl0gfD0gb3JkKHRleHRbaV0pIDw8ICgoaSAlIDQpIDw8IDMpDQogICAgICAgICAgICBpICs9IDENCiAgICAgICAgdG1wW2kgPj4gMl0gfD0gMHg4MCA8PCAoKGkgJSA0KSA8PCAzKQ0KICAgICAgICBpZiBpID4gNTU6DQogICAgICAgICAgICBjcnlwdGN5Y2xlKHJldCwgdG1wKTsNCiAgICAgICAgICAgIGZvciBpIGluIHJhbmdlKDE2KToNCiAgICAgICAgICAgICAgICB0bXBbaV0gPSAwDQogICAgICAgIHRtcFsxNF0gPSB0eHRMZW4gKiA4Ow0KICAgICAgICBjcnlwdGN5Y2xlKHJldCwgdG1wKTsNCiAgICAgICAgcmV0dXJuIHJldA0KICAgIGRlZiByZXplZG93YSh0ZXh0KToNCiAgICAgICAgcmV0dXJuIGhleChqY3N5cyh0ZXh0KSkNCiAgICByZXR1cm4gcmV6ZWRvd2EoaW5fYWJjKQ0K'
                tmp = base64.b64decode(tmp)
                _myFun = compile(tmp, '', 'exec')
                vGlobals = {"__builtins__": None, 'len': len, 'list': list, 'ord': ord, 'range': range}
                vLocals = {'abc': ''}
                exec _myFun in vGlobals, vLocals
                myFun1 = vLocals['abc']
            except Exception as e:
                control.log('Altube err1 [%s]' % e)
            control.log('ALLTUBE cokie URL %s' % str(mycookie))

            data = client.request(urlparse.urljoin(self.base_link, '/jsverify.php?op=tag'), cookie=mycookie)
            try:
                data = client.byteify(json.loads(data))
                d = {}
                for i in range(len(data['key'])):
                    d[data['key'][i]] = data['hash'][i]
                tmp = ''
                for k in sorted(d.keys()):
                    tmp += d[k]
                mycookie = 'tmvh=%s;%s' % (myFun1(tmp),mycookie)

            except Exception as e:
                control.log('Altube err3 [%s]' % e)

            control.log("XXXXXXXXXXX %s" % mycookie)

            # http://alltube.tv/special.php?hosting=openload&id=oU9oQLz4F-U&width=673&height=471.09999999999997
            link = client.request(myurl[-1].decode('base64')+ '&width=673&height=471.09999999999997', cookie=mycookie)
            match = re.search('<iframe src="(.+?)"', link)
            if match:
                control.log('Altube  link [%s]' % match.group(1))
                linkVideo = match.group(1)
                return resolvers.request(linkVideo)
            return
        except:
            return

