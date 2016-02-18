
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


import re
import urllib2
import urlparse
import cookielib
import xbmc,os
from control import dataPath

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko'
cj = cookielib.MozillaCookieJar()
cookiefile = os.path.join(dataPath, 'alina.cookie')

class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        print('Stopping Redirect',response)
        return response

    https_response = http_response

def solve_equation(equation):
    try:
        offset = 1 if equation[0] == '+' else 0
        return int(eval(equation.replace('!+[]', '1').replace('!![]', '1').replace('[]', '0').replace('(', 'str(')[offset:]))
    except:
        pass

def solve(url, html, wait=True):
    try: cj.load(cookiefile,ignore_discard=True)
    except: pass
    headers = {'User-Agent': USER_AGENT, 'Referer': url}
    cj.load(ignore_discard=True)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)

    request = urllib2.Request(url)
    for key in headers: request.add_header(key, headers[key])
    try:
        response = urllib2.urlopen(request)
        html = response.read()
    except urllib2.HTTPError as e:
        html = e.read()
    solver_pattern = 'var t,r,a,f,\s*([^=]+)={"([^"]+)":([^}]+)};.+challenge-form\'\);.*?\n.*?;(.*?);a\.value'
    vc_pattern = 'input type="hidden" name="jschl_vc" value="([^"]+)'
    pass_pattern = 'input type="hidden" name="pass" value="([^"]+)'
    init_match = re.search(solver_pattern, html, re.DOTALL)
    vc_match = re.search(vc_pattern, html)
    pass_match = re.search(pass_pattern, html)

    if not init_match or not vc_match or not pass_match:
        print("Couldn't find attribute: init: |%s| vc: |%s| pass: |%s| No cloudflare check?" % (init_match, vc_match, pass_match))
        return False

    init_dict, init_var, init_equation, equations = init_match.groups()
    vc = vc_match.group(1)
    password = pass_match.group(1)

    # print("VC is: %s" % (vc), xbmc.LOGDEBUG)
    varname = (init_dict, init_var)
    result = int(solve_equation(init_equation.rstrip()))
    print('Initial value: |%s| Result: |%s|' % (init_equation, result), )

    for equation in equations.split(';'):
            equation = equation.rstrip()
            if equation[:len('.'.join(varname))] != '.'.join(varname):
                    print('Equation does not start with varname |%s|' % (equation), )
            else:
                    equation = equation[len('.'.join(varname)):]

            expression = equation[2:]
            operator = equation[0]
            if operator not in ['+', '-', '*', '/']:
                print('Unknown operator: |%s|' % (equation))
                continue

            result = int(str(eval(str(result) + operator + str(solve_equation(expression)))))
            print('intermediate: %s = %s' % (equation, result), )

    scheme = urlparse.urlparse(url).scheme
    domain = urlparse.urlparse(url).hostname
    result += len(domain)
    print('Final Result: |%s|' % (result), )

    if wait:
            print('Sleeping for 5 Seconds')
            xbmc.sleep(5000)

    url = '%s://%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s&pass=%s' % (scheme, domain, vc, result, password)
    print('url: %s' % (url), cj)
    request = urllib2.Request(url)
    for key in headers:
        request.add_header(key, headers[key])
        print("---",key, headers[key])

    #try:
    opener = urllib2.build_opener(NoRedirection)
    urllib2.install_opener(opener)
    response = urllib2.urlopen(request)
    while response.getcode() in [301, 302, 303, 307]:
        if cj is not None:
            cj.extract_cookies(response, request)
        request = urllib2.Request(response.info().getheader('location'))
        for key in headers: request.add_header(key, headers[key])
        if cj is not None:
            cj.add_cookie_header(request)

        response = urllib2.urlopen(request)
    final = response.read()
#except urllib2.HTTPError as e:
    #    log_utils.log('CloudFlare Error: %s on url: %s' % (e.code, url), log_utils.LOGWARNING)
    #    return False

    if cj is not None:
        cj.save()
    return final

def resolve(url):
    return solve(url)