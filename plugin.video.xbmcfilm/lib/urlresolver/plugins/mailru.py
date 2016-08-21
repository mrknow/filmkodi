"""
    OVERALL CREDIT TO:
        t0mm0, Eldorado, VOINAGE, BSTRDMKR, tknorris, smokdpi, TheHighway

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
import json
import urllib
from lib import helpers
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class MailRuResolver(UrlResolver):
    name = "mail.ru"
    domains = ['mail.ru', 'my.mail.ru', 'videoapi.my.mail.ru', 'api.video.mail.ru']
    pattern = '(?://|\.)(mail\.ru)/.+?/(inbox|mail)/(.+?)/.+?/(\d*)\.html'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        response = self.net.http_GET(web_url)
        html = response.content

        if html:
            try:
                js_data = json.loads(html)
                headers = dict(response._response.info().items())
                cookie = ''
                if 'set-cookie' in headers: cookie = '|' + urllib.urlencode({'Cookie': headers['set-cookie']})

                sources = [('%s' % video['key'], '%s%s' % (video['url'], cookie)) for video in js_data['videos']]
                sources = sources[::-1]
                source = helpers.pick_source(sources, self.get_setting('auto_pick') == 'true')
                source = source.encode('utf-8')

                return source
                
            except:
                raise ResolverError('No playable video found.')

        else: 
            raise ResolverError('No playable video found.')

    def get_url(self, host, media_id):
        location, user, media_id = media_id.split('|')
        return 'http://videoapi.my.mail.ru/videos/%s/%s/_myvideo/%s.json?ver=0.2.60' % (location, user, media_id)

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return (r.groups()[0], '%s|%s|%s' % (r.groups()[1], r.groups()[2], r.groups()[3]))
        else:
            return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (cls.__name__))
        return xml
