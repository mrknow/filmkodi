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


import re,sys,cookielib,urllib,urllib2,urlparse,gzip,StringIO,HTMLParser,time,random,base64

from resources.lib.libraries import cache
from resources.lib.libraries import control
from resources.lib.libraries import workers


def shrink_host(url):
    u = urlparse.urlparse(url)[1].split('.')
    u = u[-2] + '.' + u[-1]
    return u.encode('utf-8')



IE_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko'
FF_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'
OPERA_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36 OPR/34.0.2036.50'
IOS_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
ANDROID_USER_AGENT = 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'
#SMU_USER_AGENT = 'URLResolver for Kodi/%s' % (addon_version)


def request(url, close=True, redirect=True, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, compression=True, output='', timeout='30', XHR=False):
    try:
        #control.log('@@@@@@@@@@@@@@ - URL:%s POST:%s' % (url, post))

        handlers = []

        if not proxy == None:
            handlers += [urllib2.ProxyHandler({'http':'%s' % (proxy)}), urllib2.HTTPHandler]
            opener = urllib2.build_opener(*handlers)
            opener = urllib2.install_opener(opener)


        if output == 'cookie' or output == 'extended' or not close == True:
            cookies = cookielib.LWPCookieJar()
            handlers += [urllib2.HTTPHandler(), urllib2.HTTPSHandler(), urllib2.HTTPCookieProcessor(cookies)]
            opener = urllib2.build_opener(*handlers)
            opener = urllib2.install_opener(opener)

        if (2, 7, 9) <= sys.version_info < (2, 7, 11):
            try:
                import ssl; ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                handlers += [urllib2.HTTPSHandler(context=ssl_context)]
                opener = urllib2.build_opener(*handlers)
                opener = urllib2.install_opener(opener)
            except:
                pass

        if url.startswith('//'): url = 'http:' + url

        try: headers.update(headers)
        except: headers = {}
        if 'User-Agent' in headers:
            pass
        elif not mobile == True:
            #headers['User-Agent'] = agent()
            headers['User-Agent'] = cache.get(randomagent, 1)
        else:
            headers['User-Agent'] = 'Apple-iPhone/701.341'
            headers['User-Agent'] = 'Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
        if 'Referer' in headers:
            pass
        elif referer == None:
            headers['Referer'] = '%s://%s/' % (urlparse.urlparse(url).scheme, urlparse.urlparse(url).netloc)
        else:
            headers['Referer'] = referer
        if not 'Accept-Language' in headers:
            headers['Accept-Language'] = 'en-US'
        if 'X-Requested-With' in headers:
            pass
        elif XHR == True:
            headers['X-Requested-With'] = 'XMLHttpRequest'
        if 'Cookie' in headers:
            pass
        elif not cookie == None:
            headers['Cookie'] = cookie
        if 'Accept-Encoding' in headers:
            pass
        elif compression and limit is None:
            headers['Accept-Encoding'] = 'gzip'


        if redirect == False:

            class NoRedirection(urllib2.HTTPErrorProcessor):
                def http_response(self, request, response): return response

            opener = urllib2.build_opener(NoRedirection)
            opener = urllib2.install_opener(opener)

            try: del headers['Referer']
            except: pass

        if isinstance(post, dict):
            post = urllib.urlencode(post)

        request = urllib2.Request(url, data=post, headers=headers)


        try:
            response = urllib2.urlopen(request, timeout=int(timeout))
        except urllib2.HTTPError as response:

            if response.code == 503:
                cf_result = response.read(5242880)
                try: encoding = response.info().getheader('Content-Encoding')
                except: encoding = None
                if encoding == 'gzip':
                    cf_result = gzip.GzipFile(fileobj=StringIO.StringIO(cf_result)).read()

                if 'cf-browser-verification' in cf_result:

                    netloc = '%s://%s' % (urlparse.urlparse(url).scheme, urlparse.urlparse(url).netloc)

                    ua = headers['User-Agent']

                    cf = cache.get(cfcookie().get, 168, netloc, ua, timeout)

                    headers['Cookie'] = cf

                    request = urllib2.Request(url, data=post, headers=headers)

                    response = urllib2.urlopen(request, timeout=int(timeout))

                elif error == False:
                    return

            elif error == False:
                return


        if output == 'cookie':
            try: result = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
            except: pass
            try: result = cf
            except: pass
            if close == True: response.close()
            return result

        elif output == 'geturl':
            result = response.geturl()
            if close == True: response.close()
            return result

        elif output == 'headers':
            result = response.headers
            if close == True: response.close()
            return result

        elif output == 'chunk':
            try: content = int(response.headers['Content-Length'])
            except: content = (2049 * 1024)
            if content < (2048 * 1024): return
            result = response.read(16 * 1024)
            if close == True: response.close()
            return result


        if limit == '0':
            result = response.read(224 * 1024)
        elif not limit == None:
            result = response.read(int(limit) * 1024)
        else:
            result = response.read(5242880)

        try: encoding = response.info().getheader('Content-Encoding')
        except: encoding = None
        if encoding == 'gzip':
            result = gzip.GzipFile(fileobj=StringIO.StringIO(result)).read()


        if 'sucuri_cloudproxy_js' in result:
            su = sucuri().get(result)

            headers['Cookie'] = su

            request = urllib2.Request(url, data=post, headers=headers)

            response = urllib2.urlopen(request, timeout=int(timeout))

            if limit == '0':
                result = response.read(224 * 1024)
            elif not limit == None:
                result = response.read(int(limit) * 1024)
            else:
                result = response.read(5242880)

            try: encoding = response.info().getheader('Content-Encoding')
            except: encoding = None
            if encoding == 'gzip':
                result = gzip.GzipFile(fileobj=StringIO.StringIO(result)).read()

        if 'Blazingfast.io' in result and 'xhr.open' in result:
            netloc = '%s://%s' % (urlparse.urlparse(url).scheme, urlparse.urlparse(url).netloc)
            ua = headers['User-Agent']
            headers['Cookie'] = cache.get(bfcookie().get, 168, netloc, ua, timeout)

            result = _basic_request(url, headers=headers, timeout=timeout, limit=limit)

        if output == 'extended':
            response_headers = response.headers
            response_code = str(response.code)
            try: cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])
            except: pass
            try: cookie = cf
            except: pass
            if close == True: response.close()
            return (result, response_code, response_headers, headers, cookie)
        else:
            if close == True: response.close()
            return result
    except Exception as e:
        control.log('Client connect url:%s Error %s' % (url,e))
        return


