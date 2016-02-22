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


import urllib,json
import re
import urllib2
import json
import xbmcgui
import xbmc
from resources.lib.libraries import cache
from resources.lib.libraries import control
from resources.lib.libraries import client



#def getCredentials():
#    user = control.setting('realdedrid_user')
#    password = control.setting('realdedrid_password')
#    if (user == '' or password == ''): return False
#    return (user, password)


def getHosts():
    try:
        if control.setting('realdebrid_authorize') == 'false': return []
        #url = 'http://real-debrid.com/api/hosters.php'
        url = 'http://api.real-debrid.com/rest/1.0/hosts/domains'
        result = cache.get(RealDebridResolver().get_hosts(), 24, url)
        hosts = json.loads('[%s]' % result)
        hosts = [i.rsplit('.' ,1)[0].lower() for i in hosts[0]]
        print("MyHosts",hosts)
        #hosts =
        #print("MyHosts",hosts)
        return hosts
    except:
        return []


def resolve(url):
    try:
        log("---1 --- %s" % control.setting('realdebrid_authorize'),xbmc.LOGNOTICE)
        if control.setting('realdebrid_authorize') == 'false': return
        log("---2 --- %s " % control.setting('realdebrid_authorize'), xbmc.LOGNOTICE)
        print("---3---",control.setting('realdebrid_token'))

        myreal = RealDebridResolver()
        #myreal.login()

        log("Mu url: %s" % url, xbmc.LOGNOTICE)
        myurl = myreal.get_media_url('www.real-debrid.com',url)

        #login_data = urllib.urlencode({'user' : user, 'pass' : password})
        #login_link = 'http://real-debrid.com/ajax/login.php?%s' % login_data
        #result = client.source(login_link, close=False)
        #result = json.loads(result)
        #error = result['error']
        #if not error == 0: raise Exception()
        #cookie = result['cookie']

        #url = 'http://real-debrid.com/ajax/unrestrict.php?link=%s' % url
        #url = url.replace('filefactory.com/stream/', 'filefactory.com/file/')
        #result = client.source(url, cookie=cookie, close=False)
        #result = json.loads(result)
        #url = result['generated_links'][0][-1]
        #url = '%s|Cookie=%s' % (url, urllib.quote_plus(cookie))
        return myurl
    except:
        return



#from urlresolver.plugnplay.interfaces import UrlResolver
#from urlresolver.plugnplay.interfaces import SiteAuth
#from urlresolver.plugnplay.interfaces import PluginSettings
#from urlresolver.plugnplay import Plugin
#from urlresolver import common
#from t0mm0.common.net import Net

CLIENT_ID = 'MUQMIQX6YWDSU'
USER_AGENT = 'URLResolver for Kodi/SPECTO'
INTERVALS = 100

