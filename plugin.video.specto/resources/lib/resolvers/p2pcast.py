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


import re,urllib,urlparse,base64
from resources.lib.libraries import client


def resolve(url):
    try:
        referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]

        page = urlparse.parse_qs(urlparse.urlparse(url).query)['id'][0]
        page = 'http://p2pcast.tv/stream.php?id=%s&live=0&p2p=0&stretching=uniform' % page

        result = client.request(page, referer=referer)


        try:
            swf = re.compile('src\s*=[\'|\"](.+?player.+?\.js)[\'|\"]').findall(result)[0]
            swf = client.request(swf)
            swf = re.compile('flashplayer\s*:\s*[\'|\"](.+?)[\'|\"]').findall(swf)[0]
        except:
            swf = 'http://cdn.p2pcast.tv/jwplayer.flash.swf'


        url = re.compile('url\s*=\s*[\'|\"](.+?)[\'|\"]').findall(result)[0]
        url = base64.b64decode(url)
        url = '%s|User-Agent=%s&Referer=%s' % (url, urllib.quote_plus(client.agent()), urllib.quote_plus(swf))

        return url
    except:
        return


