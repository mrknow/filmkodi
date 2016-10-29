"""
mightyupload urlresolver plugin
Copyright (C) 2013 Lynx187

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
from lib import jsunpack
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class MightyuploadResolver(UrlResolver):
    name = "mightyupload"
    domains = ["mightyupload.com"]
    pattern = '(?://|\.)(mightyupload\.com)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        stream_url = None
        form_values = helpers.get_hidden(html)
        html = self.net.http_POST(web_url, form_data=form_values).content
        r = re.search('<IFRAME SRC="(.*?)" .*?></IFRAME>', html, re.DOTALL)
        if r:
            html = self.net.http_GET(r.group(1)).content
        r = re.search("<div id=\"player_code\">.*?<script type='text/javascript'>(.*?)</script>", html, re.DOTALL)
        if not r:
            raise ResolverError('Unable to resolve Mightyupload link. Player config not found.')
        r_temp = re.search("file: '([^']+)'", r.group(1))
        if r_temp:
            stream_url = r_temp.group(1)
        else:
            js = jsunpack.unpack(r.group(1))
            r = re.search("'file','([^']+)'", js.replace('\\', ''))
            if not r:
                r = re.search('"src"value="([^"]+)', js.replace('\\', ''))

            if not r:
                raise ResolverError('Unable to resolve Mightyupload link. Filelink not found.')

            stream_url = r.group(1)

        if stream_url:
            return stream_url + '|' + urllib.urlencode({'User-Agent': common.IE_USER_AGENT})
        else:
            raise ResolverError('Unable to resolve link')

    def get_url(self, host, media_id):
        return 'http://www.mightyupload.com/embed-%s.html' % (media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False
