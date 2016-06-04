'''
Allmyvideos urlresolver plugin
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
import urllib
import urlparse
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class VidSpotResolver(UrlResolver):
    name = "vidspot"
    domains = ["vidspot.net"]
    pattern = '(?://|\.)(vidspot\.net)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        url = self.get_url(host, media_id)
        html = self.net.http_GET(url).content

        data = {}
        r = re.findall(r'type="hidden" name="(.+?)"\s* value="?(.+?)">', html)
        for name, value in r:
            data[name] = value

        html = self.net.http_POST(url, data).content

        r = re.search('"sources"\s*:\s*\[(.*?)\]', html, re.DOTALL)
        if r:
            fragment = r.group(1)
            stream_url = None
            for match in re.finditer('"file"\s*:\s*"([^"]+)', fragment):
                stream_url = match.group(1)

            if stream_url:
                stream_url = '%s?%s&direct=false' % (stream_url.split('?')[0], urlparse.urlparse(stream_url).query)
                return stream_url + '|' + urllib.urlencode({'User-Agent': common.IE_USER_AGENT})
            else:
                raise ResolverError('could not find file')
        else:
            raise ResolverError('could not find sources')

    def get_url(self, host, media_id):
        return 'http://vidspot.net/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
