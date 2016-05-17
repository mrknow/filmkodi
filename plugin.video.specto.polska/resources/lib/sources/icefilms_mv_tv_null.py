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


import re,urllib,urlparse,random

from resources.lib.libraries import control
from resources.lib.libraries import client
from resources.lib import resolvers


class source:
    def __init__(self):
        self.base_link = 'http://ipv6.icefilms.info'
        self.link_1 = 'http://ipv6.icefilms.info'
        self.link_2 = 'https://icefilms.unblocked.pw'
        self.moviesearch_link = '/movies/a-z/%s'
        self.tvsearch_link = '/tv/a-z/%s'
        self.video_link = '/membersonly/components/com_iceplayer/video.php?h=374&w=631&vid=%s&img='
        self.resp_link = '/membersonly/components/com_iceplayer/video.phpAjaxResp.php?id=%s&s=%s&iqs=&url=&m=%s&cap= &sec=%s&t=%s&image=%s'
        self.headers = {}


    def get_movie(self, imdb, title, year):
        try:
            query = re.sub('^THE\s+|^A\s+', '', title.strip().upper())[0]
            if not query.isalpha(): query = '1'
            query = self.moviesearch_link % query

            result = ''
            links = [self.link_1]
            for base_link in links:
                result = client.source(urlparse.urljoin(base_link, query), headers=self.headers)
                if 'Donate' in str(result): break

            imdb = re.sub('[^0-9]', '', imdb)

            result = result.decode('iso-8859-1').encode('utf-8')
            result = re.compile('id=%s>.+?href=(.+?)>' % imdb).findall(result)[0]

            url = client.replaceHTMLCodes(result)
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
            except: pass
            url = '%s?%s' % (urlparse.urlparse(url).path, urlparse.urlparse(url).query)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_show(self, imdb, tvdb, tvshowtitle, year):
        try:
            query = re.sub('^THE\s+|^A\s+', '', tvshowtitle.strip().upper())[0]
            if not query.isalpha(): query = '1'
            query = self.tvsearch_link % query

            result = ''
            links = [self.link_1]
            for base_link in links:
                result = client.source(urlparse.urljoin(base_link, query), headers=self.headers)
                if 'Donate' in str(result): break

            imdb = re.sub('[^0-9]', '', imdb)

            result = result.decode('iso-8859-1').encode('utf-8')
            result = re.compile('id=%s>.+?href=(.+?)>' % imdb).findall(result)[0]

            url = client.replaceHTMLCodes(result)
            try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
            except: pass
            url = '%s?%s' % (urlparse.urlparse(url).path, urlparse.urlparse(url).query)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_episode(self, url, imdb, tvdb, title, date, season, episode):
        try:
            if url == None: return

            result = ''
            links = [self.link_1]
            for base_link in links:
                result = client.source(urlparse.urljoin(base_link, url), headers=self.headers)
                if 'Donate' in str(result): break

            result = result.decode('iso-8859-1').encode('utf-8')
            result = urllib.unquote_plus(result)

            url = re.compile('(/ip[.]php.+?>%01dx%02d)' % (int(season), int(episode))).findall(result)[0]
            url = re.compile('(/ip[.]php.+?)&').findall(url)[-1]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return


    def get_sources(self, url, hosthdDict, hostDict, locDict):
        try:
            sources = []

            if url == None: return sources

            t = urlparse.parse_qs(urlparse.urlparse(url).query)['v'][0]
            url = self.video_link % t

            result = ''
            links = [self.link_1]
            for base_link in links:
                result = client.source(urlparse.urljoin(base_link, url), headers=self.headers)
                if 'ripdiv' in str(result): break

            result = result.decode('iso-8859-1').encode('utf-8')

            secret = re.compile('lastChild[.]value="(.+?)"').findall(result)[0]

            s_start = re.search('(?:\s+|,)s\s*=(\d+)', result)
            s_start = int(s_start.group(1))
                
            m_start = re.search('(?:\s+|,)m\s*=(\d+)', result)
            m_start = int(m_start.group(1))

            image = re.compile('<iframe[^>]*src="([^"]+)').findall(result)
            image = image[0] if len(image) > 0 else ''
            image = urllib.quote(image)

            links = client.parseDOM(result, 'div', attrs = {'class': 'ripdiv'})

            hd = [i for i in links if '>HD 720p<' in i]
            sd = [i for i in links if '>DVDRip / Standard Def<' in i]
            if len(sd) == 0: sd = [i for i in links if '>DVD Screener<' in i]
            if len(sd) == 0: sd = [i for i in links if '>R5/R6 DVDRip<' in i]

            if len(hd) > 0: hd = hd[0].split('<p>')
            if len(sd) > 0: sd = sd[0].split('<p>')
            links = [(i, 'HD') for i in hd] + [(i, 'SD') for i in sd]


            for i in links:
                try:
                    quality = i[1]

                    host = client.parseDOM(i[0], 'a')[-1]
                    host = re.sub('\s|<.+?>|</.+?>|.+?#\d*:', '', host)
                    host = host.strip().lower()
                    if quality == 'HD' and not host in hosthdDict: raise Exception()
                    if quality == 'SD' and not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    s = s_start + random.randint(3, 1000)
                    m = m_start + random.randint(21, 1000)

                    url = client.parseDOM(i[0], 'a', ret='onclick')[-1]
                    url = re.compile('[(](.+?)[)]').findall(url)[0]
                    url = self.resp_link % (url, s, m, secret, t, image)
                    url = url.encode('utf-8')

                    sources.append({'source': host, 'quality': quality, 'provider': 'Icefilms', 'url': url})
                except:
                    pass

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            post = urlparse.parse_qsl(urlparse.urlparse(url).query, True)
            post = [i for i in post if not i[0] == 'image']
            post = post

            query = urlparse.parse_qs(urlparse.urlparse(url).query)

            image = urllib.unquote(query['image'][0])

            ref = self.video_link % query['t'][0]

            url = urlparse.urlparse(url).path
            url += '?s=%s&t=%s&app_id=Specto505' % (query['id'][0], query['t'][0])

            links = [self.link_1]
            for base_link in links:
                referer = urlparse.urljoin(base_link, ref)
                cookie = client.request(referer, output='cookie')
                result = client.request(urlparse.urljoin(base_link, url), post=post, referer=referer, cookie=cookie)
                if 'com_iceplayer' in str(result): break

            self.img_parser(image, referer)

            url = urlparse.parse_qs(urlparse.urlparse(result).query)['url'][0]
            url = resolvers.request(url)

            return url
        except:
            return


    def img_parser(self, image, referer):
        try:
            if not image.startswith('http:'): image = 'http:' + image

            d = control.windowDialog

            result = client.request(image, referer=referer, close=False)

            for match in re.finditer("<img\s+src='([^']+)'\s+width='(\d+)'\s+height='(\d+)'", result):
                img_url, width, height = match.groups()
                img_url = client.replaceHTMLCodes(img_url)
                width = int(width)
                height = int(height)
                if width > 0 and height > 0:
                    left = (1280 - width) / 2
                    f = control.image(left, 0, width, height, img_url)
                    d.addControl(f)
                else:
                    client.request(img_url, referer=image, close=False)

            d.show()

            control.dialog.ok(control.addonInfo('name'), str('Continue to Video'), '')

            match = re.search("href='([^']+)", result)
            if match and random.randint(0, 100) < 5:
                result = client.request(match.group(1), close=False)
                match = re.search("location=decode\('([^']+)", result)
                client.request(match.group(1))


            try: d.removeControl(f) ; d.close()
            except: return
        except:
            try: d.removeControl(f) ; d.close()
            except: return


