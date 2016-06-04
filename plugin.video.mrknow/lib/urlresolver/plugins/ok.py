"""
OK urlresolver XBMC Addon
Copyright (C) 2016 Seberoth

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
import xbmcgui
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class OKResolver(UrlResolver):
    name = "ok.ru"
    domains = ['ok.ru', 'odnoklassniki.ru']
    pattern = '(?://|\.)(ok.ru|odnoklassniki.ru)/(?:videoembed|video)/(.+)'
    header = {"User-Agent": common.OPERA_USER_AGENT}
    qual_map = {'full': '1080', 'hd': '720', 'sd': '480', 'low': '360', 'lowest': '240', 'mobile': '144'}

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        vids = self.__get_Metadata(media_id)

        purged_jsonvars = {}
        lines = []
        best = '0'

        for entry in vids['urls']:
            quality = self.__replaceQuality(entry['name'])
            lines.append(quality)
            purged_jsonvars[quality] = entry['url'] + '|' + urllib.urlencode(self.header)
            if int(quality) > int(best): best = quality

        if len(lines) == 1:
            return purged_jsonvars[lines[0]].encode('utf-8')
        else:
            if self.get_setting('auto_pick') == 'true':
                return purged_jsonvars[str(best)].encode('utf-8')
            else:
                result = xbmcgui.Dialog().select('Choose the link', lines)

        if result != -1:
            return purged_jsonvars[lines[result]].encode('utf-8')
        else:
            raise ResolverError('No link selected')

        raise ResolverError('No video found')

    def __replaceQuality(self, qual):
        return self.qual_map.get(qual.lower(), '000')

    def __get_Metadata(self, media_id):
        url = "http://www.ok.ru/dk?cmd=videoPlayerMetadata&mid=" + media_id
        html = self.net.http_GET(url, headers=self.header).content
        json_data = json.loads(html)
        info = dict()
        info['urls'] = []
        for entry in json_data['videos']:
            info['urls'].append(entry)
        return info

    def get_url(self, host, media_id):
        return 'http://%s/videoembed/%s' % (host, media_id)

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
