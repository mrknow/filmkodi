"""
    OVERALL CREDIT TO:
        t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway

    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

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
"""

import re
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class AliezResolver(UrlResolver):
    name = "aliez"
    domains = ['aliez.me']
    pattern = '(?://|\.)(aliez\.me)/(?:(?:player/video\.php\?id=([0-9]+)&s=([A-Za-z0-9]+))|(?:video/([0-9]+)/([A-Za-z0-9]+)))'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        response = self.net.http_GET(web_url)
        html = response.content

        if html:
            try:
                stream_url = re.search(r"file:\s'(.+?)'", html).groups()[0]
                return stream_url
                
            except:
                pass

        raise ResolverError('No playable video found.')

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url, re.I)
        if r:
            r = filter(None, r.groups())
            r = [r[0], '%s|%s' % (r[1], r[2])]
            return r
        else:
            return False
    
    def get_url(self, host, media_id):
        media_id = media_id.split("|")
        return self._default_get_url(host, media_id, 'http://emb.%s/player/video.php?id=%s&s=%s&w=590&h=332' % (host, media_id[0], media_id[1]))
