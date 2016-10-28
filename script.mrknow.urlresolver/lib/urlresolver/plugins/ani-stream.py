"""
ani-stream urlresolver plugin
Copyright (C) 2016 quartoxuna

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import re
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class AniStreamResolver(UrlResolver):
    name = "ani-stream"
    domains = ["ani-stream.com"]
    pattern = '(?://|\.)(www\.ani-stream\.com)/([0-9a-zA-Z\.-]+)'

    def __init__(self):
        self.net = common.Net(http_debug=True)

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        resp = self.net.http_GET(web_url)
        html = resp.content
        if re.search('>(File Not Found)<', html):
            raise ResolverError('File Not Found or removed')

        r = re.search("file: '(.+?)',", html)
        if r:
            return r.group(1)
        else:
            raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://www.ani-stream.com/%s' % (media_id)
