'''
Vidbull urlresolver plugin
Copyright (C) 2013 Vinnydude

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

class VidbullResolver(UrlResolver):
    name = "vidbull"
    domains = ["vidbull.com"]
    pattern = '(?://|\.)(vidbull\.com)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        headers = {
            'User-Agent': common.IOS_USER_AGENT
        }

        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers=headers).content
        match = re.search('<source\s+src="([^"]+)', html)
        if match:
            return match.group(1)
        else:
            raise ResolverError('File Link Not Found')

    def get_url(self, host, media_id):
        return 'http://www.vidbull.com/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

