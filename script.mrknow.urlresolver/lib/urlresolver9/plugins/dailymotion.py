'''
dailymotion urlresolver plugin
Copyright (C) 2011 cyrus007

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
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class DailymotionResolver(UrlResolver):
    name = 'dailymotion'
    domains = ['dailymotion.com']
    pattern = '(?://|\.)(dailymotion\.com)/(?:video|embed|sequence|swf)(?:/video)?/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        if '"reason":"video attribute|explicit"' in html:
            headers = {'User-Agent': common.FF_USER_AGENT, 'Referer': web_url}
            url_back = '/embed/video/%s' % media_id
            web_url = 'http://www.dailymotion.com/family_filter?enable=false&urlback=%s' % urllib.quote_plus(url_back)
            html = self.net.http_GET(url=web_url, headers=headers).content

        html = html.replace('\\', '')

        livesource = re.findall('"auto"\s*:\s*.+?"url"\s*:\s*"(.+?)"', html)

        sources = re.findall('"(\d+)"\s*:.+?"url"\s*:\s*"([^"]+)', html)

        if not sources and not livesource:
            raise ResolverError('File not found')

        if livesource and not sources:
            return self.net.http_HEAD(livesource[0]).get_url()

        sources = sorted(sources, key=lambda x: x[0])[::-1]

        source = helpers.pick_source(sources)

        if not '.m3u8' in source:
            raise ResolverError('File not found')

        vUrl = self.net.http_GET(source).content
        vUrl = re.search('(http.+?m3u8)', vUrl)

        if vUrl:
            return vUrl.group(1)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'http://www.dailymotion.com/embed/video/%s' % media_id

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml
