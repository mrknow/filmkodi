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

class WatchersResolver(UrlResolver):
    name = "watchers"
    domains = ['watchers.to']
    pattern = '(?://|\.)(watchers\.to)/(?:embed-)?([a-zA-Z0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        response = self.net.http_GET(web_url)
        html = response.content

        if html:
            ip_loc = re.search('<img src="http://([\d.]+)/.+?"', html).groups()[0]
            id_media = re.search('([a-zA-Z0-9]+)(?=\|+?download)', html).groups()[0]
            m3u8 = 'http://%s/hls/%s/index-v1-a1.m3u8' % (ip_loc, id_media)

            if m3u8:
                return m3u8

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)
