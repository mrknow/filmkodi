"""    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
    
    Special thanks for help with this resolver go out to t0mm0, jas0npc,
    mash2k3, Mikey1234,voinage and of course Eldorado. Cheers guys :)
"""

import re
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class VidtoResolver(UrlResolver):
    name = "vidto"
    domains = ["vidto.me"]
    pattern = '(?://|\.)(vidto\.me)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        if jsunpack.detect(html):
            js_data = jsunpack.unpack(html)

            max_label = 0
            stream_url = ''
            for match in re.finditer('label:\s*"(\d+)p"\s*,\s*file:\s*"([^"]+)', js_data):
                label, link = match.groups()
                if int(label) > max_label:
                    stream_url = link
                    max_label = int(label)
            if stream_url:
                return stream_url
            else:
                raise ResolverError("File Link Not Found")

    def get_url(self, host, media_id):
        return 'http://vidto.me/embed-%s.html' % media_id


    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False