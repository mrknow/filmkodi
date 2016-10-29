# -*- coding: utf-8 -*-
"""
openload.io urlresolver plugin
Copyright (C) 2015 tknorris

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""


import re
import urllib
import urllib2
from urlresolver9 import common
from lib.aa_decoder import AADecoder
from urlresolver9.resolver import ResolverError

net = common.Net()

def baseN(num, b, numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
    return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

def conv(s):
    match = re.search('toString\([^\d]*(\d+)', s)
    add = int(match.group(1)) if match else 0
    
    match = re.search('{function\s+(.*?)\(', s)
    func_name = match.group(1) if match else 'unknown'
    
    common.log_utils.log('|%s| |%s|' % (add, func_name))
    s = s.replace(' ', '')
    match = re.search('}return(.*)', s)
    if match:
        s = match.group(1)
        
    result = ''
    for part in s.split('+'):
        common.log_utils.log(part)
        if part.startswith(func_name):
            match = re.search('\(\s*(\d+)\s*,\s*(\d+)\s*\)', part)
            if match:
                a, b = match.groups()
                a = int(a) + add
                result += baseN(int(b), a)
        elif part[0] == '"' and part[-1] == '"':
            result += part[1:-1]
        else:
            common.log_utils.log('Unrecognized Part: %s' % (part))
    
    common.log_utils.log(result)
    return result

def get_media_url(url):
    try:
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = net.http_GET(url, headers=headers).content.encode('utf-8')
        decodes = [AADecoder(match.group(1)).decode() for match in re.finditer('<script[^>]+>(ﾟωﾟﾉ[^<]+)<', html, re.DOTALL)]
        if not decodes:
            raise ResolverError('No Encoded Section Found. Deleted?')
        
        common.log_utils.log(decodes)
        enc_index = 0
        for text in decodes:
            match = re.search('welikekodi_ya_rly\s*=\s*(.*?)([0-9/\*\-\+ ]+)', text)
            if match:
                enc_index = eval(match.group(2))
                if 'round' in match.group(1):
                    enc_index = int(round(enc_index))
        
        common.log_utils.log('chosen encode: %s' % (decodes[enc_index]))
        match = re.search('window\..+?=(.*?);', decodes[enc_index])
        if not match:
            match = re.search('.*attr\(\"href\",\((.*)', decodes[enc_index])
        
        if match:
            common.log_utils.log('to conv: %s' % (match.group(1)))
            dtext = conv(match.group(1))
            dtext = dtext.replace('https', 'http')
            request = urllib2.Request(dtext, None, headers)
            response = urllib2.urlopen(request)
            url = response.geturl()
            response.close()

        url += '|' + urllib.urlencode({'Referer': url, 'User-Agent': common.IOS_USER_AGENT})
        return url
    
    except Exception as e:
        common.log_utils.log_debug('Exception during openload resolve parse: %s' % e)
        raise

    raise ResolverError('Unable to resolve openload.io link. Filelink not found.')
