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


import re,urllib
from resources.lib.libraries import client


def resolve(url):
    try:
        id = url.split("?v=")[-1].split("/")[-1].split("?")[0].split("&")[0]
        result = client.request('http://www.youtube.com/watch?v=%s' % id)

        message = client.parseDOM(result, 'div', attrs = {'id': 'unavailable-submessage'})
        message = ''.join(message)

        alert = client.parseDOM(result, 'div', attrs = {'id': 'watch7-notification-area'})

        if re.search('LIVE_WATCHING_NOW', result):
            url = live(result, id)
            if not url == None: return url

        if len(alert) > 0: raise Exception()
        if re.search('[a-zA-Z]', message): raise Exception()

        url = 'plugin://plugin.video.youtube/play/?video_id=%s' % id
        return url
    except:
        return


def live(result, id):
    try:
        hls = re.compile('"hlsvp" *: *"(.+?)"').findall(result)
        if len(hls) == 0:
            url = 'https://www.youtube.com/watch?v=%s' % id
            url = 'http://translate.googleusercontent.com/translate_c?anno=2&hl=en&sl=mt&tl=en&u=%s' % url
            hls = client.request(url)
            hls = re.compile('"hlsvp" *: *"(.+?)"').findall(hls)

        url = urllib.unquote(hls[0]).replace('\\/', '/')

        result = client.request(url)
        result = result.replace('\n','')
        url = re.compile('RESOLUTION *= *(\d*)x\d{1}.+?(http.+?\.m3u8)').findall(result)
        url = [(int(i[0]), i[1]) for i in url]
        url.sort()
        url = url[-1][1]
        return url
    except:
        return

