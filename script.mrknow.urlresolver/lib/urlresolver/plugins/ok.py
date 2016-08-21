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
from lib import helpers
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
        sources = []
        for entry in vids['urls']:
            quality = self.__replaceQuality(entry['name'])
            sources.append((quality, entry['url']))

        try: sources.sort(key=lambda x:int(x[0]), reverse=True)
        except: pass
        source = helpers.pick_source(sources, self.get_setting('auto_pick') == 'true')
        source = source.encode('utf-8') + '|' + urllib.urlencode(self.header)
        return source

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

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml
