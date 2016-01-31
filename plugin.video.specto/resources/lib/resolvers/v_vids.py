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


import urllib
from resources.lib.libraries import client


def resolve(url):
    try:
        result = client.request(url)

        post = {}
        f = client.parseDOM(result, 'Form', attrs = {'name': 'F1'})[0]
        k = client.parseDOM(f, 'input', ret='name', attrs = {'type': 'hidden'})
        for i in k: post.update({i: client.parseDOM(f, 'input', ret='value', attrs = {'name': i})[0]})
        post.update({'method_free': '', 'method_premium': ''})
        post = urllib.urlencode(post)

        result = client.request(url, post=post)

        url = client.parseDOM(result, 'a', ret='href', attrs = {'id': 'downloadbutton'})[0]
        return url
    except:
        return

