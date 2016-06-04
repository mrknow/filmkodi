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


import re,urllib,urlparse,json,base64,time, random,string
import cookielib,os

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import client2

from resources.lib.libraries import control
from resources.lib import resolvers




class source:
    def __init__(self):
        self.domains = ['putlocker.systems']
        self.base_link = 'http://www.putlocker.systems/'
        self.myrandom = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(25))


    def get_movie(self, imdb, title, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []
            control.log('#PUTLOCKER1 %s' % url)

            if url == None: return sources

            if not str(url).startswith('http'):

                data = urlparse.parse_qs(url)
                data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

                title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

                imdb = data['imdb']
                match = title.replace('-', '').replace(':', '').replace('\'', '').replace(' ', '-').replace('--', '-').lower()

                if 'tvshowtitle' in data:
                    url = '%s/show/%s/season/%01d/episode/%01d' % (self.base_link, match, int(data['season']), int(data['episode']))
                else:
                    url = '%s/movie/%s' % (self.base_link, match)
                #control.log('#PUTLOCKER2 %s' % url)

                #result = client.source(url, output='title')
                result = client2.http_get(url)

                if '%TITLE%' in result: raise Exception()

                cookie_file = os.path.join(control.cookieDir, '%s_cookies.lwp' % client2.shrink_host(url))
                #cookie_file = os.path.join('/home/mrknow/.kodi/userdata/addon_data/plugin.video.specto/Cookies','%s_cookies.lwp' % client2.shrink_host((url)))
                cj = cookielib.LWPCookieJar(cookie_file)
                try: cj.load(ignore_discard=True)
                except: pass
                auth = cj._cookies['www.putlocker.systems']['/']['__utmx'].value
                headers = {}

                if not imdb in result: raise Exception()

            else:
                result, headers, content, cookie = client.source(url, output='extended')

            #control.log('#PUTLOCKER3 %s' % auth)

            auth = 'Bearer %s' % urllib.unquote_plus(auth)

            headers['Authorization'] = auth
            headers['X-Requested-With'] = 'XMLHttpRequest'
            headers['Referer'] = url

            u = 'http://www.putlocker.systems/ajax/embeds.php'

            action = 'getEpisodeEmb' if '/episode/' in url else 'getMovieEmb'

            elid = urllib.quote(base64.encodestring(str(int(time.time()))).strip())

            token = re.findall("var\s+tok\s*=\s*'([^']+)", result)[0]

            idEl = re.findall('elid\s*=\s*"([^"]+)', result)[0]

            post = {'action': action, 'idEl': idEl, 'token': token, 'elid': elid}
            r = client2.http_get(u, data=post, headers=headers)
            #print r
            #control.log('#PUTLOCKER4 %s' % r)

            r = str(json.loads(r))
            r = client.parseDOM(r, 'iframe', ret='.+?') + client.parseDOM(r, 'IFRAME', ret='.+?')
            #control.log('#PUTLOCKER5 %s' % r)

            links = []

            for i in r:
                try: links += [{'source': 'gvideo', 'quality': client.googletag(i)[0]['quality'], 'url': i}]
                except: pass

            links += [{'source': 'openload.co', 'quality': 'SD', 'url': i} for i in r if 'openload.co' in i]

            links += [{'source': 'videomega.tv', 'quality': 'SD', 'url': i} for i in r if 'videomega.tv' in i]
            links += [{'source': 'Allmyvideos', 'quality': 'SD', 'url': i} for i in r if 'allmyvideos.net' in i]

            for i in links: sources.append({'source': i['source'], 'quality': i['quality'], 'provider': 'Putlocker', 'url': i['url']})
            #control.log('#PUTLOCKER6 SOURCES %s' % sources)

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            url = resolvers.request(url)
            return url
        except:
            return