def source(url, close=True, error=False, proxy=None, post=None, headers=None, mobile=False, safe=False, referer=None, cookie=None, output='', timeout='30'):
    return request(url, close, error, proxy, post, headers, mobile, safe, referer, cookie, output, timeout)


def parseDOM(html, name=u"", attrs={}, ret=False):
    # Copyright (C) 2010-2011 Tobias Ussing And Henrik Mosgaard Jensen

    if attrs is None: attrs = {}
    if isinstance(html, str):
        try:
            html = [html.decode("utf-8")]  # Replace with chardet thingy
        except:
            try:
                html = [html.decode("utf-8", "replace")]
            except:
                html = [html]
    elif isinstance(html, unicode):
        html = [html]
    elif not isinstance(html, list):
        return ''

    if not name.strip():
        return ''

    if not isinstance(attrs, dict):
        return ''

    ret_lst = []
    for item in html:
        for match in re.findall('(<[^>]*\n[^>]*>)', item):
            item = item.replace(match, match.replace('\n', ' ').replace('\r', ' '))

        if not attrs:
            pattern = '(<%s(?: [^>]*>|/?>))' % (name)
            this_list = re.findall(pattern, item, re.M | re.S | re.I)
        else:
            last_list = None
            for key in attrs:
                pattern = '''(<%s [^>]*%s=['"]%s['"][^>]*>)''' % (name, key, attrs[key])
                this_list = re.findall(pattern, item, re.M | re. S | re.I)
                if not this_list and ' ' not in attrs[key]:
                    pattern = '''(<%s [^>]*%s=%s[^>]*>)''' % (name, key, attrs[key])
                    this_list = re.findall(pattern, item, re.M | re. S | re.I)

                if last_list is None:
                    last_list = this_list
                else:
                    last_list = [item for item in this_list if item in last_list]
            this_list = last_list

        lst = this_list

        if isinstance(ret, str):
            lst2 = []

            for match in lst:
                pattern = '''<%s[^>]* %s\s*=\s*(?:(['"])(.*?)\\1|([^'"].*?)(?:>|\s))''' % (name, ret)
                results = re.findall(pattern, match, re.I | re.M | re.S)
                lst2 += [result[1] if result[1] else result[2] for result in results]

            lst = lst2
        else:
            lst2 = []
            for match in lst:
                end_str = "</%s" % (name)
                start_str = '<%s' % (name)

                start = item.find(match)
                end = item.find(end_str, start)
                pos = item.find(start_str, start + 1)

                while pos < end and pos != -1:  # Ignore too early </endstr> return
                    tend = item.find(end_str, end + len(end_str))
                    if tend != -1:
                        end = tend
                    pos = item.find(start_str, pos + 1)

                if start == -1 and end == -1:
                    result = ''
                elif start > -1 and end > -1:
                    result = item[start + len(match):end]
                elif end > -1:
                    result = item[:end]
                elif start > -1:
                    result = item[start + len(match):]
                else:
                    result = ''

                if ret:
                    endstr = item[end:item.find(">", item.find(end_str)) + 1]
                    result = match + result + endstr

                result = result.strip()

                item = item[item.find(result, item.find(match)):]
                lst2.append(result)
            lst = lst2
        ret_lst += lst

    return ret_lst


