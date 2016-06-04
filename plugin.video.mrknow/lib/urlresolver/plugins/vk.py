"""
VK urlresolver XBMC Addon
Copyright (C) 2015 tknorris

Version 0.0.1 

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
"""
import re
import json
import urllib
import urlparse
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError
import xbmcgui

class VKResolver(UrlResolver):
    name = "VK.com"
    domains = ["vk.com"]
    pattern = '(?://|\.)(vk\.com)/(?:video_ext\.php\?|video)(.+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        headers = {
            'User-Agent': common.IE_USER_AGENT
        }

        query = urlparse.parse_qs(media_id)

        try: oid, video_id = query['oid'][0], query['id'][0]
        except: oid, video_id = re.findall('(.*)_(.*)', media_id)[0]

        try: hash = query['hash'][0]
        except: hash = self.__get_hash(oid, video_id)

        api_url = 'http://api.vk.com/method/video.getEmbed?oid=%s&video_id=%s&embed_hash=%s' % (oid, video_id, hash)

        html = self.net.http_GET(api_url).content
        html = re.sub(r'[^\x00-\x7F]+', ' ', html)

        try: result = json.loads(html)['response']
        except: result = self.__get_private(oid, video_id)

        quality_list = []
        link_list = []
        best_link = ''
        for quality in ['url240', 'url360', 'url480', 'url540', 'url720']:
            if quality in result:
                quality_list.append(quality[3:])
                link_list.append(result[quality])
                best_link = result[quality]

        if self.get_setting('auto_pick') == 'true' and best_link:
            return best_link + '|' + urllib.urlencode(headers)
        else:
            if quality_list:
                if len(quality_list) > 1:
                    result = xbmcgui.Dialog().select('Choose the link', quality_list)
                    if result == -1:
                        raise ResolverError('No link selected')
                    else:
                        return link_list[result] + '|' + urllib.urlencode(headers)
                else:
                    return link_list[0] + '|' + urllib.urlencode(headers)

        raise ResolverError('No video found')

    def __get_private(self, oid, video_id):
        private_url = 'http://vk.com/al_video.php?act=show_inline&al=1&video=%s_%s' % (oid, video_id)
        html = self.net.http_GET(private_url).content
        html = re.sub(r'[^\x00-\x7F]+', ' ', html)
        match = re.search('var\s+vars\s*=\s*({.+?});', html)
        try: return json.loads(match.group(1))
        except: return {}
        return {}

    def __get_hash(self, oid, video_id):
        hash_url = 'http://vk.com/al_video.php?act=show_inline&al=1&video=%s_%s' % (oid, video_id)
        html = self.net.http_GET(hash_url).content
        html = html.replace('\'', '"').replace(' ', '')
        html = re.sub(r'[^\x00-\x7F]+', ' ', html)
        match = re.search('"hash2"\s*:\s*"(.+?)"', html)
        if match: return match.group(1)
        match = re.search('"hash"\s*:\s*"(.+?)"', html)
        if match: return match.group(1)
        return ''

    def get_url(self, host, media_id):
        return 'http://vk.com/video_ext.php?%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml
