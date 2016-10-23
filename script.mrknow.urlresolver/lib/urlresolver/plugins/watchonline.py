# -*- coding: UTF-8 -*-
"""
    Kodi urlresolver plugin
    Copyright (C) 2016  alifrezser

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
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class WatchonlineResolver(UrlResolver):
    name = "watchonline"
    domains = ["watchonline.to"]
    pattern = '(?://|\.)(watchonline\.to)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()
        self.user_agent = common.IE_USER_AGENT
        self.net.set_user_agent(self.user_agent)
        self.headers = {'User-Agent': self.user_agent}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        for match in re.finditer('(eval\(function.*?)</script>', html, re.DOTALL):
            js_data = jsunpack.unpack(match.group(1))
            js_data = js_data.replace('\\\'', '\'')

        r = re.search('{\s*file\s*:\s*["\']([^{}]+\.mp4)["\']', js_data)

        if r:
            return r.group(1)
        else:
            raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'http://www.%s/embed-%s.html' % (host, media_id)
