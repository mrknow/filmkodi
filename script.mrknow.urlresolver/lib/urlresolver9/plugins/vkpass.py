# -*- coding: utf-8 -*-

"""
VKPass urlresolver XBMC Addon based on VKResolver
Copyright (C) 2015 Seberoth
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
from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class VKPassResolver(UrlResolver):
    name = "VKPass.com"
    domains = ["vkpass.com"]
    pattern = '(?://|\.)(vkpass\.com)/token/(.+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        base_url = self.get_url(host, media_id)
        soup = self.net.http_GET(base_url).content
        html = soup.decode('cp1251')
        vBlocks = re.findall('{(file.*?label.*?)}', html)
        html5 = re.findall('}\((.*?)\)\)<', html)

        if not vBlocks and not html5:
            raise ResolverError('No vsource found')

        data = {}
        data['purged_jsonvars'] = {}
        data['lines'] = []

        if html5:
            for source in html5:
                params = source.split(',')
                data = self.__decodeLinks(params[0], params[3].split('|'), data)
        elif vBlocks:
            data = self.__getFlashVids()

        sources = [(line, data['purged_jsonvars'][line]) for line in data['lines']]
        try: sources.sort(key=lambda x: int(x[0][3:]), reverse=True)
        except: pass
        source = helpers.pick_source(sources)
        return source + helpers.append_headers({'User-Agent': common.IE_USER_AGENT})

    def __decodeLinks(self, html, list, data):
        if "source" not in list:
            return data

        numerals = "0123456789abcdefghijklmnopqrstuvwxyz"
        letters = re.findall('([0-9a-z])', html)
        for letter in letters:
            html = re.sub('\\b' + letter + '\\b', list[numerals.index(letter)], html)

        sources = re.findall('<source.*?>', html)

        for source in sources:
            url = re.findall('src="(.*?)"', source)
            res = re.findall('res="(.*?)"', source)

            data['lines'].append(res[0])
            data['purged_jsonvars'][res[0]] = url[0]
            if int(res[0]) > int(data['best']): data['best'] = res[0]

        return data

    def __getFlashVids(self, vBlocks, data):
        for block in vBlocks:
            vItems = re.findall('([a-z]*):"(.*?)"', block)
            if vItems:
                quality = ''
                url = ''

                for item in vItems:
                    if 'file' in item[0]:
                        url = item[1]
                    if 'label' in item[0]:
                        quality = re.sub("[^0-9]", "", item[1])
                        data['lines'].append(quality)
                        if int(quality) > int(data['best']): data['best'] = quality

                data['purged_jsonvars'][quality] = url

        return data

    def get_url(self, host, media_id):
        return 'http://vkpass.com/token/%s' % media_id
