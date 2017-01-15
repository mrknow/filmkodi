# -*- coding: utf-8 -*-

###################################################
# LOCAL import
###################################################

###################################################
# FOREIGN import
###################################################
from binascii import hexlify
import re
import time
import string
import codecs
import urllib
###################################################
try:
    from hashlib import md5
    def hex_md5(e):
        return md5(e).hexdigest()
except:
    pass

def printDBG(msg=''):
    print msg

def printExc(msg=''):
    print msg

def int2base(x, base):
    digs = string.digits + string.lowercase
    if x < 0: sign = -1
    elif x==0: return '0'
    else: sign = 1
    x *= sign
    digits = []
    while x:
        digits.append(digs[x % base])
        x /= base
    if sign < 0:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)
    
def JS_toString(x, base):
    return int2base(x, base)

# returns timestamp in milliseconds
def JS_DateValueOf():
    return time.time()*1000
    
def JS_FromCharCode(*args): 
    return ''.join(map(unichr, args))
    
def unicode_escape(s):
    decoder = codecs.getdecoder('unicode_escape')
    return re.sub(r'\\u[0-9a-fA-F]{4,}', lambda m: decoder(m.group(0))[0], s).encode('utf-8')

def drdX_fx(e):
    t = {}
    n = 0
    r = 0
    i = []
    s = ""
    o = JS_FromCharCode
    u = [[65, 91], [97, 123], [48, 58], [43, 44], [47, 48]]
    
    for z in range(len(u)):
        n = u[z][0]
        while n < u[z][1]:
            i.append(o(n))
            n += 1
    n = 0
    while n < 64:
        t[i[n]] = n
        n += 1
        
    n = 0
    while n < len(e):
        a = 0
        f = 0
        l = 0
        c = 0
        h = e[n:n+72]
        while l < len(h):
            f = t[h[l]]
            a = (a << 6) + f
            c += 6
            while c >= 8:
                c -= 8
                s += o((a >> c) % 256)
            l += 1
        
        n += 72
    return s


    
####################################################
# myobfuscate.com 
####################################################
def MYOBFUSCATECOM_OIO(data, _0lllOI="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=", enc=''):
    i = 0;
    while i < len(data):
        h1 = _0lllOI.find(data[i]);
        h2 = _0lllOI.find(data[i+1]);
        h3 = _0lllOI.find(data[i+2]);
        h4 = _0lllOI.find(data[i+3]);
        i += 4;
        bits = h1 << 18 | h2 << 12 | h3 << 6 | h4;
        o1 = bits >> 16 & 0xff;
        o2 = bits >> 8 & 0xff;
        o3 = bits & 0xff;
        if h3 == 64:
            enc += chr(o1);
        else:
            if h4 == 64:
                enc += chr(o1) + chr(o2);
            else:
                enc += chr(o1) + chr(o2) + chr(o3);
    return enc

def MYOBFUSCATECOM_0ll(string, baseRet=''):
    ret = baseRet
    i = len(string) - 1
    while i >= 0:
        ret += string[i]
        i -= 1
    return ret
    
def VIDEOMEGA_decryptPlayerParams(p, a, c, k, e, d):
    def e1(c):
        return JS_toString(c, 36)
        return ret
    def k1(matchobj):
        return d[matchobj.group(0)]
    def e2(t=None):
        return '\\w+'
    e = e1
    if True:
        while c != 0:
            c -= 1
            tmp1 = e(c)
            d[tmp1] = k[c]
            if '' == d[tmp1]: 
                d[tmp1] = e(c)
        c = 1
        k = [k1]
        e = e2
    while c != 0:
        c -= 1
        if k[c]:
            reg = '\\b' + e(c) + '\\b'
            p = re.sub(reg, k[c], p)
    return p
            
def SAWLIVETV_decryptPlayerParams(p, a, c, k, e, d):
    def e1(c):
        if c < a:
            ret = ''
        else:
            ret = e(c / a)
        c = c % a
        if c > 35:
            ret += chr(c+29)
        else:
            ret += JS_toString(c, 36)
        return ret
    def k1(matchobj):
        return d[matchobj.group(0)]
    def e2(t=None):
        return '\\w+'
    e = e1
    if True:
        while c != 0:
            c -= 1
            tmp1 = e(c)
            d[tmp1] = k[c]
            if '' == d[tmp1]: 
                d[tmp1] = e(c)
        c = 1
        k = [k1]
        e = e2
    while c != 0:
        c -= 1
        if k[c]:
            reg = '\\b' + e(c) + '\\b'
            p = re.sub(reg, k[c], p)
    return p

