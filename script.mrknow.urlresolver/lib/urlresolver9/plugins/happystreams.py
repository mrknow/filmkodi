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
from lib import jsunpack
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class HappyStreamsResolver(UrlResolver):
    name = "happystreams"
    domains = ['happystreams.net']
    pattern = '(?://|\.)(happystreams\.net)/([0-9a-zA-Z/-]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id): # need fix
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        data = helpers.get_hidden(html)
        furl = 'http://happystreams.net/dl'
        headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': web_url, 'Cookie': self.__get_cookies(host, html)}
        html = self.net.http_POST(url=furl, form_data=data, headers=headers).content
        html = helpers.add_packed_data(html)
        source = re.search(r'file:\"(.*?)\"', html).groups()[0]
        return source

    def __get_cookies(self, host, html):
        cookies = ['ref_url=http%3A%2F%2Fhappystreams.net%2F']
        for match in re.finditer("\$\.cookie\(\s*'([^']+)'\s*,\s*'([^']+)", html):
            key, value = match.groups()
            cookies.append('%s=%s' % (key, value))
        return '; '.join(cookies)

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/{media_id}')
        
