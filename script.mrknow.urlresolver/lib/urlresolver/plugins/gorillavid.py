"""
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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class GorillavidResolver(UrlResolver):
    name = "gorillavid"
    domains = ["gorillavid.in", "gorillavid.com"]
    pattern = '(?://|\.)(gorillavid\.(?:in|com))/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        resp = self.net.http_GET(web_url)
        html = resp.content
        r = re.findall(r"<title>404 - Not Found</title>", html)
        if r:
            raise ResolverError('File Not Found or removed')
        post_url = resp.get_url()
        form_values = helpers.get_hidden(html)
        html = self.net.http_POST(post_url, form_data=form_values).content
        r = re.search('file: "(.+?)"', html)
        if r:
            return r.group(1)
        else:
            raise ResolverError('Unable to resolve Gorillavid link')

    def get_url(self, host, media_id):
        return 'http://gorillavid.in/%s' % (media_id)


    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False