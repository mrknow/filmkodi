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
import urllib2
import json
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError
from urlresolver9.common import i18n

import js2py
import os

API_BASE_URL = 'https://api.openload.co/1'
INFO_URL = API_BASE_URL + '/streaming/info'
GET_URL = API_BASE_URL + '/streaming/get?file={media_id}'
FILE_URL = API_BASE_URL + '/file/info?file={media_id}'

try:
    compat_chr = unichr  # Python 2
except NameError:
    compat_chr = chr
#urllib2.urlopen("https://your-test-server.local", context=ctx)

class OpenLoadResolver(UrlResolver):
    name = "openload"
    domains = ["openload.io", "openload.co"]
    #pattern = '(?://|\.)(openload\.(?:io|co))/(?:embed|f)/([0-9a-zA-Z\-_]+)'
    pattern = '(?://|\.)(openload\.(?:io|co))/(?:embed|f)/([0-9a-zA-Z-_]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        try:

            myurl = 'http://openload.co/embed/%s' % media_id
            HTTP_HEADER = {'User-Agent': common.FF_USER_AGENT,'Referer': myurl}  # 'Connection': 'keep-alive'

            response = self.net.http_GET(myurl, headers=HTTP_HEADER)
            html = response.content
            common.log_utils.log_notice('%s; DIRECTORY' % os.getcwd())

            videoUrl = media_id


            if not self.__file_exists(media_id):
                raise ResolverError('File Not Available')

            try:
                ol_id = re.findall(r'''<span[^>]+id=(["'])[^"']+\1[^>]*>(?P<id>[0-9A-Za-z]+)</span>''',html)
                video_url = 'https://openload.co/stream/%s?mime=true'

                decoded = self._eval_id_decoding(html, ol_id[0][-1])
                video_url = video_url % decoded
                return video_url
            except Exception as e:
                common.log_utils.log_notice('%s; falling back to method with pairing, error: %s' % (media_id,e))

                #video_url = self.__check_auth(media_id)
                #if not video_url:
                #    video_url = self.__auth_ip(media_id)


            if video_url:
                return video_url
            else:
                raise ResolverError(i18n('no_ol_auth'))

            #return videoUrl + helpers.append_headers({'User-Agent': common.FF_USER_AGENT})
            return videoUrl
            # video_url = 'https://openload.co/stream/%s?mime=true' % myvidurl


        except Exception as e:
            common.log_utils.log_notice('Exception during openload resolve parse: %s' % e)
            print("Error", e)
            raise

    def get_url(self, host, media_id):
        return 'http://openload.io/embed/%s' % media_id

    def __file_exists(self, media_id):
        js_data = self.__get_json(FILE_URL.format(media_id=media_id))
        return js_data.get('result', {}).get(media_id, {}).get('status') == 200

    def __auth_ip(self, media_id):
        js_data = self.__get_json(INFO_URL)
        pair_url = js_data.get('result', {}).get('auth_url', '')
        if pair_url:
            pair_url = pair_url.replace('\/', '/')
            header = i18n('ol_auth_header')
            line1 = i18n('auth_required')
            line2 = i18n('visit_link')
            line3 = i18n('click_pair') % (pair_url)
            with common.kodi.CountdownDialog(header, line1, line2, line3) as cd:
                return cd.start(self.__check_auth, [media_id])

    def __check_auth(self, media_id):
        try:
            js_data = self.__get_json(GET_URL.format(media_id=media_id))
        except ResolverError as e:
            status, msg = e
            if status == 403:
                return
            else:
                raise ResolverError(msg)

        return js_data.get('result', {}).get('url')

    def __get_json(self, url):
        result = self.net.http_GET(url).content
        common.log_utils.log(result)
        js_result = json.loads(result)
        if js_result['status'] != 200:
            raise ResolverError(js_result['status'], js_result['msg'])
        return js_result

    def _eval_id_decoding(self, webpage, ol_id):
        try:
            # raise # uncomment to test method with pairing
            js_code = re.findall(
                ur"(ﾟωﾟﾉ=.*?\('_'\);.*?)ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //\*´∇｀\*/ \['_'\];"
            ,webpage, re.DOTALL)[0]
            #common.log_utils.log_notice('js_code: %s' % js_code)
            js_code = re.sub('''if\s*\([^\}]+?typeof[^\}]+?\}''', '', js_code)
            js_code = re.sub('''if\s*\([^\}]+?document[^\}]+?\}''', '', js_code)
        except Exception as e:
            print 'Could not find JavaScript %s' % e
            raise ResolverError('Could not find JavaScript %s' % e)


        js_code = '''
            var id = "%s"
              , decoded
              , document = {}
              , window = this
              , $ = function(){
                  return {
                    text: function(a){
                      if(a)
                        decoded = a;
                      else
                        return id;
                    },
                    ready: function(a){
                      a()
                    }
                  }
                };
            (function(d){
              var f = function(){};
              var s = '';
              var o = null;
              ['close','createAttribute','createDocumentFragment','createElement','createElementNS','createEvent','createNSResolver','createRange','createTextNode','createTreeWalker','evaluate','execCommand','getElementById','getElementsByName','getElementsByTagName','importNode','open','queryCommandEnabled','queryCommandIndeterm','queryCommandState','queryCommandValue','write','writeln'].forEach(function(e){d[e]=f;});
              ['anchors','applets','body','defaultView','doctype','documentElement','embeds','firstChild','forms','images','implementation','links','location','plugins','styleSheets'].forEach(function(e){d[e]=o;});
              ['URL','characterSet','compatMode','contentType','cookie','designMode','domain','lastModified','referrer','title'].forEach(function(e){d[e]=s;});
            })(document);
            %s;
            decoded;''' % (ol_id, js_code)

        try:
            decoded = js2py.eval_js(js_code)
            if ' ' in decoded or decoded == '':
                raise
            return decoded
        except:
            raise ResolverError('Could not eval ID decoding')