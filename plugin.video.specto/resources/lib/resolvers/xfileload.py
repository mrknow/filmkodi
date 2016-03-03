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


import urllib,urllib2,time
from resources.lib.libraries import client
from resources.lib.libraries import captcha


def resolve(url):
    try:
        result = client.request(url, close=False)

        post = {}
        f = client.parseDOM(result, 'Form', attrs = {'action': '' })
        k = client.parseDOM(f, 'input', ret='name', attrs = {'type': 'hidden'})
        for i in k: post.update({i: client.parseDOM(f, 'input', ret='value', attrs = {'name': i})[0]})
        post.update(captcha.request(result))


        request = urllib2.Request(url, post)

        for i in range(0, 5):
            try:
                response = urllib2.urlopen(request, timeout=10)
                result = response.read()
                response.close()
                if 'download2' in result: raise Exception()
                url = client.parseDOM(result, 'a', ret='href', attrs = {'target': ''})[0]
                return url
            except:
                time.sleep(1)
    except:
        return

