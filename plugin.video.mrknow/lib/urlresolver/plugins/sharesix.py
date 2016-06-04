'''
sharesix urlresolver plugin
Copyright (C) 2014 tknorris

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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class SharesixResolver(UrlResolver):
    name = "sharesix"
    domains = ["sharesix.com"]
    pattern = '(?://|\.)(sharesix\.com)(?:/f)?/([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.IE_USER_AGENT}

        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search('<a[^>]*id="go-next"[^>*]href="([^"]+)', html)
        if r:
            next_url = 'http://' + host + r.group(1)
            html = self.net.http_GET(next_url, headers=headers).content

        if 'file you were looking for could not be found' in html:
            raise ResolverError('File Not Found or removed')

        r = re.search("var\s+lnk\d+\s*=\s*'(.*?)'", html)
        if r:
            stream_url = r.group(1) + '|' + urllib.urlencode(headers)
            return stream_url
        else:
            raise ResolverError('Unable to locate link')

    def get_url(self, host, media_id):
        return 'http://sharesix.com/f/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
