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
from urlresolver9.plugins.openload import OpenLoadResolver

import re

class GreevidResolver(UrlResolver):
    name = "greevid"
    domains = ['greevid.com']
    pattern = '(?://|\.)(greevid\.com)/(?:video_)?([a-zA-Z0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        openload = OpenLoadResolver()
        stream_url = ''
        streams = set()
        count = 1
        for match in re.finditer('<iframe.*src="https://href\.li/\?(.*?)".*>', html):
            print "m",match.group(1)
            print "m2", re.finditer(openload.pattern,match.group(1))
            for match2 in re.finditer(OpenLoadResolver.pattern,match.group(1)):
                stream_url = openload.get_media_url(match2.group(1), match2.group(2))
        return stream_url

    def get_url(self, host, media_id):
        return 'http://greevid.com/video_%s' % (media_id)
