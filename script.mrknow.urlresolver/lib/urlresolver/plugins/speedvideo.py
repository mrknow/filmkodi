'''
SpeedVideo.net urlresolver plugin
Copyright (C) 2014 TheHighway and tknorris

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
'''

import re
import base64
from urlresolver import common
from urlresolver.resolver import UrlResolver

class SpeedVideoResolver(UrlResolver):
    name = "speedvideo"
    domains = ["speedvideo.net"]
    domain = "speedvideo.net"
    pattern = '(?://|\.)(speedvideo\.net)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        a = re.compile('var\s+linkfile *= *"(.+?)"').findall(html)[0]
        b = re.compile('var\s+linkfile *= *base64_decode\(.+?\s+(.+?)\)').findall(html)[0]
        c = re.compile('var\s+%s *= *(\d*)' % b).findall(html)[0]

        stream_url = a[:int(c)] + a[(int(c) + 10):]
        stream_url = base64.b64decode(stream_url)

        return stream_url

    def get_url(self, host, media_id):
        return 'http://speedvideo.net/embed-%s.html' % media_id
