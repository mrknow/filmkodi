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


import re,urllib,urlparse,json
from resources.lib.libraries import client


def resolve(url):
    try:
        try: oid, id = urlparse.parse_qs(urlparse.urlparse(url).query)['oid'][0] , urlparse.parse_qs(urlparse.urlparse(url).query)['id'][0]
        except: oid, id = re.compile('\/video(.*)_(.*)').findall(url)[0]
        try: hash = urlparse.parse_qs(urlparse.urlparse(url).query)['hash'][0]
        except: hash = _hash(oid, id)

        u = 'http://api.vk.com/method/video.getEmbed?oid=%s&video_id=%s&embed_hash=%s' % (oid, id, hash)
 
        result = client.request(u)
        result = re.sub(r'[^\x00-\x7F]+',' ', result)

        try: result = json.loads(result)['response']
        except: result = _private(oid, id)

        url = []
        try: url += [{'quality': 'HD', 'url': result['url720']}]
        except: pass
        try: url += [{'quality': 'SD', 'url': result['url540']}]
        except: pass
        try: url += [{'quality': 'SD', 'url': result['url480']}]
        except: pass
        if not url == []: return url
        try: url += [{'quality': 'SD', 'url': result['url360']}]
        except: pass
        if not url == []: return url
        try: url += [{'quality': 'SD', 'url': result['url240']}]
        except: pass

        if not url == []: return url

    except:
        return


def _hash(oid, id):
    try:
        url = 'http://vk.com/al_video.php?act=show_inline&al=1&video=%s_%s' % (oid, id)
        result = client.request(url)
        result = result.replace('\'', '"').replace(' ', '')

        hash = re.compile('"hash2":"(.+?)"').findall(result)
        hash += re.compile('"hash":"(.+?)"').findall(result)
        hash = hash[0]

        return hash
    except:
        return

def _private(oid, id):
    try:
        url = 'http://vk.com/al_video.php?act=show_inline&al=1&video=%s_%s' % (oid, id)

        result = client.request(url)
        result = re.compile('var vars *= *({.+?});').findall(result)[0]
        result = re.sub(r'[^\x00-\x7F]+',' ', result)
        result = json.loads(result)

        return result
    except:
        return

