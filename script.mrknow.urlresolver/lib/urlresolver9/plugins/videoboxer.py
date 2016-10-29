"""
    OVERALL CREDIT TO:
        t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway

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
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class VideoBoxerResolver(UrlResolver):
    name = "videoboxer.co"
    domains = ['videoboxer.co']
    pattern = '(?://|\.)(videoboxer\.co)/(?:watch|embed)/([a-zA-Z0-9]+)'
    header = {"User-Agent": common.OPERA_USER_AGENT}

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        response = self.net.http_GET(web_url)
        html = response.content

        if html:
            try:
                source = re.search('file:"(.*?)"', html).group(1)
                source = source + '|' + urllib.urlencode(self.header)
                '''headers = dict(response._response.info().items())
                if 'set-cookie' in headers: 
                    cookie = urllib.urlencode({'Cookie': headers['set-cookie']})
                    source = '%s&%s' % (source, cookie)'''

                return source
                
            except:
                raise ResolverError('No playable video found.')

        else: 
            raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return 'http://%s/embed/%s' % (host, media_id)
