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
from resources.lib.libraries import captcha


def resolve(url):
    try:
        result = client.request(url)
        result = result.decode('iso-8859-1').encode('utf-8')

        post = {}
        f = client.parseDOM(result, 'Form', attrs = {'name': 'freeorpremium'})[0]
        k = client.parseDOM(f, 'input', ret='name', attrs = {'type': 'hidden'})
        for i in k: post.update({i: client.parseDOM(f, 'input', ret='value', attrs = {'name': i})[0]})
        post.update({'method_isfree': 'Click for Free Download'})

        result = client.request(url, post=post)
        result = result.decode('iso-8859-1').encode('utf-8')

        post = {}
        f = client.parseDOM(result, 'Form', attrs = {'name': 'F1'})[0]
        k = client.parseDOM(f, 'input', ret='name', attrs = {'type': 'hidden'})
        for i in k: post.update({i: client.parseDOM(f, 'input', ret='value', attrs = {'name': i})[0]})
        post.update(captcha.request(result))

        result = client.request(url, post=post)
        result = result.decode('iso-8859-1').encode('utf-8')

        url = client.parseDOM(result, 'a', ret='href', attrs = {'onclick': 'DL.+?'})[0]
        return url
    except:
        return


def check(url):
    try:
        base = 'http://uploadrocket.net/?op=checkfiles'
        post = {'op': 'checkfiles', 'process': 'Check URLs', 'list': url}

        result = client.request(base, post=post)
        if result == None: return False

        result = client.parseDOM(result, 'Table', attrs = {'class': 'tbl1'})[0]
        result = client.parseDOM(result, 'td', attrs = {'style': '.+?'})[0]
        if 'Not found' in result: return False

        return True
    except:
        return False


