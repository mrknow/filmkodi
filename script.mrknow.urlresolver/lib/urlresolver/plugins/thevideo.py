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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

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
        sources = re.findall(r"'?label'?\s*:\s*'([^']+)p'\s*,\s*'?file'?\s*:\s*'([^']+)", html, re.I)
        if sources:
            vt = self.__auth_ip(media_id)
            if vt:
                source = helpers.pick_source(sources, self.get_setting('auto_pick') == 'true')
                return '%s?direct=false&ua=1&vt=%s|User-Agent=%s' % (source, vt, common.SMU_USER_AGENT)
        else:
            raise ResolverError('Unable to locate links')

    def __auth_ip(self, media_id):
        vt = self.__check_auth(media_id)
        if vt: return vt
        
        header = 'TheVideo.me Stream Authorization'
        line1 = 'To play this video, authorization is required'
        line2 = 'Visit the link below to authorize the devices on your network:'
        line3 = '[B][COLOR blue]https://thevideo.me/pair[/COLOR][/B] then "Activate Streaming"'
        with common.kodi.ProgressDialog(header, line1=line1, line2=line2, line3=line3) as pd:
            pd.update(100)
            start = time.time()
            expires = time_left = 300  # give user 5 minutes
            interval = 5  # check url every 5 seconds
            while time_left > 0:
                vt = self.__check_auth(media_id)
                if vt: return vt
                
                time_left = expires - int(time.time() - start)
                progress = time_left * 100 / expires
                pd.update(progress)
                for _ in range(INTERVALS):
                    common.kodi.sleep(interval * 1000 / INTERVALS)
                    if pd.is_canceled(): return
        
    def __check_auth(self, media_id):
        url = 'https://thevideo.me/pair?file_code=%s&check' % (media_id)
        try: js_result = json.loads(self.net.http_GET(url, headers=self.headers).content)
        except ValueError: raise ResolverError('Unusable Authorization Response')
        if js_result.get('status'):
            return js_result.get('response', {}).get('vt')
        
    def get_url(self, host, media_id):
        return 'http://%s/embed-%s.html' % (host, media_id)

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml
