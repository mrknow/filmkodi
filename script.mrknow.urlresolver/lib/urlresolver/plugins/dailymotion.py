'''
dailymotion urlresolver plugin
Copyright (C) 2011 cyrus007

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
import urllib2
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class DailymotionResolver(UrlResolver):
    name = 'dailymotion'
    domains = ['dailymotion.com']
    pattern = '(?://|\.)(dailymotion\.com)/(?:video|embed|sequence|swf)(?:/video)?/([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        html = html.replace('\\', '')

        auto = re.findall('"auto"\s*:\s*.+?"url"\s*:\s*"(.+?)"', html)
        qualities = re.findall('"(\d+?)"\s*:\s*.+?"url"\s*:\s*"(.+?)"', html)

        if auto and not qualities:
            return auto[0]

        qualities = [(int(i[0]), i[1]) for i in qualities]
        qualities = sorted(qualities, key=lambda x: x[0])[::-1]

        videoUrl = [i[1] for i in qualities]

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


        if not '.m3u8' in vUrl: return
        vUrl = self.net.http_GET(vUrl).content
        vUrl = re.findall('(http(?:s|)://.+?)\n', vUrl)
        vUrl = [i for i in vUrl if '.m3u8' in i][0]
        return vUrl

    def get_url(self, host, media_id):
        return 'http://www.dailymotion.com/embed/video/%s' % media_id

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting label="Video Quality" id="%s_quality" type="enum" values="High|Medium|Low" default="0" />' % (cls.__name__))
        return xml
