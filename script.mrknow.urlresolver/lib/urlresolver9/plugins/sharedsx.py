'''
shared.sx urlresolver plugin
Copyright (C) 2014 Lars-Daniel Weber

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
'''

import re
import urllib
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class SharedsxResolver(UrlResolver):
    name = "sharedsx"
    domains = ["shared.sx"]
    pattern = '(?://|\.)(shared\.sx)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers={'Referer': web_url}).content

        data = helpers.get_hidden(html)
        html = self.net.http_POST(web_url, data, headers=({'Referer': web_url, 'X-Requested-With': 'XMLHttpRequest'})).content

        r = re.search(r'class="stream-content" data-url', html)
        if not r: raise ResolverError('page structure changed')
        r = re.findall(r'data-url="?(.+?)"', html)
        stream_url = r[0] + helpers.append_headers({'User-Agent': common.IE_USER_AGENT})

        return stream_url

    def get_url(self, host, media_id):
        return 'http://shared.sx/%s' % media_id
