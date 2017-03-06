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

from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError
import re

class VshareResolver(UrlResolver):
    name = "vshare"
    domains = ['vshare.io']
    pattern = '(?://|\.)(vshare\.io)/\w?/(\w+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        response = self.net.http_GET(web_url, headers=headers)
        html = response.content
        sources = re.findall('''['"]?url['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([^'"]*)''', html)
        if sources:
            print "S",sources[-1][0].replace('\\','')
            return sources[-1][0].replace('\\','')
        return helpers.pick_source(sources) + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return 'http://vshare.io/v/%s/width-620/height-280/' % media_id
