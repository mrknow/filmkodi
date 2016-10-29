"""
urlresolver XBMC Addon
Copyright (C) 2016 lambda

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
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class Shared2meResolver(UrlResolver):
    name = 'shared2.me'
    domains = ['shared2.me']
    pattern = '(?://|\.)(shared2\.me)/(?:play|frame)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        stream_url = re.compile('path *: *"(http.+?)"').findall(html)[-1]
        return stream_url

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://shared2.me/frame/%s' % media_id
