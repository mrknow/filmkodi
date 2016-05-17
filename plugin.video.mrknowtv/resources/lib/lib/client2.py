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


import re,sys,urllib2,HTMLParser, urllib, urlparse
#import xbmc
import random, base64
from StringIO import StringIO
import cookielib, gzip, os

from resources.lib.libraries import cloudflare2
from resources.lib.libraries import control
from resources.lib.libraries import cache

class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        control.log('Stopping Redirect')
        return response
    https_response = http_response

def shrink_host(url):
    u = urlparse.urlparse(url)[1].split('.')
    u = u[-2] + '.' + u[-1]
    return u.encode('utf-8')

def fix_bad_cookies(cookies):
    for domain in cookies:
        for path in cookies[domain]:
            for key in cookies[domain][path]:
                cookie = cookies[domain][path][key]
                if cookie.expires > sys.maxint:
                    control.log('Fixing cookie expiration for %s: was: %s now: %s' % (key, cookie.expires, sys.maxint))
                    cookie.expires = sys.maxint
    return cookies

def get_sucuri_cookie(html):
    if 'sucuri_cloudproxy_js' in html:
        match = re.search("S\s*=\s*'([^']+)", html)
        if match:
            s = base64.b64decode(match.group(1))
            s = s.replace(' ', '')
            s = re.sub('String\.fromCharCode\(([^)]+)\)', r'chr(\1)', s)
            s = re.sub('\.slice\((\d+),(\d+)\)', r'[\1:\2]', s)
            s = re.sub('\.charAt\(([^)]+)\)', r'[\1]', s)
            s = re.sub('\.substr\((\d+),(\d+)\)', r'[\1:\1+\2]', s)
            s = re.sub(';location.reload\(\);', '', s)
            s = re.sub(r'\n', '', s)
            s = re.sub(r'document\.cookie', 'cookie', s)
            try:
                cookie = ''
                exec(s)
                match = re.match('([^=]+)=(.*)', cookie)
                if match:
                    return {match.group(1): match.group(2)}
            except Exception as e:
                control.log('Exception during sucuri js: %s' % (e))

    return {}

def http_get(url, cookies=None, data=None, multipart_data=None, headers=None, allow_redirect=True, method=None, require_debrid=False, cache_limit=8):
    #control.log('--=-=-==-=-=-=- CLIENT2 url: %s' % (url))


    html = cached_http_get(url, shrink_host(url), control.DEFAULT_TIMEOUT, cookies=cookies, data=data, multipart_data=multipart_data,
                                 headers=headers, allow_redirect=allow_redirect, method=method, require_debrid=require_debrid,
                                 cache_limit=cache_limit)
    sucuri_cookie = get_sucuri_cookie(html)
    if sucuri_cookie:
        control.log('Setting sucuri cookie: %s' % (sucuri_cookie))
        if cookies is not None:
            cookies = cookies.update(sucuri_cookie)
        else:
            cookies = sucuri_cookie
        html = cached_http_get(url, shrink_host(url), control.DEFAULT_TIMEOUT, cookies=cookies, data=data, multipart_data=multipart_data,
                                     headers=headers, allow_redirect=allow_redirect, method=method, require_debrid=require_debrid,
                                     cache_limit=0)
    return html

