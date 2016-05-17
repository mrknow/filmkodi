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


import re,urlparse
from resources.lib.libraries import client
from resources.lib.libraries import unwise


def resolve(url):
    try:
        referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        page = url.replace(referer, '').replace('&referer=', '').replace('referer=', '')

        result = client.request(url, referer=referer)
        result = re.compile("}[(]('.+?' *, *'.+?' *, *'.+?' *, *'.+?')[)]").findall(result)[-1]
        result = unwise.execute(result)

        strm = re.compile("file *: *[\'|\"](.+?)[\'|\"]").findall(result)
        strm = [i for i in strm if i.startswith('rtmp')][0]
        url = '%s pageUrl=%s live=1 timeout=10' % (strm, page)
        return url
    except:
        return

