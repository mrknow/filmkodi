"""
Exashare.com urlresolver XBMC Addon
Copyright (C) 2014 JUL1EN094

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
from lib import helpers

from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class ExashareResolver(UrlResolver):
    name = "exashare"
    domains = ["exashare.com", "uame8aij4f.com", "yahmaib3ai.com"]
    pattern = '(?://|\.)((?:yahmaib3ai|uame8aij4f|exashare)\.com)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url('exashare.com', media_id)
        html = self.net.http_GET(web_url).content

        try: web_url = re.search('src="([^"]+)', html).group(1)
        except: raise ResolverError('Unable to locate link')

        return helpers.get_media_url(web_url)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)
