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
from lib import helpers
import random
from lib.aa_decoder import AADecoder
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class RapidVideoResolver(UrlResolver):
    name = "rapidvideo.com"
    domains = ["rapidvideo.com"]
    pattern = '(?://|\.)(rapidvideo\.com)/(?:embed/|)?([0-9A-Za-z]+)'

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
        match = re.search('hide\(\);(.*?;)\s*//', html, re.DOTALL)
        if match:
            dtext = AADecoder(match.group(1)).decode()
            match = re.search('"?sources"?\s*:\s*\[(.*?)\]', dtext, re.DOTALL)
            if match:
                for match in re.finditer('''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([^'"]*)''', match.group(1), re.DOTALL):
                    stream_url, _label = match.groups()
                    stream_url = stream_url.replace('\/', '/')
                    stream_url += '|User-Agent=%s&Referer=%s' % (common.FF_USER_AGENT, web_url)
                    return stream_url

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'https://www.rapidvideo.com/embed/%s' % media_id
