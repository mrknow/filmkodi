# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Lib AADecode JS and scraper of the possible cases in the returns decoded.
# File: /lib/aadecode.py
# Use:
#     from aadecode import decode as aadecode
#     text_decode = aadecode(text_encode)
# @robalo & @Cmos
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# ------------------------------------------------------------

import urllib, urllib2
url = 'http://paste.filmkodi.com/api/create'
#data = urllib.urlencode({'name' : 'joe', 'age'  : '10'})

text = """
 Date: Sun, 20 Nov 2016 20:25:52 GMT
                                            Content-Type: text/html; charset=UTF-8
                                            Transfer-Encoding: chunked
                                            Connection: close
                                            Cache-Control: no-cache
                                            Location: http://yoy.tv
                                            Set-Cookie: laravel_session=eyJpdiI6IkMwTER0K2dJOHQzZmFDRThkNEYzSFE9PSIsInZhbHVlIjoidkxPTUtzcjJUcE80ajdrQXpNRDZLTEZJdkhTOFwvaDhnWXdoYXBrejk4VzFCbkh4WldZbUpTYk1YWHVHXC9lV3dLZXE2akFXa1hNdXAzZHFWTjZNSlU2QT09IiwibWFjIjoiYWNmMGI3ODE0YjAwMTMwMTdhY2YzZDQxZGRmYjMwNTllZWI4N2YzYzMxYzg5YTk2MDc1OGIwZjUzZGVhOWY0NiJ9; expires=Sun, 20-Nov-2016 22:25:52 GMT; Max-Age=7200; path=/; httponly
                                            Set-Cookie: 798562bab0fea9b32db285c5f0a261658a19e3c6=eyJpdiI6InJQUmxnRTlzUTZ1REdlWkY2NnR5Ync9PSIsInZhbHVlIjoiWHk1VVVoQzBheXdHVDIxRzNuMDRTdz09IiwibWFjIjoiYzA1ZDUwNjRmM2VkZTliNWVhMmVmNjE0MTAzYzEwOGExOGQwMDViNjFmZTZhZmQyY2VjN2E4YzFiYzA1MjcwMCJ9; expires=Tue, 22-Nov-2011 20:25:51 GMT; Max-Age=-157680001; path=/; httponly
                                            Set-Cookie: remember_82e5d2c56bdd0811318f0cf078b78bfc=eyJpdiI6IlRtQlVFdzNJME4rMldiR3pSSEwzNFE9PSIsInZhbHVlIjoiTWMwZVNETTBPNktxaVltWXJaOHZzWnBTN3dkR2tRZGJXREs4RzJnTWlMZ1p1dUVkZEk2ZjBsbGRic0pcL3EzWkZ6SnhIbnlCdjc3QlJwM0pHbkl6eXhcL2twQ01xRG9cLzRtSEdHY2JIZ2M5TVE9IiwibWFjIjoiOWM5NjVhOTA0MTBjYTk5MmM2Y2ZiZTk1NzM1YTNkNTM5NmM3NzQ3Yjg3NTUxZWM3OTM5ODdhNjUyNjk0YmUzYyJ9; expires=Fri, 19-Nov-2021 20:25:51 GMT; Max-Age=157679999; path=/; httponly
                                            Set-Cookie: 7e7470da57460acde684dc5ef8c1616eac54cd72=eyJpdiI6Ild5UDFjQ2s5aFNyd2hYZDVJMGdld0E9PSIsInZhbHVlIjoiaWV5T3JKcnA1bnVVVmZxZlczQXY0TXdmaHpEWEl5TGplclFrWDZqQ3k3eEt3UjhpaVlTSHNCdW53VFdVVkx2c0V3S1BZUVwvcDY1M0U5dVVqQ2oxbVwvSlppeDNkejFtNE5hc0V4TEloZ1RWZWhLMmxJYVhOWUEra044YjQwWE9iZDZYXC9ITHZVYUZOVnU4VjRvUlZcLzByNTl0VExOdjhQa2VQOU1CMit3MjFoTDhsNGw5dUIxUkl2U3p3QTJ0bkpEWlkzbUkrZW04akFPaDh6Vnc5a01hZ2tKbjNsMmJXWGtGaU9vNkNxQUtDVHAyQzQ3cUVHRFwvU1lGNzVWeldzZlJFSFIxMXRtSFFicHBLaDB1eU9yeW1ZcjU3YTdrdTBzSk4wZVwva0hkczl5NGZcL1JlWVhEajNSaGVRWlUrTGZBRmhlajdTT0lxYlBXUGxXQmxzRmF0N0xWWlBTZWt6QmhUODk1Rm8zNGRJdVA0bVNWWVYyamt2Ym93KzgydU9NbUZxbXVPXC9jUlhEXC9wd00yWUdWYzI4N0piaVl0bGJsVEFFbFRuSFBsU09LZit5ZnJCWkpNSHR6WlIreHZBQTF5dEhEViIsIm1hYyI6IjBlNDE4YzVjMDRhYmUwMGNmMjQ2ZWY1NTNmNDFjOTI4OGYzYmE0NjIwOTI4YTdkMTY2ZDJiMDJmNzVkZGNjODAifQ%3D%3D; expires=Sun, 20-Nov-2016 22:25:52 GMT; Max-Age=7200; path=/; httponly
                                            Server: cloudflare-nginx
                                            CF-RAY: 304ea230049a4082-HAM


"""

