
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
#import log_utils
import xbmc

USER_AGENT='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'

LOGDEBUG = xbmc.LOGDEBUG
LOGERROR = xbmc.LOGERROR
LOGFATAL = xbmc.LOGFATAL
LOGINFO = xbmc.LOGINFO
LOGNONE = xbmc.LOGNONE
LOGNOTICE = xbmc.LOGNOTICE
LOGSEVERE = xbmc.LOGSEVERE
LOGWARNING = xbmc.LOGWARNING

def log(msg, level=xbmc.LOGNOTICE):
    # override message level to force logging when addon logging turned on
    if addon.getSetting('addon_debug') == 'true' and level == xbmc.LOGDEBUG:
        level = xbmc.LOGNOTICE
    
    try:
        if isinstance(msg, unicode):
            msg = '%s (ENCODED)' % (msg.encode('utf-8'))

        xbmc.log('%s: %s' % (name, msg), level)
    except Exception as e:
        try: xbmc.log('Logging Failure: %s' % (e), level)
        except: pass  # just give up

class NoRedirection(urllib2.HTTPErrorProcessor):
    def http_response(self, request, response):
        log('Stopping Redirect', LOGDEBUG)
        return response

    https_response = http_response

def solve_equation(equation):
    try:
        offset = 1 if equation[0] == '+' else 0
        return int(eval(equation.replace('!+[]', '1').replace('!![]', '1').replace('[]', '0').replace('(', 'str(')[offset:]))
    except:
        pass

def solve(url, cj, user_agent=None, wait=True):
    print("--- --- ",user_agent)
    if user_agent is None: user_agent = USER_AGENT
    headers = {'User-Agent': user_agent, 'Referer': url}
    print("--- --- ")
    if cj is not None:
        try: cj.load(ignore_discard=True)
        except: pass
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
    print("--- --- ")

    request = urllib2.Request(url)
    for key in headers: request.add_header(key, headers[key])
    try:
        response = urllib2.urlopen(request)
        html = response.read()
    except urllib2.HTTPError as e:
        html = e.read()
    print("--- --- ")

    solver_pattern = 'var t,r,a,f,\s*([^=]+)={"([^"]+)":([^}]+)};.+challenge-form\'\);.*?\n.*?;(.*?);a\.value'
    vc_pattern = 'input type="hidden" name="jschl_vc" value="([^"]+)'
    pass_pattern = 'input type="hidden" name="pass" value="([^"]+)'
    init_match = re.search(solver_pattern, html, re.DOTALL)
    vc_match = re.search(vc_pattern, html)
    pass_match = re.search(pass_pattern, html)

    if not init_match or not vc_match or not pass_match:
        log("Couldn't find attribute: init: |%s| vc: |%s| pass: |%s| No cloudflare check?" % (init_match, vc_match, pass_match), LOGWARNING)
        return False

    init_dict, init_var, init_equation, equations = init_match.groups()
    vc = vc_match.group(1)
    password = pass_match.group(1)

    # log("VC is: %s" % (vc), xbmc.LOGDEBUG)
    varname = (init_dict, init_var)
    result = int(solve_equation(init_equation.rstrip()))
    log('Initial value: |%s| Result: |%s|' % (init_equation, result), LOGDEBUG)

    for equation in equations.split(';'):
            equation = equation.rstrip()
            if equation[:len('.'.join(varname))] != '.'.join(varname):
                    log('Equation does not start with varname |%s|' % (equation), LOGDEBUG)
            else:
                    equation = equation[len('.'.join(varname)):]

            expression = equation[2:]
            operator = equation[0]
            if operator not in ['+', '-', '*', '/']:
                log('Unknown operator: |%s|' % (equation), LOGWARNING)
                continue

            result = int(str(eval(str(result) + operator + str(solve_equation(expression)))))
            log('intermediate: %s = %s' % (equation, result), LOGDEBUG)

    scheme = urlparse.urlparse(url).scheme
    domain = urlparse.urlparse(url).hostname
    result += len(domain)
    log('Final Result: |%s|' % (result), LOGDEBUG)

    if wait:
            log('Sleeping for 5 Seconds', LOGDEBUG)
            xbmc.sleep(5000)

    url = '%s://%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s&pass=%s' % (scheme, domain, vc, result, password)
    log('url: %s' % (url), LOGDEBUG)
    request = urllib2.Request(url)
    for key in headers: request.add_header(key, headers[key])
    try:
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
    except urllib2.HTTPError as e:
        log('CloudFlare Error: %s on url: %s' % (e.code, url), LOGWARNING)
        return False

    if cj is not None:
        cj.save()
        
    return final
