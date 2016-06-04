'''
playwire urlresolver plugin
Copyright (C) 2013 icharania

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
import xml.etree.ElementTree as ET
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class PlaywireResolver(UrlResolver):
    name = "playwire"
    domains = ["playwire.com"]
    pattern = '(?://|\.)(cdn\.playwire\.com.+?\d+)/(?:config|embed)/(\d+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        if web_url.endswith('xml'):  # xml source
            root = ET.fromstring(html)
            stream = root.find('src')
            if stream is not None:
                stream = stream.text
                if stream.endswith('.f4m'):
                    html = self.net.http_GET(stream).content
                    try: return re.findall('<baseURL>(.+?)</baseURL>', html)[0] + '/' + re.findall('<media url="(.+?)"', html)[0]
                    except: pass
            else:
                accessdenied = root.find('Message')
                if accessdenied is not None:
                    raise ResolverError('You do not have permission to view this content')

                raise ResolverError('No playable video found.')
        else:  # json source
            r = re.search('"src":"(.+?)"', html)
            if r:
                return r.group(1)
            else:
                raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        if not 'v2' in host:
            return 'http://%s/embed/%s.xml' % (host, media_id)
        else:
            return 'http://%s/config/%s.json' % (host, media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
