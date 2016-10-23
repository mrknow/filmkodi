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
from lib import helpers
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

        data = helpers.get_hidden(html)
        data['method_free'] = 'Kostenloser stream / Kostenloser Download'
        html = self.net.http_POST(web_url, data).content

        js_data = re.findall('(eval\(function.*?)</script>', html.replace('\n', ''))

        for i in js_data:
            try: html += jsunpack.unpack(i)
            except: pass

        html = html.replace('\\\'', '\'')
        html = html.replace('\\\'', '\'')

        stream_url = re.findall('<param\s+name="src"\s*value="([^"]+)', html)
        stream_url += re.findall("'file'\s*,\s*'(.+?)'", html)
        stream_url = [i for i in stream_url if not i.endswith('.srt')]

        if stream_url:
            return stream_url[0]

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://www.xvidstage.com/%s' % media_id
