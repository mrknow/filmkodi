"""
    Kodi urlresolver plugin
    Copyright (C) 2014  smokdpi
    Updated by Gujal (c) 2016

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

import re, time
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class FlashxResolver(UrlResolver):
    name = "flashx"
    domains = ["flashx.tv"]
    pattern = '(?://|\.)(flashx\.tv)/(?:embed-|dl\?|embed.php\?c=)?([0-9a-zA-Z/-]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        resp = self.net.http_GET(web_url)
        html = resp.content
        cfdcookie = resp._response.info()['set-cookie']
        cfduid = re.search('cfduid=(.*?);', cfdcookie).group(1)
        file_id = re.search("'file_id', '(.*?)'", html).group(1)
        aff = re.search("'aff', '(.*?)'", html).group(1)
        headers = { 'Referer': web_url,
                    'Cookie': '__cfduid=' + cfduid + '; lang=1'}
        surl = re.search('src="(.*?\?c=' + file_id + ')',html).group(1)
        dummy = self.net.http_GET(url=surl, headers=headers).content
        headers = { 'Referer': web_url,
                    'Cookie': '__cfduid=' + cfduid + '; lang=1; file_id=' + file_id + '; aff=' + aff }
        html = self.net.http_GET(url=web_url, headers=headers).content
        fname = re.search('name="fname" value="(.*?)"', html).group(1)
        hash = re.search('name="hash" value="(.*?)"', html).group(1)
        fdata = { 'op': 'download1',
                  'usr_login': '',
                  'id': media_id,
                  'fname': fname,
                  'referer': '',
                  'hash': hash,
                  'imhuman': 'Proceed to video' }
        furl = 'http://www.flashx.tv/dl?' + media_id
        time.sleep(5)
        html = self.net.http_POST(url=furl, form_data=fdata, headers=headers).content
        strhtml = jsunpack.unpack(re.search('(eval\(function.*?)</script>', html, re.DOTALL).group(1))
        stream = re.search('file:"([^"]*)",label', strhtml).group(1)

        if stream:
            return stream
        else:
            raise ResolverError('Filelink not found.')

    def get_url(self, host, media_id):
        return 'http://www.flashx.tv/%s.html' % media_id
