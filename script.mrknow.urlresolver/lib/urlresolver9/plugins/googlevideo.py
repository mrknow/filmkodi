"""
    Kodi urlresolver plugin
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

from urlresolver9 import common, hmf
from urlresolver9.resolver import UrlResolver, ResolverError
from lib import helpers
import re
import json
import urllib2


class GoogleResolver(UrlResolver):
    name = "googlevideo"
    domains = ["googlevideo.com", "googleusercontent.com", "get.google.com",
               "plus.google.com", "googledrive.com", "drive.google.com", "docs.google.com"]
    pattern = 'https?://(.*?(?:\.googlevideo|(?:plus|drive|get|docs)\.google|google(?:usercontent|drive))\.com)/(.*?(?:videoplayback\?|[\?&]authkey|host/)*.+)'

    def __init__(self):
        self.net = common.Net()
        self.itag_map = {'5': '240', '6': '270', '17': '144', '18': '360', '22': '720', '34': '360', '35': '480',
                         '36': '240', '37': '1080', '38': '3072', '43': '360', '44': '480', '45': '720', '46': '1080',
                         '82': '360 [3D]', '83': '480 [3D]', '84': '720 [3D]', '85': '1080p [3D]', '100': '360 [3D]',
                         '101': '480 [3D]', '102': '720 [3D]', '92': '240', '93': '360', '94': '480', '95': '720',
                         '96': '1080', '132': '240', '151': '72', '133': '240', '134': '360', '135': '480',
                         '136': '720', '137': '1080', '138': '2160', '160': '144', '264': '1440',
                         '298': '720', '299': '1080', '266': '2160', '167': '360', '168': '480', '169': '720',
                         '170': '1080', '218': '480', '219': '480', '242': '240', '243': '360', '244': '480',
                         '245': '480', '246': '480', '247': '720', '248': '1080', '271': '1440', '272': '2160',
                         '302': '2160', '303': '1080', '308': '1440', '313': '2160', '315': '2160', '59': '480'}

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        response, video_urls = self._parse_google(web_url)
        if video_urls:
            video = helpers.pick_source(video_urls)
        else:
            video = None

        headers = {'User-Agent': common.FF_USER_AGENT}
        if response is not None:
            res_headers = response.get_headers(as_dict=True)
            if 'Set-Cookie' in res_headers:
                headers['Cookie'] = res_headers['Set-Cookie']

        if not video:
            if ('redirector.' in web_url) or ('googleusercontent' in web_url):
                video = urllib2.urlopen(web_url).geturl()
            elif 'googlevideo.' in web_url:
                video = web_url + helpers.append_headers(headers)
        else:
            if ('redirector.' in video) or ('googleusercontent' in video):
                video = urllib2.urlopen(video).geturl()

        if video:
            if 'plugin://' in video:  # google plus embedded videos may result in this
                return video
            else:
                return video + helpers.append_headers(headers)

        raise ResolverError('File not found')

    def get_url(self, host, media_id):
        return 'https://%s/%s' % (host, media_id)

    def _parse_google(self, link):
        sources = []
        response = None
        if re.match('https?://get[.]', link):
            if link.endswith('/'): link = link[:-1]
            vid_id = link.split('/')[-1]
            response = self.net.http_GET(link)
            sources = self.__parse_gget(vid_id, response.content)
        elif re.match('https?://plus[.]', link):
            response = self.net.http_GET(link)
            sources = self.__parse_gplus(response.content)
        elif 'drive.google' in link or 'docs.google' in link:
            response = self.net.http_GET(link)
            sources = self._parse_gdocs(response.content)
        return response, sources

    def __parse_gplus(self, html):
        sources = []
        match = re.search('<c-wiz.+?track:impression,click".*?jsdata\s*=\s*".*?(http[^"]+)"', html, re.DOTALL)
        if match:
            source = match.group(1).replace('&amp;', '&').split(';')[0]
            resolved = hmf.HostedMediaFile(url=source).resolve()
            if resolved:
                sources.append(('Unknown Quality', resolved))
        return sources

    def __parse_gget(self, vid_id, html):
        sources = []
        match = re.search('.+return\s+(\[\[.*?)\s*}}', html, re.DOTALL)
        if match:
            try:
                js = self.parse_json(match.group(1))
                for top_item in js:
                    if isinstance(top_item, list):
                        for item in top_item:
                            if isinstance(item, list):
                                for item2 in item:
                                    if isinstance(item2, list):
                                        for item3 in item2:
                                            if vid_id in str(item3):
                                                sources = self.__extract_video(item2)
                                                if sources:
                                                    return sources
            except Exception as e:
                pass
        return sources

    def __extract_video(self, item):
        sources = []
        for e in item:
            if isinstance(e, dict):
                for key in e:
                    for item2 in e[key]:
                        if isinstance(item2, list):
                            for item3 in item2:
                                if isinstance(item3, list):
                                    for item4 in item3:
                                        if isinstance(item4, unicode):
                                            item4 = item4.encode('utf-8')
                                            
                                        if isinstance(item4, basestring):
                                            item4 = urllib2.unquote(item4).decode('unicode_escape')
                                            for match in re.finditer('url=(?P<link>[^&]+).*?&itag=(?P<itag>[^&]+)', item4):
                                                link = match.group('link')
                                                itag = match.group('itag')
                                                quality = self.itag_map.get(itag, 'Unknown Quality [%s]' % itag)
                                                sources.append((quality, link))
                                            if sources:
                                                return sources
        return sources

    def _parse_gdocs(self, html):
        urls = []
        for match in re.finditer('\[\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\]', html):
            key, value = match.groups()
            if key == 'fmt_stream_map':
                items = value.split(',')
                for item in items:
                    _source_itag, source_url = item.split('|')
                    if isinstance(source_url, unicode):
                        source_url = source_url.encode('utf-8')
                        
                    source_url = source_url.decode('unicode_escape')
                    quality = self.itag_map.get(_source_itag, 'Unknown Quality [%s]' % _source_itag)
                    source_url = urllib2.unquote(source_url)
                    urls.append((quality, source_url))
                return urls

        return urls

    @staticmethod
    def parse_json(html):
        if html:
            try:
                if not isinstance(html, unicode):
                    if html.startswith('\xef\xbb\xbf'):
                        html = html[3:]
                    elif html.startswith('\xfe\xff'):
                        html = html[2:]
                js_data = json.loads(html)
                if js_data is None:
                    return {}
                else:
                    return js_data
            except ValueError:
                return {}
        else:
            return {}
