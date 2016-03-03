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


import re,urllib,time
from resources.lib.libraries import client
from resources.lib.libraries import jsunpack


def resolve(url):
    try:
        url = url.replace('/embed-', '/')
        url = re.compile('//.+?/([\w]+)').findall(url)[0]
        page = 'http://cloudyvideos.com/%s' % url

        result = client.request(page, close=False)

        if '>File Not Found<' in result: raise Exception()

        post = {}
        f = client.parseDOM(result, 'Form', attrs = {'action': ''})
        k = client.parseDOM(f, 'input', ret='name', attrs = {'type': 'hidden'})
        for i in k: post.update({i: client.parseDOM(f, 'input', ret='value', attrs = {'name': i})[0]})
        post = post


        for i in range(0, 5):
            try:
                result = client.request(page, post=post, close=False)

                url = re.compile("file *: *'(.+?)'").findall(result)

                if len(url) == 0:
                    result = re.compile('(eval.*?\)\)\))').findall(result)
                    result = [i for i in result if '|download|' in i][0]
                    result = jsunpack.unpack(result)
                    url = client.parseDOM(result, 'embed', ret='src')
                    url += re.compile("file *: *[\'|\"](.+?)[\'|\"]").findall(result)

                url = [i for i in url if not i.endswith('.srt')]
                url = 'http://' + url[0].split('://', 1)[-1]
                return url
            except:
                time.sleep(1)

    except:
        return


