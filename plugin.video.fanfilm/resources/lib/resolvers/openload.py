# -*- coding: utf-8 -*-

'''
    Specto Add-on
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


import re,urllib,json,time,urllib2
from resources.lib.libraries import client
from resources.lib.libraries import client2
from resources.lib.libraries import control

FF_USER_AGENT = urllib.quote_plus('Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0')
openloadhdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

def resolve(url):
    #try:
    control.log('[openload] - 1 %s' % url)
    if check(url) == False: return
    control.log('[openload] - 2 %s' % url)
    id = re.compile('//.+?/(?:embed|f)/([0-9a-zA-Z-_]+)').findall(url)[0]
    myurl = 'https://openload.co/embed/%s' % id


    html = client.request(myurl, headers=openloadhdr)

    videourl = decodeOpenLoad(html)
    control.log('[openload] - 2 %s' % videourl)

    return videourl

def check(url):
    try:
        ifstream = re.search('//.+?/(?:embed|f)/([0-9a-zA-Z-_]+)',(url)[0])
        if ifstream: return True
        id = re.compile('//.+?/(?:embed|f)/([0-9a-zA-Z-_]+)').findall(url)[0]
        url = 'https://openload.co/embed/%s/' % id

        result = client2.http_get(url)
        if result == None: return False
        if '>We are sorry!<' in result: return False
        return True
    except:
        return False


def decodeOpenLoad(html):
    # decodeOpenLoad made by mortael, please leave this line for proper credit :)
    aastring = re.compile("<script[^>]+>(ﾟωﾟﾉ[^<]+)<", re.DOTALL | re.IGNORECASE).findall(html)
    hahadec = decodeOpenLoad2(aastring[0])
    haha = re.compile(r"welikekodi_ya_rly = Math.round([^;]+);", re.DOTALL | re.IGNORECASE).findall(hahadec)[0]
    haha = eval("int" + haha)

    videourl1 = decodeOpenLoad2(aastring[haha])

    return videourl1


def decodeOpenLoad2(aastring):
    aastring = aastring.replace("(ﾟДﾟ)[ﾟεﾟ]+(oﾟｰﾟo)+ ((c^_^o)-(c^_^o))+ (-~0)+ (ﾟДﾟ) ['c']+ (-~-~1)+", "")
    aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ) + (ﾟΘﾟ))", "9")
    aastring = aastring.replace("((ﾟｰﾟ) + (ﾟｰﾟ))", "8")
    aastring = aastring.replace("((ﾟｰﾟ) + (o^_^o))", "7")
    aastring = aastring.replace("((o^_^o) +(o^_^o))", "6")
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

    decodestring = re.search(r"\\\+([^(]+)", aastring, re.DOTALL | re.IGNORECASE).group(1)
    decodestring = "\\+" + decodestring
    decodestring = decodestring.replace("+", "")
    decodestring = decodestring.replace(" ", "")

    decodestring = decode(decodestring)
    decodestring = decodestring.replace("\\/", "/")

    if 'toString' in decodestring:
        base = re.compile(r"toString\(a\+(\d+)", re.DOTALL | re.IGNORECASE).findall(decodestring)[0]
        base = int(base)
        match = re.compile(r"(\(\d[^)]+\))", re.DOTALL | re.IGNORECASE).findall(decodestring)
        for repl in match:
            match1 = re.compile(r"(\d+),(\d+)", re.DOTALL | re.IGNORECASE).findall(repl)
            base2 = base + int(match1[0][0])
            repl2 = base10toN(int(match1[0][1]), base2)
            decodestring = decodestring.replace(repl, repl2)
        decodestring = decodestring.replace("+", "")
        decodestring = decodestring.replace("\"", "")
        videourl = re.search(r"(http[^\}]+)", decodestring, re.DOTALL | re.IGNORECASE).group(1)
        videourl = videourl.replace("https", "http")
    else:
        return decodestring

    UA = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0'
    headers = {'User-Agent': UA}

    req = urllib2.Request(videourl, None, headers)
    res = urllib2.urlopen(req)
    videourl = res.geturl()

    return videourl

def decode(encoded):
    for octc in (c for c in re.findall(r'\\(\d{2,3})', encoded)):
        encoded = encoded.replace(r'\%s' % octc, chr(int(octc, 8)))
    return encoded.decode('utf8')


def base10toN(num, n):
    num_rep = {10: 'a',
               11: 'b',
               12: 'c',
               13: 'd',
               14: 'e',
               15: 'f',
               16: 'g',
               17: 'h',
               18: 'i',
               19: 'j',
               20: 'k',
               21: 'l',
               22: 'm',
               23: 'n',
               24: 'o',
               25: 'p',
               26: 'q',
               27: 'r',
               28: 's',
               29: 't',
               30: 'u',
               31: 'v',
               32: 'w',
               33: 'x',
               34: 'y',
               35: 'z'}
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