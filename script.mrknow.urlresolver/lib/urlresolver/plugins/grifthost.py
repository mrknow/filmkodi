"""
grifthost urlresolver plugin
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
from lib import helpers
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class GrifthostResolver(UrlResolver):
    name = "grifthost"
    domains = ["grifthost.com"]
    pattern = '(?://|\.)(grifthost\.com)/(?:embed-)?([0-9a-zA-Z/]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        data = helpers.get_hidden(html)
        data['method_free'] = 'Proceed to Video'
        html = self.net.http_POST(web_url, form_data=data).content
        stream_url = ''
        for match in re.finditer('(eval\(function.*?)</script>', html, re.DOTALL):
            js_data = jsunpack.unpack(match.group(1))
            match2 = re.search('<param\s+name="src"\s*value="([^"]+)', js_data)
            if match2:
                stream_url = match2.group(1)
            else:
                match2 = re.search('file\s*:\s*"([^"]+)', js_data)
                if match2:
                    stream_url = match2.group(1)

        if stream_url:
            return stream_url + '|' + urllib.urlencode({'User-Agent': common.IE_USER_AGENT, 'Referer': web_url})

        raise ResolverError('Unable to resolve grifthost link. Filelink not found.')

    def get_url(self, host, media_id):
        return 'http://grifthost.com/%s' % (media_id)
