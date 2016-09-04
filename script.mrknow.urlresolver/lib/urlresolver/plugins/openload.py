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
import base64
import math
import urllib
import urllib2
# import xbmc
# from lib import captcha_lib
# from lib.aa_decoder import AADecoder
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
from lib.png import Reader as PNGReader
from HTMLParser import HTMLParser
#OL_SOURCE = 'https://offshoregit.com/tvaresolvers/ol_gmu.py'
#OL_PATH = os.path.join(common.plugins_path, 'ol_gmu.py')

class OpenLoadResolver(UrlResolver):
    name = "openload"
    domains = ["openload.io", "openload.co"]
    pattern = '(?://|\.)(openload\.(?:io|co))/(?:embed|f)/([0-9a-zA-Z-_]+)'

    def __init__(self):
        self.net = common.Net()

            
    def get_media_url(self, host, media_id):
        try:
            myurl = 'http://openload.co/embed/%s' % media_id
            HTTP_HEADER = {
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                'Accept-Encoding': 'none',
                'Accept-Language': 'en-US,en;q=0.8',
                'Referer': myurl}  # 'Connection': 'keep-alive'
            resp = self.net.http_GET(myurl, headers=HTTP_HEADER)
            html = resp.content
            #cfcookie = html._response.info()['set-cookie']
            #cfcookie = resp._response.headers
            if any(x in html for x in ['We are sorry', 'File not found']):
                raise Exception('The file was removed')

            m = re.search(r'<span id="hiddenurl">(.+?)<\/span>', html)

            if not m:
                raise Exception("Video link encrypted data is not available.")

            enc_data = m.group(1).strip()
            enc_data = HTMLParser().unescape(enc_data)

            # print enc_data

            video_url_chars = []

            for c in enc_data:
                j = ord(c)
                if j >= 33 and j <= 126:
                    j = ((j + 14) % 94) + 33
                video_url_chars += chr(j)
            print video_url_chars;
            myvidurl = ''.join(video_url_chars)
            print "--", myvidurl
            myvidurl  = myvidurl [0:-1] +chr(ord(myvidurl [-1])+2)
            print "--",myvidurl

            #var x = $("#hiddenurl").text();
	        #var s=[];for(var i=0;i<x.length;i++){var j=x.charCodeAt(i);if((j>=33)&&(j<=126)){s[i]=String.fromCharCode(33+((j+14)%94));}else{s[i]=String.fromCharCode(j);}}
	        #var tmp=s.join("");
	        #var str = tmp.substring(0, tmp.length - 1) + String.fromCharCode(tmp.slice(-1).charCodeAt(0) + 2);
	        #$("#streamurl").text(str);

            video_url = 'https://openload.co/stream/%s?mime=true' % myvidurl
            common.log_utils.log_notice('A openload resolve parse: %s' % video_url)
            return video_url


        except Exception as e:
            common.log_utils.log_notice('Exception during openload resolve parse: %s' % e)
            print("Error",e)
            raise


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


    def parserOPENLOADIO(self, baseUrl):
        #print("parserOPENLOADIO baseUrl[%r]" % baseUrl)
        common.log_utils.log_notice('openload resolve : %s' % baseUrl)

        HTTP_HEADER = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Referer': baseUrl}  # 'Connection': 'keep-alive'

        data = self.net.http_GET(baseUrl, headers=HTTP_HEADER).content

        # If you want to use the code for openload please at least put the info from were you take it:
        # for example: "Code take from plugin IPTVPlayer: "https://gitlab.com/iptvplayer-for-e2/iptvplayer-for-e2/"
        # It will be very nice if you send also email to me samsamsam@o2.pl and inform were this code will be used

        # get image data
        imageData = re.search('''<img[^>]*?id="linkimg"[^>]*?src="([^"]+?)"''', data, re.IGNORECASE).group(1)
        #common.log_utils.log_notice('openload resolve : 1.1 %s' % imageData)

        imageData = base64.b64decode(imageData.split('base64,')[-1])
        x, y, pixel, meta = PNGReader(bytes=imageData).read()
        #common.log_utils.log_notice('openload resolve : 1.2 %s' % pixel)

        imageData = None
        imageStr = ''
        try:
            for item in pixel:
                for p in item:
                    common.log_utils.log_notice('openload resolve : 1.7 %s' % p)
                    imageStr += chr(p)
        except:
            pass

        # split image data
        imageTabs = []
        i = -1
        for idx in range(len(imageStr)):
            if imageStr[idx] == '\0':
                break
            if 0 == (idx % (12 * 20)):
                imageTabs.append([])
                i += 1
                j = -1
            if 0 == (idx % (20)):
                imageTabs[i].append([])
                j += 1
            imageTabs[i][j].append(imageStr[idx])

        # get signature data
        #sts, data = self.cm.getPage('https://openload.co/assets/js/obfuscator/numbers.js', {'header': HTTP_HEADER})
        data = self.net.http_GET('https://openload.co/assets/js/obfuscator/n.js', headers=HTTP_HEADER).content

        signStr = re.search('''['"]([^"^']+?)['"]''', data, re.IGNORECASE).group(1)

        # split signature data
        signTabs = []
        i = -1
        for idx in range(len(signStr)):
            if signStr[idx] == '\0':
                break
            if 0 == (idx % (11 * 26)):
                signTabs.append([])
                i += 1
                j = -1
            if 0 == (idx % (26)):
                signTabs[i].append([])
                j += 1
            signTabs[i][j].append(signStr[idx])

        # get link data
        linkData = {}
        for i in [2, 3, 5, 7]:
            linkData[i] = []
            tmp = ord('c')
            for j in range(len(signTabs[i])):
                for k in range(len(signTabs[i][j])):
                    if tmp > 122:
                        tmp = ord('b')
                    if signTabs[i][j][k] == chr(int(math.floor(tmp))):
                        if len(linkData[i]) > j:
                            continue
                        tmp += 2.5;
                        if k < len(imageTabs[i][j]):
                            linkData[i].append(imageTabs[i][j][k])
        res = []
        for idx in linkData:
            res.append(''.join(linkData[idx]).replace(',', ''))

        res = res[3] + '~' + res[1] + '~' + res[2] + '~' + res[0]
        videoUrl = 'https://openload.co/stream/{0}?mime=true'.format(res)
        dtext = videoUrl.replace('https', 'http')
        request = urllib2.Request(dtext, None, HTTP_HEADER)
        response = urllib2.urlopen(request)
        url = response.geturl()
        response.close()
        url += '|' + urllib.urlencode({'Referer': url, 'User-Agent': common.IOS_USER_AGENT})
        return url
