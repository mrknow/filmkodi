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

import re, json
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class IndavideoResolver(UrlResolver):
    name = "indavideo"
    domains = ["indavideo.hu"]
    pattern = '(?://|\.)(indavideo\.hu)/(?:player/video/|video/)([^/]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        data = json.loads(html)

        if data['success'] == '0':
            html = self.net.http_GET('http://indavideo.hu/video/%s' % media_id).content

            hash = re.search('emb_hash.+?value\s*=\s*"([^"]+)', html)
            if not hash:
                raise ResolverError('File not found')

            web_url = self.get_url(host, hash.group(1))

            html = self.net.http_GET(web_url).content
            data = json.loads(html)

        if data['success'] == '1':
            video_file = data['data']['video_file']
            if video_file == '':
                raise ResolverError('File removed')

            video_file = video_file.rsplit('/', 1)[0] + '/'
            sources = list(set(data['data']['flv_files']))
            sources = [(i.rsplit('.', 2)[-2] + 'p', i.split('?')[0] + '?channel=main') for i in sources]
            sources = sorted(sources, key=lambda x: x[0])[::-1]
            return video_file + helpers.pick_source(sources)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'http://amfphp.indavideo.hu/SYm0json.php/player.playerHandler.getVideoData/%s' % (media_id)