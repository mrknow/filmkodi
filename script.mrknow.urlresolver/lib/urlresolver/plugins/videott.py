'''
videott urlresolver plugin
Copyright (C) 2015 icharania

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
import json
import urlparse
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class VideoTTResolver(UrlResolver):
    name = "videott"
    domains = ["video.tt"]
    pattern = '(?://|\.)(video\.tt)/(?:video\/|embed\/|watch_video\.php\?v=)(\w+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        json_url = 'http://www.video.tt/player_control/settings.php?v=%s' % media_id
        data = self.net.http_GET(json_url).content
        data = json.loads(data)

        vids = data['settings']['res']

        if vids:
            vUrlsCount = len(vids)

            if (vUrlsCount > 0):
                q = self.get_setting('quality')
                # Lowest Quality
                li = 0

                if q == '1':
                    # Medium Quality
                    li = (int)(vUrlsCount / 2)
                elif q == '2':
                    # Highest Quality
                    li = vUrlsCount - 1

                vUrl = vids[li]['u'].decode('base-64')
                return vUrl

        else:
            vUrl = data['settings']['config']

            vUrl = [i[1].decode('base-64') for i in vUrl.items() if i[0].startswith('token')]
            vUrl = [(urlparse.parse_qsl(urlparse.urlparse(i).query), i) for i in vUrl]
            vUrl = [([x[1] for x in i[0] if x[0] == 'r'], i[1]) for i in vUrl]
            vUrl = [(i[0][0], i[1]) for i in vUrl if i[0]]
            vUrl = vUrl[0][1]
            return vUrl

        raise ResolverError('The requested video was not found.')

    def get_url(self, host, media_id):
        return 'http://www.video.tt/watch_video.php?v=%s' % media_id

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting label="Video Quality" id="%s_quality" type="enum" values="High|Medium|Low" default="0" />' % (cls.__name__))
        return xml
