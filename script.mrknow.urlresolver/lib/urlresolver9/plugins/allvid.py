# -*- coding: UTF-8 -*-
"""
    Copyright (C) 2014  smokdpi

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
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class AllVidResolver(UrlResolver):
    name = "allvid"
    domains = ["allvid.ch"]
    pattern = '(?://|\.)(allvid\.ch)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.IE_USER_AGENT,
                   'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content

        iframe = re.findall('<iframe\s+src\s*=\s*"([^"]+)', html, re.DOTALL)[0]
        if iframe:
            html = self.net.http_GET(iframe, headers=headers).content

        html = helpers.add_packed_data(html)
        sources = helpers.scrape_sources(html, result_blacklist=['dl'])
        return helpers.pick_source(sources) + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)
