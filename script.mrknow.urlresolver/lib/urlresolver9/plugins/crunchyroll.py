'''
Crunchyroll urlresolver plugin
Copyright (C) 2013 voinage

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
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class CrunchyRollResolver(UrlResolver):
    name = "crunchyroll"
    domains = ["crunchyroll.com"]
    pattern = '(?://|\.)(crunchyroll\.com)/.+?/.+?([^a-zA-Z-+]{6})'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET('http://www.crunchyroll.com/android_rpc/?req=RpcApiAndroid_GetVideoWithAcl&media_id=%s' % media_id, {'Host': 'www.crunchyroll.com',
                                                                                                                                      'X-Device-Uniqueidentifier': 'ffffffff-931d-1f73-ffff-ffffaf02fc5f',
                                                                                                                                      'X-Device-Manufacturer': 'HTC',
                                                                                                                                      'X-Device-Model': 'HTC Desire',
                                                                                                                                      'X-Application-Name': 'com.crunchyroll.crunchyroid',
                                                                                                                                      'X-Device-Product': 'htc_bravo',
                                                                                                                                      'X-Device-Is-GoogleTV': '0'}).content
        mp4 = re.compile(r'"video_url":"(.+?)","h"').findall(html.replace('\\', ''))[0]
        return mp4

    def get_url(self, host, media_id):
        return 'http://www.crunchyroll.com/android_rpc/?req=RpcApiAndroid_GetVideoWithAcl&media_id=%s' % media_id
