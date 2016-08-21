"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0
 
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class VidUpResolver(UrlResolver):
    name = "vidup.org"
    domains = ["vidup.org"]
    pattern = '(?://|\.)(vidup\.org)/(?:embed\.php\?file=)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        
        match = re.search("clip:\s+{\s+url:\s\"([^\"']+)", html)
        if match:
            stream_url = match.group(1)
            return stream_url.replace(" ", "%20")

        raise ResolverError('Unable to resolve vidup.org link. Filelink not found.')

    def get_url(self, host, media_id):
        return 'http://%s/embed.php?file=%s' % (host, media_id)
