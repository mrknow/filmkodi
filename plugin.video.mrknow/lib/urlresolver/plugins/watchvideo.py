'''
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
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class WatchVideoResolver(UrlResolver):
    name = "watchvideo.us"
    domains = ["watchvideo.us", "watchvideo4.us"]
    pattern = '(?://|\.)(watchvideo[0-9]?\.us)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        if html.find('404 Not Found') >= 0:
            raise ResolverError('File Removed')

        if html.find('Video is processing') >= 0:
            raise ResolverError('File still being processed')

        packed = re.search('(eval\(function.*?)\s*</script>', html, re.DOTALL)
        if packed:
            js = jsunpack.unpack(packed.group(1))
        else:
            js = html

        link = re.search('(?:m3u8").*?"(.*?)"', js)
        if link:
            common.log_utils.log_debug('watchvideo.us Link Found: %s' % link.group(1))
            return link.group(1)

        raise ResolverError('Unable to find watchvideo.us video')

    def get_url(self, host, media_id):
        return 'http://%s/%s.html' % (host, media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
