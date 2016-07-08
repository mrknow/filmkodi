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
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class AllVidResolver(UrlResolver):
    name = "allvid"
    domains = ["allvid.ch"]
    pattern = '(?://|\.)(allvid\.ch)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()
        self.user_agent = common.IE_USER_AGENT
        self.net.set_user_agent(self.user_agent)
        self.headers = {'User-Agent': self.user_agent}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        self.headers['Referer'] = web_url
        html = self.net.http_GET(web_url, headers=self.headers).content

        r = re.search('<iframe\s+src\s*=\s*"([^"]+)', html, re.DOTALL)

        if r:
            web_url = r.group(1)
            html = self.net.http_GET(web_url, headers=self.headers).content

        for match in re.finditer('(eval\(function.*?)</script>', html, re.DOTALL):
            js_data = jsunpack.unpack(match.group(1))
            js_data = js_data.replace('\\\'', '\'')

            r = re.search('sources\s*:\s*\[\s*\{\s*file\s*:\s*["\'](.+?)["\']', js_data)

            if r:
                return r.group(1)
        else:
            raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'http://%s/embed-%s.html' % (host, media_id)
