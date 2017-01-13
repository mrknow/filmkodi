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
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError
from HTMLParser import HTMLParser
import time
import urllib
import base64
from lib.png import Reader as PNGReader

try:
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
except:
    pass

try:
    compat_chr = unichr  # Python 2
except NameError:
    compat_chr = chr
#urllib2.urlopen("https://your-test-server.local", context=ctx)

class OpenLoadResolver(UrlResolver):
    name = "openload"
    domains = ["openload.io", "openload.co"]
    pattern = '(?://|\.)(openload\.(?:io|co))/(?:embed|f)/([0-9a-zA-Z-_]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        try:

            myurl = 'http://openload.co/embed/%s' % media_id
            HTTP_HEADER = {'User-Agent': common.FF_USER_AGENT,'Referer': myurl}  # 'Connection': 'keep-alive'

            response = self.net.http_GET(myurl, headers=HTTP_HEADER)
            html = response.content
            #common.log_utils.log_notice('1 openload html: %s' % (html))
            mylink = self.get_mylink(html)
            HTTP_HEADER = {'Cookie': response.get_headers(as_dict=True).get('Set-Cookie', ''),
                       'User-Agent': common.FF_USER_AGENT, 'Referer':myurl}

            if set('[<>=!@#$%^&*()+{}":;\']+$').intersection(mylink):
                common.log_utils.log_notice('############################## ERROR A openload mylink: %s' % (mylink))
                time.sleep(2)
                html = self.net.http_GET(myurl, headers=HTTP_HEADER).content
                mylink = self.get_mylink(html)
                if set('[<>=!@#$%^&*()+{}":;\']+$').intersection(mylink):
                    common.log_utils.log_notice('############################## ERROR A openload mylink: %s' % (mylink))
                    time.sleep(2)
                    html = self.net.http_GET(myurl, headers=HTTP_HEADER).content
                    mylink = self.get_mylink(html)

            #common.log_utils.log_notice('A openload mylink: %s' % mylink)
            #print "Mylink", mylink, urllib.quote_plus(mylink)
            videoUrl = 'https://openload.co/stream/{0}?mime=true'.format(mylink)
            common.log_utils.log_notice('A openload resolve parse: %s' % videoUrl)

            req = urllib2.Request(videoUrl, None, HTTP_HEADER)
            try:
                #common.log_utils.log_notice('ssl ok')
                res = urllib2.urlopen(req, context=ctx)
            except:
                #common.log_utils.log_notice('ssl not ok')
                res = urllib2.urlopen(req)
            videoUrl = res.geturl()
            res.close()

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

        n = re.findall('<span id="(.*?)">(.*?)</span>', html)
        print "y",n
        ol_id = n[0][1]
        print ol_id

        def parseInt(sin):
            m = re.search(r'^(\d+)[.,]?\d*?', str(sin))
            return int(m.groups()[-1]) if m and not callable(sin) else None

        first_three_chars = int(float(ol_id[0:][:3]))
        fifth_char = int(float(ol_id[3:5]))
        num = 5;
        txt = ''
        while num < len(ol_id):
            txt += compat_chr(int(float(ol_id[num:][:3])) + first_three_chars - fifth_char * int(float(ol_id[num + 3:][:2])))
            num += 5

        return txt

        enc_data = HTMLParser().unescape(y)

        res = []
        for c in enc_data:
            j = ord(c)
            if j >= 33 and j <= 126:
                j = ((j + 14) % 94)
                j = j + 33
            res += chr(j)
        mylink = ''.join(res)

        tmp100 = re.findall('<script type="text/javascript">(ﾟωﾟ.*?)</script>', html, re.DOTALL)
        encdata = ''
        tmpEncodedData = tmp100[0].split('┻━┻')
        for tmpItem in tmpEncodedData:
            try:
                encdata += self.decodeOpenLoad(tmpItem)
            except:
                pass

        #print "AAAAA",encdata

        exit()
        encnumbers = re.findall('return(.*?);', encdata, re.DOTALL)
        print encnumbers

        #https://openload.co/stream/rZ04_L_uRuU~1478308714~95.160.0.0~VWnfq0ig?mime=true
        #https://openload.co/stream/JlSTfXTluk8~1478209703~46.169.0.0~49kqoQ-2?mime=true')


        encnumbers1 = re.findall('(\d+).*?(\d+)', encnumbers[0])[0]
        encnumbers2 = re.findall('(\d+) \- (\d+)', encnumbers[1])[0]
        encnumbers4 = re.findall('(\d+)', encnumbers[3])[0]

        number1 = int(encnumbers1[0]) + int(encnumbers1[1])
        number2 = int(encnumbers2[0]) - int(encnumbers2[1]) + number1
        number4 = int(encnumbers4[0])
        number3 = number2 - number4

        print "num1", number1
        print "num2", number2
        print "num4", number4
        print "num3", number3
        print "a",len(mylink)-number2
        #	var str =
        # tmp.substring(0, tmp.length - number2())
        # + String.fromCharCode(tmp.slice(0 - number2()).charCodeAt(0) + number3())
        # + tmp.substring(tmp.length - number2() + 1);
        #        mylink = ''.join(res)[0:-3] + chr(ord(''.join(res)[-1]) -2 3)

        #https://openload.co/stream/ExatdBfcJ38~1478307277~95.160.0.0~hppYZUHF?mime=true
        mynewlink1 = mylink[0:-number2]
        mynewlink2 = chr(ord(mylink[-number2])+number3)
        mynewlink3 = mylink[len(mylink)-number2+1:]
        print "my2", mynewlink1,mynewlink2,mynewlink3
        mynewlink = mynewlink1+mynewlink2+mynewlink3


        return mynewlink




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

