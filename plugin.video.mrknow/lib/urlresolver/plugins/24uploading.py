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
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

MAX_TRIES = 3

class TwentyFourUploadingResolver(UrlResolver):
    name = "24uploading"
    domains = ["24uploading.com"]
    pattern = '(?://|\.)(24uploading\.com)/([0-9a-zA-Z/]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        tries = 0
        while tries < MAX_TRIES:
            data = {}
            for match in re.finditer(r'type="hidden"\s+name="(.+?)"\s+value="(.*?)"', html):
                key, value = match.groups()
                data[key] = value
            data['method_free'] = 'Free Download'

            html = self.net.http_POST(web_url, form_data=data).content

            for match in re.finditer('(eval\(function.*?)</script>', html, re.DOTALL):
                js_data = jsunpack.unpack(match.group(1))
                js_data = js_data.replace('\\\'', '\'')

                match2 = re.search("\"html5\".*?file\s*:\s*'([^']+)", js_data)
                if match2:
                    stream_url = match2.group(1)
                    return stream_url

            tries += 1

        raise ResolverError('Unable to resolve 24uploading link. Filelink not found.')

    def get_url(self, host, media_id):
        return 'http://24uploading.com/%s' % (media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
