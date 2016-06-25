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
from urlresolver import common
from lib.aa_decoder import AADecoder
from urlresolver.resolver import ResolverError

net = common.Net()

def get_media_url(url):
    def baseN(num, b, numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
        return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

    def conv(s, addfactor=None):
        if 'function()' in s:
            addfactor = s.split('b.toString(')[1].split(')')[0]
            fname = re.findall('function\(\)\{function (.*?)\(', s)[0]
            s = s.replace(fname, 'myfunc')
            s = ''.join(s.split('}')[1:])
        if '+' not in s:
            if '.0.toString' in s:
                ival, b = s.split('.0.toString(')
                b = b.replace(')', '')
                return baseN(int(ival), int(eval(b)))
            elif 'myfunc' in s:
                b, ival = s.split('myfunc(')[1].split(',')
                ival = ival.replace(')', '').replace('(', '').replace(';', '')
                b = b.replace(')', '').replace('(', '').replace(';', '')
                b = eval(addfactor.replace('a', b))
                return baseN(int(ival), int(b))
            else:
                return eval(s)
        r = ''
        for ss in s.split('+'):
            r += conv(ss, addfactor)
        return r

    try:
        web_url = url
        headers = {'User-Agent': common.FF_USER_AGENT}
        html = net.http_GET(web_url, headers=headers).content.encode('utf-8')
        aaencoded = re.findall('<script type="text/javascript">(ﾟωﾟ.*?)</script>', html, re.DOTALL)
        if aaencoded:
            enc_index = re.search('welikekodi_ya_rly\s*=\s*([0-9/\*\-\+ ]+);', html)  # only digits, math ops, whitespace. [^;] too loose for eval
            if enc_index:
                enc_index = eval(enc_index.group(1))
                dtext = AADecoder(aaencoded[enc_index]).decode()
                dtext1 = re.findall('window\..+?=(.*?);', dtext)
                if len(dtext1) == 0:
                    dtext1 = re.findall('.*attr\(\"href\",\((.*)', dtext)
                dtext = conv(dtext1[0])
                return dtext.replace("https", "http") + '|User-Agent=%s' % common.FF_USER_AGENT

    except Exception as e:
        common.log_utils.log_debug('Exception during openload resolve parse: %s' % e)
        raise

    raise ResolverError('Unable to resolve openload.io link. Filelink not found.')
