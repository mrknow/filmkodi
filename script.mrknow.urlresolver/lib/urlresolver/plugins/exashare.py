"""
Exashare.com urlresolver XBMC Addon
Copyright (C) 2014 JUL1EN094

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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class ExashareResolver(UrlResolver):
    name = "exashare"
    domains = ["exashare.com"]
    pattern = '(?://|\.)(exashare\.com)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):

        web_url = self.get_url('exashare.com', media_id)

        html = self.net.http_GET(web_url).content

        try: r = re.search('src="([^"]+)', html).group(1)
        except: return

        headers = {'Referer': web_url}

        html = self.net.http_GET(r, headers=headers).content

        stream_url = re.search('file\s*:\s*"(http.+?)"', html)

        if stream_url:
            return stream_url.group(1)
        else:
            raise ResolverError('Unable to locate link')

    def get_url(self, host, media_id):
        return 'http://%s/embed-%s.html' % (host, media_id)
