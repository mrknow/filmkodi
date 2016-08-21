"""
    urlresolver XBMC Addon
    Copyright (C) 2015 tknorris

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

class TusfilesResolver(UrlResolver):
    name = "tusfiles"
    domains = ['tusfiles.net']
    pattern = '(?://|\.)(tusfiles\.net)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        direct_url = 'http://%s/%s' % (host, media_id)
        for web_url in [self.get_url(host, media_id), direct_url]:
            html = self.net.http_GET(web_url).content
            for match in re.finditer('(eval\(function.*?)</script>', html, re.DOTALL):
                js_data = jsunpack.unpack(match.group(1))

                stream_url = re.findall('<param\s+name="src"\s*value="([^"]+)', js_data)
                stream_url += re.findall('file\s*:\s*[\'|\"](.+?)[\'|\"]', js_data)
                stream_url = [i for i in stream_url if not i.endswith('.srt')]

                if stream_url:
                    return stream_url[0]

        raise ResolverError('Unable to locate link')

    def get_url(self, host, media_id):
        return 'http://%s/embed-%s.html' % (host, media_id)
