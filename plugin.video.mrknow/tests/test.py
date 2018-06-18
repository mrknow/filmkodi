#o=107984:d6409c8683f029ee9a82629175a972b5
#o=107991:58c49f51a3049f43be326cf7b8107415

import random, string, sys





sys.path.append('/home/mrknow/Dokumenty/praca/kodi/filmkodi/plugin.video.mrknow/mylib/')
sys.path.append('/home/mrknow/Dokumenty/praca/kodi/filmkodi/script.mrknow.urlresolver/lib')


#print ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(25))


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
web_url = 'https://openload.co/embed/rZ04_L_uRuU'
#pattern = '(?://|\.)(openload\.(?:io|co))/(?:embed|f)/([0-9a-zA-Z-_]+)'
#import re

#r = re.search(pattern, web_url, re.I)
#print r.group(0)

import resolveurl as urlresolver

hmf = urlresolver.HostedMediaFile(url=web_url, include_disabled=True, include_universal=False)
print "HMF",hmf
if hmf.valid_url() == True:
    url = hmf.resolve()
    print("RESOLVED",url)
exit()
#import  mrknow_pCommon
#mrknow_pCommon.mystat(url='http://aso.pl')

import urllib2, socket

socket.setdefaulttimeout(180)

# read the list of proxy IPs in proxyList
proxyList = ['89.250.207.195:80','172.30.1.1:8080', '172.30.3.3:8080'] # there are two sample proxy ip

def is_bad_proxy(pip):
    try:
        proxy_handler = urllib2.ProxyHandler({'http': pip})
        opener = urllib2.build_opener(proxy_handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib2.install_opener(opener)
        req=urllib2.Request('http://kodi.filmkodi.com')  # change the url address here
        sock=urllib2.urlopen(req, timeout=10)
    except urllib2.HTTPError, e:
        print 'Error code: ', e.code
        return e.code
    except Exception, detail:

        print "ERROR:", detail
        return 1
    return 0

for item in proxyList:
    if is_bad_proxy(item):
        print "Bad Proxy", item
    else:
        print item, "is working"

print "aaa"
