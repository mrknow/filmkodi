"""
Youwatch urlresolver XBMC Addon
Copyright (C) 2015 tknorris
Updated by alifrezser (c) 2016

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
import urllib
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

MAX_TRIES = 5

class YouWatchResolver(UrlResolver):
    name = "youwatch"
    domains = ["youwatch.org", "chouhaa.info"]
    pattern = '(?://|\.)(youwatch\.org|chouhaa\.info)/(?:embed-)?([A-Za-z0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        web_url = self.net.http_GET(web_url)._response.url
        headers = {'Referer': web_url}

        tries = 0
        while tries < MAX_TRIES:
            html = self.net.http_GET(web_url).content
            html = html.replace('\n', '')
            r = re.search('<iframe\s+src\s*=\s*"([^"]+)', html)
            if r:
                web_url = r.group(1)
            else:
                break
            tries += 1
        
        html = self.net.http_GET(web_url, headers=headers).content
        r = re.search('file\s*:\s*"([^"]+)', html)
        if r:
            return r.group(1) + '|' + urllib.urlencode({'Referer': web_url})

        raise ResolverError('Unable to resolve youwatch link. Filelink not found.')

    def get_url(self, host, media_id):
        return 'http://youwatch.org/embed-%s.html' % media_id