def replaceHTMLCodes(txt):
    txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
    txt = HTMLParser.HTMLParser().unescape(txt)
    txt = txt.replace("&quot;", "\"")
    txt = txt.replace("&amp;", "&")
    txt = txt.strip()
    return txt

def cleanHTMLCodes(txt):
    txt = txt.replace("'", "")
    txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
    txt = HTMLParser.HTMLParser().unescape(txt)
    txt = txt.replace("&quot;", "\"")
    txt = txt.replace("&amp;", "&")

    return txt

def agent():
    return cache.get(randomagent, 24)

def randomagent():
    BR_VERS = [
        ['%s.0' % i for i in xrange(18, 50)],
        ['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101', '38.0.2125.104', '38.0.2125.111', '39.0.2171.71', '39.0.2171.95', '39.0.2171.99',
         '40.0.2214.93', '40.0.2214.111',
         '40.0.2214.115', '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81', '43.0.2357.124', '44.0.2403.155', '44.0.2403.157', '45.0.2454.101',
         '45.0.2454.85', '46.0.2490.71',
         '46.0.2490.80', '46.0.2490.86', '47.0.2526.73', '47.0.2526.80', '48.0.2564.116', '49.0.2623.112', '50.0.2661.86', '51.0.2704.103', '52.0.2743.116',
         '53.0.2785.143', '54.0.2840.71'],
        ['11.0'],
        ['8.0', '9.0', '10.0', '10.6']]
    WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1', 'Windows NT 5.0']
    FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
    RAND_UAS = ['Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
                'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
                'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko',
                'Mozilla/5.0 (compatible; MSIE {br_ver}; {win_ver}{feature}; Trident/6.0)']
    index = random.randrange(len(RAND_UAS))
    return RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[index]))

def googletag(url):
    quality = re.compile('itag=(\d*)').findall(url)
    quality += re.compile('=m(\d*)$').findall(url)
    try: quality = quality[0]
    except: return []
    #control.log('<><><><><><><><><><><><> %s <><><><><><><><><>' % quality)
    if quality in ['37', '137', '299', '96', '248', '303', '46']:
        return [{'quality': u'1080p', 'url': url}]
    elif quality in ['22', '84', '136', '298', '120', '95', '247', '302', '45', '102']:
        return [{'quality': u'HD', 'url': url}]
    elif quality in ['35', '44', '135', '244', '94', '59']:
        return [{'quality': u'SD', 'url': url}]
    elif quality in ['18', '34', '43', '82', '100', '101', '134', '243', '93']:
        return [{'quality': u'SD', 'url': url}]
    elif quality in ['5', '6', '36', '83', '133', '242', '92', '132']:
        return [{'quality': u'SD', 'url': url}]
    else:
        return [{'quality': u'HD', 'url': url}]

def file_quality_openload(url):
    try:
        if '1080' in url:
            return {'quality': '1080p'}
        elif '720' in url:
            return {'quality': 'HD'}
        else:
            return {'quality': 'SD'}
    except:
        return {'quality': 'SD', 'url': url}

