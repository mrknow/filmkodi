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
import urllib
from lib import jsunpack
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
        #self.headers = {'User-Agent': common.SMU_USER_AGENT}
        self.headers = {'User-Agent': common.FF_USER_AGENT,
                        'Accept-Language':'en-US,en;q=0.5',
                        'Host': "thevideo.me"}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        headers = {
            'User-Agent': common.FF_USER_AGENT,
            'Referer': web_url
        }
        headers.update(self.headers)
        response = self.net.http_GET(web_url, headers=headers)
        headers['Cookie'] = response.get_headers(as_dict=True).get('Set-Cookie', '')
        print "Headers",headers
        sources1 = []

        html = response.content
        sources = helpers.parse_sources_list(html)
        match = re.search(r"""try_again\s*=\s*['"]([^'^"]+?)['"]""", html, re.DOTALL)
        if match:
            print "UR",match.group(1)
            print "AAA"
            response1 = self.net.http_GET('http://thevideo.me/jwv/%s' %  match.group(1), headers=headers).content
            js = jsunpack.unpack(response1)
            #print "R",js
            ret_headers = {
                'User-Agent': common.FF_USER_AGENT,
                 'Referer': 'http://thevideo.me/player/jw/7/jwplayer.flash.swf'
                }
            vt = re.findall("""b=['"]([^"]+)['"],c=['"]([^"]+)['"]""", js)

        for i, j in enumerate(sources):
            #print "i1 -->",sources[i][1]
            sources1.append([
                sources[i][0],
                sources[i][1] + '?direct=false&%s&%s' % (vt[0][0], vt[0][1])
                    ])
        return helpers.pick_source(sources1) + helpers.append_headers(ret_headers)


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
        #https://thevideo.me/embed-zo5jqio9my56-640x360.html
        return self._default_get_url(host, media_id, 'http://{host}/embed-{media_id}-640x360.html')
        #return self._default_get_url(host, media_id)
