# -*- coding: UTF-8 -*-
"""
    Copyright (C) 2014  smokdpi

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
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
import xbmc

class UpToBoxResolver(UrlResolver):
    name = "uptobox"
    domains = ["uptobox.com", "uptostream.com"]
    pattern = '(?://|\.)(uptobox.com|uptostream.com)/(?:iframe/)?([0-9A-Za-z_]+)'

    def __init__(self):
        self.net = common.Net()
        self.user_agent = common.IE_USER_AGENT
        self.net.set_user_agent(self.user_agent)
        self.headers = {'User-Agent': self.user_agent}

    def get_media_url(self, host, media_id):

        try:
            web_url = self.get_url(host, media_id)
            self.headers['Referer'] = web_url

            html = self.net.http_GET(web_url, headers=self.headers).content
            if isinstance(html, unicode):
                html = html.encode('utf-8', 'ignore')

            if 'Uptobox.com is not available in your country' in html:
                raise Exception()

            r = re.search('(You have to wait (?:[0-9]+ minute[s]*, )*[0-9]+ second[s]*)', html)
            if r:
                raise Exception()

            data = helpers.get_hidden(html)
            for i in range(0, 3):
                try:
                    html = self.net.http_POST(web_url, data, headers=self.headers).content
                    if isinstance(html, unicode):
                        html = html.encode('utf-8', 'ignore')

                    stream_url = re.search('<a\shref\s*=[\'"](.+?)[\'"]\s*>\s*<span\sclass\s*=\s*[\'"]button_upload green[\'"]\s*>', html).group(1)
                    return stream_url
                except:
                    xbmc.sleep(1000)
        except:
            pass

        try:
            web_url = self.get_stream_url(host, media_id)
            self.headers['Referer'] = web_url

            html = self.net.http_GET(web_url, headers=self.headers).content
            if isinstance(html, unicode):
                html = html.encode('utf-8', 'ignore')

            if 'Uptobox.com is not available in your country' in html:
                raise Exception()
            '''
            r = re.search('(You have reached the limit of *[0-9]+ minute[s]*)', html)
            if r:
                raise Exception()
            '''

            sources = re.compile('<source.+?src\s*=\s*[\'"](.+?)[\'"].+?data-res\s*=\s*[\'"](.+?)[\'"].*?/>').findall(html)
            sources = [(i[0], int(re.sub('[^0-9]', '', i[1]))) for i in sources]
            sources = sorted(sources, key=lambda k: k[1])

            stream_url = sources[-1][0]
            if stream_url.startswith('//'):
                stream_url = 'http:' + stream_url

            return stream_url
        except:
            pass

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'http://uptobox.com/%s' % media_id

    def get_stream_url(self, host, media_id):
        return 'http://uptostream.com/%s' % media_id