class cfcookie:
    def __init__(self):
        self.cookie = None


    def get(self, netloc, ua, timeout):
        threads = []

        for i in range(0, 15): threads.append(workers.Thread(self.get_cookie, netloc, ua, timeout))
        [i.start() for i in threads]

        for i in range(0, 30):
            if not self.cookie == None: return self.cookie
            time.sleep(1)


    def get_cookie(self, netloc, ua, timeout):
        try:
            headers = {'User-Agent': ua}

            request = urllib2.Request(netloc, headers=headers)

            try:
                response = urllib2.urlopen(request, timeout=int(timeout))
            except urllib2.HTTPError as response:
                result = response.read(5242880)
                try: encoding = response.info().getheader('Content-Encoding')
                except: encoding = None
                if encoding == 'gzip':
                    result = gzip.GzipFile(fileobj=StringIO.StringIO(result)).read()

            jschl = re.findall('name="jschl_vc" value="(.+?)"/>', result)[0]

            init = re.findall('setTimeout\(function\(\){\s*.*?.*:(.*?)};', result)[-1]

            builder = re.findall(r"challenge-form\'\);\s*(.*)a.v", result)[0]

            decryptVal = self.parseJSString(init)

            lines = builder.split(';')

            for line in lines:

                if len(line) > 0 and '=' in line:

                    sections=line.split('=')
                    line_val = self.parseJSString(sections[1])
                    decryptVal = int(eval(str(decryptVal)+sections[0][-1]+str(line_val)))

            answer = decryptVal + len(urlparse.urlparse(netloc).netloc)

            query = '%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s' % (netloc, jschl, answer)

            if 'type="hidden" name="pass"' in result:
                passval = re.findall('name="pass" value="(.*?)"', result)[0]
                query = '%s/cdn-cgi/l/chk_jschl?pass=%s&jschl_vc=%s&jschl_answer=%s' % (netloc, urllib.quote_plus(passval), jschl, answer)
                time.sleep(6)

            cookies = cookielib.LWPCookieJar()
            handlers = [urllib2.HTTPHandler(), urllib2.HTTPSHandler(), urllib2.HTTPCookieProcessor(cookies)]
            opener = urllib2.build_opener(*handlers)
            opener = urllib2.install_opener(opener)

            try:
                request = urllib2.Request(query, headers=headers)
                response = urllib2.urlopen(request, timeout=int(timeout))
            except:
                pass

            cookie = '; '.join(['%s=%s' % (i.name, i.value) for i in cookies])

            if 'cf_clearance' in cookie: self.cookie = cookie
        except:
            pass


    def parseJSString(self, s):
        try:
            offset=1 if s[0]=='+' else 0
            val = int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:]))
            return val
        except:
            pass


class bfcookie:

    def __init__(self):
        self.COOKIE_NAME = 'BLAZINGFAST-WEB-PROTECT'

    def get(self, netloc, ua, timeout):
        try:
            headers = {'User-Agent': ua, 'Referer': netloc}
            result = _basic_request(netloc, headers=headers, timeout=timeout)

            match = re.findall('xhr\.open\("GET","([^,]+),', result)
            if not match:
                return False

            url_Parts = match[0].split('"')
            url_Parts[1] = '1680'
            url = urlparse.urljoin(netloc, ''.join(url_Parts))

            match = re.findall('rid=([0-9a-zA-Z]+)', url_Parts[0])
            if not match:
                return False

            headers['Cookie'] = 'rcksid=%s' % match[0]
            result = _basic_request(url, headers=headers, timeout=timeout)
            return self.getCookieString(result, headers['Cookie'])
        except:
            return

    # not very robust but lazieness...
    def getCookieString(self, content, rcksid):
        vars = re.findall('toNumbers\("([^"]+)"', content)
        value = self._decrypt(vars[2], vars[0], vars[1])
        cookie = "%s=%s;%s" % (self.COOKIE_NAME, value, rcksid)
        return cookie

    def _decrypt(self, msg, key, iv):
        from binascii import unhexlify, hexlify
        import pyaes
        msg = unhexlify(msg)
        key = unhexlify(key)
        iv = unhexlify(iv)
        if len(iv) != 16: return False
        decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, iv))
        plain_text = decrypter.feed(msg)
        plain_text += decrypter.feed()
        f = hexlify(plain_text)
        return f


class sucuri:
    def __init__(self):
        self.cookie = None


    def get(self, result):
        try:
            s = re.compile("S\s*=\s*'([^']+)").findall(result)[0]
            s = base64.b64decode(s)
            s = s.replace(' ', '')
            s = re.sub('String\.fromCharCode\(([^)]+)\)', r'chr(\1)', s)
            s = re.sub('\.slice\((\d+),(\d+)\)', r'[\1:\2]', s)
            s = re.sub('\.charAt\(([^)]+)\)', r'[\1]', s)
            s = re.sub('\.substr\((\d+),(\d+)\)', r'[\1:\1+\2]', s)
            s = re.sub(';location.reload\(\);', '', s)
            s = re.sub(r'\n', '', s)
            s = re.sub(r'document\.cookie', 'cookie', s)

            cookie = '' ; exec(s)
            self.cookie = re.compile('([^=]+)=(.*)').findall(cookie)[0]
            self.cookie = '%s=%s' % (self.cookie[0], self.cookie[1])

            return self.cookie
        except:
            pass

def parseJSString(s):
    try:
        offset=1 if s[0]=='+' else 0
        val = int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:]))
        return val
    except:
        pass

def googlepass(url):
    try:
        try:
            headers = dict(urlparse.parse_qsl(url.rsplit('|', 1)[1]))
        except:
            headers = None
        url = url.split('|')[0].replace('\\', '')
        url = request(url, headers=headers, output='geturl')
        if 'requiressl=yes' in url:
            url = url.replace('http://', 'https://')
        else:
            url = url.replace('https://', 'http://')
        if headers: url += '|%s' % urllib.urlencode(headers)
        return url
    except:
        return