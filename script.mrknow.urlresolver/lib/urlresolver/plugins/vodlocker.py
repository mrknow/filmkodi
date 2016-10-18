"""
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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class VodlockerResolver(UrlResolver):
    name = "vodlocker.com"
    domains = ["vodlocker.com"]
    pattern = '(?://|\.)(vodlocker\.com)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        link = self.net.http_GET(web_url).content
        if 'FILE WAS DELETED' in link:
            raise ResolverError('File deleted.')

        video_link = str(re.compile('file[: ]*"(.+?)"').findall(link)[0])

        if len(video_link) > 0:
            return video_link
        else:
            raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return 'http://vodlocker.com/embed-%s-640x400.html' % media_id
