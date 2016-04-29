
#
#      Copyright (C) 2015 tknorris (Derived from Mikey1234's & Lambda's)
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#
#  This code is a derivative of the YouTube plugin for XBMC and associated works
#  released under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 3

import re,urllib,urlparse,time

from resources.lib.libraries import cache
from resources.lib.libraries import client
from resources.lib.libraries import control



def request(url, post=None, headers=None, mobile=False, safe=False, timeout='30'):
    try:
        control.log('[cloudflare] request %s' % url)
        try: headers.update(headers)
        except: headers = {}

        agent = cache.get(cloudflareAgent, 168)

        if not 'User-Agent' in headers: headers['User-Agent'] = agent

        u = '%s://%s' % (urlparse.urlparse(url).scheme, urlparse.urlparse(url).netloc)

        cookie = cache.get(cloudflareCookie, 168, u, post, headers, mobile, safe, timeout)

        result = client.request(url, cookie=cookie, post=post, headers=headers, mobile=mobile, safe=safe, timeout=timeout, output='response', error=True)

        if result[0] == '503':
            agent = cache.get(cloudflareAgent, 0) ; headers['User-Agent'] = agent

            cookie = cache.get(cloudflareCookie, 0, u, post, headers, mobile, safe, timeout)

            result = client.request(url, cookie=cookie, post=post, headers=headers, mobile=mobile, safe=safe, timeout=timeout)
        else:
            result= result[1]
        #control.log('[cloudflare] result  %s' % result)

        return result
    except:
        return


def source(url, post=None, headers=None, mobile=False, safe=False, timeout='30'):
    return request(url, post, headers, mobile, safe, timeout)


def cloudflareAgent():
    return client.randomagent()


def cloudflareCookie(url, post, headers, mobile, safe, timeout):
    try:
        result = client.request(url, post=post, headers=headers, mobile=mobile, safe=safe, timeout=timeout, error=True)

        jschl = re.compile('name="jschl_vc" value="(.+?)"/>').findall(result)[0]
        init = re.compile('setTimeout\(function\(\){\s*.*?.*:(.*?)};').findall(result)[0]
        builder = re.compile(r"challenge-form\'\);\s*(.*)a.v").findall(result)[0]
        decryptVal = parseJSString(init)
        lines = builder.split(';')

        for line in lines:
            if len(line)>0 and '=' in line:
                sections=line.split('=')
                line_val = parseJSString(sections[1])
                decryptVal = int(eval(str(decryptVal)+sections[0][-1]+str(line_val)))

        answer = decryptVal + len(urlparse.urlparse(url).netloc)

        query = '%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s' % (url, jschl, answer)

        if 'type="hidden" name="pass"' in result:
            passval = re.compile('name="pass" value="(.*?)"').findall(result)[0]
            query = '%s/cdn-cgi/l/chk_jschl?pass=%s&jschl_vc=%s&jschl_answer=%s' % (url, urllib.quote_plus(passval), jschl, answer)
            time.sleep(5)

        cookie = client.request(query, post=post, headers=headers, mobile=mobile, safe=safe, timeout=timeout, output='cookie', error=True)
        return cookie
    except:
        pass


def parseJSString(s):
    try:
        offset=1 if s[0]=='+' else 0
        val = int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:]))
        return val
    except:
        pass