def OPENLOADIO_decryptPlayerParams(p, a, c, k, e, d):
    def e1(c):
        return c
    def e2(t=None):
        return '\\w+'
    def k1(matchobj):
        return d[int(matchobj.group(0))]
    e = e1
    if True:
        while c != 0:
            c -= 1
            d[c] = k[c]
            if c < len(k):
                d[c] = k[c]
            else:
                d[c] = c
        c = 1
        k = [k1]
        e = e2
    while c != 0:
        c -= 1
        if k[c]:
            reg = '\\b' + e(c) + '\\b'
            p = re.sub(reg, k[c], p)
    return p

def TEAMCASTPL_decryptPlayerParams(p, a, c, k, e=None, d=None):
    def e1(c):
        if c < a:
            ret = ''
        else:
            ret = e(c / a)
        c = c % a
        if c > 35:
            ret += chr(c+29)
        else:
            ret += JS_toString(c, 36)
        return ret
    e = e1
    while c != 0:
        c -= 1
        if k[c]:
            reg = '\\b' + e(c) + '\\b'
            p = re.sub(reg, k[c], p)
    return p

###############################################################################
# VIDUP.ME HELPER FUNCTIONS
###############################################################################
# there is problem in exec when this functions are class methods
# sub (even static) or functions
# Code example:
#<div id="player_code" style="height:100% ; width:100%; visibility:none;"><span id='flvplayer'></span>
#<script type='text/javascript' src='http://vidup.me/player/jwplayer.js'></script>
#<script type='text/javascript'>eval(function(p,a,c,k,e,d){while(c--)if(k[c])p=p.replace(new RegExp('\\b'+c.toString(a)+'\\b','g'),k[c]);return p}('1l(\'1k\').1j({\'1i\':\'/7/7.1h\',a:"0://g.f.e.c:1g/d/1f/1e.1d",1c:"0",\'1b\':\'9\',\'1a\':\'19\',\'18\':\'h%\',\'17\':\'h%\',\'16\':\'15\',\'14\':\'13\',\'12\':\'11\',\'10\':\'0://g.f.e.c/i/z/6.y\',\'b\':\'0://5.4/7/b.x\',\'w\':\'v\',\'2.a\':\'0://5.4/u/t.s\',\'2.8\':\'0://5.4/6\',\'2.r\':\'q\',\'2.p\':\'o\',\'2.n\':\'9-m\',\'l\':{\'k-1\':{\'8\':\'0://5.4/6\'},\'j-3\':{}}});',36,58,'http||logo||me|vidup|yx616ubt7l82|player|link|bottom|file|skin|187||116|39|84|100||timeslidertooltipplugin|fbit|plugins|right|position|false|hide|_blank|linktarget|png|logoheader|images|000000|screencolor|zip|jpg|00049|image|always|allowscriptaccess|true|allowfullscreen|7022|duration|height|width|transparent|wmode|controlbar|provider|flv|video|zesaswuvnsv27kymojykzci5bbll4pqkmqipzoez4eakqgfaacm7fbqf|182|swf|flashplayer|setup|flvplayer|jwplayer'.split('|')))
#</script>
#<br></div>
#
#       
def getParamsTouple(code, type=1, r1=False, r2=False ):
    mark1 = "}("
    mark2 = "))"
    if r1:
        idx1 = code.rfind(mark1)
    else:
        idx1 = code.find(mark1)
    if -1 == idx1: return ''
    idx1 += len(mark1)
    if r2:
        idx2 = code.rfind(mark2, idx1)
    else:
        idx2 = code.find(mark2, idx1)
    if -1 == idx2: return ''
    idx2 += type
    return code[idx1:idx2]
 
def unpackJSPlayerParams(code, decryptionFun, type=1, r1=False, r2=False):
    printDBG('unpackJSPlayerParams')
    code = getParamsTouple(code, type, r1, r2)
    return unpackJS(code, decryptionFun)
    
