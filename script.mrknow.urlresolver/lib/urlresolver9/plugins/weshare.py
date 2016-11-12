"""
grifthost urlresolver plugin
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
"""

import re
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class WeShareResolver(UrlResolver):
    name = "weshare.me"
    domains = ["weshare.me"]
    pattern = '(?://|\.)(weshare\.me)/(?:services/mediaplayer/site/_embed(?:\.max)?\.php\?u=)?([A-Za-z0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = helpers.scrape_sources(html)
        if not sources:
            match = re.search('''href="([^"]+)[^>]+>\(download\)''', html, re.DOTALL)
            if match:
                sources = [('Download', match.group(1))]

        headers['Referer'] = web_url
        return helpers.pick_source(sources) + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return 'https://weshare.me/services/mediaplayer/site/_embed.max.php?u=%s' % (media_id)
