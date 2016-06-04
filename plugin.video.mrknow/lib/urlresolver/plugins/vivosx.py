'''
vivo.sx urlresolver plugin
Copyright (C) 2015 y2000j

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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class VivosxResolver(UrlResolver):
    name = "vivosx"
    domains = ["vivo.sx"]
    pattern = '(?://|\.)(vivo\.sx)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        # get landing page
        html = self.net.http_GET(web_url, headers={'Referer': web_url}).content

        # read POST variables into data
        data = {}
        r = re.findall(r'type="hidden" name="(.+?)"\s* value="?(.+?)"', html)
        if not r: raise Exception('page structure changed')
        for name, value in r: data[name] = value

        # get video page using POST variables
        html = self.net.http_POST(web_url, data, headers=({'Referer': web_url, 'X-Requested-With': 'XMLHttpRequest'})).content

        # search for content tag
        r = re.search(r'class="stream-content" data-url', html)
        if not r: raise ResolverError('page structure changed')

        # read the data-url
        r = re.findall(r'data-url="?(.+?)"', html)
        if not r: raise ResolverError('video not found')

        # return media URL
        return r[0]

    def get_url(self, host, media_id):
        return 'http://vivo.sx/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
