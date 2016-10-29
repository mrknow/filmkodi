'''
    urlresolver Kodi plugin
    Copyright (C) 2016 Gujal

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
'''

import re
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class YouLOLResolver(UrlResolver):
    name = "youlol.biz"
    domains = ["youlol.biz", "shitmovie.com"]
    pattern = '(?://|\.)(youlol\.biz|shitmovie\.com)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        if 'Not Found' in html:
            raise ResolverError('File Removed')

        if 'Video is processing' in html:
            raise ResolverError('File still being processed')

        match = re.search('sources\s*:\s*\[(.*?)\]', html, re.DOTALL)
        if match:
            sources = re.findall('''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^{,]*(?:,['"]?label['"]?\s*:\s*['"]([^'"]*))?''', match.group(1))
            sources = [(s[1], s[0]) for s in sources]
            return helpers.pick_source(sources, self.get_setting('auto_pick') == 'true')

        raise ResolverError('Unable to find youlol video')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'http://{host}/{media_id}.html')

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml
