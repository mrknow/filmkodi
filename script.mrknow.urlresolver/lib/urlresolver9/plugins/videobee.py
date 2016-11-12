'''
videobee urlresolver plugin
Copyright (C) 2016 Gujal

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

from lib import helpers
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class VideoBeeResolver(UrlResolver):
    name = "thevideobee.to"
    domains = ["thevideobee.to"]
    pattern = '(?://|\.)(thevideobee\.to)/(?:embed-)?([0-9A-Za-z]+)'

    def get_media_url(self, host, media_id):
        return helpers.get_media_url(self.get_url(host, media_id))

    def get_url(self, host, media_id):
        return 'https://thevideobee.to/embed-%s.html' % media_id