class UrlResolver:

    class ResolverError(Exception):
        xbmc.log('[SPECTO RES1]: %s' % (Exception), xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    # override message level to force logging when addon logging turned on
    #if addon.getSetting('addon_debug') == 'true' and level == xbmc.LOGDEBUG:
    level = xbmc.LOGNOTICE

    try:
        if isinstance(msg, unicode):
            msg = '%s (ENCODED)' % (msg.encode('utf-8'))

        xbmc.log('[SPECTO]: %s' % (msg), level)
    except Exception as e:
        try: xbmc.log('Logging Failure: %s' % (e), level)
        except: pass  # just give up



class RealDebridResolver():
    name = "Real-Debrid"
    domains = ["*"]

    def __init__(self):
        self.hosters = None
        self.hosts = None
        self.headers = {'User-Agent': USER_AGENT}

    def get_media_url(self, host, media_id, retry=False):
        try:
            url = 'http://api.real-debrid.com/rest/1.0/unrestrict/link'
            headers = self.headers
            headers['Authorization'] = 'Bearer %s' % (control.setting('realdebrid_token'))
            data = {'link': media_id}
            myresult = client.request(url, post=data, headers=headers,output='response2')
            result = myresult[1]
            log(">>> RealDebrid res %s   >>>>>> DATA: %s " % (myresult[0],myresult [1]))
            if myresult[0] != '200':
                raise ValueError(myresult[0])
        except ValueError as e:
            log("RealDebrid ERROR %s RETRY: %s" % (e,retry))
            print ("Myre",e,myresult[0]=='401',control.setting('realdebrid_refresh'))
            if not retry and myresult[0] == 401:
                if control.setting('realdebrid_refresh'):
                    self.refresh_token()
                    return self.get_media_url(host, media_id, retry=True)
                else:
                    control.set_setting('realdebrid_client_id', '')
                    control.set_setting('realdebrid_client_secret', '')
                    control.set_setting('realdebrid_token', '')
                    raise UrlResolver.ResolverError('Real Debrid Auth Failed & No Refresh Token')
            else:
                try:
                    js_result = json.loads(e.read())
                    if 'error' in js_result:
                        msg = js_result['error']
                    else:
                        msg = 'Unknown Error (1)'
                except:
                    msg = 'Unknown Error (2)'
                raise UrlResolver.ResolverError('Real Debrid Error: %s (%s)' % (msg, e.code))
        except Exception as e:
            raise UrlResolver.ResolverError('Unexpected Exception during RD Unrestrict: %s' % (e))
        else:
            js_result = json.loads(result)
            links = []
            link = self.__get_link(js_result)
            if link is not None: links.append(link)
            if 'alternative' in js_result:
                for alt in js_result['alternative']:
                    link = self.__get_link(alt)
                    if link is not None: links.append(link)

            if len(links) == 1 or control.setting('realdebrid_autopick') == 'true':
                return links[0][1]
            elif len(links) > 1:
                sd = xbmcgui.Dialog()
                ret = sd.select('Select a Link', [link[0] for link in links])
                if ret > -1:
                    return links[ret][1]
            else:
                raise UrlResolver.ResolverError('No usable link from Real Debrid')

    def __get_link(self, link):
        if 'download' in link:
            if 'quality' in link:
                label = '[%s] %s' % (link['quality'], link['download'])
            else:
                label = link['download']
            return (label, link['download'])

    # SiteAuth methods
    def login(self):
        print("login - 1")
        if control.setting('realdebrid_token') == '':
            print("login - 2")
            self.authorize_resolver()

    def refresh_token(self):
        print("Refresh",control.setting('realdebrid_client_id'))
        url = 'http://api.real-debrid.com/oauth/v2/token'
        client_id = control.setting('realdebrid_client_id')
        client_secret = control.setting('realdebrid_client_secret')
        refresh_token = control.setting('realdebrid_refresh')
        data = {'client_id': client_id, 'client_secret': client_secret, 'code': refresh_token, 'grant_type': 'http://oauth.net/grant_type/device/1.0'}
        log('Refreshing Expired Real Debrid Token: |%s|%s|' % (client_id, refresh_token))
        try:
            js_result = json.loads(client.source(url, post=data, headers=self.headers))
            log('Refreshed Real Debrid Token: |%s|' % (js_result))
            control.set_setting('realdebrid_token', js_result['access_token'])
            control.set_setting('realdebrid_refresh', js_result['refresh_token'])
        except Exception as e:
            # empty all auth settings to force a re-auth on next use
            control.set_setting('realdebrid_client_id', '')
            control.set_setting('realdebrid_client_secret', '')
            control.set_setting('realdebrid_token', '')
            control.set_setting('realdebrid_refresh', '')
            raise UrlResolver.ResolverError('Unable to Refresh Real Debrid Token: %s' % (e))

    def authorize_resolver(self):
        log("Auth - 1")
        url = 'https://api.real-debrid.com/oauth/v2/device/code?client_id=%s&new_credentials=yes' % (CLIENT_ID)
        log("Auth - 2")
        mydata = client.request(url, headers=self.headers)
        print("Auth - 3", mydata)
        js_result = json.loads(mydata)
        print("Auth - 4",js_result)
        pd = xbmcgui.DialogProgress()
        line1 = 'Go to URL: %s' % (js_result['verification_url'])
        line2 = 'When prompted enter: %s' % (js_result['user_code'])
        print("Auth - 5",line1,line2)

        try:
            pd.create('URL Resolver Real Debrid Authorization', line1, line2)

            interval = int(js_result['interval']) * 30000
            device_code = js_result['device_code']
            print("sleep - 4",interval)

            while True:
                try:
                    for i in range(INTERVALS):
                        print("Auth - 7",i)
                        pd.update( i)
                        if pd.iscanceled(): break
                        xbmc.sleep(interval / INTERVALS)
                    url = 'https://api.real-debrid.com/oauth/v2/device/credentials?client_id=%s&code=%s' % (CLIENT_ID, device_code)
                    js_result = json.loads(client.source(url, headers=self.headers))
                    print("Auth - 6",js_result)

                except Exception as e:
                    log('Exception during RD auth: %s' % (e))

                else:
                    break
        finally:
            pd.close()

        url = 'https://api.real-debrid.com/oauth/v2/token'
        data = {'client_id': js_result['client_id'], 'client_secret': js_result['client_secret'], 'code': device_code, 'grant_type': 'http://oauth.net/grant_type/device/1.0'}
        control.set_setting('realdebrid_client_id', js_result['client_id'])
        control.set_setting('realdebrid_client_secret', js_result['client_secret'])
        log('Authorizing Real Debrid: %s' % (js_result['client_id']))
        js_result = json.loads(client.source(url, post=data, headers=self.headers))
        log('Authorizing Real Debrid Result: |%s|' % (js_result))
        control.set_setting('realdebrid_token', js_result['access_token'])
        control.set_setting('realdebrid_refresh', js_result['refresh_token'])

    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'www.real-debrid.com', url

    def get_all_hosters(self):
        if self.hosters is None:
            try:
                url = 'http://api.real-debrid.com/rest/1.0/hosts/regex'
                self.hosters = []
                js_result = json.loads(client.source(url, headers=self.headers).content)
                regexes = [regex.lstrip('/').rstrip('/').replace('\/', '/') for regex in js_result]
                self.hosters = [re.compile(regex) for regex in regexes]
            except Exception as e:
                log('Error getting RD regexes: %s' % (e))
                self.hosters = []
        log('RealDebrid hosters : %s' % self.hosters)
        return self.hosters

    def get_hosts(self):
        if self.hosts is None:
            try:
                url = 'http://api.real-debrid.com/rest/1.0/hosts/domains'
                self.hosts = json.loads(client.source(url, headers=self.headers))
            except Exception as e:
                log('Error getting RD hosts: %s' % (e))
                self.hosts = []
        #log('RealDebrid hosts : %s' % self.hosts)

    def valid_url(self, url, host):
        if control.setting('realdebrid_authorize') == 'false': return False
        log('in valid_url %s : %s' % (url, host))
        if url:
            self.get_all_hosters()
            for host in self.hosters:
                # log('RealDebrid checking host : %s' %str(host))
                if re.search(host, url):
                    log('RealDebrid Match found')
                    return True
        elif host:
            self.get_hosts()
            if host.startswith('www.'): host = host.replace('www.', '')
            if any(host in item for item in self.hosts):
                return True
        return False
"""
        self.trakt_user = control.setting('trakt_user')

    # PluginSettings methods
    def get_settings_xml(self):
        xml = PluginSettings.get_settings_xml(self)
        xml += '<setting id="%s_authorize" type="bool" label="I have a Real Debrid Account" default="false"/>\n' % (self.__class__.__name__)
        xml += '<setting type="lsep" label="***RD Authorization will be performed when you select the first RD link***"/>\n'
        xml += '<setting id="%s_autopick" type="bool" label="Choose Primary Link Automatically" default="false"/>\n' % (self.__class__.__name__)
        xml += '<setting id="%s_token" visible="false" type="text" default=""/>\n' % (self.__class__.__name__)
        xml += '<setting id="%s_refresh" visible="false" type="text" default=""/>\n' % (self.__class__.__name__)
        xml += '<setting id="%s_client_id" visible="false" type="text" default=""/>\n' % (self.__class__.__name__)
        xml += '<setting id="%s_client_secret" visible="false" type="text" default=""/>\n' % (self.__class__.__name__)
        return xml

    # to indicate if this is a universal resolver
    def isUniversal(self):
        return True
"""

myrealdebrid =  RealDebridResolver()
myh = myrealdebrid.get_hosts()
