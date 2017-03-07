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


from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError
import re

class RaptuResolver(UrlResolver):
    name = "raptu"
    domains = ['raptu.com']
    pattern = '(?://|\.)(raptu\.com)/(?:embed/|\?v=)([a-zA-Z0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        sources = []
        streams = set()
        count = 1
        for match in re.finditer('(http[^"]*\.mp4)', html):
            print "m",match.group(1).replace('\\','')
            stream_url = match.group(1).replace('\\','')
            if stream_url not in streams:
                sources.append(('Source %s' % (count), stream_url))
                streams.add(stream_url)
                count += 1

        return helpers.pick_source(sources) + helpers.append_headers(headers)

        #return helpers.get_media_url(self.get_url(host, media_id))

    def get_url(self, host, media_id):
        return 'https://www.raptu.com/?v=%s' % (media_id)
        #return self._default_get_url(host, media_id)
