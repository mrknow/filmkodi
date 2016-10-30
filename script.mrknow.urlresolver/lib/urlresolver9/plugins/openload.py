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
                'User-Agent': common.IOS_USER_AGENT,
                'Referer': myurl}  # 'Connection': 'keep-alive'
            html = self.net.http_GET(myurl, headers=HTTP_HEADER).content
            mylink = self.get_mylink(html)
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

            common.log_utils.log_notice('A openload mylink: %s' % mylink)
            #print "Mylink", mylink, urllib.quote_plus(mylink)
            videoUrl = 'https://openload.co/stream/{0}?mime=true'.format(mylink)
            common.log_utils.log_notice('A openload resolve parse: %s' % videoUrl)

            dtext = videoUrl.replace('https', 'http')
            headers = {'User-Agent': HTTP_HEADER['User-Agent']}
            req = urllib2.Request(dtext, None, headers)
            res = urllib2.urlopen(req)
            videourl = res.geturl()
            res.close()

            return videourl
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
        y = n[0][1]
        magic = ord(y[-1])
        y = "	".join(y.split(chr(magic - 1)))
        y = chr(magic - 1).join(y.split(y[-1]))
        y = chr(magic).join(y.split("	"))
        enc_data = y
        print enc_data
        enc_data = HTMLParser().unescape(enc_data)
        res = []
        for c in enc_data:
            j = ord(c)
            if j >= 33 and j <= 126:
                j = ((j + 14) % 94)
                j = j + 33
            res += chr(j)
        mylink = ''.join(res)[0:-1] + chr(ord(''.join(res)[-1]) + 3)
        return mylink

