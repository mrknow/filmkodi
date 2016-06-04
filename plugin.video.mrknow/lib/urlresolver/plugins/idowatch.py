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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class IDoWatchResolver(UrlResolver):
    name = "idowatch"
    domains = ["idowatch.net"]
    pattern = '(?://|\.)(idowatch\.net)/([0-9a-zA-Z]+)\.html'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        match = re.search('''["']?sources['"]?\s*:\s*\[(.*?)\]''', html, re.DOTALL)
        if match:
            for match in re.finditer('''['"]?file['"]?\s*:\s*['"]?([^'"]+)''', match.group(1), re.DOTALL):
                stream_url = match.group(1)
                if not stream_url.endswith('smil'):
                    return match.group(1) + '|User-Agent=%s' % (common.FF_USER_AGENT)

        raise ResolverError('Unable to resolve idowatch link. Filelink not found.')

    def get_url(self, host, media_id):
        return 'http://idowatch.net/%s' % (media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
