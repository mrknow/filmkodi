'''
urlresolver XBMC Addon
Copyright (C) 2013 Bstrdsmkr

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
import urllib2
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class PromptfileResolver(UrlResolver):
    name = "promptfile"
    domains = ["promptfile.com"]
    pattern = '(?://|\.)(promptfile\.com)/(?:l|e)/([0-9A-Za-z\-]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        data = {}
        r = re.findall(r'type="hidden"\s*name="(.+?)"\s*value="(.*?)"', html)
        for name, value in r:
            data[name] = value
        html = self.net.http_POST(web_url, data).content
        html = re.compile(r'clip\s*:\s*\{.*?url\s*:\s*[\"\'](.+?)[\"\']', re.DOTALL).search(html)
        if not html:
            raise ResolverError('File Not Found or removed')
        stream_url = html.group(1)
        stream_url = urllib2.urlopen(urllib2.Request(stream_url)).geturl()
        return stream_url

    def get_url(self, host, media_id):
        return 'http://www.promptfile.com/e/%s' % (media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
