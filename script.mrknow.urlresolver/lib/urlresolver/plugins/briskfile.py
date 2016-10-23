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
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class BriskfileResolver(UrlResolver):
    name = "briskfile"
    domains = ["briskfile.com"]
    pattern = '(?://|\.)(briskfile\.com)/(?:l|e)/([0-9A-Za-z\-]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        match = re.search('''val\(\)\s*\+\s*['"]([^"']+)''', html)
        suffix = match.group(1) if match else ''
        common.log_utils.log(html)
        data = helpers.get_hidden(html)
        for name in data:
            data[name] = data[name] + suffix
        
        common.log_utils.log(data)
        headers['Referer'] = web_url
        html = self.net.http_POST(web_url, form_data=data, headers=headers).content
        html = re.compile(r'clip\s*:\s*\{.*?(?:url|src)\s*:\s*[\"\'](.+?)[\"\']', re.DOTALL).search(html)
        if not html:
            raise ResolverError('File Not Found or removed')
        stream_url = html.group(1)
        req = urllib2.Request(stream_url)
        for key in headers:
            req.add_header(key, headers[key])
        stream_url = urllib2.urlopen(req).geturl()
        return stream_url + helpers.append_headers(headers)

    def get_url(self, host, media_id):
        return 'http://www.briskfile.com/l/%s' % (media_id)
