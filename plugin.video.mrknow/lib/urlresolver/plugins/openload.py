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
import json
import urllib
from lib import captcha_lib
from lib.aa_decoder import AADecoder
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
import xbmc


class OpenLoadResolver(UrlResolver):
    name = "openload"
    domains = ["openload.io", "openload.co"]
    pattern = '(?://|\.)(openload\.(?:io|co))/(?:embed|f)/([0-9a-zA-Z-_]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        def baseN(num, b, numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
            return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

        def conv(s, addfactor=None):
            if 'function()' in s:
                addfactor = s.split('b.toString(')[1].split(')')[0]
                fname = re.findall('function\(\)\{function (.*?)\(', s)[0]
                s = s.replace(fname, 'myfunc')
                s = ''.join(s.split('}')[1:])
            if '+' not in s:
                if '.0.toString' in s:
                    ival, b = s.split('.0.toString(')
                    b = b.replace(')', '')
                    return baseN(int(ival), int(eval(b)))
                elif 'myfunc' in s:
                    b, ival = s.split('myfunc(')[1].split(',')
                    ival = ival.replace(')', '').replace('(', '')
                    b = b.replace(')', '').replace('(', '')
                    b = eval(addfactor.replace('a', b))
                    return baseN(int(ival), int(b))
                else:
                    return eval(s)
            r = ''
            for ss in s.split('+'):
                r += conv(ss, addfactor)
            return r

        try:
            web_url = self.get_url(host, media_id)
            headers = {'User-Agent': common.FF_USER_AGENT}
            html = self.net.http_GET(web_url, headers=headers).content.encode('utf-8')
            aaencoded = re.findall('id=\"olvideo\".*\n.*?text/javascript\">(.*)</script>', html)[0]
            dtext = AADecoder(aaencoded).decode()
            dtext = re.findall('window.vs=(.*?);', dtext)[0]
            dtext = conv(dtext)
            return dtext.replace("https", "http") + '|User-Agent=%s' % common.FF_USER_AGENT

        except Exception as e:
            common.log_utils.log_debug('Exception during openload resolve parse: %s' % e)

        # Commented out because, by default, all openload videos no longer work with their API so it's a waste
        #         try:
        #             info_url = 'https://api.openload.io/1/file/info?file=%s' % (media_id)
        #             js_result = self.__get_json(info_url)
        #             if 'result' in js_result and media_id in js_result['result']:
        #                 if js_result['result'][media_id]['status'] != 200:
        #                     raise ResolverError('File Not Available')
        #             ticket_url = 'https://api.openload.io/1/file/dlticket?file=%s' % (media_id)
        #             js_result = self.__get_json(ticket_url)
        #             video_url = 'https://api.openload.io/1/file/dl?file=%s&ticket=%s' % (media_id, js_result['result']['ticket'])
        #             captcha_url = js_result['result'].get('captcha_url', None)
        #             if captcha_url:
        #                 captcha_response = captcha_lib.get_response(captcha_url)
        #                 if captcha_response:
        #                     video_url += '&captcha_response=%s' % urllib.quote(captcha_response)
        #             xbmc.sleep(js_result['result']['wait_time'] * 1000)
        #             js_result = self.__get_json(video_url)
        #             return js_result['result']['url'] + '?mime=true'
        #         except ResolverError:
        #             raise
        #         except Exception as e:
        #             raise ResolverError('Exception in openload: %s' % (e))

        raise ResolverError('Unable to resolve openload.io link. Filelink not found.')

    def __get_json(self, url):
        result = self.net.http_GET(url).content
        js_result = json.loads(result)
        common.log_utils.log_debug(js_result)
        if js_result['status'] != 200:
            raise ResolverError(js_result['msg'])
        return js_result

    def get_url(self, host, media_id):
        return 'http://openload.io/embed/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