def unpackJS(data, decryptionFun, addCode=''):
    paramsCode = addCode
    paramsCode += 'paramsTouple = (' + data + ')'
    try:
        paramsAlgoObj = compile(paramsCode, '', 'exec')
    except:
        printExc('unpackJS compile algo code EXCEPTION')
        return ''
    vGlobals = {"__builtins__": None, 'string': string, 'decodeURIComponent':urllib.unquote, 'unescape':urllib.unquote}
    vLocals = { 'paramsTouple': None }

    try:
        exec( paramsAlgoObj, vGlobals, vLocals )
    except:
        printExc('unpackJS exec code EXCEPTION')
        return ''
    # decrypt JS Player params
    try:
        return decryptionFun(*vLocals['paramsTouple'])
    except:
        printExc('decryptPlayerParams EXCEPTION')
    return ''
    
def VIDUPME_decryptPlayerParams(p=None, a=None, c=None, k=None, e=None, d=None):
    while c > 0:
        c -= 1
        if k[c]:
            p = re.sub('\\b'+ int2base(c, a) +'\\b', k[c], p)
    return p
    
###############################################################################


###############################################################################
# VIDEOWEED HELPER FUNCTIONS
###############################################################################
def VIDEOWEED_decryptPlayerParams(w, i, s, e):
    lIll = 0
    ll1I = 0
    Il1l = 0
    ll1l = []
    l1lI = []
    while True:
        if lIll < 5: l1lI.append(w[lIll])
        elif lIll < len(w): ll1l.append(w[lIll])
        lIll += 1
        if ll1I < 5: l1lI.append(i[ll1I])
        elif ll1I < len(i): ll1l.append(i[ll1I])
        ll1I += 1
        if Il1l < 5: l1lI.append(s[Il1l])
        elif Il1l < len(s): ll1l.append(s[Il1l])
        Il1l += 1
        if len(w) + len(i) + len(s) + len(e) == len(ll1l) + len(l1lI) + len(e): break

    lI1l = ''.join(ll1l)
    I1lI = ''.join(l1lI)
    ll1I = 0
    l1ll = []

    lIll = 0
    while lIll < len(ll1l):
        ll11 = -1;
        if ord(I1lI[ll1I]) % 2: ll11 = 1
        l1ll.append( JS_FromCharCode( int( lI1l[lIll:lIll+2], 36 ) - ll11 ) )
        ll1I += 1;
        if ll1I >= len(l1lI): ll1I = 0

        lIll += 2
    return ''.join(l1ll)

def VIDEOWEED_unpackJSPlayerParams(code):
    sts, code = CParsingHelper.rgetDataBeetwenMarkers(code, 'eval(function', '</script>')
    if not sts: return ''
    while True:
        mark1 = "}("
        mark2 = "));"
        idx1 = code.rfind(mark1)
        if -1 == idx1: return ''
        idx1 += len(mark1)
        idx2 = code.rfind(mark2, idx1)
        if -1 == idx2: return ''
        #idx2 += 1
        
        paramsCode = 'paramsTouple = (' + code[idx1:idx2] + ')'
        paramsAlgoObj = compile(paramsCode, '', 'exec')
        try:
            paramsAlgoObj = compile(paramsCode, '', 'exec')
        except:
            printDBG('unpackJSPlayerParams compile algo code EXCEPTION')
            return ''
        vGlobals = {"__builtins__": None, 'string': string}
        vLocals = { 'paramsTouple': None }
        try:
            exec( paramsAlgoObj, vGlobals, vLocals )
        except:
            printDBG('unpackJSPlayerParams exec code EXCEPTION')
            return ''
        # decrypt JS Player params
        code = VIDEOWEED_decryptPlayerParams(*vLocals['paramsTouple'])
        try:
            code = VIDEOWEED_decryptPlayerParams(*vLocals['paramsTouple'])
            if -1 == code.find('eval'):
                return code
        except:
            printDBG('decryptPlayerParams EXCEPTION')
            return ''
    return ''
    
    
def pythonUnescape(data):
    sourceCode = "retData = '''%s'''" % data
    try:
        code = compile(sourceCode, '', 'exec')
    except:
        printExc('pythonUnescape compile algo code EXCEPTION')
        return ''
    vGlobals = {"__builtins__": None, 'string': string}
    vLocals = { 'paramsTouple': None }
    try:
        exec( code, vGlobals, vLocals )
    except:
        printExc('pythonUnescape exec code EXCEPTION')
        return ''
    return vLocals['retData']
    
###############################################################################

