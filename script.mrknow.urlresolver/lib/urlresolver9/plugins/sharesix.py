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
import time
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class SharesixResolver(UrlResolver):
    name = "sharesix"
    domains = ["sharesix.com"]
    pattern = '(?://|\.)(sharesix\.com)(?:/f)?/([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0",
                   "Accept-Language":"en-US,en;q=0.5",
                   "Accept-Encoding": "gzip, deflate",
                   "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                   "Upgrade-Insecure-Requests":"1"}

        html = self.net.http_GET(web_url, headers=headers).content
        print(html)
        exit()

        r = re.search('<a[^>]*href="([^"]+)[^>]*>(Watch online|Fast download|Slow direct download|Free)', html)
        print("R0",r.group(0))
        exit()

        if r:
            next_url = 'http://' + host + r.group(1)
            headers['Referer'] = web_url
            html = self.net.http_GET(next_url, headers=headers).content

        if 'file you were looking for could not be found' in html:
            raise ResolverError('File Not Found or removed')

        r = re.search("var\s+lnk1\d+\s*=\s*'(.*?)'", html)

        print("R1", r.group(0))

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
