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
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class VideowoodResolver(UrlResolver):
    name = "videowood"
    domains = ['videowood.tv']
    pattern = '(?://|\.)(videowood\.tv)/(?:embed/|video/)([0-9a-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        stream_url = None
        headers = {'Referer': web_url}
        html = self.net.http_GET(web_url, headers=headers).content
        if "This video doesn't exist." in html:
            raise ResolverError('The requested video was not found.')
        packed = re.search('(eval\(function\(p,a,c,k,e,d\)\{.+\))', html)
        unpacked = None
        if packed:
            # change radix before trying to unpack, 58-61 seen in testing, 62 worked for all
            packed = re.sub(r"(.+}\('.*', *)\d+(, *\d+, *'.*?'\.split\('\|'\))", "\g<01>62\g<02>", packed.group(1))
            unpacked = jsunpack.unpack(packed)
        if unpacked:
            r = re.search('.+["\']file["\']\s*:\s*["\'](.+?/video\\\.+?)["\']', unpacked)
            if r:
                stream_url = r.group(1).replace('\\', '')
        if stream_url:
            return stream_url
        else:
            raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'http://videowood.tv/embed/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
