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


import re,urllib
from resources.lib.libraries import client


def resolve(url):
    try:
        url = url.replace('/embed-', '/')
        url = re.compile('//.+?/([\w]+)').findall(url)[0]

        u = 'http://nosvideo.com/vj/video.php?u=%s&w=&h=530' % url
        r = 'http://nosvideo.com/%s' % url

        result = client.request(u, referer=r)

        url = client.parseDOM(result, 'source', ret='src', attrs = {'type': 'video/.+?'})
        url += client.parseDOM(result, 'source', ret='src', attrs = {'type': 'video/mp4'})
        url = url[-1]

        return url
    except:
        return

