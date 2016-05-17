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


import re,urllib
from resources.lib.libraries import client
import xbmc

def resolve(url):
    try:
        url = url.replace('/embed-', '/')
        url = re.compile('//.+?/([\w]+)').findall(url)[0]
        page = 'http://allmyvideos.net/%s' % url

        result = client.request(page, close=False)

        post = {}
        f = client.parseDOM(result, 'form', attrs = {'action': ''})
        k = client.parseDOM(f, 'input', ret='name', attrs = {'type': 'hidden'})
        for i in k: post.update({i: client.parseDOM(f, 'input', ret='value', attrs = {'name': i})[0]})
        post = post

        result = client.request(page, post=post)

        url = re.compile('"file" *: *"(http.+?)"').findall(result)[-1]
        url += '&direct=false&ua=false'
        xbmc.sleep(2000)
        #return url + '|' + urllib.urlencode({ 'User-Agent': client.IE_USER_AGENT })
        return
    except:
        return

