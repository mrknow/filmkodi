"""
myvidstream urlresolver plugin
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
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

MAX_TRIES = 3

class myVidStream(UrlResolver):
    name = "myvidstream"
    domains = ["myvidstream.net"]
    pattern = '(?://|\.)(myvidstream\.net)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        tries = 0
        while tries < MAX_TRIES:
            data = {}

            for match in re.finditer('(eval\(function.*?)</script>', html, re.DOTALL):
                js_data = jsunpack.unpack(match.group(1))
                js_data = js_data.replace('\\\'', '\'')

                match2 = re.search("\('file','([^']+)", js_data)
                if match2:
                    stream_url = match2.group(1)
                    return stream_url.replace(" ", "%20")

            tries += 1

        raise ResolverError('Unable to resolve myvidstream link. Filelink not found.')

    def get_url(self, host, media_id):
        return 'http://%s/embed-%s.html' % (host, media_id)