class captchaParser:
    def __init__(self):
        pass

    def textCaptcha(self, data):
        strTab = []
        valTab = []
        match = re.compile("padding-(.+?):(.+?)px;padding-top:.+?px;'>(.+?)<").findall(data)
        if len(match) > 0:
            for i in range(len(match)):
                value = match[i]
                strTab.append(value[2])
                strTab.append(int(value[1]))
                valTab.append(strTab)
                strTab = []
                if match[i][0] == 'left':
                    valTab.sort(key=lambda x: x[1], reverse=False)
                else:
                    valTab.sort(key=lambda x: x[1], reverse=True)
        return valTab

    def reCaptcha(self, data):
        pass
    
################################################################################

def decorateUrl(url, metaParams={}):
    retUrl = strwithmeta( url )
    retUrl.meta.update(metaParams)
    urlLower = url.lower()
    if 'iptv_proto' not in retUrl.meta:
        if urlLower.startswith('merge://'):
            retUrl.meta['iptv_proto'] = 'merge'
        elif urlLower.split('?')[0].endswith('.m3u8'):
            retUrl.meta['iptv_proto'] = 'm3u8'
        elif urlLower.split('?')[0].endswith('.f4m'):
            retUrl.meta['iptv_proto'] = 'f4m'
        elif urlLower.startswith('rtmp'):
            retUrl.meta['iptv_proto'] = 'rtmp'
        elif urlLower.startswith('https'):
            retUrl.meta['iptv_proto'] = 'https'
        elif urlLower.startswith('http'):
            retUrl.meta['iptv_proto'] = 'http'
        elif urlLower.startswith('file'):
            retUrl.meta['iptv_proto'] = 'file'
        elif urlLower.startswith('rtsp'):
            retUrl.meta['iptv_proto'] = 'rtsp'
        elif urlLower.startswith('mms'):
            retUrl.meta['iptv_proto'] = 'mms'
        elif urlLower.startswith('mmsh'):
            retUrl.meta['iptv_proto'] = 'mmsh'
        elif 'protocol=hls' in url.lower():
            retUrl.meta['iptv_proto'] = 'm3u8'
    return retUrl

def getDirectM3U8Playlist(M3U8Url, checkExt=True, variantCheck=True, cookieParams={}):
    if checkExt and not M3U8Url.split('?')[0].endswith('.m3u8'):
        return []
        
    cm = common()
    meta = strwithmeta(M3U8Url).meta
    params, postData = cm.getParamsFromUrlWithMeta(M3U8Url)
    params.update(cookieParams)
    
    retPlaylists = []
    try:
        finallM3U8Url = meta.get('iptv_m3u8_custom_base_link', '') 
        if '' == finallM3U8Url:
            params['return_data'] = False
            sts, response = cm.getPage(M3U8Url, params, postData)
            finallM3U8Url = response.geturl()
            data = response.read().strip()
            response.close()
        else:
            sts, data = cm.getPage(M3U8Url, params, postData)
            data = data.strip()
            
        m3u8Obj = m3u8.inits(data, finallM3U8Url)
        if m3u8Obj.is_variant:
            for playlist in m3u8Obj.playlists:
                item = {}
                if not variantCheck or playlist.absolute_uri.split('?')[-1].endswith('.m3u8'):
                    meta.update({'iptv_proto':'m3u8', 'iptv_bitrate':playlist.stream_info.bandwidth})
                    item['url'] = strwithmeta(playlist.absolute_uri, meta)
                else:
                    meta.pop('iptv_proto', None)
                    item['url'] = decorateUrl(playlist.absolute_uri, meta)
                
                item['bitrate'] = playlist.stream_info.bandwidth
                if None != playlist.stream_info.resolution:
                    item['with'] = playlist.stream_info.resolution[0]
                    item['heigth'] = playlist.stream_info.resolution[1]
                else:
                    item['with'] = 0
                    item['heigth'] = 0
                item['codec'] = playlist.stream_info.codecs
                item['name']  = "bitrate: %s res: %dx%d kodek: %s" % ( item['bitrate'], \
                                                                        item['with'],    \
                                                                        item['heigth'],  \
                                                                        item['codec'] )
                retPlaylists.append(item)
        else:
            item = {'name':'m3u8', 'url':M3U8Url, 'codec':'unknown', 'with':0, 'heigth':0, 'bitrate':'unknown'}
            retPlaylists.append(item)
    except:
        printExc()
    return retPlaylists
    
