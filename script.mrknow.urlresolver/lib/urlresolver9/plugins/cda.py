"""
    urlresolver XBMC Addon
    Copyright (C) 2015 tknorris

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
from lib import jsunpack
from urlresolver9 import common
from urlresolver9.resolver import UrlResolver, ResolverError

class VideowoodResolver(UrlResolver):
    name = "cda"
    domains = ['cda.pl', 'www.cda.pl', 'ebd.cda.pl']
    pattern = '(?://|\.)(cda\.pl)/(?:.\d+x\d+|video)/([0-9a-zA-Z]+).*?'

    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        print "ALA CDA"
        web_url = self.get_url(host, media_id)
        headers = {'Referer': web_url, 'User-Agent': common.FF_USER_AGENT}
        html = self.net.http_GET(web_url, headers=headers).content
        #print html
        try: html = html.encode('utf-8')
        except: pass
        #if "This video doesn't exist." in html:
        #    raise ResolverError('The requested video was not found.')
        
        #match = re.search('<a data-quality="(.*?)" href="(.*?)".*?>(.*?)</a>', html, re.DOTALL)
        match = re.compile('<a data-quality="(.*?)" href="(.*?)".*?>(.*?)</a>', re.DOTALL).findall(html)
        match20 = re.search("['\"]file['\"]:['\"](.*?\.mp4)['\"]", html)

        print match

        if match:
            mylinks =sorted(match, key=lambda x: x[2])
            print mylinks[-1][1]
            html = self.net.http_GET(mylinks[-1][1], headers=headers).content
            #print html
            match20 = re.search("['\"]file['\"]:['\"](.*?\.mp4)['\"]", html)
            if match20:
                mylink = match20.group(1).replace("\\", "")
                print "CDA.PL - STEP 3 %s " % mylink
                return mylink + '|Cookie=PHPSESSID=1&Referer=http://static.cda.pl/flowplayer/flash/flowplayer.commercial-3.2.18.swf'

            html = jsunpack.unpack(re.search("eval(.*?)\{\}\)\)", html, re.DOTALL).group(1))
            match7 = re.search('src="(.*?).mp4"',html)
            if match7:
                return match7.group(1)+'.mp4|Cookie=PHPSESSID=1&Referer=http://static.cda.pl/flowplayer/flash/flowplayer.commercial-3.2.18.swf'            #aa_text = aa_decoder.AADecoder(match.group(1)).decode()
        else:
            match20 = re.search("['\"]file['\"]:['\"](.*?\.mp4)['\"]", html)
            if match20:
                mylink = match20.group(1).replace("\\", "")
                print "CDA.PL - STEP 3 %s " % mylink
                return mylink + '|Cookie=PHPSESSID=1&Referer=http://static.cda.pl/flowplayer/flash/flowplayer.commercial-3.2.18.swf'
            html1 = jsunpack.unpack(re.search("eval(.*?)\{\}\)\)", html, re.DOTALL).group(1))
            match7 = re.search('src="(.*?).mp4"',html1)

            if match7:
                return match7.group(1)+'.mp4|Cookie=PHPSESSID=1&Referer=http://static.cda.pl/flowplayer/flash/flowplayer.commercial-3.2.18.swf'            #aa_text = aa_decoder.AADecoder(match.group(1)).decode()
        raise ResolverError('Video Link Not Found')

    def get_url(self, host, media_id):
        return 'http://ebd.cda.pl/620x368/%s' % media_id

