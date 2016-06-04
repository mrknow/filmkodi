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

import re,urllib,urlparse,json,base64

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import client2
from resources.lib.libraries import cache
from resources.lib.libraries import control

import cookielib, os
cookie_file = os.path.join(control.dataPath , 'mycookie'+'.cookies')
cj = cookielib.LWPCookieJar()

class source:
    def __init__(self):
        self.base_link = 'http://www.pelispedia.tv'
        self.search_link = 'aHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vY3VzdG9tc2VhcmNoL3YxZWxlbWVudD9rZXk9QUl6YVN5Q1ZBWGlVelJZc01MMVB2NlJ3U0cxZ3VubU1pa1R6UXFZJnJzej1maWx0ZXJlZF9jc2UmbnVtPTEwJmhsPWVuJmN4PTAwMDc0NjAzOTU3ODI1MDQ0NTkzNTp3cW1odGszam5fbyZnb29nbGVob3N0PXd3dy5nb29nbGUuY29tJnE9JXM='
        self.search2_link = '/api/more.php?rangeStart=%s&tipo=serie'
        self.search3_link = '/buscar/?s=%s'


    def get_movie(self, imdb, title, year):
        try:
            t = cleantitle.get(title)

            query = '%s %s' % (title, year)
            query = base64.b64decode(self.search_link) % urllib.quote_plus(query)

            result = client2.http_get(query, headers={'Referer': self.base_link})
            result = json.loads(result)['results']

            result = [(i['url'], i['titleNoFormatting']) for i in result]
            result = [(i[0], re.findall('(?:^Ver |)(.+?)(?: HD |)\((\d{4})', i[1])) for i in result]
            result = [(i[0], i[1][0][0], i[1][0][1]) for i in result if len(i[1]) > 0]

            r = [i for i in result if t == cleantitle.get(i[1]) and year == i[2]]

            if len(r) == 0:
                t = 'http://www.imdb.com/title/%s' % imdb
                t = client.source(t, headers={'Accept-Language': 'es-ES'})
                t = client.parseDOM(t, 'title')[0]
                t = re.sub('(?:\(|\s)\d{4}.+', '', t).strip()
                t = cleantitle.get(t)

                r = [i for i in result if t == cleantitle.get(i[1]) and year == i[2]]

            try:
                url = re.findall('//.+?(/.+)', r[0][0])[0]
            except:
                url = r[0][0]
            try:
                url = re.findall('(/.+?/.+?/)', url)[0]
            except:
                pass
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            return url
        except:
            pass

        try:
            t = cleantitle.get(title)

            query = self.search3_link % urllib.quote_plus(cleantitle.query(title))
            query = urlparse.urljoin(self.base_link, query)

            result = client2.http_get(query)
            result = re.sub(r'[^\x00-\x7F]+', '', result)
            print("R",result)


            r = result.split('<li class=')
            r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'i'), re.findall('\((\d{4})\)', i)) for i in
                 r]
            r = [(i[0][0], re.sub('\(|\)', '', i[1][0]), i[2][0]) for i in r if
                 len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]
            r = [i[0] for i in r if t == cleantitle.get(i[1]) and year == i[2]][0]

            try:
                url = re.findall('//.+?(/.+)', r)[0]
            except:
                url = r
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            return url
        except:
            pass

    def pelispedia_tvcache(self):
        result = []

        for i in range(0, 10):
            try:
                u = self.search2_link % str(i * 48)
                u = urlparse.urljoin(self.base_link, u)

                r = str(client2.http_get(u))
                r = re.sub(r'[^\x00-\x7F]+', '', r)
                r = r.split('<li class=')
                r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'i'), re.findall('\((\d{4})\)', i)) for i
                     in r]
                r = [(i[0][0], re.sub('\(|\)', '', i[1][0]), i[2][0]) for i in r if
                     len(i[0]) > 0 and len(i[1]) > 0 and len(i[2]) > 0]

                if len(r) == 0: break
                result += r
            except:
                pass

        if len(result) == 0: return
        result = [(re.sub('http.+?//.+?/', '/', i[0]), cleantitle.get(i[1]), i[2]) for i in result]
        return result


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            result = cache.get(self.pelispedia_tvcache, 120)

            tvshowtitle = cleantitle.get(tvshowtitle)

            result = [i[0] for i in result if tvshowtitle == i[1] and year == i[2]][0]

            url = urlparse.urljoin(self.base_link, result)
            url = urlparse.urlparse(url).path
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, premiered, season, episode):
        if url == None: return
        url = [i for i in url.split('/') if not i == ''][-1]
        url = '/pelicula/%s-season-%01d-episode-%01d/' % (url, int(season), int(episode))
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')
        return url


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        control.log("><><><><> PELISPEDIA SOURCE %s" % url)
        try:
            sources = []

            if url == None: return sources

            r = urlparse.urljoin(self.base_link, url)

            result = client2.http_get(r)

            f = client.parseDOM(result, 'iframe', ret='src')
            f = [i for i in f if 'iframe' in i][0]

            result = client2.http_get(f, headers={'Referer': r})

            r = client.parseDOM(result, 'div', attrs={'id': 'botones'})[0]
            r = client.parseDOM(r, 'a', ret='href')
            r = [(i, urlparse.urlparse(i).netloc) for i in r]
            r = [i[0] for i in r if 'pelispedia' in i[1]]

            links = []

            for u in r:
                result = client2.http_get(u, headers={'Referer': f})

                try:
                    url = re.findall('sources\s*:\s*\[(.+?)\]', result)[0]
                    url = re.findall('"file"\s*:\s*"(.+?)"', url)
                    url = [i.split()[0].replace('\\/', '/') for i in url]

                    for i in url:
                        try:
                            links.append(
                                {'source': 'gvideo', 'quality': client.googletag(i)[0]['quality'], 'url': i})
                        except:
                            pass
                except:
                    pass

                try:
                    headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': u}

                    post = re.findall('gkpluginsphp.*?link\s*:\s*"([^"]+)', result)[0]
                    post = urllib.urlencode({'link': post})

                    url = urlparse.urljoin(self.base_link, '/Pe_flv_flsh/plugins/gkpluginsphp.php')
                    url = client.source(url, data=post, headers=headers)
                    url = json.loads(url)['link']

                    links.append({'source': 'gvideo', 'quality': 'HD', 'url': url})
                except:
                    pass

                try:
                    headers = {'X-Requested-With': 'XMLHttpRequest'}

                    post = re.findall('var\s+parametros\s*=\s*"([^"]+)', result)[0]
                    post = urlparse.parse_qs(urlparse.urlparse(post).query)['pic'][0]
                    post = urllib.urlencode({'sou': 'pic', 'fv': '21', 'url': post})

                    url = urlparse.urljoin(self.base_link, '/Pe_Player_Html5/pk/pk/plugins/protected.php')
                    url = client2.http_get(url, data=post, headers=headers)
                    url = json.loads(url)[0]['url']

                    links.append({'source': 'cdn', 'quality': 'HD', 'url': url})
                except:
                    pass

            for i in links: sources.append(
                {'source': i['source'], 'quality': i['quality'], 'provider': 'Pelispedia', 'url': i['url'],
                 'direct': True, 'debridonly': False})

            return sources
        except:
            return sources


    def resolve(self, url):
        control.log("##pelispedia %s " % url)

        return url


