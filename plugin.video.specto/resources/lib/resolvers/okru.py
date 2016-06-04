# -*- coding: utf-8 -*-

'''
    Specto Add-on
    Copyright (C) 2015 lambda

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
'''


import re,urllib,urlparse,base64, json
from resources.lib.libraries import client
from resources.lib.libraries import control


OPERA_USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36 OPR/34.0.2036.50'
header = {"User-Agent": OPERA_USER_AGENT}
qual_map = {'full': '1080', 'hd': '720', 'sd': '480', 'low': '360', 'lowest': '240', 'mobile': '144'}


def __replaceQuality(qual):
    return qual_map.get(qual.lower(), '000')


def __get_Metadata(media_id):
    url = "http://www.ok.ru/dk?cmd=videoPlayerMetadata&mid=" + media_id
    html = client.source(url, headers=header)
    json_data = json.loads(html)
    info = dict()
    info['urls'] = []
    for entry in json_data['videos']:
        info['urls'].append(entry)
    return info

def resolve(url):
    try:
        purged_jsonvars = {}
        lines = []
        best = '0'
        #referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        #(?://|\.)(ok.ru|odnoklassniki.ru)/(?:videoembed|video)/(.+)
        media_id = re.compile('(?://|\.)(ok.ru|odnoklassniki.ru)/(?:videoembed|video)/(.+)').findall(url)[0][1]
        vids = __get_Metadata(media_id)
        #control.log('saaa %s ' % vids)

        for entry in vids['urls']:
            quality = __replaceQuality(entry['name'])
            lines.append(quality)
            purged_jsonvars[quality] = entry['url'] + '|' + urllib.urlencode(header)
            if int(quality) > int(best): best = quality

        if len(lines) == 1:
            return purged_jsonvars[lines[0]].encode('utf-8')
        else:
            return purged_jsonvars[str(best)].encode('utf-8')

        if result != -1:
            return purged_jsonvars[lines[result]].encode('utf-8')
        else:
            raise ResolverError('No link selected')

        raise ResolverError('No video found')
#        swf = re.compile('src\s*=[\'|\"](.+?player.+?\.js)[\'|\"]').findall(result)[0]

    except:
        return


