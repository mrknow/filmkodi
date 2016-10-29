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
import urllib2
from HTMLParser import HTMLParser
from urlresolver9 import common
from urlresolver9.resolver import ResolverError

net = common.Net()

def get_media_url(url):
    try:
        HTTP_HEADER = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Referer': url}  # 'Connection': 'keep-alive'

        html = net.http_GET(url, headers=HTTP_HEADER).content

        hiddenurl = HTMLParser().unescape(re.search('hiddenurl">(.+?)<\/span>', html, re.IGNORECASE).group(1))
    
        s = []
        for i in hiddenurl:
            j = ord(i)
            if (j >= 33 & j <= 126):
                s.append(chr(33 + ((j + 14) % 94)))
            else:
                s.append(chr(j))
        res = ''.join(s)
        videoUrl = 'https://openload.co/stream/{0}?mime=true'.format(res)
        dtext = videoUrl.replace('https', 'http')
        headers = {'User-Agent': HTTP_HEADER['User-Agent']}
        req = urllib2.Request(dtext, None, headers)
        res = urllib2.urlopen(req)
        videourl = res.geturl()
        res.close()
        return videourl
    except Exception as e:
        common.log_utils.log_debug('Exception during openload resolve parse: %s' % e)
        raise

    raise ResolverError('Unable to resolve openload.io link. Filelink not found.')
