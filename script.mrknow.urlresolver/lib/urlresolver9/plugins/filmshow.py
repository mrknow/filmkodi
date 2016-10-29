'''
FilmShow urlresolver plugin
Copyright (C) 2016 Gujal

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
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class FilmShowResolver(UrlResolver):
    name = "www.filmshowonline.net"
    domains = ["www.filmshowonline.net"]
    pattern = '(?://|\.)(filmshowonline\.net)/(?:videos/)?([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        r = re.search('data-config="(.*?)"', html)
        if r:
            rid = re.search('com/(\d*)/.*/(\d*)/', r.group(1))
            rurl = 'https://cdn.video.playwire.com/%s/videos/%s/video-sd.mp4?hosting_id=%s' % \
                   (str(rid.group(1)), str(rid.group(2)), str(rid.group(1)))
            return rurl

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://www.filmshowonline.net/videos/%s/' % media_id
