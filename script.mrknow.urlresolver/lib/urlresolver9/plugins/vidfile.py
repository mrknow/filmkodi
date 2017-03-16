'''
    urlresolver XBMC Addon
    Copyright (C) 2016 MavWolverine

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
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class VidFileResolver(UrlResolver):
    name = "vidfile"
    domains = ["vidfile.net"]
    pattern = '(?://|\.)(vidfile.net)/v/([0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        response = self.net.http_GET(web_url)
        html = response.content
        headers = {'User-Agent': common.IE_USER_AGENT, 'Referer': web_url,
                   'Cookie':response.get_headers(as_dict=True).get('Set-Cookie', '').split(';')[0]}

        if 'File was deleted' in html:
            raise ResolverError('File Removed')

        if 'Video is processing' in html:
            raise ResolverError('File still being processed')

        packed = re.search('(eval\(function.*?)\s*</script>', html, re.DOTALL)
        if packed:
            js = jsunpack.unpack(packed.group(1))
        else:
            js = html

        link = re.search('(http(?:s|)://[^"]*.mp4)', js)
        if link:
            common.log_utils.log_debug('vidfile.net Link Found: %s' % link.group(1))
            print "a", response.get_headers(as_dict=True).get('Set-Cookie', '').split(';')[0]
            return link.group(1)  + helpers.append_headers(headers)

        raise ResolverError('Unable to find vidfile.xyz video')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/v/{media_id}')
