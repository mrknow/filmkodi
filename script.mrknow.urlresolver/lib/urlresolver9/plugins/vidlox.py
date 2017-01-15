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
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class VidloxResolver(UrlResolver):
    name = "vidlox"
    domains = ['vidlox.tv']
    pattern = '(?://|\.)(vidlox\.tv)/(?:embed-|)([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()
        self.headers = {'User-Agent': common.FF_USER_AGENT}



    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url, headers=self.headers).content
        common.log_utils.log(html)
        default_url = self.__get_def_source(html)
        common.log_utils.log(default_url)
        return default_url

    def __get_def_source(self, html):
        default_url = ''
        match = re.search('sources\s*:\s*\[(.*?)\]', html, re.DOTALL)
        common.log_utils.log(match)
        if match:
            match = re.search('"(https://.*?[^"])"', match.group(1))
            if match:
                default_url = match.group(1) + helpers.append_headers(self.headers)
        return default_url
        #return helpers.get_media_url(self.get_url(host, media_id), result_blacklist=['dl'])

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://vidlox.tv/embed-{media_id}.html')
