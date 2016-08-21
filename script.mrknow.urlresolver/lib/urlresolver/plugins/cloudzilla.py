"""
TheFile.me urlresolver plugin
Copyright (C) 2013 voinage

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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class CloudZillaResolver(UrlResolver):
    name = "cloudzilla"
    domains = ['cloudzilla.to', 'neodrive.co']
    pattern = '(?://|\.)(cloudzilla.to|neodrive.co)/(?:share/file|embed)/([A-Za-z0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        match = re.search('vurl\s*=\s*"([^"]+)', html)
        if match:
            return match.group(1)
        else:
            raise ResolverError('Unable to resolve cloudtime link. Filelink not found.')

    def get_url(self, host, media_id):
        return 'http://%s/embed/%s' % (host, media_id)
