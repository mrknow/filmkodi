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
import xbmc

class UpToBoxResolver(UrlResolver):
    name = "uptobox"
    domains = ["uptobox.com", "uptostream.com"]
    pattern = '(?://|\.)(uptobox.com|uptostream.com)/(?:iframe/)?([0-9A-Za-z_]+)'

    def __init__(self):
        self.net = common.Net()
        self.user_agent = common.IE_USER_AGENT
        self.net.set_user_agent(self.user_agent)
        self.headers = {'User-Agent': self.user_agent}

    def get_media_url(self, host, media_id):
        try:
            web_url = self.get_stream_url(host, media_id)
            stream_url = helpers.get_media_url(web_url)
        except:
            stream_url = None

        if not stream_url:
            stream_url = self.__box_url(host, media_id)

        if stream_url:
            return stream_url
        else:
            raise ResolverError('File not found')

    def __box_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        self.headers['Referer'] = web_url

        html = self.net.http_GET(web_url, headers=self.headers).content
        if isinstance(html, unicode): html = html.encode('utf-8', 'ignore')

        if 'not available in your country' in html:
            raise ResolverError('Unavailable in your country')

        r = re.search('You have to wait (\d+ minutes?,\s*)?\d+ seconds?', html, re.I)
        if r:
            raise ResolverError('Cooldown in effect')

        data = helpers.get_hidden(html)
        for _ in range(0, 3):
            html = self.net.http_POST(web_url, data, headers=self.headers).content
            if isinstance(html, unicode): html = html.encode('utf-8', 'ignore')
            match = re.search('''href\s*=\s*['"]([^'"]+)[^>]+>\s*<span[^>]+class\s*=\s*['"]button_upload green['"]''', html)
            if match:
                stream_url = match.group(1)
                return stream_url.replace(' ', '%20') + helpers.append_headers(self.headers)
            else:
                common.kodi.sleep(1000)

    def get_url(self, host, media_id):
        return 'http://uptobox.com/%s' % media_id

    def get_stream_url(self, host, media_id):
        return 'https://uptostream.com/iframe/%s' % media_id
