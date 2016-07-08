"""
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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

MAX_TRIES = 3

class VidUpMeResolver(UrlResolver):
    name = "vidup.me"
    domains = ["vidup.me", "beta.vidup.me"]
    pattern = '(?://|\.)(vidup\.me)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        best_stream_url = ''
        max_quality = 0
        for match in re.finditer('(eval\(function.*?)</script>', html, re.DOTALL):
            js_data = jsunpack.unpack(match.group(1))
            js_data = js_data.replace("\\'", "'")
            r = re.findall(r"label\s*:\s*'([^']+)p'\s*,\s*file\s*:\s*'([^']+)", js_data)
            if r:
                for quality, stream_url in r:
                    if int(quality) >= max_quality:
                        best_stream_url = stream_url
                        max_quality = int(quality)

            if best_stream_url:
                return best_stream_url

            raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://beta.vidup.me/embed-%s.html' % media_id
