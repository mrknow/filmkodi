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


import re,urlparse,json
from resources.lib.libraries import client


def resolve(url):
    try:
        channel = re.compile('[/v/|/view#]([\w]+)').findall(url)[-1]

        url = 'http://veetle.com/index.php/stream/ajaxStreamLocation/%s/android-hls' % channel
        result = client.request(url, mobile=True)
        url = json.loads(result)

        m3u8 = url['payload']

        url = client.request(m3u8).splitlines()
        url = [i for i in url if '.m3u8' in i]
        if len(url) == 0: return m3u8
        url = urlparse.urljoin(m3u8, url[0])

        return url
    except:
        return

