'''
Nosvideo urlresolver plugin
Copyright (C) 2013 Vinnydude

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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class NosvideoResolver(UrlResolver):
    name = "nosvideo"
    domains = ["nosvideo.com", "noslocker.com"]
    pattern = '(?://|\.)(nosvideo.com|noslocker.com)/(?:\?v\=|embed/|.+?\u=)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        if 'File Not Found' in html:
            raise ResolverError('File Not Found')

        web_url = 'http://nosvideo.com/vj/video.php?u=%s&w=&h=530' % media_id

        html = self.net.http_GET(web_url).content

        smil_url = re.compile('\':\'(.+?)\'').findall(html)
        smil_url = [i for i in smil_url if '.smil' in i][0]

        html = self.net.http_GET(smil_url).content

        streamer = re.findall('base\s*=\s*"(.+?)"', html)[0]
        playpath = re.findall('src\s*=\s*"(.+?)"', html)[0]

        stream_url = '%s playpath=%s' % (streamer, playpath)

        return stream_url

    def get_url(self, host, media_id):
        return 'http://nosvideo.com/%s' % media_id

