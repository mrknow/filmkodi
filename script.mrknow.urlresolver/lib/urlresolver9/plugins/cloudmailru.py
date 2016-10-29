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

import re
import json
import urllib
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class MailRuResolver(UrlResolver):
    name = "cloud.mail.ru"
    domains = ['cloud.mail.ru']
    pattern = '(?://|\.)(cloud.mail\.ru)/public/([0-9A-Za-z]+/[0-9A-Za-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        print("M",media_id)
        web_url = self.get_url(host, media_id)
        response = self.net.http_GET(web_url)
        r = response.content
        r = re.sub(r'[^\x00-\x7F]+', ' ', r)
        print("u1",r)
        tok = re.findall('"tokens"\s*:\s*{\s*"download"\s*:\s*"([^"]+)', r)[0]
        url = re.findall('"weblink_get"\s*:\s*\[.+?"url"\s*:\s*"([^"]+)', r)[0]
        print url
        url = '%s/%s?key=%s' % (url, media_id, tok)
        print("AAAAA", url)
        return url
        #raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        print 'https://%s/public/%s' % (host, media_id)
        return 'https://%s/public/%s' % (host, media_id)

