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
import urllib2
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class YourUploadResolver(UrlResolver):
    name = "yourupload.com"
    domains = ["yourupload.com", "yucache.net"]
    pattern = '(?://|\.)(yourupload\.com|yucache\.net)/(?:watch|embed)?/?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        headers = {
            'User-Agent': common.IE_USER_AGENT,
            'Referer': web_url
        }

        html = self.net.http_GET(web_url, headers=headers).content

        r = re.search("file\s*:\s*'(.+?)'", html)
        if r:
            stream_url = r.group(1)
            stream_url = urllib2.urlopen(urllib2.Request(stream_url, headers=headers)).geturl()

            return stream_url
        else:
            raise ResolverError('no file located')

    def get_url(self, host, media_id):
        return 'http://www.yourupload.com/embed/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
