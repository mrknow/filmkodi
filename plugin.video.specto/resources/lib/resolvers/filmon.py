# -*- coding: utf-8 -*-

'''
    Genesis Add-on
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
        if '/vod/' in url:
            url = re.compile('/(\d+)').findall(url)[-1]
            url = 'http://www.filmon.com/vod/info/%s' % url
        elif '/tv/' in url:
            url = url.replace('/tv/', '/channel/')
        elif not '/channel/' in url:
            raise Exception()


        headers = {'X-Requested-With': 'XMLHttpRequest'}

        result = client.request(url, headers=headers)
        result = json.loads(result)

        try:
            result = result['streams']
        except:
            result = result['data']['streams']
            result = [i[1] for i in result.iteritems()]

        strm = [(i['url'], int(i['watch-timeout'])) for i in result]
        strm = [i for i in strm if '.m3u8' in i[0]]
        strm.sort()
        strm = strm[-1][0]

        url = client.request(strm).splitlines()
        url = [i for i in url if '.m3u8' in i]
        if len(url) == 0: return strm
        url = urlparse.urljoin(strm, url[0])

        return url
    except:
        return

