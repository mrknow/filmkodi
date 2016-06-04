# -*- coding: UTF-8 -*-
"""
    Copyright (C) 2015  tknorris

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
import xml.etree.ElementTree as ET
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class MediaPlayBoxResolver(UrlResolver):
    name = "MediaPlayBox"
    domains = ["mediaplaybox.com"]
    pattern = '(?://|\.)(mediaplaybox\.com)/video/(.*)'

    def __init__(self):
        self.net = common.Net()
        self.net.set_user_agent(common.IE_USER_AGENT)
        self.headers = {'User-Agent': common.IE_USER_AGENT}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        patterns = [
            'property="og:video"\s+content="[^"]+\?f=([^"]+)',
            'itemprop="embedURL"\s+content="[^"]+\?f=([^"]+)',
            '<embed[^>]+src="[^"]+\?f=([^"]+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                xml = self.net.http_GET(match.group(1)).content
                root = ET.fromstring(xml)
                result = root.find('./video/src')
                if result is not None:
                    return result.text

        raise ResolverError('Unable to find mediaplaybox video')

    def get_url(self, host, media_id):
        return 'http://mediaplaybox.com/video/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
