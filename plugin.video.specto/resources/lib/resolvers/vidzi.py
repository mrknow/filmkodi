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


import re,urllib,time
from resources.lib.libraries import client
from resources.lib.libraries import jsunpack


def resolve(url):
    try:
        result = client.request(url, mobile=True, close=False)

        try:
            post = {}
            f = client.parseDOM(result, 'Form', attrs = {'method': 'POST'})[0]
            f = f.replace('"submit"', '"hidden"')
            k = client.parseDOM(f, 'input', ret='name', attrs = {'type': 'hidden'})
            for i in k: post.update({i: client.parseDOM(f, 'input', ret='value', attrs = {'name': i})[0]})
            post = urllib.urlencode(post)
        except:
            post=None

        for i in range(0, 10):
            try:
                result = client.request(url, post=post, mobile=True, close=False)
                result = result.replace('\n','')

                result = re.compile('(eval.*?\)\)\))').findall(result)[-1]
                result = jsunpack.unpack(result)

                result = re.compile('sources *: *\[.+?\]').findall(result)[-1]
                result = re.compile('file *: *"(http.+?)"').findall(result)

                url = [i for i in result if not '.m3u8' in i]
                if len(url) > 0: return '%s|Referer=%s' % (url[0], urllib.quote_plus('http://vidzi.tv/nplayer/jwplayer.flash.swf'))
                url = [i for i in result if '.m3u8' in i]
                if len(url) > 0: return url[0]
            except:
                time.sleep(1)
    except:
        return

