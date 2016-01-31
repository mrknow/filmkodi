# -*- coding: utf-8 -*-

'''
    Genesis Add-on
    Copyright (C) 2015 lambda

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re,urllib,json,time
from resources.lib.libraries import client
from resources.lib.libraries import captcha

#TODO: Dodać bez captcha

def resolve(url):
    try:
        if check(url) == False: return

        id = re.compile('//.+?/(?:embed|f)/([0-9a-zA-Z-_]+)').findall(url)[0]

        myurl = 'https://openload.co/embed/%s' % id

        result = client.request(myurl)
        #print("data", result)
        #print("myurl", myurl)
        def decodeOpenLoad(html):

            aastring = re.search(r"<video(?:.|\s)*?<script\s[^>]*?>((?:.|\s)*?)</script", html, re.DOTALL | re.IGNORECASE).group(1)
            aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ) + (ﾟΘﾟ))", "9")
            aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ))","8")
            aastring = aastring.replace("((ﾟｰﾟ) + (o^_^o))","7")
            aastring = aastring.replace("((o^_^o) +(o^_^o))","6")
            aastring = aastring.replace("((ﾟｰﾟ) + (ﾟΘﾟ))","5")
            aastring = aastring.replace("(ﾟｰﾟ)","4")
            aastring = aastring.replace("((o^_^o) - (ﾟΘﾟ))","2")
            aastring = aastring.replace("(o^_^o)","3")
            aastring = aastring.replace("(ﾟΘﾟ)","1")
            aastring = aastring.replace("(c^_^o)","0")
            aastring = aastring.replace("(ﾟДﾟ)[ﾟεﾟ]","\\")
            aastring = aastring.replace("(3 +3 +0)","6")
            aastring = aastring.replace("(3 - 1 +0)","2")
            aastring = aastring.replace("(1 -0)","1")
            aastring = aastring.replace("(4 -0)","4")

            #printDBG(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n %s <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n" % aastring)

            decodestring = re.search(r"\\\+([^(]+)", aastring, re.DOTALL | re.IGNORECASE).group(1)
            decodestring = "\\+"+ decodestring
            decodestring = decodestring.replace("+","")
            decodestring = decodestring.replace(" ","")

            decodestring = decode(decodestring)
            decodestring = decodestring.replace("\\/","/")
            #print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n %s <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n" % decodestring)
            videourl = re.compile('window.vr ="([^"]+)"').findall(decodestring)
            #print("videp",videourl)
            if len(videourl)>0:
                linkvideo = videourl[0]
            else:
                linkvideo=''
            return linkvideo

        def decode(encoded):
            for octc in (c for c in re.findall(r'\\(\d{2,3})', encoded)):
                encoded = encoded.replace(r'\%s' % octc, chr(int(octc, 8)))
            return encoded.decode('utf8')
        # end https://github.com/whitecream01/WhiteCream-V0.0.1/blob/master/plugin.video.uwc/plugin.video.uwc-1.0.51.zip?raw=true


        videoUrl = decodeOpenLoad(result)
        return videoUrl
    except:
        #print("dupa")
        return



def check(url):
    try:
        id = re.compile('//.+?/(?:embed|f)/([0-9a-zA-Z-_]+)').findall(url)[0]
        url = 'https://openload.co/embed/%s/' % id

        result = client.request(url)
        if result == None: return False
        if '>We are sorry!<' in result: return False
        return True
    except:
        return False


