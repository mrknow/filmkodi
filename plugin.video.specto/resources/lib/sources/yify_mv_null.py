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


import re,urllib,urlparse,json

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client


class source:
    def __init__(self):
        self.base_link = 'http://yify.tv'
        self.search_link = '/wp-admin/admin-ajax.php'
        self.search_link2 = '?s=%s'
        self.pk_link = '/player/pk/pk/plugins/player_p2.php'


    def get_movie(self, imdb, title, year):
        try:
            query = self.search_link2 % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)

            for i in range(5):
                result = client.source(query, close=False)
                if not result == None: break

            result = client.parseDOM(result, 'section', attrs = {'id': 'contentrea'})[0]

            title = cleantitle.movie(title)
            years = ['%s' % str(year), '%s' % str(int(year)+1), '%s' % str(int(year)-1)]

            result = zip(client.parseDOM(result, 'a', ret='href'), client.parseDOM(result, 'a'))
            result = [(i[0], re.compile('(^Watch Full "|^Watch |)(.+? \d{4})').findall(i[1])) for i in result]
            result = [(i[0], i[1][0][-1]) for i in result if len(i[1]) > 0]
            result = [(i[0], re.compile('(.+?) (\d{4})$').findall(i[1])) for i in result]
            result = [(i[0], i[1][0][0], i[1][0][1]) for i in result if len(i[1]) > 0]
            result = [i for i in result if any(x in i[2] for x in years)]
            result = [i[0] for i in result if title == cleantitle.movie(i[1])][0]

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

            base = urlparse.urljoin(self.base_link, url)

            for i in range(5):
                result = client.source(base, close=False)
                if not result == None: break

            result = client.parseDOM(result, 'script', attrs = {'type': 'text/javascript'})
            result = [i for i in result if 'parametros;' in i][0]
            result = 'function' + result.split('function', 1)[-1]
            result = result.rsplit('parametros;', 1)[0] + 'parametros;'


            from resources.lib.libraries import js2py

            result = js2py.evaljs.eval_js(result)
            result = str(result)


            links = re.compile('pic=([^&]+)').findall(result)
            links = [x for y,x in enumerate(links) if x not in links[:y]]

            for i in links:
                try:
                    url = urlparse.urljoin(self.base_link, self.pk_link)
                    post = {'url': i, 'fv': '16', 'sou': 'pic'}

                    result = client.source(url, post=post, referer=base)
                    result = json.loads(result)

                    try: sources.append({'source': 'GVideo', 'quality': '1080p', 'provider': 'YIFY', 'url': [i['url'] for i in result if i['width'] == 1920 and 'google' in i['url']][0]})
                    except: pass
                    try: sources.append({'source': 'GVideo', 'quality': 'HD', 'provider': 'YIFY', 'url': [i['url'] for i in result if i['width'] == 1280 and 'google' in i['url']][0]})
                    except: pass

                    try: sources.append({'source': 'YIFY', 'quality': '1080p', 'provider': 'YIFY', 'url': [i['url'] for i in result if i['width'] == 1920 and not 'google' in i['url']][0]})
                    except: pass
                    try: sources.append({'source': 'YIFY', 'quality': 'HD', 'provider': 'YIFY', 'url': [i['url'] for i in result if i['width'] == 1280 and not 'google' in i['url']][0]})
                    except: pass
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            if 'google' in url:
                url = client.request(url, output='geturl')
                if 'requiressl=yes' in url: url = url.replace('http://', 'https://')
                else: url = url.replace('https://', 'http://')

            else:
                url = '%s|User-Agent=%s' % (url, urllib.quote_plus(client.agent()))

            return url
        except:
            return


