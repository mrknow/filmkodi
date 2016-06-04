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


import re
from resources.lib.libraries import client
from resources.lib.libraries import control



def resolve(url):
    try:
        id = re.compile('//.+?/.+?/([\w]+)').findall(url)
        id += re.compile('//.+?/.+?v=([\w]+)').findall(url)
        id = id[0]

        url = 'http://www.cloudtime.to/video/%s' % id

        result = client.request(url)
        post = {}
        f = client.parseDOM(result, 'form', attrs = {'action': ''})
        k = client.parseDOM(f, 'input', ret='name', attrs = {'type': 'hidden'})
        for i in k: post.update({i: client.parseDOM(f, 'input', ret='value', attrs = {'name': i})[0]})
        post = post

        result = client.request(url, post=post)

        key = re.compile('flashvars.filekey=(.+?);').findall(result)[-1]
        try: key = re.compile('\s+%s="(.+?)"' % key).findall(result)[-1]
        except: pass

        url = 'http://www.cloudtime.to/api/player.api.php?key=%s&file=%s' % (key, id)
        result = client.request(url)

        url = re.compile('url=(.+?)&').findall(result)[0]
        return url
    except:
        return

