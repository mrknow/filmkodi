# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 lambda

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


import urllib,json,time
import urlparse

from resources.lib.libraries import cache
from resources.lib.libraries import control
from resources.lib.libraries import client


def rdAuthorize():
    try:
        CLIENT_ID = 'TC3DG7YFNBKQK'
        USER_AGENT = 'SPECTO for Kodi/1.0'

        if not '' in credentials()['realdebrid'].values():
            if control.yesnoDialog(control.lang(32411).encode('utf-8'), control.lang(32413).encode('utf-8'), '', 'RealDebrid', control.lang(32415).encode('utf-8'), control.lang(32414).encode('utf-8')):
                control.set_setting('realdebrid_client_id','')
                control.set_setting('realdebrid_client_secret', '')
                control.set_setting('realdebrid_token', '')
                control.set_setting('realdebrid_refresh', '')
                control.set_setting('realdebrid_auth', '')
            raise Exception()

        headers = {'User-Agent': USER_AGENT}
        url = 'https://api.real-debrid.com/oauth/v2/device/code?client_id=%s&new_credentials=yes' % (CLIENT_ID)
        result = client.request(url, headers=headers)
        result = json.loads(result)
        verification_url = control.lang(30416).encode('utf-8') + '[COLOR skyblue]%s[/COLOR]' % (result['verification_url'])
        user_code = control.lang(30417).encode('utf-8') + '[COLOR skyblue]%s[/COLOR]' % (result['user_code'])
        device_code = result['device_code']
        interval = result['interval']

        progressDialog = control.progressDialog
        progressDialog.create('RealDebrid', verification_url, user_code)

        for i in range(0, 3600):
            try:
                if progressDialog.iscanceled(): break
                time.sleep(1)
                if not float(i) % interval == 0: raise Exception()
                url = 'https://api.real-debrid.com/oauth/v2/device/credentials?client_id=%s&code=%s' % (CLIENT_ID, device_code)
                result = client.request(url, headers=headers, error=True)
                result = json.loads(result)
                if 'client_secret' in result: break
            except:
                pass

        try: progressDialog.close()
        except: pass

        id, secret = result['client_id'], result['client_secret']

        url = 'https://api.real-debrid.com/oauth/v2/token'
        post = {'client_id': id, 'client_secret': secret, 'code': device_code, 'grant_type': 'http://oauth.net/grant_type/device/1.0'}

        result = client.request(url, post=post, headers=headers)
        result = json.loads(result)

        token, refresh = result['access_token'], result['refresh_token']

        control.set_setting('realdebrid_client_id', id)
        control.set_setting('realdebrid_client_secret', secret)
        control.set_setting('realdebrid_token', token)
        control.set_setting('realdebrid_refresh', refresh)
        control.set_setting('realdebrid_auth', '*************')
        raise Exception()
    except:
        control.openSettings('3.13')


def rdDict():
    try:
        if '' in credentials()['realdebrid'].values(): raise Exception()
        url = 'https://api.real-debrid.com/rest/1.0/hosts/domains'
        result = cache.get(client.request, 24, url)
        hosts = json.loads(result)
        hosts = [i.lower() for i in hosts]
        return hosts
    except:
        return []


def pzDict():
    try:
        if '' in credentials()['premiumize'].values(): raise Exception()
        user, password = credentials()['premiumize']['user'], credentials()['premiumize']['pass']
        url = 'http://api.premiumize.me/pm-api/v1.php?method=hosterlist&params[login]=%s&params[pass]=%s' % (user, password)
        result = cache.get(client.request, 24, url)
        hosts = json.loads(result)['result']['hosterlist']
        hosts = [i.lower() for i in hosts]
        return hosts
    except:
        return []


def adDict():
    try:
        if '' in credentials()['alldebrid'].values(): raise Exception()
        url = 'http://alldebrid.com/api.php?action=get_host'
        result = cache.get(client.request, 24, url)
        hosts = json.loads('[%s]' % result)
        hosts = [i.lower() for i in hosts]
        return hosts
    except:
        return []


def rpDict():
    try:
        if '' in credentials()['rpnet'].values(): raise Exception()
        url = 'http://premium.rpnet.biz/hoster2.json'
        result = cache.get(client.request, 24, url)
        result = json.loads(result)
        hosts = result['supported']
        hosts = [i.lower() for i in hosts]
        return hosts
    except:
        return []


def debridDict():
    return {
    'realdebrid': rdDict(),
    'premiumize': pzDict(),
    'alldebrid': adDict(),
    'rpnet': rpDict()
    }


def credentials():
    return {
        'realdebrid': {
        'id': control.setting('realdebrid_client_id'),
        'secret': control.setting('realdebrid_client_secret'),
        'token': control.setting('realdebrid_token'),
        'refresh': control.setting('realdebrid_refresh')
    },
        'premiumize': {
        'user': control.setting('premiumize.user'),
        'pass': control.setting('premiumize.pin')
    },
        'alldebrid': {
        'user': control.setting('alldebrid.user'),
        'pass': control.setting('alldebrid.pass')
    },
        'rpnet': {
        'user': control.setting('rpnet.user'),
        'pass': control.setting('rpnet.api')
    }}


