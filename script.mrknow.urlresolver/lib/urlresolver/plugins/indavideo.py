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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class IndavideoResolver(UrlResolver):
    name = "indavideo"
    domains = ["indavideo.hu"]
    pattern = '(?://|\.)(indavideo\.hu)/(?:player/video/|video/)(.*)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        hash = re.search('emb_hash.+?value="(.+?)"', html)
        if not hash:
            raise ResolverError('File not found')

        url = 'http://amfphp.indavideo.hu/SYm0json.php/player.playerHandler.getVideoData/' + hash.group(1)

        html = self.net.http_GET(url).content
        if '"success":"1"' in html:
            html = json.loads(html)['data']
            flv_files = list(set(html['flv_files']))
            sources = [(html['video_file'].rsplit('/', 1)[0] + '/' + i) for i in flv_files]
            sources = [(i.rsplit('.', 2)[1], i) for i in sources]
            source = helpers.pick_source(sources, self.get_setting('auto_pick') == 'true')

            return source
        
        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'http://indavideo.hu/video/%s' % (media_id)

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml