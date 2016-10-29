"""
    urlresolver XBMC Addon
    Copyright (C) 2014 tknorris

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
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class BestreamsResolver(UrlResolver):
    name = "bestreams"
    domains = ["bestreams.net"]
    pattern = '(?://|\.)(bestreams\.net)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        headers = {'User-Agent': common.IOS_USER_AGENT}

        html = self.net.http_GET(web_url, headers=headers).content

        r = re.search('file\s*:\s*"(http.+?)"', html)

        if r:
            return r.group(1)
        else:
            raise ResolverError("File Link Not Found")

    def get_url(self, host, media_id):
        return 'http://bestreams.net/embed-%s.html' % media_id
