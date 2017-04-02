'''
vidzi urlresolver plugin
Copyright (C) 2014 Eldorado

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

from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError
import re

class trtResolver(UrlResolver):
    name = "trt"
    domains = ["trt.pl"]
    pattern = '(?://|\.)(trt\.pl)/(?:film)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        print "HTML"
        try:
            r = re.findall('<a href="([^"]+)" class="mainPlayerQualityHref" data-url="([^"]+)">720p</a>', html)[0][0]
            print r
            html = self.net.http_GET('https://www.trt.pl%s' % r ).content
        except:
            pass
        try:
            r = re.findall('src="(http[^"]+mp4)"', html)[0]
            return r
        except:
            raise ResolverError('File not found or removed')

    def get_url(self, host, media_id):
        return 'https://www.trt.pl/film/%s' % media_id
