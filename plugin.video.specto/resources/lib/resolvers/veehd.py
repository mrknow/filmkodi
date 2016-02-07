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


import re,urllib,urlparse
from resources.lib.libraries import client


def resolve(url):
    try:
        result = client.request(url, close=False)
        result = result.replace('\n','')

        url = re.compile('function\s*load_download.+?src\s*:\s*"(.+?)"').findall(result)[0]
        url = urlparse.urljoin('http://veehd.com', url)

        result = client.request(url, close=False)

        i = client.parseDOM(result, 'iframe', ret='src')
        if len(i) > 0:
            i = urlparse.urljoin('http://veehd.com', i[0])
            client.request(i, close=False)
            result = client.request(url)

        url = re.compile('href *= *"([^"]+(?:mkv|mp4|avi))"').findall(result)
        url += re.compile('src *= *"([^"]+(?:divx|avi))"').findall(result)
        url += re.compile('"url" *: *"(.+?)"').findall(result)
        url = urllib.unquote(url[0])
        return url
    except:
        return

