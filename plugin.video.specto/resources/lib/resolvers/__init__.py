# -*- coding: utf-8 -*-

'''
    Genesis Add-on
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


import re,urllib,urlparse

from resources.lib.libraries import client
from resources.lib.resolvers import realdebrid
from resources.lib.resolvers import premiumize


def request(url):
    try:
        if '</regex>' in url:
            import regex ; url = regex.resolve(url)

        rd = realdebrid.resolve(url)
        if not rd == None: return rd
        pz = premiumize.resolve(url)
        if not pz == None: return pz

        if url.startswith('rtmp'):
            if len(re.compile('\s*timeout=(\d*)').findall(url)) == 0: url += ' timeout=10'
            return url

        u = urlparse.urlparse(url).netloc
        u = u.replace('www.', '').replace('embed.', '')
        u = u.lower()

        r = [i['class'] for i in info() if u in i['netloc']][0]
        r = __import__(r, globals(), locals(), [], -1)
        r = r.resolve(url)

        if r == None: return r
        elif type(r) == list: return r
        elif not r.startswith('http'): return r

        try: h = dict(urlparse.parse_qsl(r.rsplit('|', 1)[1]))
        except: h = dict('')

        if not 'User-Agent' in h: h['User-Agent'] = client.agent()
        if not 'Referer' in h: h['Referer'] = url

        r = '%s|%s' % (r.split('|')[0], urllib.urlencode(h))
        return r
    except:
        return url


def info():
    return [{
        'class': '',
        'netloc': ['oboom.com', 'rapidgator.net', 'uploaded.net'],
        'host': ['Oboom', 'Rapidgator', 'Uploaded'],
        'quality': 'High',
        'captcha': False,
        'a/c': True
    }, {
        'class': '_180upload',
        'netloc': ['180upload.com'],
        'host': ['180upload'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'allmyvideos',
        'netloc': ['allmyvideos.net'],
        'host': ['Allmyvideos'],
        'quality': 'Medium',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'allvid',
        'netloc': ['allvid.ch'],
        'host': ['Allvid'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'bestreams',
        'netloc': ['bestreams.net'],
        'host': ['Bestreams'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'clicknupload',
        'netloc': ['clicknupload.com'],
        'host': ['Clicknupload'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'cloudtime',
        'netloc': ['cloudtime.to'],
        'host': ['Cloudtime'],
        'quality': 'Medium',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'cloudyvideos',
        'netloc': ['cloudyvideos.com'],
        #'host': ['Cloudyvideos'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'cloudzilla',
        'netloc': ['cloudzilla.to'],
        'host': ['Cloudzilla'],
        'quality': 'Medium',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'daclips',
        'netloc': ['daclips.in'],
        'host': ['Daclips'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'dailymotion',
        'netloc': ['dailymotion.com']
    }, {
        'class': 'datemule',
        'netloc': ['datemule.com']
    }, {
        'class': 'divxpress',
        'netloc': ['divxpress.com'],
        'host': ['Divxpress'],
        'quality': 'Medium',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'exashare',
        'netloc': ['exashare.com'],
        'host': ['Exashare'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'fastvideo',
        'netloc': ['fastvideo.in', 'faststream.in', 'rapidvideo.ws'],
        'host': ['Fastvideo', 'Faststream'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'filehoot',
        'netloc': ['filehoot.com'],
        'host': ['Filehoot'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'filenuke',
        'netloc': ['filenuke.com', 'sharesix.com'],
        'host': ['Filenuke', 'Sharesix'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'filmon',
        'netloc': ['filmon.com']
    }, {
        'class': 'filepup',
        'netloc': ['filepup.net']
    }, {
        'class': 'googledocs',
        'netloc': ['docs.google.com', 'drive.google.com']
    }, {
        'class': 'googlephotos',
        'netloc': ['photos.google.com']
    }, {
        'class': 'googlepicasa',
        'netloc': ['picasaweb.google.com']
    }, {
        'class': 'googleplus',
        'netloc': ['plus.google.com']
    }, {
        'class': 'gorillavid',
        'netloc': ['gorillavid.com', 'gorillavid.in'],
        'host': ['Gorillavid'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'grifthost',
        'netloc': ['grifthost.com'],
        #'host': ['Grifthost'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'hdcast',
        'netloc': ['hdcast.me']
    }, {
        'class': 'hugefiles',
        'netloc': ['hugefiles.net'],
        'host': ['Hugefiles'],
        'quality': 'High',
        'captcha': True,
        'a/c': False
    }, {
        'class': 'ipithos',
        'netloc': ['ipithos.to'],
        'host': ['Ipithos'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'ishared',
        'netloc': ['ishared.eu'],
        'host': ['iShared'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'kingfiles',
        'netloc': ['kingfiles.net'],
        'host': ['Kingfiles'],
        'quality': 'High',
        'captcha': True,
        'a/c': False
    }, {
        'class': 'letwatch',
        'netloc': ['letwatch.us'],
        'host': ['Letwatch'],
        'quality': 'Medium',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'mailru',
        'netloc': ['mail.ru', 'my.mail.ru', 'videoapi.my.mail.ru', 'api.video.mail.ru']
    }, {
        'class': 'mightyupload',
        'netloc': ['mightyupload.com'],
        'host': ['Mightyupload'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'movdivx',
        'netloc': ['movdivx.com'],
        'host': ['Movdivx'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'movpod',
        'netloc': ['movpod.net', 'movpod.in'],
        'host': ['Movpod'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'movshare',
        'netloc': ['movshare.net'],
        'host': ['Movshare'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'mrfile',
        'netloc': ['mrfile.me'],
        'host': ['Mrfile'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'mybeststream',
        'netloc': ['mybeststream.xyz']
    }, {
        'class': 'nosvideo',
        'netloc': ['nosvideo.com'],
        #'host': ['Nosvideo'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'novamov',
        'netloc': ['novamov.com'],
        'host': ['Novamov'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'nowvideo',
        'netloc': ['nowvideo.eu', 'nowvideo.sx'],
        'host': ['Nowvideo'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'openload',
        'netloc': ['openload.io', 'openload.co'],
        'host': ['Openload'],
        'quality': 'High',
        'captcha': True,
        'a/c': False
    }, {
        'class': 'p2pcast',
        'netloc': ['p2pcast.tv']
    }, {
        'class': 'primeshare',
        'netloc': ['primeshare.tv'],
        'host': ['Primeshare'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'promptfile',
        'netloc': ['promptfile.com'],
        'host': ['Promptfile'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'putstream',
        'netloc': ['putstream.com'],
        'host': ['Putstream'],
        'quality': 'Medium',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'realvid',
        'netloc': ['realvid.net'],
        'host': ['Realvid'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'sawlive',
        'netloc': ['sawlive.tv']
    }, {
        'class': 'sharerepo',
        'netloc': ['sharerepo.com'],
        'host': ['Sharerepo'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'skyvids',
        'netloc': ['skyvids.net'],
        'host': ['Skyvids'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'speedvideo',
        'netloc': ['speedvideo.net']
    }, {
        'class': 'stagevu',
        'netloc': ['stagevu.com'],
        'host': ['StageVu'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'streamcloud',
        'netloc': ['streamcloud.eu'],
        'host': ['Streamcloud'],
        'quality': 'Medium',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'streamin',
        'netloc': ['streamin.to'],
        'host': ['Streamin'],
        'quality': 'Medium',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'thefile',
        'netloc': ['thefile.me'],
        'host': ['Thefile'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'thevideo',
        'netloc': ['thevideo.me'],
        'host': ['Thevideo'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'turbovideos',
        'netloc': ['turbovideos.net'],
        'host': ['Turbovideos'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'tusfiles',
        'netloc': ['tusfiles.net'],
        'host': ['Tusfiles'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'up2stream',
        'netloc': ['up2stream.com'],
        'host': ['Up2stream'],
        'quality': 'Medium',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'uploadc',
        'netloc': ['uploadc.com', 'uploadc.ch', 'zalaa.com'],
        'host': ['Uploadc', 'Zalaa'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'uploadrocket',
        'netloc': ['uploadrocket.net'],
        'host': ['Uploadrocket'],
        'quality': 'High',
        'captcha': True,
        'a/c': False
    }, {
        'class': 'uptobox',
        'netloc': ['uptobox.com'],
        'host': ['Uptobox'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'v_vids',
        'netloc': ['v-vids.com'],
        'host': ['V-vids'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'vaughnlive',
        'netloc': ['vaughnlive.tv', 'breakers.tv', 'instagib.tv', 'vapers.tv']
    }, {
        'class': 'veehd',
        'netloc': ['veehd.com']
    }, {
        'class': 'veetle',
        'netloc': ['veetle.com']
    }, {
        'class': 'vidbull',
        'netloc': ['vidbull.com'],
        'host': ['Vidbull'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'videomega',
        'netloc': ['videomega.tv'],
        #'host': ['Videomega'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'videopremium',
        'netloc': ['videopremium.tv', 'videopremium.me']
    }, {
        'class': 'videoweed',
        'netloc': ['videoweed.es'],
        'host': ['Videoweed'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'vidlockers',
        'netloc': ['vidlockers.ag'],
        'host': ['Vidlockers'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'vidspot',
        'netloc': ['vidspot.net'],
        'host': ['Vidspot'],
        'quality': 'Medium',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'vidto',
        'netloc': ['vidto.me'],
        'host': ['Vidto'],
        'quality': 'Medium',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'vidzi',
        'netloc': ['vidzi.tv'],
        'host': ['Vidzi'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'vimeo',
        'netloc': ['vimeo.com']
    }, {
        'class': 'vk',
        'netloc': ['vk.com']
    }, {
        'class': 'vodlocker',
        'netloc': ['vodlocker.com'],
        'host': ['Vodlocker'],
        'quality': 'Low',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'xfileload',
        'netloc': ['xfileload.com'],
        'host': ['Xfileload'],
        'quality': 'High',
        'captcha': True,
        'a/c': False
    }, {
        'class': 'xvidstage',
        'netloc': ['xvidstage.com'],
        'host': ['Xvidstage'],
        'quality': 'Medium',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'youtube',
        'netloc': ['youtube.com'],
        'host': ['Youtube'],
        'quality': 'Medium',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'zettahost',
        'netloc': ['zettahost.tv'],
        'host': ['Zettahost'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }, {
        'class': 'zstream',
        'netloc': ['zstream.to'],
        'host': ['zStream'],
        'quality': 'High',
        'captcha': False,
        'a/c': False
    }]


