# -*- coding: utf-8 -*-
"""
openload.io urlresolver plugin
Copyright (C) 2015 tknorris

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
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class StreamangoResolver(UrlResolver):
    name = "streamango"
    domains = ["streamango.com"]
    pattern = '(?://|\.)(streamango\.(?:io|com))/(?:embed|f)/([0-9a-zA-Z-_]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        sources = re.findall('type:"video/mp4",src:"([^"]+)"', html)
        if sources:
            source = sources[0]
            if not 'http' in source:
                source = 'https:' + source

            return source + helpers.append_headers({'User-Agent': common.IE_USER_AGENT})

        else:
            raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://streamango.com/embed/%s' % media_id
