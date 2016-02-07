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
from resources.lib.libraries import client


def resolve(url):
    try:
        try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['urlback'][0]
        except: pass

        id = re.compile('/video/([\w]+)').findall(url)[0]

        u = 'http://www.dailymotion.com/sequence/full/%s' % id
        result = client.request(u)
        result = urllib.unquote(result).replace('\\/', '/').replace('\n', '').replace('\'', '"').replace(' ', '')

        content = re.compile('"content_type":"(.+?)"').findall(result)
        content = '' if len(content) == 0 else content[0]

        if content == 'live':
            url = re.compile('"autoURL":"(.+?)"').findall(result)[0]
            protocol = urlparse.parse_qs(urlparse.urlparse(url).query)['protocol'][0]
            url = url.replace('protocol=%s' % protocol, 'protocol=hls')
            url += '&redirect=0'

            url = client.request(url)
            return url

        else:
            u = 'http://www.dailymotion.com/embed/video/%s' % id

            result = client.request(u, cookie='ff=off')
            result = urllib.unquote(result).replace('\\/', '/').replace('\n', '').replace('\'', '"').replace(' ', '')

            url = []
            try: url += [{'quality': 'HD', 'url': client.request(re.compile('"720":.+?"url":"(.+?)"').findall(result)[0], output='geturl')}]
            except: pass
            try: url += [{'quality': 'SD', 'url': client.request(re.compile('"480":.+?"url":"(.+?)"').findall(result)[0], output='geturl')}]
            except: pass
            if not url == []: return url
            try: url += [{'quality': 'SD', 'url': client.request(re.compile('"380":.+?"url":"(.+?)"').findall(result)[0], output='geturl')}]
            except: pass
            if not url == []: return url
            try: url += [{'quality': 'SD', 'url': client.request(re.compile('"240":.+?"url":"(.+?)"').findall(result)[0], output='geturl')}]
            except: pass

            if url == []: return
            return url
    except:
        return

