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
import urllib
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class AuEngineResolver(UrlResolver):
    name = "auengine.com"
    domains = ["auengine.com"]
    pattern = '(?://|\.)(auengine\.com)/embed.php\?file=([0-9a-zA-Z\-_]+)[&]*'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        resp = self.net.http_GET(web_url)
        html = resp.content
        r = re.search("video_link\s=\s'(.+?)';", html)
        if r:
            return urllib.unquote_plus(r.group(1))
        else:
            raise ResolverError('no file located')

    def get_url(self, host, media_id):
        return 'http://www.auengine.com/embed.php?file=%s' % (media_id)
