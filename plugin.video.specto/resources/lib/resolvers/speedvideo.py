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


import re,base64
from resources.lib.libraries import client


def resolve(url):
    try:
        url = url.replace('/embed-', '/')
        url = re.compile('//.+?/([\w]+)').findall(url)[0]
        url = 'http://speedvideo.net/embed-%s.html' % url

        result = client.request(url)

        a = re.compile('var\s+linkfile *= *"(.+?)"').findall(result)[0]
        b = re.compile('var\s+linkfile *= *base64_decode\(.+?\s+(.+?)\)').findall(result)[0]
        c = re.compile('var\s+%s *= *(\d*)' % b).findall(result)[0]

        url = a[:int(c)] + a[(int(c) + 10):]
        url = base64.urlsafe_b64decode(url)
        return url
    except:
        return

