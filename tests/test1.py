# -*- coding: utf-8 -*-

import sys
import os

sys.path.append('./tests/lib')
sys.path.append('./script.mrknow.urlresolver/lib/')
sys.path.append('./script.mrknow.urlresolver/lib/urlresolver9')


web_url = 'http://embed.nowvideo.sx/embed/?v=27e41183d1328'
web_url = 'http://videomega.tv/iframe.php?width=720&height=400&ref=98vnW2gQtGGtQg2Wnv89'
web_url = 'http://vidto.me/embed-hthii6ksp7uz-730x411.html'
#web_url = 'http://openload.co/embed/XfsaMfvMRNo'
#web_url = 'http://vshare.io/d/ddc910b'
#web_url = 'http://ebd.cda.pl/580x498/663851dc'
#web_url = 'http://gorillavid.in/8b87wig3n30q'
#web_url = 'https://openload.co/embed/rZ04_L_uRuU'
#web_url = 'https://vidlox.tv/embed-j4pzucajvet6.html'
#web_url = 'http://www.flashx.tv/embed-egswcgpenc6x.html'
#web_url = 'http://www.cda.pl/video/1261071a2'
web_url = 'https://openload.co/embed/Kj-sOfuOymw'
#web_url = 'https://thevideo.me/sdr83iga0g41'
#web_url = 'http://openload.co/embed/1GKfsGz1kXo'
#web_url = 'https://anyfiles.pl/The-Magicians-S02E06-PL/Kino-i-TV/video/181739'
#web_url = '//www.rapidvideo.com/embed/3iqLVgbQ'
#web_url = 'https://vidfile.net/v/58p58r7337sr9'
#web_url = 'http://streamango.com/embed/mqrtkmcsdmrssbpb'
web_url = 'http://thevideo.me/3c8n4re9donp'
#web_url = 'http://vidto.me/ea68pxdq14yz.html'
#web_url = 'http://ebd.cda.pl/638x469/12894331c'
#web_url = 'http://ebd.cda.pl/638x469/128965436'
#web_url = 'http://vidto.me/ruf9h72x2604.html'
web_url = 'https://www.trt.pl/film/297j7mtenu/Nice-Guys-Rowni-goscie-The-Nice-Guys-2016-LEKTOR'
web_url = 'http://ebd.cda.pl/638x469/13226752c'
web_url = 'http://ebd.cda.pl/638x469/13226752c'

#pattern = '(?://|\.)(openload\.(?:io|co))/(?:embed|f)/([0-9a-zA-Z-_]+)'
#import re

#r = re.search(pattern, web_url, re.I)
#print r.group(0)

print("PATHS",sys.path)
print("CURENT PATHS",os.getcwd())

try:
    import urlresolver
except:
    import urlresolver9 as urlresolver
hmf = urlresolver.HostedMediaFile(url=web_url, include_disabled=True, include_universal=False)
def test_cda():
    #assert inc(3) == 5
    hmf = urlresolver.HostedMediaFile(url=web_url, include_disabled=True, include_universal=False)
    assert hmf.valid_url() == True

    if hmf.valid_url() == True:
        url = hmf.resolve()
        print url
        print type(url)
        assert isinstance(url, unicode)
        assert url != None
        print("RESOLVED",url)

