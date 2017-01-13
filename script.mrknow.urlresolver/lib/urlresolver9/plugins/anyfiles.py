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
import urllib2
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class AnyFilesResolver(UrlResolver):
    name = "anyfiles"
    domains = ["anyfiles.pl"]
    pattern = '(?://|\.)(anyfiles\.pl)/.*?(?:id=|v=|/)([0-9]+)'

    def __init__(self):
        self.net = common.Net()
        self.user_agent = common.IE_USER_AGENT
        self.headers = {'User-Agent': self.user_agent}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        self.headers['Referer'] = web_url
        html = self.net.http_GET(web_url, headers=self.headers).content
        r = re.search('src="/?(pcs\?code=[^"]+?)"', html, re.DOTALL)
        if r:
            web_url = 'http://video.anyfiles.pl/%s' % (r.group(1))
            html = self.net.http_GET(web_url, headers=self.headers).content
            match = re.search('(http[^"]+?mp4)', html)
            if match:
                return match.group(1)

        else:
            raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return "http://video.anyfiles.pl/w.jsp?id=%s&width=620&height=349&pos=&skin=0" % (media_id)