import re
alina = re.findall('Set-Cookie: (.*?);',text)
print alina

print ";".join(alina)

exit()

data = {}
data['title'] = '%s-%s' % ('alina', 'mailna')
data['title'] = data['title'].replace('plugin.video.', '')[0:29]
data['text'] = text
data['lang'] = 'text'
data = urllib.urlencode(data)

req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
print response.read()
exit()

import re

alina = """
                                            #X-IPLA-LIVE-START: 20161029T140006Z
                                            #X-IPLA-LIVE-LAST: 20161029T160502Z
                                            #X-IPLA-SEEKABLE-TO: 20161029T160319Z
                                            #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1928000
                                            /6B44C047/11633/0/hls720/hd/list.m3u8
                                            #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=64000
                                            /6B44C047/11633/0/hls720/mob4ios/list.m3u8
"""
link = re.findall("#EXT-X-STREAM-INF:.*,BANDWIDTH=\d+\s+[^/](.*?m3u8)", alina, re.MULTILINE)
print link
el = [x for x in link if "mob" in x ][0]
print el
exit()


def decode(text):
    text = re.sub(r"\s+|/\*.*?\*/", "", text)
    data = text.split("+(ﾟДﾟ)[ﾟoﾟ]")[1]
    chars = data.split("+(ﾟДﾟ)[ﾟεﾟ]+")[1:]

    txt = ""
    for char in chars:
        char = char \
            .replace("(oﾟｰﾟo)","u") \
            .replace("c", "0") \
            .replace("(ﾟДﾟ)['0']", "c") \
            .replace("ﾟΘﾟ", "1") \
            .replace("!+[]", "1") \
            .replace("-~", "1+") \
            .replace("o", "3") \
            .replace("_", "3") \
            .replace("ﾟｰﾟ", "4") \
            .replace("(+", "(")
        char = re.sub(r'\((\d)\)', r'\1', char)

        c = ""; subchar = ""
        for v in char:
            c+= v
            try: x = c; subchar+= str(eval(x)); c = ""
            except: pass
        if subchar != '': txt+= subchar + "|"
    txt = txt[:-1].replace('+','')

    txt_result = "".join([ chr(int(n, 8)) for n in txt.split('|') ])

    return toStringCases(txt_result)

def toStringCases(txt_result):
    sum_base = ""
    m3 = False
    if ".toString(" in txt_result:
        if "+(" in  txt_result:
            m3 = True
            sum_base = "+"+find_single_match(txt_result,".toString...(\d+).")
            txt_pre_temp = find_multiple_matches(txt_result,"..(\d),(\d+).")
            txt_temp = [ (n, b) for b ,n in txt_pre_temp ]
        else:
            txt_temp = find_multiple_matches(txt_result, '(\d+)\.0.\w+.([^\)]+).')
        for numero, base in txt_temp:
            code = toString( int(numero), eval(base+sum_base) )
            if m3:
                txt_result = re.sub( r'"|\+', '', txt_result.replace("("+base+","+numero+")", code) )
            else:
                txt_result = re.sub( r"'|\+", '', txt_result.replace(numero+".0.toString("+base+")", code) )
    return txt_result

def toString(number,base):
    string = "0123456789abcdefghijklmnopqrstuvwxyz"
    if number < base:
        return string[number]
    else:
        return toString(number//base,base) + string[number%base]


alina = """
     .jwplayer .jwcontrolbar {
                                                        display: inline-block !important;
                                                        opacity: 1 !important;
                                                    }
                                                </style>
                                                <script type='text/javascript' src='http://dotstream.tv/jquery-1.10.2.min.js'></script>
                                                <script language='javascript'>
                                                    var a = 2573;
                                                    var b = 18260;
                                                    var c = 0;
                                                    var d = 16683;
                                                    var f = 83;
                                                    var v_part = '/live/tv822?keys=oJtXuK0olX_IMyJdG9RSug&keyt=1476415206';
                                                    var ad_data;
                                                    var fup='';
                                                    var ad_index=1;
                                                    var ad_timer=0;
                                                    var ad_delay=25;
                                                    var ad_delay_timer;
                                                    var ad_pre_delay=0;
                                                    var ad_index=0;
                                                    var ad_repeat=-1;
                                                    var adup_index;
                                                    var my_status = 'init';
                                                    var adblock_time=0;
                                                    var popstatus;
                                                    var index_sum = 1;
                                                    function popupwindow () {
                                                        open("http://dotstream.tv/adl.php?id=" + adup_index + "&type=adup","new_window","toolbar=0,location=0,status=0,menubar=0,scrollbars=0,resizable=0, width=1024,height=768,top=0,left=0");
                                                        popstatus = 0;
                                                        newWin.focus();
                                                    }
                                                    $.ajaxSetup ({
                                                        cache: false
                                                    });
                                                    $(document).ready(function(){
                                                        $.ajax({
                                                            dataType: 'json',
                                                            url: 'adinit.php',
                                                            success: function(jsondata){
                                                                ad_data=jsondata;
                                                            }
                                                        });

"""

print re.compile('.*var a =\s*([^;]+).*var b =\s*([^;]+).*var c =\s*([^;]+).*var d =\s*([^;]+).*var f =\s*([^;]+).*var v_part =\s*\'([^\']+).*', re.DOTALL).findall(alina)
