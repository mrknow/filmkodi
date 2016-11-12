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
import urllib
import re
from lib import captcha_lib
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

MAX_TRIES = 3

class UploadzResolver(UrlResolver):
    name = "uploadz.co"
    domains = ["uploadz.co"]
    pattern = '(?://|\.)(uploadz\.co)/([0-9a-zA-Z/]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        tries = 0
        while tries < MAX_TRIES:
            data = helpers.get_hidden(html, index=0)
            data.update(captcha_lib.do_captcha(html))

            html = self.net.http_POST(web_url, form_data=data).content
            match = re.search('href="([^"]+)[^>]*>Download<', html, re.DOTALL)
            if match:
                return match.group(1)
            tries += 1

        raise ResolverError('Unable to resolve uploadz.co link. Filelink not found.')

    def get_url(self, host, media_id):
        return 'https://uploadz.co/%s' % (media_id)
