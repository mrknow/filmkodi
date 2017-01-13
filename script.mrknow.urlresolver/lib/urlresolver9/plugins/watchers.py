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
from lib import jsunpack
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

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
            packed = re.search('(eval\(function.*?)\s*</script>', html, re.DOTALL)
            if packed:
                js = jsunpack.unpack(packed.group(1))
            else:
                js = html

            video_url = None

            link = re.search('([^"]*.m3u8)', js)
            if link:
                video_url = link.group(1)
                common.log_utils.log_debug('watchers.to Link Found: %s' % video_url)

            if not video_url:
                link = re.search('([^"]*.mp4)', js)
                if link:
                    video_url = link.group(1)
                    common.log_utils.log_debug('watchers.to Link Found: %s' % video_url)

            if video_url:
                return video_url

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)
