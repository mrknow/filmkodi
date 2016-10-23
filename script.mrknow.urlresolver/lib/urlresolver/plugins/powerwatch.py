"""
powerwatch urlresolver plugin based on StreamcloudResolver
Copyright (C) 2016 Seberoth

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
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class PowerwatchResolver(UrlResolver):
    name = "powerwatch"
    domains = ["powerwatch.pw"]
    pattern = '(?://|\.)(powerwatch\.pw)/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        resp = self.net.http_GET(web_url)
        html = resp.content
        post_url = resp.get_url()

        if re.search('>(File Not Found)<', html):
            raise ResolverError('File Not Found or removed')

        common.kodi.sleep(5000)

        data = helpers.get_hidden(html)
        html = self.net.http_POST(post_url, data).content

        r = re.search('file:"(.+?)",', html)
        if r:
            return r.group(1)
        else:
            raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/{media_id}')
