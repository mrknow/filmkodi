"""
    urlresolver XBMC Addon
    Copyright (C) 2015 tknorris

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
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class FilehootResolver(UrlResolver):
    name = "filehoot"
    domains = ['filehoot.com']
    pattern = '(?://|\.)(filehoot\.com)/(?:embed-)?([0-9a-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.FF_USER_AGENT}

        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url, headers=headers).content

        if '404 Not Found' in html:
            raise ResolverError('The requested video was not found.')

        url = helpers.scrape_sources(html)

        if url:
            return url[0][1] + helpers.append_headers(headers)

        raise ResolverError('No video link found.')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)
