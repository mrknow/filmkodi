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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class FilehootResolver(UrlResolver):
    name = "filehoot"
    domains = ['filehoot.com']
    pattern = '(?://|\.)(filehoot\.com)/(?:embed-)?([0-9a-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        if '404 Not Found' in html:
            raise ResolverError('The requested video was not found.')

        pattern = "file\s*:\s*'([^']+)'\s*,\s*'provider'\s*:\s*'http"
        match = re.search(pattern, html)
        if match:
            return match.group(1)

        raise ResolverError('No video link found.')

    def get_url(self, host, media_id):
        return 'http://%s/embed-%s.html' % (host, media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
