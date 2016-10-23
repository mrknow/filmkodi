# -*- coding: UTF-8 -*-
"""
    Copyright (C) 2014  smokdpi

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

import re,os
from lib import jsunpack
from urlresolver import common
from urlresolver.resolver import UrlResolver, ResolverError

class AllVidResolver(UrlResolver):
    name = "anyfiles"
    domains = ["anyfiles.pl"]
    pattern = '(?://|\.)(anyfiles\.pl)/.*(?:id=|/)([0-9]+)'
    profile_path = common.profile_path
    cookie_file = os.path.join(profile_path, '%s.cookies' % name)


    def __init__(self):
        self.net = common.Net()
        self.user_agent = common.IE_USER_AGENT
        self.net.set_user_agent(self.user_agent)
        self.headers = {'User-Agent': self.user_agent}
        try: os.makedirs(os.path.dirname(self.cookie_file))
        except OSError: pass


    def get_media_url(self, host, media_id):
        print "media",media_id
        web_url = self.get_url(host, media_id)
        resp = self.net.http_GET(web_url)
        html = resp.content
        web_url = self.get_url2(host, media_id)
        self.headers['Referer'] = web_url
        html = self.net.http_GET(web_url, headers=self.headers).content
        r = re.search('src="/?(pcs\?code=[^"]+?)"', html, re.DOTALL)
        print r.group(1)
        if r:
            web_url = 'http://video.anyfiles.pl/%s' % r.group(1)
            html = self.net.http_GET(web_url, headers=self.headers).content
            match = re.search('(http[^"]+?mp4)',html)
            print html
            if match:
                return match.group(1)

        else:
            raise ResolverError('File not found')

    def get_url(self, host, media_id):
        #return 'http://%s/embed-%s.html' % (host, media_id)
        return "http://video.anyfiles.pl/videos.jsp?id=%s" % media_id


    def get_url2(self, host, media_id):
        # return 'http://%s/embed-%s.html' % (host, media_id)
        return "http://video.anyfiles.pl/w.jsp?id=%s&width=620&height=349&pos=&skin=0" % media_id
