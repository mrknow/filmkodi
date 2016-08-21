'''
clicknupload urlresolver plugin
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
'''

import re
import urllib
from lib import captcha_lib
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
import xbmc

MAX_TRIES = 3

class UploadXResolver(UrlResolver):
    name = "uploadx"
    domains = ["uploadx.org"]
    pattern = '(?://|\.)(uploadx\.org)/([0-9a-zA-Z/]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        tries = 0
        while tries < MAX_TRIES:
            data = helpers.get_hidden(html)
            data['method_free'] = 'Free+Download+>>'
            data.update(captcha_lib.do_captcha(html))
            headers = {
                'Referer': web_url
            }
            common.log_utils.log_debug(data)
            html = self.net.http_POST(web_url, data, headers=headers).content
            if tries > 0:
                xbmc.sleep(6000)

            if 'File Download Link Generated' in html:
                r = re.search('href="([^"]+)[^>]>Download<', html, re.I)
                if r:
                    return r.group(1) + '|' + urllib.urlencode({'User-Agent': common.IE_USER_AGENT})

            tries = tries + 1

        raise ResolverError('Unable to locate link')

    def get_url(self, host, media_id):
        return 'http://uploadx.org/%s' % media_id
