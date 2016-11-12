'''
thevideo urlresolver plugin
Copyright (C) 2014 Eldorado

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
import json
import time
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

INTERVALS = 5

class TheVideoResolver(UrlResolver):
    name = "thevideo"
    domains = ["thevideo.me"]
    pattern = '(?://|\.)(thevideo\.me)/(?:embed-|download/)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()
        self.headers = {'User-Agent': common.SMU_USER_AGENT}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'Referer': web_url
        }
        headers.update(self.headers)
        html = self.net.http_GET(web_url, headers=headers).content
        sources = helpers.parse_sources_list(html)
        if sources:
            vt = self.__auth_ip(media_id)
            if vt:
                source = helpers.pick_source(sources)
                return '%s?direct=false&ua=1&vt=%s' % (source, vt) + helpers.append_headers({'User-Agent': common.SMU_USER_AGENT})
        else:
            raise ResolverError('Unable to locate links')

    def __auth_ip(self, media_id):
        header = 'TheVideo.me Stream Authorization'
        line1 = 'To play this video, authorization is required'
        line2 = 'Visit the link below to authorize the devices on your network:'
        line3 = '[B][COLOR blue]https://thevideo.me/pair[/COLOR][/B] then "Activate Streaming"'
        with common.kodi.CountdownDialog(header, line1, line2, line3) as cd:
            return cd.start(self.__check_auth, [media_id])
        
    def __check_auth(self, media_id):
        common.log_utils.log('Checking Auth: %s' % (media_id))
        url = 'https://thevideo.me/pair?file_code=%s&check' % (media_id)
        try: js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        except ValueError: raise ResolverError('Unusable Authorization Response')
        common.log_utils.log('Auth Result: %s' % (js_result))
        if js_result.get('status'):
            return js_result.get('response', {}).get('vt')
        
    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id)
