'''
YoutubeDL urlresolver plugin
Copyright (C) 2018 Robert Kalinowski <robert.kalinowski@shatkbits.com>

This plugin is proxy to great youtube-dl project.
See https://github.com/rg3/youtube-dl/

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

#from __future__ import absolute_import, unicode_literals
from __future__ import unicode_literals

from urlresolver9.resolver import UrlResolver, ResolverError
from youtube_dl.YoutubeDL import YoutubeDL, DownloadError


class VidziResolver(UrlResolver):
    name = "youtube-dl"
    domains = ["*"]
    pattern = r'^(.*)()$'
    #pattern = r'^((?:.*?//|\.)([^/]*).*)$'
    #pattern = r'(?://|\.)([^/]*)/(.*)$'
    priority = 200

    def get_media_url(self, host, media_id):
        opts = {
            'quiet': True,
            'no_color': True,
        }
        with YoutubeDL(opts) as ydl:
            try:
                # host is full URL in our case
                info = ydl.extract_info(host, download=False)
            except DownloadError as e:
                raise ResolverError
            if not 'url' in info:
                raise ResolverError
            return info['url']

    def get_url(self, host, media_id):
        return host

