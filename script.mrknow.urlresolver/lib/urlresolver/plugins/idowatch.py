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
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class IDoWatchResolver(UrlResolver):
    name = 'idowatch'
    domains = ['idowatch.net']
    pattern = '(?://|\.)(idowatch\.net)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        if 'File Not Found' in html:
            raise ResolverError('File Removed')
            
        try: html += jsunpack.unpack(re.search('(eval\(function.*?)</script>', html, re.DOTALL).group(1))
        except: pass

        match = re.findall('''["']?sources['"]?\s*:\s*\[(.*?)\]''', html)

        if match:
            stream_url = re.findall('''['"]?file['"]?\s*:\s*['"]?([^'"]+)''', match[0])
            stream_url = [i for i in stream_url if not i.endswith('smil')]
            if stream_url:
                return stream_url[0] + '|' + urllib.urlencode({'User-Agent': common.FF_USER_AGENT})

        raise ResolverError('Unable to resolve idowatch link. Filelink not found.')

    def get_url(self, host, media_id):
        return 'http://idowatch.net/%s.html' % (media_id)