def getF4MLinksWithMeta(manifestUrl, checkExt=True):
    if checkExt and not manifestUrl.split('?')[0].endswith('.f4m'):
        return []
        
    cm = common()
    headerParams, postData = cm.getParamsFromUrlWithMeta(manifestUrl)
    
    retPlaylists = []
    sts, data = cm.getPage(manifestUrl, headerParams, postData)
    if sts:
        liveStreamDetected = False
        if 'live' == CParsingHelper.getDataBeetwenMarkers('<streamType>', '</streamType>', False):
            liveStreamDetected = True
        bitrates = re.compile('bitrate="([0-9]+?)"').findall(data)
        for item in bitrates:
            link = strwithmeta(manifestUrl, {'iptv_proto':'f4m', 'iptv_bitrate':item})
            if liveStreamDetected:
                link.meta['iptv_livestream'] = True
            retPlaylists.append({'name':'[f4m/hds] bitrate[%s]' % item, 'url':link})
        
        if 0 == len(retPlaylists):
            link = strwithmeta(manifestUrl, {'iptv_proto':'f4m'})
            if liveStreamDetected:
                link.meta['iptv_livestream'] = True
            retPlaylists.append({'name':'[f4m/hds]', 'url':link})
    return retPlaylists
    
    

def decode(encoded):
    for octc in (c for c in re.findall(r'\\(\d{2,3})', encoded)):
        encoded = encoded.replace(r'\%s' % octc, chr(int(octc, 8)))
    return encoded.decode('utf8')

