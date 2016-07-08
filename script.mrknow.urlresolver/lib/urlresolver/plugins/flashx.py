"""
    Kodi urlresolver plugin
    Copyright (C) 2014  smokdpi

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
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class FlashxResolver(UrlResolver):
    name = "flashx"
    domains = ["flashx.tv"]
    pattern = '(?://|\.)(flashx\.tv)/(?:embed-|dl|embed\.php\?c=)([0-9a-zA-Z/]+)'

    def __init__(self):
        self.net = common.Net()
        print 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

    def get_media_url(self, host, media_id):
        print 'AAdddddddddddd'
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        print html
        try: html = jsunpack.unpack(re.search('(eval\(function.*?)</script>', html, re.DOTALL).group(1))
        except: pass

        stream = re.findall('file\s*:\s*"(http.*?)"\s*,\s*label\s*:\s*"', html, re.DOTALL)

        if stream:
            return stream[-1]
        else:
            raise ResolverError('Unable to resolve Flashx link. Filelink not found.')

    def get_url(self, host, media_id):
        return 'http://www.flashx.tv/playit-%s.html' % media_id


    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False