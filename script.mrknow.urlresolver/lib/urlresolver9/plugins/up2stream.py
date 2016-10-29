"""
up2stream urlresolver plugin
Copyright (C) 2015 tknorris

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
import urllib
import urllib2
from lib import jsunpack
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class NoRedirection(urllib2.HTTPErrorProcessor):

    def http_response(self, request, response):
        return response

    https_response = http_response

class Up2StreamResolver(UrlResolver):
    name = "up2stream"
    domains = ["up2stream.com"]
    pattern = '(?://|\.)(up2stream\.com)/view\.php.+?ref=([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        headers = {
            'User-Agent': common.IOS_USER_AGENT,
            'Referer': web_url
        }

        html = self.net.http_GET(web_url, headers=headers).content

        for match in re.finditer('(eval\(function.*?)</script>', html, re.DOTALL):
            html += jsunpack.unpack(match.group(1))

        match = re.findall('<source[^>]*src="([^"]+)', html)
        match += re.findall('"src","([^"]+)', html)

        try:
            stream_url = match[-1]

            r = urllib2.Request(stream_url, headers=headers)
            r = int(urllib2.urlopen(r, timeout=15).headers['Content-Length'])

            if r > 1048576:
                stream_url += '|' + urllib.urlencode(headers)
                return stream_url
        except:
            ResolverError("File Not Playable")

    def get_url(self, host, media_id):
        return 'http://up2stream.com/view.php?ref=%s' % media_id