def status():
    try:
        c = [i for i in credentials().values() if not '' in i.values()]
        if len(c) == 0: return False
        else: return True
    except:
        return False

def getHosts():
    myhosts = rdDict()
    for i in range(len(myhosts)):
        myhosts[i] = myhosts[i].split('.')[-2].encode('utf-8')

    #control.log("@@@@  REALDEBRID HOSTS %s ### " % (myhosts))
    return myhosts


def resolve(url, debrid='realdebrid'):
    u = url
    u = u.replace('filefactory.com/stream/', 'filefactory.com/file/')
    #control.log("@@@@  REALDEBRID INIT %s ### %s" % (url,debrid))
    try:
        u1 = urlparse.urlparse(url)[1].split('.')
        u1 = u[-2] + '.' + u[-1]
        if status() is False:raise Exception()
        if not debrid == 'realdebrid' and not debrid == True: raise Exception()
        #raise Exception()

        if '' in credentials()['realdebrid'].values(): raise Exception()
        id, secret, token, refresh = credentials()['realdebrid']['id'], credentials()['realdebrid']['secret'], credentials()['realdebrid']['token'], credentials()['realdebrid']['refresh']

        USER_AGENT = 'Kodi Exodus/3.0'

        post = {'link': u}
        headers = {'Authorization': 'Bearer %s' % token, 'User-Agent': USER_AGENT}
        url = 'http://api.real-debrid.com/rest/1.0/unrestrict/link'

        result = client.request(url, post=post, headers=headers, error=True)
        control.log('@@ DEBRID  RESULTS@@ %s' % result)

        result = json.loads(result)

        if 'error' in result and result['error'] == 'bad_token':
            result = client.request('https://api.real-debrid.com/oauth/v2/token', post={'client_id': id, 'client_secret': secret, 'code': refresh, 'grant_type': 'http://oauth.net/grant_type/device/1.0'}, headers={'User-Agent': USER_AGENT}, error=True)
            result = json.loads(result)
            control.log('Refreshing Expired Real Debrid Token: |%s|%s|' % (id, refresh))
            control.log('Refreshing Expired : |%s|' % (result))

            if 'error' in result: return
            token, refresh = result['access_token'], result['refresh_token']

            control.set_setting('realdebrid_token', token)
            control.set_setting('realdebrid_refresh', refresh)

            headers['Authorization'] = 'Bearer %s' % result['access_token']
            result = client.request(url, post=post, headers=headers)
            result = json.loads(result)
        if 'error' in result and result['error'] == 'file_unavailable':
            control.log("@@@@  REALDEBRID FILE UNAVAIL %s ### %s" % (url))

            return

        url = result['download']
        control.log('@@ DEBRID  URl@@ %s' % url)

        return url
    except:
        pass

    try:
        if not debrid == 'premiumize' and not debrid == True: raise Exception()

        if '' in credentials()['premiumize'].values(): raise Exception()
        user, password = credentials()['premiumize']['user'], credentials()['premiumize']['pass']

        url = 'http://api.premiumize.me/pm-api/v1.php?method=directdownloadlink&params[login]=%s&params[pass]=%s&params[link]=%s' % (user, password, urllib.quote_plus(u))
        result = client.request(url, close=False)
        url = json.loads(result)['result']['location']
        return url
    except:
        pass

    try:
        if not debrid == 'alldebrid' and not debrid == True: raise Exception()

        if '' in credentials()['alldebrid'].values(): raise Exception()
        user, password = credentials()['alldebrid']['user'], credentials()['alldebrid']['pass']

        login_data = {'action': 'login', 'login_login': user, 'login_password': password}
        login_link = 'http://alldebrid.com/register/?%s' % login_data
        cookie = client.request(login_link, output='cookie', close=False)

        url = 'http://www.alldebrid.com/service.php?link=%s' % urllib.quote_plus(u)
        result = client.request(url, cookie=cookie, close=False)
        url = client.parseDOM(result, 'a', ret='href', attrs = {'class': 'link_dl'})[0]
        url = client.replaceHTMLCodes(url)
        url = '%s|Cookie=%s' % (url, urllib.quote_plus(cookie))
        return url
    except:
        pass

    try:
        if not debrid == 'rpnet' and not debrid == True: raise Exception()

        if '' in credentials()['rpnet'].values(): raise Exception()
        user, password = credentials()['rpnet']['user'], credentials()['rpnet']['pass']

        login_data = {'username': user, 'password': password, 'action': 'generate', 'links': u}
        login_link = 'http://premium.rpnet.biz/client_api.php?%s' % login_data
        result = client.request(login_link, close=False)
        result = json.loads(result)
        url = result['links'][0]['generated']
        return url
    except:
        return




