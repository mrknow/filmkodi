"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

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
import urllib
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class MovshareResolver(UrlResolver):
    name = "movshare"
    domains = ["movshare.net", 'wholecloud.net', 'vidgg.to']
    pattern = '(?://|\.)(movshare.net|wholecloud.net|vidgg.to)/(?:video/|embed(?:/|\.php)\?(?:v|id)=)([A-Za-z0-9]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        try:
            stream_url = ''
            r = re.search('flashvars.filekey=(.+?);', html)
            if r:
                r = r.group(1)
                try: filekey = re.search('var\s+%s\s*=\s*"([^"]+)' % (r), html).group(1)
                except: filekey = r
                player_url = 'http://%s/api/player.api.php?key=%s&file=%s' % (host, urllib.quote(filekey), media_id)
                html = self.net.http_GET(player_url).content
                r = re.search('url=(.+?)&', html)
                if r:
                    stream_url = r.group(1)
        except:
            common.log_utils.log("no embedded urls found using first method")
            
        try:
            r = re.search('id="player"[^>]+src="([^"]+)', html, re.DOTALL)
            if r:
                stream_url = r.group(1)
            
        except:
            print "no embedded urls found using second method"

        if stream_url:
            return '%s|Referer=%s' % (stream_url, web_url)
        else:
            raise ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
        if 'vidgg' in host:
            return 'http://%s/embed/?id=%s' % (host, media_id)
        else:
            return 'http://%s/embed/?v=%s' % (host, media_id)
