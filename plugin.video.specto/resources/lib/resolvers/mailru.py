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


import re,json,urllib
import requests


def resolve(url):
    try:
        usr = re.compile('/mail/(.+?)/').findall(url)[0]
        vid = re.compile('(\d*)[.]html').findall(url)[0]
        url = 'http://videoapi.my.mail.ru/videos/mail/%s/_myvideo/%s.json?ver=0.2.60' % (usr, vid)

        result = requests.get(url).content
        cookie = requests.get(url).headers['Set-Cookie']

        u = json.loads(result)['videos']
        h = "|Cookie=%s" % urllib.quote(cookie)

        url = []
        try: url += [[{'quality': '1080p', 'url': i['url'] + h} for i in u if i['key'] == '1080p'][0]]
        except: pass
        try: url += [[{'quality': 'HD', 'url': i['url'] + h} for i in u if i['key'] == '720p'][0]]
        except: pass
        try: url += [[{'quality': 'SD', 'url': i['url'] + h} for i in u if not (i['key'] == '1080p' or i ['key'] == '720p')][0]]
        except: pass

        if url == []: return
        return url
    except:
        return