# function decodeOpenload(html) provide html from embedded openload page, gives back the video url
# if you want to use this, ask me nice :)
exec("import re;import base64");exec((lambda p,y:(lambda o,b,f:re.sub(o,b,f))(r"([0-9a-f]+)",lambda m:p(m,y),base64.b64decode("NDIgNTAoMjMpOgoKCSMgNTAgMzggNDYgMjYsIDJjIDM3IDM5IDNkIDJmIDJlIDI5IDopCgkxNSA9IDQ3LmIoMjUiPDEyKD86LnxcMzIpKj88MTZcMzJbXj5dKj8+KCg/Oi58XDMyKSo/KTwvMTYiLCAyMywgNDcuNTEgfCA0Ny4zMCkuNTIoMSkKCgkxNSA9IDE1LjM2KCIxZCIsIiIpCgkxNSA9IDE1LjM2KCIoNDAgKyA0MCArIDRlKSIsICI5IikKCTE1ID0gMTUuMzYoIig0MCArIDQwKSIsIjgiKQoJMTUgPSAxNS4zNigiKDQwICsgKDFhXjMzXjFhKSkiLCI3IikKCTE1ID0gMTUuMzYoIigoMWFeMzNeMWEpICsoMWFeMzNeMWEpKSIsIjYiKQoJMTUgPSAxNS4zNigiKDQwICsgNGUpIiwiNSIpCgkxNSA9IDE1LjM2KCI0MCIsIjQiKQoJMTUgPSAxNS4zNigiKCgxYV4zM14xYSkgLSA0ZSkiLCIyIikKCTE1ID0gMTUuMzYoIigxYV4zM14xYSkiLCIzIikKCTE1ID0gMTUuMzYoIjRlIiwiMSIpCgkxNSA9IDE1LjM2KCIoKyErW10pIiwiMSIpCgkxNSA9IDE1LjM2KCIoY14zM14xYSkiLCIwIikKCTE1ID0gMTUuMzYoIigwKzApIiwiMCIpCgkxNSA9IDE1LjM2KCIxNCIsIlxcIikgIAoJMTUgPSAxNS4zNigiKDMgKzMgKzApIiwiNiIpCgkxNSA9IDE1LjM2KCIoMyAtIDEgKzApIiwiMiIpCgkxNSA9IDE1LjM2KCIoIStbXSshK1tdKSIsIjIiKQoJMTUgPSAxNS4zNigiKC1+LX4yKSIsIjQiKQoJMTUgPSAxNS4zNigiKC1+LX4xKSIsIjMiKQoJMTUgPSAxNS4zNigiKC1+MCkiLCIxIikKCTE1ID0gMTUuMzYoIigtfjEpIiwiMiIpCgkxNSA9IDE1LjM2KCIoLX4zKSIsIjQiKQoJMTUgPSAxNS4zNigiKDAtMCkiLCIwIikKCQoJMTggPSA0Ny5iKDI1IlxcXCsoW14oXSspIiwgMTUsIDQ3LjUxIHwgNDcuMzApLjUyKDEpCgkxOCA9ICJcXCsiKyAxOAoJMTggPSAxOC4zNigiKyIsIiIpCgkxOCA9IDE4LjM2KCIgIiwiIikKCQoJMTggPSAzMSgxOCkKCTE4ID0gMTguMzYoIlxcLyIsIi8iKQoJCgkzYSAnMTEnIDJhIDE4OgoJCTEwID0gNDcuNDgoMjUiMTFcKGFcKyhcZCspIiwgNDcuNTEgfCA0Ny4zMCkuM2UoMTgpWzBdCgkJMTAgPSAyMigxMCkKCQkyMCA9IDQ3LjQ4KDI1IihcKFxkW14pXStcKSkiLCA0Ny41MSB8IDQ3LjMwKS4zZSgxOCkKCQkyZiAxYyAyYSAyMDoKCQkJZiA9IDQ3LjQ4KDI1IihcZCspLChcZCspIiwgNDcuNTEgfCA0Ny4zMCkuM2UoMWMpCgkJCTFmID0gMTAgKyAyMihmWzBdWzBdKQoJCQkxZSA9IDIxKDIyKGZbMF1bMV0pLDFmKQoJCQkxOCA9IDE4LjM2KDFjLDFlKQoJCTE4ID0gMTguMzYoIisiLCIiKQoJCTE4ID0gMTguMzYoIlwiIiwiIikKCQk0OSA9IDQ3LmIoMjUiKDNiW15cfV0rKSIsIDE4LCA0Ny41MSB8IDQ3LjMwKS41MigxKQoJMjQ6CgkJNDkgPSA0Ny5iKDI1IjQ0XDMyPz1cMzI/XCJ8JyhbXlwiJ10rKSIsIDE4LCA0Ny41MSB8IDQ3LjMwKS41MigxKQoJCgkxOSA9ICIxNy4xMi4iICsgIjRiIiArICI0ZiIgKyAiYyIKCTJkID0gIjE3LjEyLiIgKyAiNGMiICsgIjFhIiArICIyNSIgKyAiNTMiICsgImEiICsgImUiICsgIjRhIgoJCgkzYSAxOSAyYSAzNS4xYignM2MnKToKCQk0ZCA9IDQ5CgkyNDoKCQk0ZCA9ICIzNDovLzQzLjI3LjNmLzMyLzEzLzJiLjQxPzQ1PTEiCgkyOCA0ZA==")))(lambda a,b:b[int("0x"+a.group(1),16)],"0|1|2|3|4|5|6|7|8|9|a|search|c|d|e|match1|base|toString|video|2ds5o61a22srpob|(ﾟДﾟ)[ﾟεﾟ]|aastring|script|plugin|decodestring|check1|o|getAddonInfo|repl|(ﾟДﾟ)[ﾟεﾟ]+(oﾟｰﾟo)+ ((c^_^o)-(c^_^o))+ (-~0)+ (ﾟДﾟ) ['c']+ (-~-~1)+|repl2|base2|match|base10toN|int|html|else|r|mortael|dropbox|return|credit|in|ahahah|please|check2|proper|for|IGNORECASE|decode|s|_|https|addon|replace|leave|made|this|if|http|path|line|findall|com|(ﾟｰﾟ)|mp4|def|www|vr|dl|by|re|compile|videourl|l|u|m|videourl2|(ﾟΘﾟ)|w|decodeOpenLoad|DOTALL|group|t".split("|")))

def base10toN(num,n):
    num_rep={10:'a',
         11:'b',
         12:'c',
         13:'d',
         14:'e',
         15:'f',
         16:'g',
         17:'h',
         18:'i',
         19:'j',
         20:'k',
         21:'l',
         22:'m',
         23:'n',
         24:'o',
         25:'p',
         26:'q',
         27:'r',
         28:'s',
         29:'t',
         30:'u',
         31:'v',
         32:'w',
         33:'x',
         34:'y',
         35:'z'}
    new_num_string=''
    current=num
    while current!=0:
        remainder=current%n
        if 36>remainder>9:
            remainder_string=num_rep[remainder]
        elif remainder>=36:
            remainder_string='('+str(remainder)+')'
        else:
            remainder_string=str(remainder)
        new_num_string=remainder_string+new_num_string
        current=current/n
    return new_num_string