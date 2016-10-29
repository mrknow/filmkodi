"""
grifthost urlresolver plugin
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
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError
from lib import jsunpack

class VidioResolver(UrlResolver):
    name = "vidio.sx"
    domains = ["vidio.sx"]
    pattern = '(?://|\.)(vidio\.sx)/(?:embed-)?([0-9a-zA-Z]+)\.html'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        for match in re.finditer('(eval\(function.*?)</script>', html, re.DOTALL):
            js_data = jsunpack.unpack(match.group(1))
            match = re.search('sources\s*:\s*\[(.*?)\]', js_data, re.DOTALL)
            if match:
                match = re.search('''['"]*file['"]*\s*:\s*['"]*([^'"]+)''', match.group(1), re.DOTALL)
                if match:
                    return match.group(1) + '|User-Agent=%s' % (common.FF_USER_AGENT)

        raise ResolverError('Unable to resolve vidio link. Filelink not found.')

    def get_url(self, host, media_id):
        return 'http://vidio.sx/%s' % (media_id)
