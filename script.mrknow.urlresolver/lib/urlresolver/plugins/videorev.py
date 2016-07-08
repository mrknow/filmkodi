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
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class VideoRevResolver(UrlResolver):
    name = "videorev"
    domains = ['videorev.cc']
    pattern = '(?://|\.)(videorev\.cc)/([a-zA-Z0-9]+)\.html'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        response = self.net.http_GET(web_url)
        html = response.content

        if html:
            smil_id = re.search('([a-zA-Z0-9]+)(?=\|smil)', html).groups()[0]
            smil_url = 'http://%s/%s.smil' % (host, smil_id)
            result = self.net.http_GET(smil_url).content
            
            base = re.search('base="(.+?)"', result).groups()[0]
            srcs = re.findall('src="(.+?)"', result)
            try:
                res = re.findall('width="(.+?)"', result)
            except:
                res = res = re.findall('height="(.+?)"', result)

            i = 0
            sources = []
            for src in srcs:
                sources.append([str(res[i]), '%s playpath=%s' % (base, src)])
                i += 1
                
            source = helpers.pick_source(sources, self.get_setting('auto_pick') == 'true')
            source = source.encode('utf-8')

            return source

        raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return 'http://%s/%s.html' % (host, media_id)

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml
            
