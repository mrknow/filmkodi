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
import urllib
import urllib2
from lib import jsunpack
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class VideoMegaResolver(UrlResolver):
    name = "videomega"
    domains = ["videomega.tv"]
    pattern = '(?://|\.)(videomega\.tv)/(?:(?:iframe|cdn|validatehash|view)\.php)?\?(?:ref|hashkey)=([a-zA-Z0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.IOS_USER_AGENT,
            'Referer': web_url
        }

        html = self.net.http_GET(web_url, headers=headers).content
        if jsunpack.detect(html):
            js_data = jsunpack.unpack(html)
            match = re.search('"src"\s*,\s*"([^"]+)', js_data)

        try:
            stream_url = match.group(1)

            r = urllib2.Request(stream_url, headers=headers)
            r = int(urllib2.urlopen(r, timeout=15).headers['Content-Length'])

            if r > 1048576:
                stream_url += '|' + urllib.urlencode(headers)
                return stream_url
        except:
            ResolverError("File Not Playable")

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return 'http://videomega.tv/cdn.php?ref=%s' % media_id
