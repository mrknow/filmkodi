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


import re,urllib,urlparse
from resources.lib.libraries import cloudflare
from resources.lib.libraries import client


def resolve(url):
    try:
        result = cloudflare.request(url)

        post = {}
        f = client.parseDOM(result, 'Form', attrs = {'action': '' })
        k = client.parseDOM(f, 'input', ret='name', attrs = {'type': 'hidden'})
        for i in k: post.update({i: client.parseDOM(f, 'input', ret='value', attrs = {'name': i})[0]})
        post.update({'method_free': 'Watch Free!'})


        result = cloudflare.request(url, post=post)
        result = result.replace('\\/', '/').replace('\n', '').replace('\'', '"').replace(' ', '')

        swfUrl = re.compile('\.embedSWF\("(.+?)"').findall(result)[0]
        swfUrl = urlparse.urljoin(url, swfUrl)

        streamer = re.compile('flashvars=.+?"file":"(.+?)"').findall(result)[0]

        playpath = re.compile('flashvars=.+?p2pkey:"(.+?)"').findall(result)[0]

        url = '%s playpath=%s conn=S:%s pageUrl=%s swfUrl=%s swfVfy=true timeout=20' % (streamer, playpath, playpath, url, swfUrl)

        return url
    except:
        return


