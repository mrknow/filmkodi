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
import urllib
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class UploadcResolver(UrlResolver):
    name = 'uploadc'
    domains = ['uploadc.com', 'uploadc.ch', 'zalaa.com']
    pattern = '(?://|\.)(uploadc.com|uploadc.ch|zalaa.com)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        for match in re.finditer('(eval\(function.*?)</script>', html, re.DOTALL):
            js_data = jsunpack.unpack(match.group(1))
            r = re.search('src="([^"]+)', js_data)
            if r:
                stream_url = r.group(1).replace(' ', '%20')
                stream_url += '|' + urllib.urlencode({'Referer': web_url})
                return stream_url

        match = re.search("'file'\s*,\s*'([^']+)", html)
        if match:
            stream_url = match.group(1).replace(' ', '%20')
            stream_url += '|' + urllib.urlencode({'Referer': web_url})
            return stream_url

        raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        return 'http://uploadc.com/embed-%s.html' % (media_id)
