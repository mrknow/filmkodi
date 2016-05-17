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


import urllib,time, re
from resources.lib.libraries import client
from resources.lib.libraries import control


def resolve(url):
    try:
        referer = url
        result = client.request(url)

        post = {}
        f = client.parseDOM(result, 'form', attrs = {'name': 'F1'})[0]
        k = client.parseDOM(f, 'input', ret='name', attrs = {'type': 'hidden'})
        for i in k: post.update({i: client.parseDOM(f, 'input', ret='value', attrs = {'name': i})[0]})
        post = post

        for i in range(0, 3):
            try:
                result = client.request(url, post=post,referer=referer)

                url = re.search('<a\shref\s*=[\'"](.+?)[\'"]\s*>\s*<span\sclass\s*=\s*[\'"]button_upload green[\'"]\s*>', result).group(1)
                control.log("UPTOBOX URL: %s" % url)
                url = ['http' + i for i in url.split('http') if 'uptobox.com' in i][0]
                return url
            except:
                time.sleep(1)
    except:
        return


def check(url):
    try:
        result = client.request(url)
        if result == None: return False

        result = client.parseDOM(result, 'span', attrs = {'class': 'para_title'})
        if any('File not found' in x for x in result): raise Exception()

        return True
    except:
        return False


