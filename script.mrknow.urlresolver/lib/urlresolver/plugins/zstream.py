"""
    urlresolver XBMC Addon
    Copyright (C) 2016 lambda

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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class ZstreamResolver(UrlResolver):
    name = 'zstream.to'
    domains = ['zstream.to']
    pattern = '(?://|\.)(zstream\.to)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        stream_url = re.compile('file *: *"(http.+?)"').findall(html)
        stream_url = [i for i in stream_url if not i.endswith('.srt')]

        if stream_url:
            return stream_url[-1]

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://zstream.to/embed-%s.html' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False