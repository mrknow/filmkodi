# -*- coding: utf-8 -*-
"""
openload.io urlresolver plugin
Copyright (C) 2015 tknorris

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
"""
import re
import os
import hashlib
# import json
# import urllib
# import xbmc
# from lib import captcha_lib
# from lib.aa_decoder import AADecoder
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

#OL_SOURCE = 'https://offshoregit.com/tvaresolvers/ol_gmu.py'
#OL_PATH = os.path.join(common.plugins_path, 'ol_gmu.py')

class OpenLoadResolver(UrlResolver):
    name = "openload"
    domains = ["openload.io", "openload.co"]
    pattern = '(?://|\.)(openload\.(?:io|co))/(?:embed|f)/([0-9a-zA-Z-_]+)'

    def __init__(self):
        self.net = common.Net()

    @common.cache.cache_method(cache_limit=8)
    def get_ol_code(self):
        try:
            a=1
            #new_py = self.net.http_GET(OL_SOURCE).content
            #if new_py:
            #    with open(OL_PATH, 'w') as f:
            #        f.write(new_py)
        except Exception as e:
            common.log_utils.log_warning('Exception during openload code retrieve: %s' % e)
            
    def get_media_url(self, host, media_id):
        try:
            #if self.get_setting('auto_update') == 'true':
            #    self.get_ol_code()
            #with open(OL_PATH, 'r') as f:
            #    py_data = f.read()
            #common.log_utils.log('ol_gmu hash: %s' % (hashlib.md5(py_data).hexdigest()))
            import ol_gmu
            web_url = self.get_url(host, media_id)
            return ol_gmu.get_media_url(web_url)
        except Exception as e:
            common.log_utils.log_debug('Exception during openload resolve parse: %s' % e)
            raise
    """
        # Commented out because, by default, all openload videos no longer work with their API so it's a waste
        try:
            info_url = 'https://api.openload.io/1/file/info?file=%s' % (media_id)
            js_result = self.__get_json(info_url)
            if 'result' in js_result and media_id in js_result['result']:
                if js_result['result'][media_id]['status'] != 200:
                    raise ResolverError('File Not Available')
            ticket_url = 'https://api.openload.io/1/file/dlticket?file=%s' % (media_id)
            js_result = self.__get_json(ticket_url)
            video_url = 'https://api.openload.io/1/file/dl?file=%s&ticket=%s' % (
            media_id, js_result['result']['ticket'])
            captcha_url = js_result['result'].get('captcha_url', None)
            if captcha_url:
                captcha_response = captcha_lib.get_response(captcha_url)
                if captcha_response:
                    video_url += '&captcha_response=%s' % urllib.quote(captcha_response)
            xbmc.sleep(js_result['result']['wait_time'] * 1000)
            js_result = self.__get_json(video_url)
            return js_result['result']['url'] + '?mime=true' + '|User-Agent=%s' % common.FF_USER_AGENT
        except ResolverError:
            raise
        except Exception as e:
            raise ResolverError('Exception in openload: %s' % (e))
    """

    """
    def __get_json(self, url):
        result = self.net.http_GET(url).content
        js_result = json.loads(result)
        common.log_utils.log_debug(js_result)
        if js_result['status'] != 200:
            raise ResolverError(js_result['msg'])
        return js_result
    """

    def get_url(self, host, media_id):
        return 'http://openload.io/embed/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_update" type="bool" label="Automatically update resolver" default="true"/>' % (cls.__name__))
        return xml
