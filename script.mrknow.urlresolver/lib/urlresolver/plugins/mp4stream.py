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
import urllib
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class Mp4streamResolver(UrlResolver):
    name = "mp4stream"
    domains = ["mp4stream.com"]
    pattern = '(?://|\.)(mp4stream\.com)/embed/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        response = self.net.http_GET(web_url)
        html = response.content
        headers = dict(response._response.info().items())

        r = re.search('sources\s*:\s*(\[.*?\])', html, re.DOTALL)

        if r:
            html = r.group(1)
            r = re.search("'file'\s*:\s*'(.+?)'", html)
            if r:
                return r.group(1) + '|' + urllib.urlencode({'Cookie': headers['set-cookie']})
            else:
                raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://mp4stream.com/embed/%s' % media_id
