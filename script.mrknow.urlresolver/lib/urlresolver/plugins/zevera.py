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
import urllib
import urllib2
import urlparse
import socket
import xml.etree.ElementTree as ET
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

MAX_REDIR = 10
TIMEOUT = 2
class NoRedirection(urllib2.HTTPErrorProcessor):

    def http_response(self, request, response):
        return response

    https_response = http_response

class ZeveraResolver(UrlResolver):
    name = "Zevera"
    domains = ["*"]
    media_url = None

    def __init__(self):
        self.hosts = []
        self.patterns = []
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        username = self.get_setting('username')
        password = self.get_setting('password')
        url = 'http://api.zevera.com/jDownloader.ashx?'
        query = urllib.urlencode({'cmd': 'generatedownloaddirect', 'login': username, 'pass': password, 'olink': media_id})
        url = url + query
        opener = urllib2.build_opener(NoRedirection)
        urllib2.install_opener(opener)
        redirs = 0
        while redirs < MAX_REDIR:
            request = urllib2.Request(url)
            request.get_method = lambda: 'HEAD'
            try:
                response = urllib2.urlopen(request, timeout=TIMEOUT)
                if response.getcode() == 200:
                    common.log_utils.log_debug('Zevera: Resolved to %s' % (url))
                    return url
                elif response.getcode() == 302:
                    url = response.info().getheader('Location')
                    redirs += 1
                    common.log_utils.log_debug('Zevera Redir #%d: %s' % (redirs, url))
                else:
                    common.log_utils.log_warning('Unexpected Zevera Response (%s): %s' % (response.getcode(), response.read()))
                    raise ResolverError('Zevera: Unexpected Response Received')
            except socket.timeout:
                common.log_utils.log_warning('Zevera timeout: %s' % (url))
                raise ResolverError('Zevera: Timeout')

        raise ResolverError('Zevera: Redirect beyond max allowed (%s)' % (MAX_REDIR))

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'zevera.com', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        try:
            hosts = []
            url = 'http://zevera.com/downloadapi.asmx/GetHosters'
            html = self.net.http_GET(url).content
            root = ET.fromstring(html)
            ns = '{http://tempuri.org/}'
            for item in root.findall('.//%shoster' % (ns)):
                is_active = item.find('%sisActive' % (ns))
                hostername = item.find('%shostername' % (ns))
                if is_active is not None and hostername is not None and is_active.text.lower() == 'true':
                    hosts.append(hostername.text)
        except Exception as e:
            common.log_utils.log_error('Error getting Zevera hosts: %s' % (e))
        common.log_utils.log_debug('Zevera Hosts: %s' % (hosts))
        return hosts

    def valid_url(self, url, host):
        if not self.hosts:
            self.hosts = self.get_all_hosters()
            
        if url:
            try: host = urlparse.urlparse(url).hostname
            except: host = 'unknown'
        if host.startswith('www.'): host = host.replace('www.', '')
        if any(host in item for item in self.hosts):
            return True

        return False

    @classmethod
    def get_settings_xml(cls):
        xml = super(cls, cls).get_settings_xml()
        xml.append('<setting id="%s_login" type="bool" label="login" default="false"/>' % (cls.__name__))
        xml.append('<setting id="%s_username" enable="eq(-1,true)" type="text" label="Username" default=""/>' % (cls.__name__))
        xml.append('<setting id="%s_password" enable="eq(-2,true)" type="text" label="Password" option="hidden" default=""/>' % (cls.__name__))
        return xml

    @classmethod
    def isUniversal(self):
        return True
