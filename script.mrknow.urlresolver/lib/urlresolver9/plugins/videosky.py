'''
    urlresolver Kodi Addon
    Copyright (C) 2016 Gujal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import re
import urllib
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class VideoSkyResolver(UrlResolver):
    name = "videosky.to"
    domains = ["videosky.to"]
    pattern = '(?://|\.)(videosky.to)/(?:embed\.php\?id=)([0-9a-z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        r = re.search('key:\s"(.+?)"', html)
        if r:
            filekey = r.group(1)

            player_url = 'http://www.videosky.to/api/player.api.php?user=&numOfErrors=0&pass=&cid2=&key=%s&file=%s&cid3=&cid=1' % (filekey, media_id)

            html = self.net.http_GET(player_url).content

            r = re.search('url=(.+?)&', html)

            if r:
                stream_url = urllib.unquote(r.group(1))
            else:
                raise ResolverError('File Not Found or removed')

        return stream_url

    def get_url(self, host, media_id):
        return 'http://www.videosky.to/embed.php?id=%s' % media_id
