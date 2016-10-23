"""
    urlresolver Kodi plugin
    Copyright (C) 2011 t0mm0
    Updated by Gujal (C) 2016

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
"""

import re
from urlresolver import common
from lib import helpers
from urlresolver.resolver import UrlResolver, ResolverError

class NowvideoResolver(UrlResolver):
    name = "nowvideo"
    domains = ['nowvideo.eu', 'nowvideo.ch', 'nowvideo.sx', 'nowvideo.co', 'nowvideo.li', 'nowvideo.fo', 'nowvideo.at', 'nowvideo.ec']
    pattern = '(?://|\.)(nowvideo\.(?:eu|ch|sx|co|li|fo|at|ec))/(?:video/|embed\.php\?\S*v=|embed/\?v=)([A-Za-z0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        stream_url = ''
        html = self.net.http_GET(web_url).content
        try:
            r = re.search('flashvars.filekey=(.+?);', html)
            if r:
                r = r.group(1)

                try: filekey = re.compile('\s+%s="(.+?)"' % r).findall(html)[-1]
                except: filekey = r

                player_url = 'http://www.nowvideo.sx/api/player.api.php?key=%s&file=%s' % (filekey, media_id)

                html = self.net.http_GET(player_url).content

                r = re.search('url=(.+?)&', html)

                if r:
                    stream_url = r.group(1)
                else:
                    raise ResolverError('File Not Found or removed')
        except:
            print "no embedded urls found using first method"
            
        try:
            r = re.search('id="player".*?src="(.*?)"', html, re.DOTALL)
            if r:
                stream_url = r.group(1)
            
        except:
            print "no embedded urls found using second method"

        if stream_url:
            return stream_url + helpers.append_headers({'Referer': web_url})
        else:
            raise ResolverError('File Not Found or removed')
        

    def get_url(self, host, media_id):
        return 'http://embed.nowvideo.sx/embed/?v=%s' % media_id
