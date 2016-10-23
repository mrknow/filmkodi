# -*- coding: utf-8 -*-
"""
     
    Copyright (C) 2016 anxdpanic
    
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
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError


class TwitchResolver(UrlResolver):
    name = 'twitch'
    domains = ['twitch.tv']
    pattern = 'https?://(?:www\.)?(twitch\.tv)/(.+?)(?:\?|$)'
    exclusion_pattern = '^https?://(?:www\.)?twitch\.tv/' \
                        '(?:directory|user|p|jobs|store|login|products|search|.+?/profile)' \
                        '(?:[?/].*)?$'

    def get_media_url(self, host, media_id):
        is_live = True if media_id.count('/') == 0 else False
        if is_live:
            return 'plugin://plugin.video.twitch/playLive/%s/-2/' % media_id
        else:
            if media_id.count('/') == 2:
                media_id_parts = media_id.split('/')
                if re.match('[a-z]', media_id_parts[1]) and re.match('[0-9]{6,}', media_id_parts[2]):
                    return 'plugin://plugin.video.twitch/playVideo/%s/-2/' % (media_id_parts[1] + media_id_parts[2])
        raise ResolverError('No streamer name or VOD ID found')

    def get_url(self, host, media_id):
        return self._default_get_url(host, media_id, 'https://{host}/{media_id}')

    @classmethod
    def _is_enabled(cls):
        if not common.has_addon('plugin.video.twitch'):
            return False
        return super(cls, cls)._is_enabled()

    def valid_url(self, url, host):
        if common.has_addon('plugin.video.twitch'):
            if re.search(self.pattern, url, re.I):
                return not re.match(self.exclusion_pattern, url, re.I) or any(host in domain.lower() for domain in self.domains)
        return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting label="This plugin calls the Twitch Add-on, change settings there." type="lsep" />')
        return xml
