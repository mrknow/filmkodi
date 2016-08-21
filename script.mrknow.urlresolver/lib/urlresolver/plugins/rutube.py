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
import urllib
import HTMLParser
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class RuTubeResolver(UrlResolver):
    name = "rutube.ru"
    domains = ['rutube.ru']
    pattern = '(?://|\.)(rutube\.ru)/play/embed/(\d*)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        response = self.net.http_GET(web_url)

        html = response.content

        if html:
            m3u8 = re.compile('video_balancer&quot;:\s*{.*?&quot;m3u8&quot;:\s*&quot;(.*?)&quot;}').findall(html)[0]
            m3u8 = HTMLParser.HTMLParser().unescape(m3u8)
            response = self.net.http_GET(m3u8)
            m3u8 = response.content
            
            sources = re.compile('\n(.+?i=(.+?))\n').findall(m3u8)
            sources = sources[::-1]
            sources = [sublist[::-1] for sublist in sources]
            
            source = helpers.pick_source(sources, self.get_setting('auto_pick') == 'true')
            source = source.encode('utf-8')

            if source:
                return source

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return 'http://rutube.ru/play/embed/%s' % media_id

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml
