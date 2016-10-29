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
from lib import jsunpack
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class IsharedResolver(UrlResolver):
    name = 'ishared.eu'
    domains = ['ishared.eu']
    pattern = '(?://|\.)(ishared\.eu)/(?:video|embed)/(.*?)(?:/|$)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        unpacked = ''
        packed = html.split('\n')
        for i in packed:
            try: unpacked += jsunpack.unpack(i).replace('\\\'', '\'')
            except: pass
        html += unpacked
        html = html

        match = re.findall('sources\s*:\s*\[.+?file\s*:\s*(.+?)\s*\,', html)

        if match:
            stream_url = re.findall('var\s+%s\s*=\s*\'(.+?)\'' % match[0], html)
            if stream_url:
                return stream_url[0]

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://ishared.eu/embed/%s' % media_id
