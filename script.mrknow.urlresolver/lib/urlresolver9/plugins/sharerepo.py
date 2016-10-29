'''
Sharerepo urlresolver plugin
Copyright (C) 2013 Vinnydude

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
import urllib2
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class SharerepoResolver(UrlResolver):
    name = "sharerepo"
    domains = ["sharerepo.com"]
    pattern = '(?://|\.)(sharerepo\.com)(?:/f)?/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.IE_USER_AGENT,
            'Referer': web_url
        }

        try:
            html = self.net.http_GET(web_url, headers=headers).content
        except urllib2.HTTPError as e:
            if e.code == 404:
                web_url = 'http://sharerepo.com/%s' % media_id
                html = self.net.http_GET(web_url, headers=headers).content
            else:
                raise

        link = re.search("file\s*:\s*'([^']+)", html)
        if link:
            common.log_utils.log_debug('ShareRepo Link Found: %s' % link.group(1))
            return link.group(1) + '|' + urllib.urlencode({'User-Agent': common.IE_USER_AGENT})
        else:
            raise ResolverError('Unable to resolve ShareRepo Link')

    def get_url(self, host, media_id):
        return 'http://sharerepo.com/f/%s' % media_id
