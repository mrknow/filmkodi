"""
urlresolver XBMC Addon
Copyright (C) 2011 t0mm0

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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class XvidstageResolver(UrlResolver):
    name = "xvidstage"
    domains = ["xvidstage.com"]
    pattern = '(?://|\.)(xvidstage\.com)/(?:embed-|)?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        for match in re.finditer('(eval.*?\)\)\))', html, re.DOTALL):
            js_data = jsunpack.unpack(match.group(1))
            js_data = js_data.replace('\\\'', '\'')

            stream_url = re.findall('<param\s+name="src"\s*value="([^"]+)', js_data)
            stream_url += re.findall("'file'\s*,\s*'(.+?)'", js_data)
            stream_url = [i for i in stream_url if not i.endswith('.srt')]

            if stream_url:
                return stream_url[0]

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://www.xvidstage.com/embed-%s.html' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

