'''
thevideo urlresolver plugin
Copyright (C) 2014 Eldorado

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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class VidMeResolver(UrlResolver):
    name = "vid.me"
    domains = ["vid.me"]
    pattern = '(?://|\.)(vid\.me)/(?:e/)?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        r = re.search('\<meta property.*og:video:url.*\s*content="([^"]+.mp4[^"]+)', html)
        if r:
            return r.group(1).replace('&amp;', '&')

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://vid.me/e/%s' % media_id
