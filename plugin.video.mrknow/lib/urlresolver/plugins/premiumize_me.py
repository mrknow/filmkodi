"""
    urlresolver XBMC Addon
    Copyright (C) 2013 Bstrdsmkr

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
import urllib
import json
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class PremiumizeMeResolver(UrlResolver):
    name = "Premiumize.me"
    domains = ["*"]
    media_url = None

    def __init__(self):
        self.hosts = []
        self.patterns = []
        self.net = common.Net()
        self.scheme = 'https' if self.get_setting('use_https') == 'true' else 'http'

    def get_media_url(self, host, media_id):
        username = self.get_setting('username')
        password = self.get_setting('password')
        url = '%s://api.premiumize.me/pm-api/v1.php?' % (self.scheme)
        query = urllib.urlencode({'method': 'directdownloadlink', 'params[login]': username, 'params[pass]': password, 'params[link]': media_id})
        url = url + query
        response = self.net.http_GET(url).content
        response = json.loads(response)
        if 'status' in response:
            if response['status'] == 200:
                link = response['result']['location']
            else:
                raise ResolverError('Link Not Found: Error Code: %s' % response['status'])
        else:
            raise ResolverError('Unexpected Response Received')

        common.log_utils.log_debug('Premiumize.me: Resolved to %s' % link)
        return link

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'premiumize.me', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        try:
                username = self.get_setting('username')
                password = self.get_setting('password')
                url = '%s://api.premiumize.me/pm-api/v1.php?' % (self.scheme)
                query = urllib.urlencode({'method': 'hosterlist', 'params[login]': username, 'params[pass]': password})
                url = url + query
                response = self.net.http_GET(url).content
                response = json.loads(response)
                result = response['result']
                log_msg = 'Premiumize.me patterns: %s hosts: %s' % (result['regexlist'], result['tldlist'])
                common.log_utils.log_debug(log_msg)
                return result['tldlist'], [re.compile(regex) for regex in result['regexlist']]
        except Exception as e:
            common.log_utils.log_error('Error getting Premiumize hosts: %s' % (e))
        return [], []

    def valid_url(self, url, host):
        if not self.patterns or not self.hosts:
            self.hosts, self.patterns = self.get_all_hosters()

        if url:
            if not url.endswith('/'): url += '/'
            for pattern in self.patterns:
                if pattern.findall(url):
                    return True
        elif host:
            if host.startswith('www.'): host = host.replace('www.', '')
            if any(host in item for item in self.hosts):
                return True

        return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_use_https" type="bool" label="Use HTTPS" default="false"/>' % (cls.__name__))
        xml.append('<setting id="%s_login" type="bool" label="login" default="false"/>' % (cls.__name__))
        xml.append('<setting id="%s_username" enable="eq(-1,true)" type="text" label="Customer ID" default=""/>' % (cls.__name__))
        xml.append('<setting id="%s_password" enable="eq(-2,true)" type="text" label="PIN" option="hidden" default=""/>' % (cls.__name__))
        return xml

    @classmethod
    def isUniversal(self):
        return True
