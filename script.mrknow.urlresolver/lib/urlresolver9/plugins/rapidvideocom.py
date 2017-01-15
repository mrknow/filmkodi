# -*- coding: utf-8 -*-
"""
urlresolver XBMC Addon
Copyright (C) 2011 t0mm0

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
import urllib
import random
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class RapidVideoResolver(UrlResolver):
    name = "rapidvideo.com"
    domains = ["rapidvideo.com", "raptu.com"]
    pattern = '(?://|\.)(rapidvideo\.com)/(?:embed/|\?v=)?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        data = helpers.get_hidden(html)
        data['confirm.y'] = random.randint(0, 120)
        data['confirm.x'] = random.randint(0, 120)
        headers['Referer'] = web_url
        post_url = web_url + '#'
        html = self.net.http_POST(post_url, form_data=data, headers=headers).content.encode('utf-8')
        sources = helpers.parse_sources_list(html)
        try: sources.sort(key=lambda x: x[0], reverse=True)
        except: pass
        return helpers.pick_source(sources)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://www.raptu.com/embed/{media_id}')
