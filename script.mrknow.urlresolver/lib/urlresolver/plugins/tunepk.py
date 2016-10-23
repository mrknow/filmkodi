'''
tunepk urlresolver plugin
Copyright (C) 2013 icharania

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

class TunePkResolver(UrlResolver):
    name = "tune.pk"
    domains = ["tune.pk"]
    pattern = '(?://|\.)(tune\.pk)/(?:player|video|play)/(?:[\w\.\?]+=)?(\d+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        link = repr(self.net.http_GET(web_url).content)
        if link.find('404 Not Found') >= 0:
            raise ResolverError('The requested video was not found.')

        videoUrl = []

        html = link.replace('\n\r', '').replace('\r', '').replace('\n', '').replace('\\', '')
        sources = re.compile('"sources"\s*:\s*\[(.+?)\]').findall(html)[0]
        sources = re.compile("{(.+?)}").findall(sources)

        for source in sources:
            video_link = str(re.compile('"file":"(.*?)"').findall(source)[0])
            videoUrl.append(video_link)

        vUrl = ''
        vUrlsCount = len(videoUrl)
        if vUrlsCount > 0:
            q = self.get_setting('quality')
            if q == '0':
                # Highest Quality
                vUrl = videoUrl[0]
            elif q == '1':
                # Medium Quality
                vUrl = videoUrl[(int)(vUrlsCount / 2)]
            elif q == '2':
                # Lowest Quality
                vUrl = videoUrl[vUrlsCount - 1]

            return vUrl
        else:
            raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        return 'http://embed.tune.pk/play/%s?autoplay=&ssl=no&inline=true' % media_id

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting label="Video Quality" id="%s_quality" type="enum" values="High|Medium|Low" default="0" />' % (cls.__name__))
        return xml
