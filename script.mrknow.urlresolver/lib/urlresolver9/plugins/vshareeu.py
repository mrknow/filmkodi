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
from lib import helpers
from lib import jsunpack
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class VshareEuResolver(UrlResolver):
    name = "vshare.eu"
    domains = ['vshare.eu']
    pattern = '(?://|\.)(vshare\.eu)/(?:embed-|)?([0-9a-zA-Z/]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        headers = {
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': common.FF_USER_AGENT
        }

        html = self.net.http_GET(web_url, headers=headers).content

        if '404 Not Found' in html or 'Has Been Removed' in html:
            raise ResolverError('The requested video was not found.')

        data = helpers.get_hidden(html)
        headers['Referer'] = web_url
        response = self.net.http_POST(web_url, data, headers=headers)
        html = response.content
        headers = {'Cookie': response.get_headers(as_dict=True).get('Set-Cookie', ''),
                   'User-Agent': common.FF_USER_AGENT}
        sources = helpers.scrape_sources(html)
        return helpers.pick_source(sources) + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return 'http://vshare.eu/%s' % (media_id)
