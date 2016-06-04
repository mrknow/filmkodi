"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0, JUL1EN094

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

import os
import sys
import re
import urllib
import json
import xbmcgui
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class AllDebridResolver(UrlResolver):
    name = "AllDebrid"
    domains = ['*']
    profile_path = common.profile_path
    cookie_file = os.path.join(profile_path, '%s.cookies' % name)
    media_url = None

    def __init__(self):
        self.allHosters = None
        self.net = common.Net()
        try:
            os.makedirs(os.path.dirname(self.cookie_file))
        except OSError:
            pass

    # UrlResolver methods
    def get_media_url(self, host, media_id):
        common.log_utils.log('in get_media_url %s : %s' % (host, media_id))
        try:
            url = 'http://www.alldebrid.com/service.php?link=%s' % media_id
            source = self.net.http_GET(url).content
            source = source.decode('utf-8')
        except Exception, e:
            raise ResolverError('alldebrid : error contacting the site')

        if re.search('login', source):
            raise ResolverError('alldebrid : Your account may have expired')
        if re.search('Hoster unsupported or under maintenance', source):
            raise ResolverError('alldebrid : unsupported hoster')
        # Go
        finallink = ''
        # try json return
        try:
            link = json.loads(source)
            streaming = link['streaming']
            line = []
            for item in streaming:
                line.append(item.encode('utf-8'))
            result = xbmcgui.Dialog().select('Choose the link', line)
            if result != -1:
                finallink = streaming[str(line[result])].encode('utf-8')
        # classic method
        except:
            link = re.compile("href='(.+?)'").findall(source)
            if len(link) != 0:
                finallink = link[0].encode('utf-8')
        # end
        common.log_utils.log('finallink is %s' % finallink)
        if finallink != '':
            self.media_url = finallink
            return finallink
        # false/errors
        elif 'Invalid link' in source:
            raise ResolverError('Invalid link')
        else:
            raise ResolverError('No generated_link')

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'www.alldebrid.com', url

    @common.cache.cache_method(cache_limit=8)
    def get_all_hosters(self):
        url = 'http://alldebrid.com/api.php?action=get_host'
        html = self.net.http_GET(url).content
        html = html.replace('"', '')
        return html.split(',')

    def valid_url(self, url, host):
        if self.allHosters is None:
            self.allHosters = self.get_all_hosters()
            
        common.log_utils.log_debug('in valid_url %s : %s' % (url, host))
        if url:
            match = re.search('//(.*?)/', url)
            if match:
                host = match.group(1)
            else:
                return False

        if host.startswith('www.'): host = host.replace('www.', '')
        if host and any(host in item for item in self.allHosters):
            return True

        return False

    def checkLogin(self):
        url = 'http://alldebrid.com/service.php'
        if not os.path.exists(self.cookie_file):
            return True
        self.net.set_cookies(self.cookie_file)
        source = self.net.http_GET(url).content
        common.log_utils.log(source)
        if re.search('login', source):
            common.log_utils.log('checkLogin returning False')
            return False
        else:
            common.log_utils.log('checkLogin returning True')
            return True

    # SiteAuth methods
    def login(self):
        if self.checkLogin():
            try:
                common.log_utils.log('Need to login since session is invalid')
                login_data = urllib.urlencode({'action': 'login', 'login_login': self.get_setting('username'), 'login_password': self.get_setting('password')})
                url = 'http://alldebrid.com/register/?' + login_data
                source = self.net.http_GET(url).content
                if re.search('Control panel', source):
                    self.net.save_cookies(self.cookie_file)
                    self.net.set_cookies(self.cookie_file)
                    return True
            except:
                common.log_utils.log('error with http_GET')
                raise ResolverError('Unexpected Error during login')
            else:
                return False
        else:
            return True

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
