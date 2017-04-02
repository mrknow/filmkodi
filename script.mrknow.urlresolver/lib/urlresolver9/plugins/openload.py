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

            videoUrl = ''

            #try:
            #    mylink = self.get_mylink(html)
            #    videoUrl = mylink
                #common.log_utils.log_notice('A openload resolve parse: %s' % videoUrl)
            #except:
            #    pass

            #try:
            #    req = urllib2.Request(videoUrl, None, HTTP_HEADER)
            #    res = urllib2.urlopen(req)
            #    videoUrl = res.geturl()
            #    res.close()
            #except Exception as e:
            #common.log_utils.log_notice('A openload primary false, backup method. Error: %s' % e)

            try:
                if not self.__file_exists(media_id):
                    raise ResolverError('File Not Available')

                video_url = self.__check_auth(media_id)
                if not video_url:
                    video_url = self.__auth_ip(media_id)
            except ResolverError:
                raise

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

    def get_mylink(self, html):
        try:
            html = html.encode('utf-8')
        except:
            pass
        if any(x in html for x in ['We are sorry', 'File not found']):
            raise Exception('The file was removed')

        #n = re.findall('<span id="(.*?)">(.*?)</span>', html)
        #Author Samsamsam
        #https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2/commit/10438fe21a1ff43bbcafcca9847d43312113b621


        ol_id = re.findall('<span[^>]+id="[^"]+"[^>]*>([0-9A-Za-z]+)</span>',html)[0]
        print ol_id

        def __decode_k(k):
            y = ord(k[0]);
            e = y - 0x37
            d = max(2, e)
            e = min(d, len(k) - 0x24 - 2)
            t = k[e:e + 0x24]
            h = 0
            g = []
            while h < len(t):
                f = t[h:h + 3]
                g.append(int(f, 0x8))
                h += 3
            v = k[0:e] + k[e + 0x24:]
            p = []
            i = 0
            h = 0
            while h < len(v):
                B = v[h:h + 2]
                C = v[h:h + 3]
                f = int(B, 0x10)
                h += 0x2

                if (i % 3) == 0:
                    f = int(C, 8)
                    h += 1
                elif i % 2 == 0 and i != 0 and ord(v[i - 1]) < 0x3c:
                    f = int(C, 0xa)
                    h += 1

                A = g[i % 0x7]
                #A = g[i % 0xc]
                f = f ^ 0xd5;
                f = f ^ A;
                p.append(chr(f))
                i += 1

            return "".join(p)

        dec = __decode_k(ol_id)
        videoUrl = 'https://openload.co/stream/{0}?mime=true'.format(dec)
        return videoUrl





        # If you want to use the code for openload please at least put the info from were you take it:
        # for example: "Code take from plugin IPTVPlayer: "https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2/"
        # It will be very nice if you send also email to me samsamsam@o2.pl and inform were this code will be used
       # start https://github.com/whitecream01/WhiteCream-V0.0.1/blob/master/plugin.video.uwc/plugin.video.uwc-1.0.51.zip?raw=true

    def decode(self,encoded):
        tab = encoded.split('\\')
        ret = ''
        for item in tab:
            try:
                ret += chr(int(item, 8))
            except Exception:
                ret += item
        return ret

    def base10toN(self,num, n):
        num_rep = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f', 16: 'g', 17: 'h', 18: 'i', 19: 'j', 20: 'k',
                   21: 'l', 22: 'm', 23: 'n', 24: 'o', 25: 'p', 26: 'q', 27: 'r', 28: 's', 29: 't', 30: 'u', 31: 'v',
                   32: 'w', 33: 'x', 34: 'y', 35: 'z'}
        new_num_string = ''
        current = num
        while current != 0:
            remainder = current % n
            if 36 > remainder > 9:
                remainder_string = num_rep[remainder]
            elif remainder >= 36:
                remainder_string = '(' + str(remainder) + ')'
            else:
                remainder_string = str(remainder)
            new_num_string = remainder_string + new_num_string
            current = current / n
        return new_num_string

    def decodeOpenLoad(self,aastring):
        # decodeOpenLoad made by mortael, please leave this line for proper credit :)
        # aastring = re.search(r"<video(?:.|\s)*?<script\s[^>]*?>((?:.|\s)*?)</script", html, re.DOTALL | re.IGNORECASE).group(1)

        aastring = aastring.replace("(ﾟДﾟ)[ﾟεﾟ]+(oﾟｰﾟo)+ ((c^_^o)-(c^_^o))+ (-~0)+ (ﾟДﾟ) ['c']+ (-~-~1)+", "")
        aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ) + (ﾟΘﾟ))", "9")
        aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ))", "8")
        aastring = aastring.replace("((ﾟｰﾟ) + (o^_^o))", "7")
        aastring = aastring.replace("((c^_^o)-(c^_^o))", "0")
        aastring = aastring.replace("((ﾟｰﾟ) + (ﾟΘﾟ))", "5")
        aastring = aastring.replace("(ﾟｰﾟ)", "4")
        aastring = aastring.replace("((o^_^o) - (ﾟΘﾟ))", "2")
        aastring = aastring.replace("(o^_^o)", "3")
        aastring = aastring.replace("(ﾟΘﾟ)", "1")
        aastring = aastring.replace("(+!+[])", "1")
        aastring = aastring.replace("(c^_^o)", "0")
        aastring = aastring.replace("(0+0)", "0")
        aastring = aastring.replace("(ﾟДﾟ)[ﾟεﾟ]", "\\")
        aastring = aastring.replace("(3 +3 +0)", "6")
        aastring = aastring.replace("(3 - 1 +0)", "2")
        aastring = aastring.replace("(!+[]+!+[])", "2")
        aastring = aastring.replace("(-~-~2)", "4")
        aastring = aastring.replace("(-~-~1)", "3")
        aastring = aastring.replace("(-~0)", "1")
        aastring = aastring.replace("(-~1)", "2")
        aastring = aastring.replace("(-~3)", "4")
        aastring = aastring.replace("(0-0)", "0")

        aastring = aastring.replace("(ﾟДﾟ).ﾟωﾟﾉ", "10")
        aastring = aastring.replace("(ﾟДﾟ).ﾟΘﾟﾉ", "11")
        aastring = aastring.replace("(ﾟДﾟ)[\'c\']", "12")
        aastring = aastring.replace("(ﾟДﾟ).ﾟｰﾟﾉ", "13")
        aastring = aastring.replace("(ﾟДﾟ).ﾟДﾟﾉ", "14")
        aastring = aastring.replace("(ﾟДﾟ)[ﾟΘﾟ]", "15")

        decodestring = re.search(r"\\\+([^(]+)", aastring, re.DOTALL | re.IGNORECASE).group(1)
        decodestring = "\\+" + decodestring
        decodestring = decodestring.replace("+", "")
        decodestring = decodestring.replace(" ", "")

        decodestring = self.decode(decodestring)
        decodestring = decodestring.replace("\\/", "/")

        if 'toString' in decodestring:
            base = re.compile(r"toString\(a\+(\d+)", re.DOTALL | re.IGNORECASE).findall(decodestring)[0]
            base = int(base)
            match = re.compile(r"(\(\d[^)]+\))", re.DOTALL | re.IGNORECASE).findall(decodestring)
            for repl in match:
                match1 = re.compile(r"(\d+),(\d+)", re.DOTALL | re.IGNORECASE).findall(repl)
                base2 = base + int(match1[0][0])
                repl2 = self.base10toN(int(match1[0][1]), base2)
                decodestring = decodestring.replace(repl, repl2)
            decodestring = decodestring.replace("+", "")
            decodestring = decodestring.replace("\"", "")
        return decodestring

    def get_url(self, host, media_id):
        return 'http://openload.co/embed/%s' % (media_id)

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