def cached_http_get(url, base_url, timeout, cookies=None, data=None, multipart_data=None, headers=None, allow_redirect=True, method=None,
                     require_debrid=False, cache_limit=8):
    #control.log('--=-=-==-=-=-=- CLIENT2 CACHE url: %s base_url:%s' % (url,base_url))
    if cookies is None: cookies = {}
    if timeout == 0: timeout = None
    if headers is None: headers = {}
    if url.startswith('//'): url = 'http:' + url
    referer = headers['Referer'] if 'Referer' in headers else url
    #control.log('Getting Url: %s cookie=|%s| data=|%s| extra headers=|%s|' % (url, cookies, data, headers))
    if data is not None:
        if isinstance(data, basestring):
            data = data
        else:
            data = urllib.urlencode(data, True)

    if multipart_data is not None:
        headers['Content-Type'] = 'multipart/form-data; boundary=X-X-X'
        data = multipart_data

    #_created, _res_header, html = cache.get_cached_url(url, data, cache_limit)
    #if html:
    #    control.log('Returning cached result for: %s' % (url))
    #    return html

    try:
        cj = _set_cookies(url, cookies)
        request = urllib2.Request(url, data=data)
        request.add_header('User-Agent', control.get_ua())
        request.add_header('Accept', '*/*')
        request.add_unredirected_header('Host', request.get_host())
        request.add_unredirected_header('Referer', referer)
        for key in headers: request.add_header(key, headers[key])
        cj.add_cookie_header(request)
        if not allow_redirect:
            opener = urllib2.build_opener(NoRedirection)
            urllib2.install_opener(opener)
        else:
            opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
            urllib2.install_opener(opener)
            opener2 = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener2)

        if method is not None: request.get_method = lambda: method.upper()
        response = urllib2.urlopen(request, timeout=timeout)
        cj.extract_cookies(response, request)
        #control.log('Response Cookies: %s - %s' % (url, cookies_as_str(cj)))
        cj._cookies = fix_bad_cookies(cj._cookies)
        cj.save(ignore_discard=True)
        if not allow_redirect and (response.getcode() in [301, 302, 303, 307] or response.info().getheader('Refresh')):
            if response.info().getheader('Refresh') is not None:
                refresh = response.info().getheader('Refresh')
                return refresh.split(';')[-1].split('url=')[-1]
            else:
                return response.info().getheader('Location')

        content_length = response.info().getheader('Content-Length', 0)
        if int(content_length) > control.MAX_RESPONSE:
            control.log('Response exceeded allowed size. %s => %s / %s' % (url, content_length, control.MAX_RESPONSE))

        if method == 'HEAD':
            return ''
        else:
            if response.info().get('Content-Encoding') == 'gzip':
                buf = StringIO(response.read(control.MAX_RESPONSE))
                f = gzip.GzipFile(fileobj=buf)
                html = f.read()
            else:
                html = response.read(control.MAX_RESPONSE)

    except urllib2.HTTPError as e:
        control.log('--=-=-==-=-=-=- CLIENT2 CACHE ERROR-1 e: %s' % (e))

        if e.code == 503 and 'cf-browser-verification' in e.read():
            html = cloudflare2.solve(url, cj, control.get_ua())
            if not html:
                return ''
        else:
            control.log('Error (%s) during scraper http get: %s' % (str(e), url))
            return ''
    except Exception as e:
        control.log('Error (%s) during scraper get: %s' % (str(e), url))
        return ''

    cache.cache_url(url, html, data)

    return html

def _set_cookies(base_url, cookies):
    cookie_file = os.path.join(control.cookieDir, '%s_cookies.lwp' % shrink_host((base_url)))
    #cookie_file = os.path.join('/home/mrknow/.kodi/userdata/addon_data/plugin.video.specto/Cookies', '%s_cookies.lwp' % shrink_host((base_url)))
    #control.log('control.cookieDir: %s' % (control.cookieDir))

    cj = cookielib.LWPCookieJar(cookie_file)
    try: cj.load(ignore_discard=True)
    except: pass
    #control.log('Before Cookies: %s - %s' % (base_url, cookies_as_str(cj)))
    domain = urlparse.urlsplit(base_url).hostname
    for key in cookies:
        c = cookielib.Cookie(0, key, str(cookies[key]), port=None, port_specified=False, domain=domain, domain_specified=True,
                             domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=False, comment=None,
                             comment_url=None, rest={})
        cj.set_cookie(c)
    cj.save(ignore_discard=True)
    #log_utils.log('After Cookies: %s - %s' % (self, scraper_utils.cookies_as_str(cj)), log_utils.LOGDEBUG)
    return cj

def cookies_as_str(cj):
    s = ''
    c = cj._cookies
    for domain in c:
        s += '{%s: ' % (domain)
        for path in c[domain]:
            s += '{%s: ' % (path)
            for cookie in c[domain][path]:
                s += '{%s=%s}' % (cookie, c[domain][path][cookie].value)
            s += '}'
        s += '} '
    return s

def replaceHTMLCodes(txt):
    txt = re.sub("(&#[0-9]+)([^;^0-9]+)", "\\1;\\2", txt)
    txt = HTMLParser.HTMLParser().unescape(txt)
    txt = txt.replace("&quot;", "\"")
    txt = txt.replace("&amp;", "&")
    return txt


