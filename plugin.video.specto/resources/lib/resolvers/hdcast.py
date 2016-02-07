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


import re,urlparse
from resources.lib.libraries import client


def resolve(url):
    try:
        id = urlparse.parse_qs(urlparse.urlparse(url).query)['id'][0]

        pageUrl = 'http://hdcast.me/embedplayer.php?id=%s&autoplay=true' % id
        swfUrl = 'http://p.jwpcdn.com/6/12/jwplayer.flash.swf'

        result = client.request(pageUrl, referer=pageUrl)

        streamer = result.replace('//file', '')
        streamer = re.compile("file *: *'(.+?)'").findall(streamer)[-1]

        token = re.compile('getJSON[(]"(.+?)".+?json[.]token').findall(result.replace('\n', ''))[-1]
        token = client.request(token, referer=pageUrl)
        token = re.compile('"token" *: *"(.+?)"').findall(token)[-1]

        url = '%s pageUrl=%s swfUrl=%s token=%s live=true timeout=20' % (streamer, pageUrl, swfUrl, token)

        return url
    except:
        return

