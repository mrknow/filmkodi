# -*- coding: utf-8 -*-

import os
import re
import urllib
import urlparse
import requests
import cookielib
import socket
from HTMLParser import HTMLParser
from fileUtils import fileExists, setFileContent, getFileContent

#------------------------------------------------------------------------------
socket.setdefaulttimeout(30)

#use ipv4 only
origGetAddrInfo = socket.getaddrinfo

def getAddrInfoWrapper(host, port, family=0, socktype=0, proto=0, flags=0):
    return origGetAddrInfo(host, port, socket.AF_INET, socktype, proto, flags)

# replace the original socket.getaddrinfo by our version
socket.getaddrinfo = getAddrInfoWrapper
#------------------------------------------------------------------------------

'''
    REQUEST classes
'''

class BaseRequest(object):
    
    def __init__(self, cookie_file=None):
        self.cookie_file = cookie_file
        self.s = requests.Session()
        if fileExists(self.cookie_file):
            self.s.cookies = self.load_cookies_from_lwp(self.cookie_file)
        #self.s.headers.update({'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'})
        self.s.headers.update({'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0'})
        self.s.headers.update({'Accept-Language' : 'en-US,en;q=0.5'})
        self.s.keep_alive = False
        self.url = ''
    
    def save_cookies_lwp(self, cookiejar, filename):
        lwp_cookiejar = cookielib.LWPCookieJar()
        for c in cookiejar:
            args = dict(vars(c).items())
            args['rest'] = args['_rest']
            del args['_rest']
            c = cookielib.Cookie(**args)
            lwp_cookiejar.set_cookie(c)
        lwp_cookiejar.save(filename, ignore_discard=True)

    def load_cookies_from_lwp(self, filename):
        lwp_cookiejar = cookielib.LWPCookieJar()
        lwp_cookiejar.load(filename, ignore_discard=True)
        return lwp_cookiejar
    
    def fixurl(self, url):
        #url is unicode (quoted or unquoted)
        try:
            #url is already quoted
            url = url.encode('ascii')
        except:
            #quote url if it is unicode
            parsed_link = urlparse.urlsplit(url)
            parsed_link = parsed_link._replace(netloc=parsed_link.netloc.encode('idna'),path=urllib.quote(parsed_link.path.encode('utf-8')))
            url = parsed_link.geturl().encode('ascii')
        #url is str (quoted)
        return url

    def getSource(self, url, form_data, referer, xml=False, mobile=False):
        url = self.fixurl(url)

        if not referer:
            referer = url
        else:
            referer = self.fixurl(referer)
        
        headers = {'Referer': referer}
        if mobile:
            self.s.headers.update({'User-Agent' : 'Mozilla/5.0 (iPad; CPU OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'})
            
        if xml:
            headers['X-Requested-With'] = 'XMLHttpRequest'
            
        if 'dinozap.info' in urlparse.urlsplit(url).netloc:
            headers['X-Forwarded-For'] = '178.162.222.111'
        if 'playerhd2.pw' in urlparse.urlsplit(url).netloc:
            headers['X-Forwarded-For'] = '178.162.222.121'
        if 'playerapp1.pw' in urlparse.urlsplit(url).netloc:
            headers['X-Forwarded-For'] = '178.162.222.122'
            
        if 'finecast.tv' in urlparse.urlsplit(url).netloc:
            self.s.headers.update({'Cookie' : 'PHPSESSID=d08b73a2b7e0945b3b1bb700f01f7d72'})
        
        if form_data:
            #ca**on.tv/key.php
            if 'uagent' in form_data[0]:
                form_data[0] = ('uagent',urllib.quote(self.s.headers['User-Agent']))
            
            if '123456789' in form_data[0]:
                import random
                cotok = str(random.randrange(100000000, 999999999))
                form_data[0] = ('token',cotok)
                r = self.s.post(url, headers=headers, data=form_data, timeout=20, cookies = {'token' : cotok})
            else:
                r = self.s.post(url, headers=headers, data=form_data, timeout=20)
            response  = r.text
        else:
            try:
                r = self.s.get(url, headers=headers, timeout=20)
                response  = r.text
            except (requests.exceptions.MissingSchema):
                response  = 'pass'
        print(">>>>>>>>>>>>> LEN <<<<<<<<<", len(response))
        #if len(response) > 10:
        if self.cookie_file:
            self.save_cookies_lwp(self.s.cookies, self.cookie_file)
        return HTMLParser().unescape(response)

#------------------------------------------------------------------------------

class DemystifiedWebRequest(BaseRequest):

    def __init__(self, cookiePath):
        super(DemystifiedWebRequest,self).__init__(cookiePath)

    def getSource(self, url, form_data, referer='', xml=False, mobile=False, demystify=False):
        data = super(DemystifiedWebRequest, self).getSource(url, form_data, referer, xml, mobile)
        if not data:
            return None

        if not demystify:
            # remove comments
            r = re.compile('<!--.*?(?!//)--!*>', re.IGNORECASE + re.DOTALL + re.MULTILINE)
            m = r.findall(data)
            if m:
                for comment in m:
                    data = data.replace(comment,'')
        else:
            import decryptionUtils as crypt
            data = crypt.doDemystify(data)

        return data

#------------------------------------------------------------------------------

class CachedWebRequest(DemystifiedWebRequest):

    def __init__(self, cookiePath, cachePath):
        super(CachedWebRequest,self).__init__(cookiePath)
        self.cachePath = cachePath
        self.cachedSourcePath = os.path.join(self.cachePath, 'page.html')
        self.currentUrlPath = os.path.join(self.cachePath, 'currenturl')
        self.lastUrlPath = os.path.join(self.cachePath, 'lasturl')

    def __setLastUrl(self, url):
        setFileContent(self.lastUrlPath, url)

    def __getCachedSource(self):
        try:
            data = getFileContent(self.cachedSourcePath)
        except:
            pass
        return data

    def getLastUrl(self):
        return getFileContent(self.lastUrlPath)
        

    def getSource(self, url, form_data, referer='', xml=False, mobile=False, ignoreCache=False, demystify=False):
        if 'live.xml' in url:
            self.cachedSourcePath = url
            data = self.__getCachedSource()
            return data
            
        if url == self.getLastUrl() and not ignoreCache:
            data = self.__getCachedSource()
        else:
            data = super(CachedWebRequest,self).getSource(url, form_data, referer, xml, mobile, demystify)
            if data:
                # Cache url
                self.__setLastUrl(url)
                # Cache page
                setFileContent(self.cachedSourcePath, data)
        return data
