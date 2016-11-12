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
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class VidtoResolver(UrlResolver):
    name = "vidto"
    domains = ["vidto.me"]
    pattern = '(?://|\.)(vidto\.me)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        html = helpers.add_packed_data(html)
        sources = []
        for match in re.finditer('label:\s*"([^"]+)"\s*,\s*file:\s*"([^"]+)', html):
            label, stream_url = match.groups()
            sources.append((label, stream_url))

        sources = sorted(sources, key=lambda x: x[0])[::-1]
        return helpers.pick_source(sources) + helpers.append_headers(headers)

        raise ResolverError("File Link Not Found")

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)
