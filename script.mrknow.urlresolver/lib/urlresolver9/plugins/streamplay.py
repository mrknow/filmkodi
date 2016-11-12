# -*- coding: UTF-8 -*-
"""
    Copyright (C) 2016 alifrezser

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

class StreamplayResolver(UrlResolver):
    name = "streamplay"
    domains = ["streamplay.to"]
    pattern = '(?://|\.)(streamplay\.to)/(?:embed-|)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT, 'Accept': '*/*'}
        html = self.net.http_GET(web_url, headers=headers).content
        html = helpers.add_packed_data(html)
        match = re.findall('[\'"]?file[\'"]?\s*:\s*[\'"]([^\'"]+)', html)
        if match:
            stream_url = [i for i in match if i.endswith('.mp4')]
            if stream_url:
                match = re.search("\$\.get\('([^']+)", html)
                if match:
                    headers.update({'Referer': web_url, 'X-Requested-With': 'XMLHttpRequest'})
                    self.net.http_GET(match.group(1), headers=headers)
                # returned stream still doesn't work, probably either a header issue or a pre-http call needed
                # commenting out until someone else can fix it
                # return stream_url[0] + helpers.append_headers({'User-Agent': common.FF_USER_AGENT})

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'http://%s/embed-%s.html' % (host, media_id)
