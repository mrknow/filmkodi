"""
    urlresolver XBMC Addon
    Copyright (C) 2012 Bstrdsmkr

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

class MovDivxResolver(UrlResolver):
    name = "movdivx"
    domains = ["movdivx.com"]
    pattern = '(?://|\.)(movdivx\.com)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        data = {}
        for match in re.finditer('type="hidden"\s*name="([^"]+)"\s*value="([^"]+)', html):
            key, value = match.groups()
            data[key] = value
        data['method_free'] = 'Continue to Stream >>'

        html = self.net.http_POST(web_url, data).content

        # get url from packed javascript
        sPattern = '(eval\(function\(p,a,c,k,e,d\).*?)</script>'
        for match in re.finditer(sPattern, html, re.DOTALL | re.IGNORECASE):
            fragment = match.group(1)
            js_data = jsunpack.unpack(fragment)
            match = re.search('name="src"\s*value="([^"]+)', js_data)
            if match:
                return match.group(1)
            else:
                match = re.search('file\s*:\s*"([^"]+)', js_data)
                if match:
                    return match.group(1)

        raise ResolverError('failed to parse link')

    def get_url(self, host, media_id):
        return 'http://movdivx.com/%s.html' % (media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
