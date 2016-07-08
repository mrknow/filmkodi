"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

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
from urlresolver import common
from urlresolver.resolver import UrlResolver

class Mp4uploadResolver(UrlResolver):
    name = "mp4upload"
    domains = ["mp4upload.com"]
    pattern = '(?://|\.)(mp4upload\.com)/(?:embed-)?([0-9a-zA-Z]+)'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content
        url = re.findall('(?:\"|\')file(?:\"|\')\s*:\s*(?:\"|\')(.+?)(?:\"|\')', html)[0]
        return url

    def get_url(self, host, media_id):
        return 'http://www.mp4upload.com/embed-%s.html' % media_id
