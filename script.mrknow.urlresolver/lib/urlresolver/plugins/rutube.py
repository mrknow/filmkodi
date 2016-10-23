"""
    OVERALL CREDIT TO:
        t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway

    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

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
import json
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class RuTubeResolver(UrlResolver):
    name = "rutube.ru"
    domains = ['rutube.ru']
    pattern = '(?://|\.)(rutube\.ru)/(?:play/embed/)?(\d*)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        json_url = 'http://rutube.ru/api/play/options/%s/?format=json&no_404=true' % media_id

        json_data = self.net.http_GET(json_url).content

        try: return json.loads(json_data)['video_balancer']['m3u8']
        except: pass

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return 'http://rutube.ru/play/embed/%s' % media_id


